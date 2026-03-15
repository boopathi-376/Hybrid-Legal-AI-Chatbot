import json
from retrieval.hybrid_search import HybridSearch
import ollama

def test_full_rag_pipeline():
    print("Initializing Hybrid Search and LLM for verification...")
    try:
        hs = HybridSearch()
        
        queries = [
            "What are the fundamental rights in the Indian Constitution?",
            "What is the punishment for murder under IPC Section 302?",
        ]
        
        for query in queries:
            print(f"\n" + "="*50)
            print(f"USER QUERY: {query}")
            
            # 1. Retrieval
            results = hs.search(query, top_k=3)
            print("\nRETRIEVED CONTEXT:")
            for i, res in enumerate(results):
                print(f"[{i+1}] (Page {res.get('page')}) (Score: {res['score']:.4f}) {res['content'][:100]}...")
            
            # 2. LLM Call
            context_text = "\n\n".join([f"Source [{i+1}] (Page {res['page']}): {res['content']}" for i, res in enumerate(results)])
            system_prompt = (
                "You are an expert legal assistant specializing in Indian law. "
                "Based on the following retrieved context, provide a clear answer with page-wise citations.\n\n"
                f"Context:\n{context_text}"
            )
            
            print("\nCALLING LLM (DeepSeek)...")
            try:
                response = ollama.chat(model='deepseek-r1:1.5b', messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': query},
                ])
                print("\nLLM ANSWER:")
                print(response['message']['content'])
            except Exception as e:
                print(f"\nLLM Call failed: {e}. (Make sure Ollama is running and model is pulled)")
            
    except Exception as e:
        print(f"Verification failed with error: {e}")

if __name__ == "__main__":
    test_full_rag_pipeline()
