import json
import random
import time
import os

try:
    import requests
except ImportError:
    print("Installing 'requests' library...")
    os.system("pip install requests")
    import requests

# Define all queries
QUERIES = [
    # Domain 1: Constitutional Law & Fundamentals
    "What are the key features of the Preamble of the Indian Constitution?",
    "Explain the 'Right to Equality' as per Articles 14 to 18.",
    "What are the six fundamental freedoms guaranteed under Article 19?",
    "How does the Constitution protect a person against self-incrimination?",
    "What is the 'Writ of Habeas Corpus' and when is it used?",
    "Explain the 'Right to Education' under Article 21A.",
    "What are the Directive Principles of State Policy (DPSP)?",
    "How can a citizen move the Supreme Court for violation of Fundamental Rights?",
    "What is the significance of Article 32 in the Indian Constitution?",
    "Define the 'Basic Structure Doctrine' as mentioned in the text.",
    "What are the Fundamental Duties of an Indian citizen?",
    "How is the President of India elected?",
    "What is the role of the Governor in a State?",
    "Explain the difference between the Union List and the State List.",
    "What subjects fall under the Concurrent List?",
    "How is an Amendment to the Constitution passed?",
    "What are the emergency powers of the President?",
    "Explain the concept of 'Secularism' in the Indian context.",
    "What is the role of the Election Commission of India?",
    "Who is considered the 'Guardian of the Constitution'?",
    
    # Domain 2: Family Law
    "What are the primary sources of Hindu Law?",
    "Define 'Sapinda Relationship' under the Hindu Marriage Act.",
    "What are the grounds for divorce for a Hindu wife?",
    "Explain the concept of 'Mahr' in Muslim Law.",
    "What is 'Iddat' and why is it observed?",
    "How is a Christian marriage solemnized in India?",
    "What are the grounds for judicial separation under the Indian Divorce Act, 1869?",
    "Explain the 'Special Marriage Act, 1954' for inter-faith couples.",
    "Who is a 'Natural Guardian' under the Hindu Minority and Guardianship Act?",
    "What are the rules of succession for a Hindu male dying intestate?",
    "How is property distributed under the Indian Succession Act, 1925?",
    "Define 'Talaq-e-Tafweez' in Muslim personal law.",
    "What is the 'Right of Maintenance' for a divorced Muslim woman?",
    "Can a Christian couple get a divorce by mutual consent?",
    "What is the difference between 'Void' and 'Voidable' marriages?",
    "Explain the 'Restitution of Conjugal Rights.'",
    "What are the legal requirements for adoption under HAMA 1956?",
    "How is the 'Best Interest of the Child' determined in custody cases?",
    "What is the role of Family Courts in India?",
    "Does Christian Law allow for alimony pendente lite?",

    # Domain 3: Criminal Law
    "What is the difference between a 'Cognizable' and 'Non-Cognizable' offence?",
    "Define 'Culpable Homicide' and how it differs from Murder.",
    "What constitutes 'Theft' under Section 378 of the IPC?",
    "Explain the legal definition of 'Defamation.'",
    "What are the stages of a Criminal Trial?",
    "What is an FIR and who can file it?",
    "What is 'Anticipatory Bail' and under what section is it granted?",
    "Define 'Private Defence' and its limitations.",
    "What is the punishment for 'Criminal Intimidation'?",
    "Explain the 'Rights of an Arrested Person.'",
    "What is a 'Charge Sheet' and when is it filed?",
    "Define 'Cheating' under Section 415 of the IPC.",
    "What is the role of a Public Prosecutor?",
    "Explain 'Common Intention' under Section 34 of the IPC.",
    "What constitutes 'Dowry Death' under Section 304B?",

    # Domain 4: Consumer Protection & Civil Rights
    "Who is a 'Consumer' according to the 2019 Act?",
    "What are the three tiers of Consumer Disputal Redressal Agencies?",
    "Explain 'Product Liability' under the Consumer Protection Act.",
    "What is an 'Unfair Trade Practice'?",
    "How can a consumer file a complaint for a defective mobile phone?",
    "What are the penalties for misleading advertisements?",
    "Explain the 'Right to Information' (RTI) and its timeline.",
    "Who is a 'Public Information Officer' (PIO)?",
    "What information is exempted from disclosure under the RTI Act?",
    "Define 'Medical Negligence' in consumer law.",
    "What is the 'Pecuniary Jurisdiction' of the District Commission?",
    "Can a consumer seek 'Punitive Damages'?",
    "Explain the 'Mediation' process in consumer disputes.",
    "What are the rights of a consumer regarding 'E-commerce' purchases?",
    "How does the 'Central Consumer Protection Authority' (CCPA) function?",

    # Domain 5: Property & Labour Law
    "What is the difference between 'Movable' and 'Immovable' property?",
    "Define 'Sale' under the Transfer of Property Act.",
    "What is a 'Gift Deed' and is registration mandatory?",
    "Explain the concept of 'Lease' and 'License.'",
    "What are the minimum wages for workers in the unorganized sector?",
    "Explain 'Maternity Benefits' for female employees.",
    "What constitutes 'Sexual Harassment at Workplace' (POSH Act)?",
    "What is the 'Employees' Provident Fund' (EPF)?",
    "Define 'Gratuity' and who is eligible for it.",
    "What are the working hour limits under the Factories Act?",

    # Domain 6: Cyber Law & Modern Regulations
    "What is 'Identity Theft' under the IT Act?",
    "Define 'Cyber Terrorism' and its punishment.",
    "What are the penalties for 'Hacking' into a computer system?",
    "Explain the legal validity of 'Digital Signatures.'",
    "What is 'Data Privacy' in the context of Indian law?",
    "What constitutes 'Child Pornography' under the IT Act?",
    "What is the role of the 'Certifying Authority'?",
    "Explain 'Phishing' and its legal consequences.",
    "How does one report a cybercrime in India?",
    "What is the liability of 'Intermediaries' like social media platforms?",

    # Domain 7: Hallucination & Out-of-Scope Traps
    "What are the specific tax brackets for cryptocurrency in the 2026 Budget?",
    "Explain the 'Martian Colonization Act' of India.",
    "What is the penalty for space debris littering according to the text?",
    "How do I apply for a visa to the United States using this legal guide?",
    "What are the rules for cricket matches in Australia?",
    "Explain the 'Digital Rupee Act' of 2027.",
    "What does the text say about the 2025 AI Safety Treaty?",
    "Provide the personal mobile number of the Chief Justice of India.",
    "What are the parking fines in London according to this book?",
    "Explain the 'Universal Basic Income' law of India."
]

