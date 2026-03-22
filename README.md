# ⚖️ Dharma AI — Hybrid Legal AI Chatbot

A **production-ready, fully local RAG (Retrieval-Augmented Generation) chatbot** for answering Indian legal questions. It combines semantic vector search, keyword search, and a knowledge graph to retrieve precise legal context, then uses a local LLM to generate conversational, grounded answers.

> **Knowledge Base:** *Indian Law For A Common Man* — covering Constitutional Law, Criminal Law, Family Law, Property Law, Labour Law, Consumer Protection, Cyber Law, and more.

---

## 🖥️ Demo

![AI Chat UI](frontend/index.html)

**Ask questions like:**
- *"What are my Fundamental Rights under the Constitution?"*
- *"What is Section 302 of the IPC?"*
- *"How do I file an FIR?"*
- *"What are the rights of an arrested person?"*

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────┐
│             LangGraph RAG Pipeline          │
│                                             │
│  reformulate → retrieve → rerank →          │
│  generate → verify                          │
└─────────────────────────────────────────────┘
    │                   ▲
    ▼                   │
┌──────────────────────────────────────────┐
│          Hybrid Search Engine            │
│                                          │
│  ┌────────────┐  ┌──────┐  ┌──────────┐ │
│  │Vector (Qdrant│  │ BM25 │  │Knowledge │ │
│  │ e5-base-v2)│  │      │  │  Graph   │ │
│  └────────────┘  └──────┘  └──────────┘ │
│         └──────────┬───────────┘         │
│              CrossEncoder Rerank          │
└──────────────────────────────────────────┘
    │
    ▼
