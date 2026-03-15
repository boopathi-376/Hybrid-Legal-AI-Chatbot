class QueryExpansion:
    def __init__(self):
        # Common legal aliases in India
        self.aliases = {
            'ipc': 'Indian Penal Code',
            'crpc': 'Code of Criminal Procedure',
            'cpc': 'Code of Civil Procedure',
            'fir': 'First Information Report',
            'rti': 'Right to Information',
            'pil': 'Public Interest Litigation',
            'constitution': 'Constitution of India',
            'supreme court': 'SC',
            'high court': 'HC',
            'it act': 'Information Technology Act',
        }

    def expand(self, query):
        expanded_query = query
        query_lower = query.lower()
        
        for alias, full_form in self.aliases.items():
            if alias in query_lower:
                # Add full form to query if only alias exists
                if full_form.lower() not in query_lower:
                    expanded_query += f" {full_form}"
        
        return expanded_query

if __name__ == "__main__":
    qe = QueryExpansion()
    test_queries = [
        "What is IPC Section 302?",
        "How to file an FIR?",
        "Rights under the Constitution"
    ]
    
    for q in test_queries:
        print(f"Original: {q}")
        print(f"Expanded: {qe.expand(q)}\n")