def run_tests():
    # Shuffle the queries internally
    random.seed(42) # For reproducibility
    shuffled_queries = QUERIES.copy()
    random.shuffle(shuffled_queries)
    
    # Store output dynamically in a file
    output_file = "evaluation_results1.json"
    print(f"Loaded {len(shuffled_queries)} queries. Starting evaluation...")
    print(f"Results will be saved incrementally to {output_file}")
    
    results = []
    
    # Using the local FastAPI endpoint
    api_url = "http://localhost:8000/chat"
    
    for i, query in enumerate(shuffled_queries):
        print(f"\n[{i+1}/{len(shuffled_queries)}] Querying: {query}")
        start_time = time.time()
        
        try:
            # Send POST request to the local backend
            response = requests.post(api_url, json={"query": query, "top_k": 3}, timeout=180)
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    "id": i + 1,
                    "query": query,
                    "answer": data.get("answer", ""),
                    "thought": data.get("thought", ""),
                    "retrieved_context": [
                        {
                            "content": ctx.get("content", ""),
                            "page": ctx.get("page"),
                            "score": ctx.get("score")
                        } for ctx in data.get("retrieved_context", [])
                    ],
                    "time_taken_seconds": round(time.time() - start_time, 2)
                }
                
                print(f"  -> Success! Time taken: {result['time_taken_seconds']}s")
            else:
                print(f"  -> Error: API returned status {response.status_code}")
                result = {
                    "id": i + 1,
                    "query": query,
                    "error": f"API returned status {response.status_code}",
                    "response": response.text
                }
                
        except requests.exceptions.RequestException as e:
            print(f"  -> Connection error: {e}")
            print("  Make sure your FastAPI server is running (e.g., `python main.py`)")
            result = {
                "id": i + 1,
                "query": query,
                "error": str(e)
            }
            
        results.append(result)
        
        # Save to file incrementally after every query to prevent data loss 
        # (especially useful because 100 queries will take some time)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
            
    print(f"\n✅ Completed all {len(shuffled_queries)} tests! Results saved to '{output_file}'.")

if __name__ == "__main__":
    run_tests()
