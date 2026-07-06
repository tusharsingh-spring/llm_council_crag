<h1 align="center">🏛️ LLM Council + CRAG</h1>

<p align="center">
  <em>Multi-LLM Deliberation System with Corrective Retrieval-Augmented Generation</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/LangGraph-workflow-ff6f00?logo=langchain&logoColor=white" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/ChromaDB-vectorstore-8B5CF6" alt="ChromaDB"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License MIT"/>
</p>

<p align="center">
  <b>Author:</b> Aryan Shivatare
</p>

---

## 📖 Overview

**LLM Council + CRAG** is a production-ready multi-agent deliberation platform that combines two powerful paradigms:

### 🏛️ LLM Council

Instead of trusting a single model's output, the system convenes a **council of LLMs** from different providers — each model independently answers the user's question, then anonymously ranks each other's responses, and finally a **Chairman model** synthesizes a final verdict. This ensemble approach catches hallucinations, biases, and blind spots that any single model might miss.

### 🔍 Corrective RAG (CRAG)

The system goes beyond naive RAG by implementing **Corrective RAG + Self-RAG** in a LangGraph pipeline:

1. **Retrieve** documents from a local ChromaDB vector store
2. **Grade** each document for relevance to the question
3. **Correct** — if all documents are irrelevant, rewrite the query and search the web (Wikipedia / Tavily)
4. **Generate** a council answer using the retrieved context
5. **Self-evaluate** — check for hallucination (is the answer grounded?) and usefulness (does it actually address the question?)
6. **Self-correct** — if hallucination is detected, re-run the council with revised context (up to configurable retries)

---

## ✨ Features

- **🏛️ 3-Stage Council Deliberation**
  - Stage 1 — Independent responses from all council members
  - Stage 2 — Anonymous peer ranking with cross-model evaluation
  - Stage 3 — Chairman synthesis of the council's collective wisdom

- **🔍 Corrective RAG (CRAG) Pipeline**
  - LangGraph-based workflow with retrieval, grading, web search fallback, and generation
  - Self-RAG with hallucination detection and answer usefulness grading
  - Automatic query rewriting for improved retrieval

- **🌐 Multi-Provider Support**
  - **Groq** — Free tier (14,400 req/day) with Llama 3.3 70B, Llama 3.1 8B, Qwen
  - **Google Gemini** — Free tier (15 RPM) with Gemini 2.5 Flash
  - **OpenAI** — Pay-as-you-go with GPT-4, GPT-3.5-turbo
  - Mix and match models from different providers for maximum diversity

- **📡 Real-Time Streaming**
  - Server-Sent Events (SSE) for live council deliberation progress
  - Watch each stage unfold in real-time via the API

- **📚 Document Ingestion CLI**
  - Ingest `.txt`, `.md`, and `.pdf` files into the vector store
  - Automatic chunking with `RecursiveCharacterTextSplitter`
  - Used for grounding council answers in your own documents

- **💬 Persistent Conversations**
  - JSON-based storage with conversation IDs
  - Auto-generated conversation titles
  - Full conversation history with all council stages preserved

- **🌍 Web Search Integration**
  - Wikipedia search for current events (100% free)
  - Tavily search for higher-quality results (optional)
  - Smart query detection for time-sensitive questions

- **⚡ Parallel Execution**
  - All council models queried simultaneously
  - Async I/O throughout (FastAPI + httpx + asyncio)

---

## 🏗️ Architecture

