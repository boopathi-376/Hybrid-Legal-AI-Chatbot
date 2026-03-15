import os
import fitz # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json

# Hierarchical Metadata Mapping based on the book's structure
# Page ranges mapped to Document Title, Domain, Chapter Header, Act Name
TOC_MAPPING = [
    {"start": 9, "end": 10, "domain": "General Overview", "chapter": "Chapter 1: Why Know the Law?", "act": None},
    {"start": 11, "end": 13, "domain": "General Overview", "chapter": "Chapter 2: A Quick Look at the Indian Legal System", "act": None},
    {"start": 14, "end": 24, "domain": "Constitutional and Judicial Framework", "chapter": "Chapter 3: Introduction to the Constitution of India", "act": "Constitution of India"},
    {"start": 25, "end": 37, "domain": "Constitutional and Judicial Framework", "chapter": "Chapter 4: Fundamental Rights and Duties", "act": "Constitution of India"},
    {"start": 38, "end": 49, "domain": "Constitutional and Judicial Framework", "chapter": "Chapter 5: The Judicial System of India", "act": "Constitution of India"},
    {"start": 50, "end": 75, "domain": "Core Legal Domains", "chapter": "Chapter 6: Criminal Law", "act": "Indian Penal Code (IPC), Code of Criminal Procedure (CrPC)"},
    {"start": 76, "end": 87, "domain": "Core Legal Domains", "chapter": "Chapter 7: Civil Law", "act": "Code of Civil Procedure (CPC), Contract Law, Law of Torts"},
    {"start": 88, "end": 101, "domain": "Core Legal Domains", "chapter": "Chapter 8: Family Law", "act": "Hindu Law, Muslim Law, Christian Law, Special Marriage Act"},
    {"start": 102, "end": 114, "domain": "Core Legal Domains", "chapter": "Chapter 9: Property Law", "act": "Transfer of Property Act, Succession Laws"},
    {"start": 115, "end": 136, "domain": "Specialized Laws and Rights", "chapter": "Chapter 10: Labour and Employment Law", "act": "Industrial Disputes Act, Factories Act, etc."},
    {"start": 137, "end": 147, "domain": "Specialized Laws and Rights", "chapter": "Chapter 11: Taxation and Finance", "act": "Income Tax Act, GST"},
    {"start": 148, "end": 171, "domain": "Specialized Laws and Rights", "chapter": "Chapter 12: Consumer Protection and Rights", "act": "Consumer Protection Act"},
    {"start": 172, "end": 186, "domain": "Specialized Laws and Rights", "chapter": "Chapter 13: Intellectual Property Rights", "act": "Patents, Trademarks, Copyrights"},
    {"start": 187, "end": 199, "domain": "Specialized Laws and Rights", "chapter": "Chapter 14: Environmental Laws", "act": "Environment (Protection) Act, etc."},
    {"start": 200, "end": 206, "domain": "Specialized Laws and Rights", "chapter": "Chapter 15: Cyber Law in India", "act": "Information Technology Act"},
    {"start": 207, "end": 220, "domain": "Reference and Conclusion", "chapter": "Chapter 16: How to Navigate the Legal System", "act": None},
    {"start": 221, "end": 222, "domain": "Reference and Conclusion", "chapter": "End Note", "act": None},
]

def get_metadata_for_page(page_num):
    for entry in TOC_MAPPING:
        if entry["start"] <= page_num <= entry["end"]:
            return {
                "doc_title": "Indian Law For A Common Man",
                "domain": entry["domain"],
                "chapter_header": entry["chapter"],
                "act_name": entry["act"]
            }
    return {
        "doc_title": "Indian Law For A Common Man",
        "domain": "General",
        "chapter_header": "Unknown Chapter",
        "act_name": None
    }

def extract_text_by_page_pymupdf(pdf_path):
    print(f"Extracting text from {pdf_path} using PyMuPDF...")
    doc = fitz.open(pdf_path)
    pages_text = []
    
    for i, page in enumerate(doc):
        text = page.get_text("text")
        if text.strip():
            # PyMuPDF pages are 0-indexed, book pages might be 1-indexed
            physical_page_num = i + 1
            meta = get_metadata_for_page(physical_page_num)
            meta["page"] = physical_page_num
            
            pages_text.append({
                "raw_text": text,
                "metadata": meta
            })
    doc.close()
    return pages_text

def contextual_chunking(pages_text, chunk_size=1000, chunk_overlap=200):
    print("Chunking text with Header Injection...")
    
    # Step 4: Recursive Character Splitting with specific legal boundaries
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[
            "\nCHAPTER",
            "\nSection",
            "\n\n",
            "\n",
            " ",
            ""
        ],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks_with_metadata = []
    
    for page_data in pages_text:
        text = page_data["raw_text"]
        meta = page_data["metadata"]
        
        # Split raw text first
        page_chunks = text_splitter.split_text(text)
        
        for chunk in page_chunks:
            # Step 3: Contextual Chunking (Header Injection)
            domain = meta.get('domain', 'Law')
            chapter = meta.get('chapter_header', 'Section')
            act = meta.get('act_name')
            act_str = f" | Act: {act}" if act else ""
            
            header = f"Context: [{domain} | {chapter}{act_str}] -- Text: "
            injected_content = header + chunk.strip()
            
            chunks_with_metadata.append({
                "content": injected_content,
                "metadata": meta
            })
            
    return chunks_with_metadata

def main():
    pdf_path = "Indian_Law_For_A_Common_Man.pdf"
    output_dir = "data"
    
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return

    # 1 & 2: Structural Extraction and Metadata
    pages_text = extract_text_by_page_pymupdf(pdf_path)
    
    # 3 & 4: Contextual Chunking and Legal Splitting
    chunks = contextual_chunking(pages_text)
    
    # Save chunks for future retrieval components
    os.makedirs(output_dir, exist_ok=True)
    chunks_path = os.path.join(output_dir, "chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(chunks)} contextualized chunks to {chunks_path}")

if __name__ == "__main__":
    main()
