import json
from sentence_transformers import CrossEncoder
from .vector_search import VectorSearch
from .bm25_search import BM25Search
from .knowledge_graph import KnowledgeGraph
from .query_expansion import QueryExpansion

class HybridSearch:
    def __init__(self, chunks_path='data/chunks.json'):
        with open(chunks_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        self.vector_search = VectorSearch()
        self.vector_search.load_index()
        
        self.bm25_search = BM25Search()
        self.bm25_search.build_index(self.chunks)
        
        self.kg = KnowledgeGraph()
        self.kg.build_graph(self.chunks)
        
        self.qe = QueryExpansion()
        
        print("Initializing CrossEncoder reranker...")
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def search(self, query, top_k=5):
        # 1. Expand Query
        expanded_query = self.qe.expand(query)
        print(f"Searching for: {expanded_query}")
        
        # We fetch more candidates initially to rerank them
        fetch_k = top_k * 3
        
        # 2. Base Retrievals
        vector_results = self.vector_search.search(expanded_query, k=fetch_k)
        bm25_results = self.bm25_search.search(expanded_query, top_k=fetch_k)
        kg_results = self.kg.search(expanded_query)
        
        # 3. Aggregate unique candidates
        unique_candidates = {}
        
        for res in vector_results:
            unique_candidates[res['content']] = {
                'content': res['content'],
                'page': res['page']
            }
            
        for res in bm25_results:
            if res['content'] not in unique_candidates:
                unique_candidates[res['content']] = {
                    'content': res['content'],
                    'page': res['page']
                }
        
        for res in kg_results:
            try:
                idx = int(res['chunk_id'].split('_')[1])
                chunk = self.chunks[idx]
                content = chunk['content']
                if content not in unique_candidates:
                    unique_candidates[content] = {
                        'content': content,
                        'page': chunk['metadata']['page']
                    }
            except Exception:
                continue
                
        candidate_list = list(unique_candidates.values())
        if not candidate_list:
            return []
            
        # 4. Cross-Encoder Reranking
        cross_inp = [[query, item['content']] for item in candidate_list]
        cross_scores = self.reranker.predict(cross_inp)
        
        # Attach new scores to candidates
        for i, score in enumerate(cross_scores):
            candidate_list[i]['score'] = float(score)
            
        # Sort candidates descending by CrossEncoder score
        reranked_results = sorted(candidate_list, key=lambda x: x['score'], reverse=True)
        
        # Return only the top_k
        return reranked_results[:top_k]

if __name__ == "__main__":
    # Note: To run this as a script, you might need to fix imports if not in a package
    # For now, this is a placeholder for the logic
    pass
