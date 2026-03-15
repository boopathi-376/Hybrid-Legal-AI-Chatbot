import json
from rank_bm25 import BM25Okapi
import re

class BM25Search:
    def __init__(self):
        self.bm25 = None
        self.chunks = []

    def tokenize(self, text):
        # Basic tokenization: lowercase and alphanumeric
        return re.findall(r'\w+', text.lower())

    def build_index(self, chunks_with_metadata):
        print("Building BM25 index...")
        self.chunks = chunks_with_metadata
        tokenized_corpus = [self.tokenize(chunk['content']) for chunk in chunks_with_metadata]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print("BM25 index built.")

    def search(self, query, top_k=3):
        if self.bm25 is None:
            return []
        
        tokenized_query = self.tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get indices of top scores
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0: # Only return matches with positive score
                chunk = self.chunks[idx]
                results.append({
                    'content': chunk['content'],
                    'page': chunk['metadata']['page'],
                    'score': float(scores[idx])
                })
        return results

if __name__ == "__main__":
    with open('data/chunks.json', 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    bm25 = BM25Search()
    bm25.build_index(chunks)
    
    test_query = "What is the punishment for murder in the Indian Penal Code?"
    results = bm25.search(test_query)
    print(f"\nBM25 Results for: '{test_query}'")
    for res in results:
        print(f"Score: {res['score']:.4f} | Page: {res['page']}\nContent: {res['content'][:200]}...\n")
