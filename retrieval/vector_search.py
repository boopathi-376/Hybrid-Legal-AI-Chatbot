import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models

class VectorSearch:
    def __init__(self, collection_name="legal_chunks", qdrant_url="http://localhost:8333"):
        print("Initializing VectorSearch with Qdrant and intfloat/e5-base-v2...")
        # e5-base-v2 requires prefixes
        self.encoder = SentenceTransformer("intfloat/e5-base-v2")
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        
    def build_index(self, chunks_path="data/chunks.json"):
        if not os.path.exists(chunks_path):
            print(f"Error: {chunks_path} not found.")
            return

        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)

        print(f"Encoding {len(chunks_data)} chunks for Qdrant...")
        
        # e5 models require "passage: " prefix for indexing
        texts = [f"passage: {chunk['content']}" for chunk in chunks_data]
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        dimension = embeddings.shape[1]

        print(f"Recreating Qdrant collection: {self.collection_name} (dim: {dimension})")
        # Ensure clean slate
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
            
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=dimension, 
                distance=models.Distance.COSINE
            )
        )

        print("Uploading points to Qdrant...")
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks_data, embeddings)):
            points.append(
                models.PointStruct(
                    id=i, 
                    vector=embedding.tolist(), 
                    payload=chunk
                )
            )
            
        self.client.upsert(
            collection_name=self.collection_name, 
            points=points
        )
        print("Qdrant index built successfully.")

    def load_index(self):
        # Qdrant manages its own persistence; just verify collection exists
        if not self.client.collection_exists(self.collection_name):
             print(f"Collection {self.collection_name} doesn't exist in Qdrant. Please build_index first.")

    def search(self, query, k=3):
        # e5 models require "query: " prefix for searching
        processed_query = f"query: {query}"
        query_vector = self.encoder.encode([processed_query])[0]
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=k
        )
        
        # Format to match existing pipeline expectation
        formatted_results = []
        for res in results:
            formatted_results.append({
                "content": res.payload["content"],
                "score": res.score,
                "metadata": res.payload["metadata"],
                "page": res.payload["metadata"].get("page")
            })
            
        return formatted_results

if __name__ == "__main__":
    vs = VectorSearch()
    vs.build_index()
    results = vs.search("What are the rights of an arrested person?")
    print("\nSearch results for: 'What are the rights of an arrested person?'")
    for res in results:
        print(f"Score: {res['score']:.4f} | Page: {res['page']}")
        print(f"Content: {res['content'][:150]}...\n")