```
                         ┌──────────────────────────────────────────┐
                         │              USER QUESTION               │
                         └────────────────────┬─────────────────────┘
                                              │
                                              ▼
                    ┌─────────────────────────────────────────────────┐
                    │           CORRECTIVE RAG PIPELINE               │
                    │                 (LangGraph)                      │
                    ├─────────────────────────────────────────────────┤
                    │                                                 │
                    │  ┌──────────┐    ┌───────────────┐             │
                    │  │ RETRIEVE │───▶│ GRADE DOCS    │             │
                    │  │ (ChromaDB)│   │ (relevant?    │             │
                    │  └──────────┘    │  irrelevant?) │             │
                    │                   └───┬───────┬───┘             │
                    │                       │       │                 │
                    │              RELEVANT │       │ ALL IRRELEVANT  │
                    │                       │       ▼                 │
                    │                       │  ┌──────────────┐      │
                    │                       │  │REWRITE QUERY │      │
                    │                       │  │(Self-RAG)    │      │
                    │                       │  └──────┬───────┘      │
                    │                       │         │               │
                    │                       │         ▼               │
                    │                       │  ┌──────────────┐      │
                    │                       │  │ WEB SEARCH   │      │
                    │                       │  │(Wikipedia/   │      │
                    │                       │  │ Tavily)      │      │
                    │                       │  └──────┬───────┘      │
                    │                       │         │               │
                    │                       ▼         ▼               │
                    │               ┌─────────────────────┐          │
                    │               │    LLM COUNCIL       │          │
                    │               │  (context-augmented)  │          │
                    │               └──────────┬──────────┘          │
                    │                          │                      │
                    │                          ▼                      │
                    │               ┌─────────────────────┐          │
                    │               │  GRADE GENERATION    │          │
                    │               │  (hallucination?     │          │
                    │               │   useful answer?)    │          │
                    │               └───┬───────┬─────────┘          │
                    │                   │       │                     │
                    │         HALLUCINATED/     │ GOOD                │
                    │          NOT USEFUL      │                     │
                    │              │            │                     │
                    │         RETRY/REWRITE     ▼                     │
                    │         (loop back)     FINAL ANSWER            │
                    └─────────────────────────────────────────────────┘
```

```
                         ┌──────────────────────────────────────────────┐
                         │            LLM COUNCIL (3-STAGE)              │
                         ├──────────────────────────────────────────────┤
                         │                                              │
                         │  ┌─────────────────────────────────────┐     │
                         │  │          STAGE 1: DELIBERATION       │     │
                         │  │                                      │     │
                         │  │  ┌─────────┐ ┌──────────┐ ┌──────┐ │     │
                         │  │  │ Groq    │ │ Google   │ │OpenAI│ │     │
                         │  │  │ Llama   │ │ Gemini   │ │ GPT  │ │     │
                         │  │  │ 3.3 70B │ │ 2.5 Flash│ │ 3.5  │ │     │
                         │  │  └────┬────┘ └────┬─────┘ └──┬───┘ │     │
                         │  │       │          │          │      │     │
                         │  │       ▼          ▼          ▼      │     │
                         │  │    Resp A     Resp B     Resp C    │     │
                         │  └─────────────────────────────────────┘     │
                         │                    │                         │
                         │                    ▼                         │
                         │  ┌─────────────────────────────────────┐     │
                         │  │         STAGE 2: PEER RANKING        │     │
                         │  │                                      │     │
                         │  │  Each model ranks anonymized         │     │
                         │  │  responses (A, B, C) best → worst   │     │
                         │  │                                      │     │
                         │  │  Aggregate rankings calculated:      │     │
                         │  │   1. Response C (avg rank: 1.3)      │     │
                         │  │   2. Response A (avg rank: 2.0)      │     │
                         │  │   3. Response B (avg rank: 2.7)      │     │
                         │  └─────────────────────────────────────┘     │
                         │                    │                         │
                         │                    ▼                         │
                         │  ┌─────────────────────────────────────┐     │
                         │  │       STAGE 3: CHAIRMAN SYNTHESIS    │     │
                         │  │                                      │     │
                         │  │  Chairman (Llama 3.3 70B) reviews:   │     │
                         │  │  • All individual responses          │     │
                         │  │  • All peer rankings                 │     │
                         │  │  • Aggregate scores                  │     │
                         │  │                                      │     │
                         │  │  Produces final, authoritative answer│     │
                         │  └─────────────────────────────────────┘     │
                         │                    │                         │
                         │                    ▼                         │
                         │            FINAL RESPONSE                    │
                         └──────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
llm_council_crag/
├── backend/
│   ├── __init__.py          # Package marker
│   ├── config.py            # API keys, model lists, constants
│   ├── openrouter.py        # Multi-provider LLM client (Groq, OpenAI, Google)
│   ├── council.py           # 3-stage council orchestration
│   ├── search.py            # Wikipedia / web search integration
│   ├── storage.py           # JSON-based conversation persistence
│   ├── vectorstore.py       # ChromaDB + sentence-transformers singleton
│   ├── ingest.py            # CLI document ingestion tool
│   ├── rag_state.py         # LangGraph TypedDict state definition
│   ├── rag_nodes.py         # LangGraph node functions (CRAG + Self-RAG)
│   ├── rag_graph.py         # LangGraph graph assembly and compilation
│   └── main.py              # FastAPI application with REST + SSE endpoints
├── data/
│   ├── conversations/       # JSON conversation files
│   └── vectorstore/         # ChromaDB persistent storage
├── test_api.py              # Test API key validity
├── test_providers.py        # Test all LLM providers
├── test_council.py          # Test full council flow
├── test_council_models.py   # Test individual council models
├── test_chairman.py         # Test chairman model isolation
├── test_full_council.py     # Test council with web search
├── test_search.py           # Test Wikipedia search integration
├── test_groq.py             # Test Groq API connection
├── demo_search.py           # Demonstration of web search feature
├── pyproject.toml           # Python project config + dependencies
├── start.ps1                # Windows PowerShell launcher
├── start.sh                 # Unix shell launcher
├── API_KEYS_GUIDE.md        # Detailed API key setup guide
├── WEB_SEARCH_FEATURE.md    # Web search feature documentation
└── GITHUB_SETUP.md          # GitHub repository setup guide
```

