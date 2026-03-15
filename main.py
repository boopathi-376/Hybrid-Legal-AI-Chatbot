import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import QueryRequest, ChatResponse, RetrievalResult
from retrieval.hybrid_search import HybridSearch
from graph import LegalRAGGraph


app = FastAPI(
    title="Hybrid Legal AI Chatbot Backend",
    description="Hybrid RAG API for Indian Legal Provisions"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    hybrid_search = HybridSearch()
    rag_graph = LegalRAGGraph(hybrid_search)
except Exception as e:
    print(f"Error initializing services: {e}")
    hybrid_search = None
    rag_graph = None


@app.get("/")
async def root():
    return {"message": "Legal Chatbot Backend is running."}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: QueryRequest):

    if rag_graph is None:
        raise HTTPException(
            status_code=500,
            detail="Retrieval system not initialized."
        )

    # Initial state for LangGraph
    initial_state = {
        "query": request.query,
        "chat_history": request.chat_history if hasattr(request, "chat_history") else [],
        "standalone_query": "",
        "documents": [],
        "generation": "",
        "thought": "",
        "confidence": ""
    }

    print(f"Starting LangGraph for: {request.query}")

    # Run LangGraph
    final_state = rag_graph.invoke(initial_state)

    # Format output
    formatted_results = []
    if "documents" in final_state:
        for res in final_state["documents"]:
            formatted_results.append(
                RetrievalResult(
                    content=res.get('content', ''),
                    score=res.get('rerank_score', res.get('score', 0.0)),
                    page=res.get('page')
                )
            )

    return ChatResponse(
        query=request.query,
        answer=final_state.get("generation", ""),
        thought=final_state.get("thought", ""),
        retrieved_context=formatted_results,
        confidence=final_state.get("confidence", "")
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)