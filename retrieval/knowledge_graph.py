import networkx as nx
import re
import json

class KnowledgeGraph:
    def __init__(self, graph_path='data/legal_graph.json'):
        self.graph = nx.Graph()
        self.graph_path = graph_path

    def build_graph(self, chunks_with_metadata):
        print("Building Knowledge Graph (Basic Entity Extraction)...")
        
        section_pattern = re.compile(r'Section\s*(\d+[A-Z]?)', re.IGNORECASE)
        article_pattern = re.compile(r'Article\s*(\d+[A-Z]?)', re.IGNORECASE)
        
        for i, chunk_data in enumerate(chunks_with_metadata):
            chunk = chunk_data['content']
            page = chunk_data['metadata']['page']
            
            sections = section_pattern.findall(chunk)
            articles = article_pattern.findall(chunk)
            
            entities = [f"Section {s}" for s in sections] + [f"Article {a}" for a in articles]
            
            # Add edges between entities mentioned in the same chunk
            for j in range(len(entities)):
                for k in range(j + 1, len(entities)):
                    if self.graph.has_edge(entities[j], entities[k]):
                        self.graph[entities[j]][entities[k]]['weight'] += 1
                    else:
                        self.graph.add_edge(entities[j], entities[k], weight=1)
                
                # Link entity to chunk index
                chunk_node = f"Chunk_{i}"
                self.graph.add_node(chunk_node, type='chunk', content=chunk[:100], page=page)
                self.graph.add_edge(entities[j], chunk_node, weight=2)

        print(f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")

    def search(self, query):
        # Find entities in query
        section_pattern = re.compile(r'Section\s*(\d+[A-Z]?)', re.IGNORECASE)
        article_pattern = re.compile(r'Article\s*(\d+[A-Z]?)', re.IGNORECASE)
        
        query_sections = section_pattern.findall(query)
        query_articles = article_pattern.findall(query)
        entities = [f"Section {s}" for s in query_sections] + [f"Article {a}" for a in query_articles]
        
        results = []
        for entity in entities:
            if self.graph.has_node(entity):
                # Find neighbors that are chunks
                neighbors = self.graph.neighbors(entity)
                for n in neighbors:
                    if str(n).startswith("Chunk_"):
                        node_data = self.graph.nodes[n]
                        results.append({
                            'entity': entity,
                            'chunk_id': n,
                            'page': node_data.get('page')
                        })
        return results

if __name__ == "__main__":
    with open('data/chunks.json', 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    kg = KnowledgeGraph()
    kg.build_graph(chunks)
    
    test_query = "Tell me about Section 302"
    results = kg.search(test_query)
    print(f"\nGraph Results for: '{test_query}'")
    for res in results:
        print(f"Found {res['entity']} in {res['chunk_id']} (Page {res.get('page')})")