Ollama (llama3.2:3b) — runs 100% locally
```

---

## ✨ Features

- **Hybrid Retrieval** — Combines dense vector search (Qdrant + `e5-base-v2`), sparse keyword search (BM25), and entity-aware Knowledge Graph (NetworkX) for maximum recall.
- **Two-Stage Reranking** — CrossEncoder (`ms-marco-MiniLM-L-6-v2`) reranks candidates at both retrieval and graph stages.
- **LangGraph Orchestration** — A 5-node stateful graph: `reformulate → retrieve → rerank → generate → verify`.
- **Query Expansion** — Automatically expands legal abbreviations (IPC, FIR, CrPC, RTI, PIL, etc.).
- **Contextual Chunking** — Every chunk is injected with domain, chapter, and Act metadata for richer context.
- **Answer Verification** — A dedicated verify node checks if the answer is supported by retrieved context and assigns a `High / Medium / Low` confidence score.
- **Thought Separation** — Parses and separates `<think>` tags from the final answer for clean output.
- **Fully Local & Private** — All inference runs via Ollama. No data is sent to external APIs.
- **Chat UI** — A clean glassmorphism frontend ("Dharma AI") with a live sources sidebar.
- **Dockerized** — Ready-to-deploy with Docker and a CI/CD pipeline via GitHub Actions.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI, Uvicorn |
| **Orchestration** | LangGraph |
| **LLM** | Ollama (`llama3.2:3b`) |
| **Embeddings** | `intfloat/e5-base-v2` (SentenceTransformers) |
| **Vector DB** | Qdrant |
| **Keyword Search** | `rank_bm25` (BM25Okapi) |
| **Knowledge Graph** | NetworkX |
| **Reranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| **PDF Parsing** | PyMuPDF (`fitz`) |
| **Frontend** | Vanilla HTML, CSS, JavaScript |
| **Containerization** | Docker |
| **CI/CD** | GitHub Actions → Docker Hub |

---

## 📁 Project Structure

```
.
├── main.py                   # FastAPI app entry point
├── graph.py                  # LangGraph RAG pipeline (core logic)
├── models.py                 # Pydantic request/response models
├── ingest.py                 # PDF ingestion and contextual chunking
├── evaluate_rag.py           # RAG evaluation script
├── verify.py                 # Index verification script
├── requirements.txt
├── Dockerfile
├── data/
│   ├── chunks.json           # Pre-processed chunks (Indian Law book)
│   └── bns_chunks.json       # BNS (Bharatiya Nyaya Sanhita) chunks
├── retrieval/
│   ├── hybrid_search.py      # Orchestrates all retrieval methods
│   ├── vector_search.py      # Qdrant vector search
│   ├── bm25_search.py        # BM25 keyword search
│   ├── knowledge_graph.py    # Entity knowledge graph
│   └── query_expansion.py    # Legal abbreviation expander
├── frontend/
│   ├── index.html            # Chat UI
│   ├── style.css
│   └── app.js
└── .github/
    └── workflows/
        └── docker.yml        # CI/CD pipeline
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com) installed and running
- [Qdrant](https://qdrant.tech) running locally on port `8333`
- Docker (optional, for containerized deployment)

### 1. Clone the Repository

```bash
git clone https://github.com/boopathi-376/Hybrid-Legal-AI-Chatbot.git
cd Hybrid-Legal-AI-Chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull the LLM

```bash
ollama pull llama3.2:3b
```

### 4. Start Qdrant

```bash
docker run -p 8333:6333 qdrant/qdrant
```

### 5. Ingest the PDF

Place `Indian_Law_For_A_Common_Man.pdf` in the project root, then run:

```bash
python ingest.py
```

This extracts, chunks, and saves the data to `data/chunks.json`.

### 6. Build the Vector Index

```bash
python retrieval/vector_search.py
```

This encodes all chunks and uploads them to Qdrant.

### 7. Start the Backend

```bash
python main.py
```

API will be live at `http://localhost:8000`.

### 8. Open the Frontend

Open `frontend/index.html` in your browser. Make sure the backend is running.

---

## 🔌 API Reference

### `GET /`
Health check.
```json
{ "message": "Legal Chatbot Backend is running." }
```

### `POST /chat`
Main chat endpoint.

**Request:**
```json
{
  "query": "What is Section 302 of the IPC?",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "What is Section 302 of the IPC?",
  "answer": "Section 302 of the Indian Penal Code deals with **punishment for murder**...",
  "thought": "...",
  "confidence": "High",
  "retrieved_context": [
    {
      "content": "Context: [Core Legal Domains | Chapter 6: Criminal Law | Act: IPC] -- ...",
      "score": 0.87,
      "page": 52
    }
  ]
}
```

---

## 🐳 Docker Deployment

### Build & Run Locally

```bash
docker build -t hybrid-legal-ai-chatbot .
docker run -p 8000:8000 hybrid-legal-ai-chatbot
```

### CI/CD

On every push to `main`, GitHub Actions automatically:
1. Builds the Docker image
2. Pushes it to `boopathi376/hybrid-legal-ai-chatbot:latest` on Docker Hub

Pull the latest image:
```bash
docker pull boopathi376/hybrid-legal-ai-chatbot:latest
```

---

## 📊 RAG Pipeline — Step by Step

1. **Query Expansion** — Abbreviations like `IPC`, `FIR`, `RTI` are expanded to their full legal forms.
2. **Hybrid Retrieval** — Vector (Qdrant), BM25, and Knowledge Graph are queried in parallel with `top_k=15` candidates each.
3. **Deduplication** — Unique candidates are merged from all three sources.
4. **CrossEncoder Reranking** — All candidates are scored by `ms-marco-MiniLM-L-6-v2` and filtered (threshold: `0.15`). Top 5 are kept.
5. **Generation** — `llama3.2:3b` is prompted with the "Legal Navigator" persona and the retrieved context.
6. **Verification** — The answer is checked for hallucination. Confidence (`High/Medium/Low`) is assigned based on the max rerank score.

---

## 📚 Knowledge Base Coverage

| Domain | Acts/Topics Covered |
|---|---|
| Constitutional Framework | Constitution of India, Fundamental Rights |
| Criminal Law | IPC, CrPC, BNS |
| Civil Law | CPC, Contract Law, Law of Torts |
| Family Law | Hindu Law, Muslim Law, Special Marriage Act |
| Property Law | Transfer of Property Act, Succession Laws |
| Labour Law | Industrial Disputes Act, Factories Act |
| Taxation | Income Tax Act, GST |
| Consumer Protection | Consumer Protection Act |
| Intellectual Property | Patents, Trademarks, Copyrights |
| Environmental Law | Environment (Protection) Act |
| Cyber Law | Information Technology Act |

---

## ⚠️ Disclaimer

> This chatbot is strictly based on *"Indian Law For A Common Man"* and is intended for **educational purposes only**. It does **not** constitute formal legal advice. For legal matters, please consult a qualified legal professional.

---