---

## 🚀 Installation & Getting Started

### Prerequisites

- **Python** `>= 3.10`
- **uv** (Python package manager) — [install guide](https://docs.astral.sh/uv/getting-started/installation/)
- At least one LLM API key (Groq is free and recommended to start)

### 1. Clone the Repository

```bash
git clone https://github.com/tusharsingh-spring/llm_council_crag.git
cd llm_council_crag
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Groq (FREE — 14,400 requests/day) 
GROQ_API_KEY=gsk_your_groq_key_here

# Google Gemini (FREE — 15 RPM)
GOOGLE_API_KEY=your_google_key_here

# OpenAI (Pay-as-you-go)
OPENAI_API_KEY=sk-your_openai_key_here

# Tavily (optional — higher quality web search)
TAVILY_API_KEY=tvly-your_tavily_key_here
```

> **Minimum setup:** Just a `GROQ_API_KEY` is enough to run the full council for **free**.

### 3. Install Dependencies

```bash
uv sync
```

### 4. Start the Backend

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Linux/macOS:**
```bash
bash start.sh
```

**Or manually:**
```bash
uv run python -m backend.main
```

The API will be available at `http://localhost:8001`.

### 5. Verify Everything Works

```bash
uv run python test_providers.py
```

---

## 📋 Usage

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/api/conversations` | List all conversations |
| `POST` | `/api/conversations` | Create a new conversation |
| `GET` | `/api/conversations/{id}` | Get conversation with messages |
| `POST` | `/api/conversations/{id}/message` | Send message (full response) |
| `POST` | `/api/conversations/{id}/message/stream` | Send message (SSE streaming) |
| `POST` | `/api/conversations/{id}/rag-message/stream` | Send message with CRAG pipeline (SSE) |

### Example: Standard Council Deliberation

```bash
# Create a conversation
curl -X POST http://localhost:8001/api/conversations

# Send a question (stores id from above)
curl -X POST http://localhost:8001/api/conversations/<CONVERSATION_ID>/message \
  -H "Content-Type: application/json" \
  -d '{"content": "What are the key differences between supervised and unsupervised learning?"}'
```

**Response structure:**
```json
{
  "stage1": [
    {
      "model": "llama-3.3-70b-versatile",
      "response": "Supervised learning uses labeled data..."
    },
    {
      "model": "gemini-2.5-flash",
      "response": "The key distinction lies in..."
    }
  ],
  "stage2": [
    {
      "model": "llama-3.3-70b-versatile",
      "ranking": "Response A provides good detail...\n\nFINAL RANKING:\n1. Response B\n2. Response A"
    }
  ],
  "stage3": {
    "model": "llama-3.3-70b-versatile",
    "response": "The council has determined that the key differences are..."
  },
  "metadata": {
    "label_to_model": {"Response A": "llama-3.3-70b-versatile", "Response B": "gemini-2.5-flash"},
    "aggregate_rankings": [
      {"model": "gemini-2.5-flash", "average_rank": 1.0, "rankings_count": 1},
      {"model": "llama-3.3-70b-versatile", "average_rank": 2.0, "rankings_count": 1}
    ]
  }
}
```

### Example: RAG-Enhanced Query (SSE Streaming)

```bash
curl -X POST http://localhost:8001/api/conversations/<CONVERSATION_ID>/rag-message/stream \
  -H "Content-Type: application/json" \
  -d '{"content": "Explain the transformer architecture based on the uploaded papers."}'
```

**SSE Event types:** `rag_retrieve` → `rag_grade` → `rag_web_search` → `stage1_complete` → `stage2_complete` → `stage3_complete` → `rag_graded_generation` → `complete`

### Ingesting Documents for RAG

```bash
# Ingest a single file
uv run python -m backend.ingest --file docs/research_paper.pdf

# Ingest a directory
uv run python -m backend.ingest --dir docs/

# Ingest raw text
uv run python -m backend.ingest --text "Your custom knowledge text here" --source "manual"
```

---

## ⚙️ Configuration

All configuration lives in `backend/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `COUNCIL_MODELS` | `["gemini-2.5-flash", "llama-3.1-8b-instant", "llama-3.3-70b-versatile", "qwen/qwen3-32b"]` | Models participating in the council |
| `CHAIRMAN_MODEL` | `"llama-3.3-70b-versatile"` | Model that synthesizes the final answer |
| `EMBEDDING_MODEL` | `"all-MiniLM-L6-v2"` | Sentence-transformer model for embeddings |
| `RAG_TOP_K` | `4` | Number of documents to retrieve per query |
| `RAG_MAX_RETRIES` | `2` | Max council re-runs on hallucination |
| `VECTORSTORE_DIR` | `"data/vectorstore"` | ChromaDB persist directory |
| `DATA_DIR` | `"data/conversations"` | Conversation JSON storage directory |

### Switching Models

Edit the `COUNCIL_MODELS` list in `backend/config.py` to customize which models sit on your council. Any model from Groq, Google Gemini, or OpenAI is supported. The model prefix determines the provider automatically:

- `gpt-*` → OpenAI
- `gemini-*` → Google
- Everything else → Groq

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` + `uvicorn` | Async REST API with SSE streaming |
| `langgraph` | CRAG + Self-RAG pipeline orchestration |
| `langchain` + `langchain-community` | Document loaders, text splitters, ChromaDB wrapper |
| `langchain-groq` | Groq provider integration |
| `langchain-google-genai` | Google Gemini integration |
| `chromadb` | Local persistent vector store |
| `sentence-transformers` | Local embeddings (all-MiniLM-L6-v2) |
| `httpx` | Async HTTP client for LLM API calls |
| `tavily-python` | Optional: higher-quality web search |
| `pydantic` | Request/response validation |
| `python-dotenv` | `.env` file loading |

---

## 📊 Model Comparison

| Provider | Model | Cost | Intelligence | Speed |
|----------|-------|------|:---:|:---:|
| Groq | llama-3.3-70b-versatile | FREE | ⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ |
| Groq | llama-3.1-8b-instant | FREE | ⭐⭐⭐ | ⚡⚡⚡⚡⚡ |
| Groq | qwen/qwen3-32b | FREE | ⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ |
| Google | gemini-2.5-flash | FREE* | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ |
| Google | gemini-2.5-pro | FREE* | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ |
| OpenAI | gpt-4 | $$$$ | ⭐⭐⭐⭐⭐ | ⚡⚡ |
| OpenAI | gpt-3.5-turbo | $ | ⭐⭐⭐ | ⚡⚡⚡⚡ |

*\*Free within rate limits (15 RPM for Google, 14,400 req/day for Groq)*

---

## 🧪 Testing

```bash
# Test connectivity of all configured providers
uv run python test_providers.py

# Test each council model individually
uv run python test_council_models.py

# Test the chairman model in isolation
uv run python test_chairman.py

# Run a full council deliberation
uv run python test_council.py

# Run council with web search demonstration
uv run python demo_search.py

# Run full council + CRAG test
uv run python test_full_council.py
```

---

## 🔮 Roadmap

- [ ] Frontend UI integration (React/Vue SPA)
- [ ] Persistent conversations with PostgreSQL / MongoDB
- [ ] Dynamic web search (auto-detect current officeholders, not hardcoded)
- [ ] Multi-source fact verification
- [ ] Docker containerization
- [ ] Streaming token-by-token response from chairman
- [ ] Council model weighting based on historical accuracy
- [ ] Multi-turn RAG with conversation memory

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">
  <sub>Built with ❤️ using FastAPI, LangGraph, ChromaDB, and a council of diverse LLMs.</sub>
</p>
