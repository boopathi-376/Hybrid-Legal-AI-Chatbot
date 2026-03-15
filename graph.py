import json
import re
from typing import Dict, List, Any
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from sentence_transformers import CrossEncoder
import ollama


class GraphState(TypedDict):
    query: str
    chat_history: List[Dict[str, str]]
    standalone_query: str
    documents: List[Dict[str, Any]]
    generation: str
    thought: str
    confidence: str


class LegalRAGGraph:

    def __init__(self, hybrid_search):
        print("Initializing Production LangGraph...")

        self.hybrid_search = hybrid_search

        # KEEPING your reranker (as requested)
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        workflow = StateGraph(GraphState)

        workflow.add_node("reformulate", self.reformulate_query_node)
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("rerank", self.rerank_node)
        workflow.add_node("generate", self.generate_node)
        workflow.add_node("verify", self.verify_node)

        workflow.add_edge(START, "reformulate")
        workflow.add_edge("reformulate", "retrieve")
        workflow.add_edge("retrieve", "rerank")
        workflow.add_edge("rerank", "generate")
        workflow.add_edge("generate", "verify")
        workflow.add_edge("verify", END)

        self.app = workflow.compile()

    # --------------------------------------------------

    def reformulate_query_node(self, state: GraphState):

        query = state["query"]
        history = state.get("chat_history", [])

        if not history:
            return {"standalone_query": query}

        prompt = f"""
Conversation History:
{history[-2:]}

User Question:
{query}

Rewrite the question as a standalone legal query.
Return ONLY the rewritten question.
"""

        response = ollama.generate(
            model="llama3.2:3b",
            prompt=prompt
        )

        return {"standalone_query": response["response"].strip()}

    # --------------------------------------------------

    def retrieve_node(self, state: GraphState):

        query = state["standalone_query"]

        docs = self.hybrid_search.search(query, top_k=15)

        print("\nRetrieved Documents:")
        for d in docs[:5]:
            print(d.get("content", "")[:120])

        return {"documents": docs}

    # --------------------------------------------------

    def rerank_node(self, state: GraphState):

        query = state["standalone_query"]
        docs = state["documents"]

        if not docs:
            return {"documents": []}

        pairs = [[query, d["content"]] for d in docs]

        scores = self.reranker.predict(pairs)

        for i, doc in enumerate(docs):
            doc["rerank_score"] = float(scores[i])

        reranked = sorted(
            docs,
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        # Filter weak matches
        reranked = [d for d in reranked if d["rerank_score"] > 0.15][:5]

        return {"documents": reranked}

    # --------------------------------------------------

    def generate_node(self, state: GraphState):
        query = state["standalone_query"]
        docs = state["documents"]

        if not docs:
            return {
                "generation": "I'm sorry, I couldn't find any specific legal information in my records to answer that. Would you like to try rephrasing your question?",
                "thought": "",
                "confidence": "Low"
            }

        # Context remains the same for the LLM's knowledge
        context_text = "\n\n".join(
            [f"Source [{i+1}] (Page {d.get('page')}): {d.get('content')}" for i, d in enumerate(docs)]
        )

        # NEW: Chatbot-style Persona Prompt
        system_prompt = f"""
You are "Legal Navigator," a helpful and professional Indian Legal Assistant. 

STYLE RULES:
1. Speak CONVERSATIONALLY. Imagine you are explaining the law to a friend.
2. Use Markdown: Use **bold** for key legal terms and bullet points for steps.
3. NO CITATIONS: Do not mention "Source [X]" or "Page Y" in your output text. 
4. Be empathetic but accurate.
5. If the information is missing, say you don't have the specific details in your records yet.

Context for your knowledge:
{context_text}
"""

        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
        )

        raw_content = response["message"]["content"]
        
        # Standard cleaning of <think> tags
        thought_match = re.search(r"<think>(.*?)(?:</think>|$)", raw_content, re.DOTALL | re.IGNORECASE)
        thought = thought_match.group(1).strip() if thought_match else ""
        clean_answer = re.sub(r"<think>.*?(?:</think>|$)", "", raw_content, flags=re.DOTALL | re.IGNORECASE).strip()

        return {
            "generation": clean_answer,
            "thought": thought
        }
    # --------------------------------------------------

    def verify_node(self, state: GraphState):

        answer = state["generation"]
        docs = state["documents"]

        if not docs:
            return {
                "confidence": "Low"
            }

        context = "\n".join([d["content"] for d in docs])

        prompt = f"""
Check if the answer is fully supported by the context.

Context:
{context}

Answer:
{answer}

If unsupported information exists respond ONLY with:
UNSUPPORTED

Otherwise respond ONLY with:
SUPPORTED
"""

        response = ollama.generate(
            model="llama3.2:3b",
            prompt=prompt
        )

        verification = response["response"]

        scores = [d["rerank_score"] for d in docs if "rerank_score" in d]

        confidence = "Low"
        if scores:
            max_score = max(scores)

            if max_score > 0.6:
                confidence = "High"
            elif max_score > 0.35:
                confidence = "Medium"

        if "UNSUPPORTED" in verification:
            return {
                "generation": "The retrieved legal sources do not fully support a reliable answer.",
                "confidence": "Low"
            }

        return {"confidence": confidence}

    # --------------------------------------------------

    def invoke(self, inputs: dict):

        return self.app.invoke(inputs)