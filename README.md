# AI SaaS Platform — Zero-Budget RAG Chatbot & Data Analyst

A full-stack SaaS platform that provides two AI-powered tools:

1. **RAG Chatbot** — Upload PDFs or website links, ask questions, get answers grounded in your documents
2. **AI Data Analyst** — Upload CSV/Excel files, ask natural language questions, receive insights and interactive charts

Built entirely with free and open-source tools. No paid APIs required.

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Frontend | Next.js 14 + Tailwind CSS | UI, file upload, chat interface |
| Backend | FastAPI (Python) | REST API, file processing, orchestration |
| LLM | Ollama (local) or HuggingFace (free API) | Text generation |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Document vectorization |
| Vector DB | FAISS (faiss-cpu) | Similarity search |
| Database | SQLite (via SQLAlchemy) | Metadata, users, chat history |
| PDF Parsing | PyMuPDF (fitz) | Extract text from PDFs |
| Web Scraping | BeautifulSoup | Extract text from URLs |
| Charts | Plotly | Interactive data visualizations |
| Code Sandbox | AST validation + restricted exec | Safe execution of generated code |

---

## Project Structure

```
personal/
├── README.md                    ← You are here
├── ARCHITECTURE.md              ← High-level system design
├── ARCHITECTURE_DEEP_DIVE.md    ← Detailed technical deep-dive
│
├── backend/
│   ├── .env                     ← Environment variables
│   ├── requirements.txt         ← Python dependencies
│   └── app/
│       ├── main.py              ← FastAPI app, CORS, startup
│       ├── config.py            ← All settings (LLM, limits, paths)
│       ├── database.py          ← SQLite models (User, Document, Dataset, Chat)
│       ├── models/
│       │   └── schemas.py       ← Pydantic request/response schemas
│       ├── routers/
│       │   ├── rag.py           ← /api/rag/* endpoints
│       │   └── analyst.py       ← /api/analyst/* endpoints
│       └── services/
│           ├── llm.py           ← HuggingFace + Ollama LLM clients
│           ├── embeddings.py    ← SentenceTransformer wrapper
│           ├── vector_store.py  ← FAISS index management
│           ├── document_parser.py ← PDF + URL text extraction
│           ├── chunker.py       ← Text splitting for RAG
│           └── code_executor.py ← Safe pandas code execution
│
└── frontend/
    ├── .env.local               ← API URL config
    ├── next.config.mjs          ← Next.js config
    ├── tailwind.config.ts       ← Tailwind CSS config
    ├── app/
    │   ├── layout.tsx           ← Root layout with navigation
    │   ├── page.tsx             ← Landing page
    │   ├── chat/
    │   │   └── page.tsx         ← RAG chatbot page
    │   └── analyst/
    │       └── page.tsx         ← Data analyst page
    ├── components/
    │   ├── ChatWindow.tsx       ← Reusable chat UI component
    │   └── FileUpload.tsx       ← Drag-and-drop file upload
    └── lib/
        └── api.ts               ← Backend API client functions
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- One of:
  - **Ollama** installed locally (recommended for development)
  - **HuggingFace account** with a free API token

---

## Setup & Run

### 1. Backend

```bash
cd personal/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure LLM provider (edit .env)
# Option A: Ollama (local, no API key needed)
#   LLM_PROVIDER=ollama
#   Install: curl -fsSL https://ollama.com/install.sh | sh
#   Pull model: ollama pull mistral:7b-instruct-v0.3-q4_K_M
#
# Option B: HuggingFace (free API, needs token)
#   LLM_PROVIDER=huggingface
#   HF_TOKEN=hf_your_token_here
#   Get token: https://huggingface.co/settings/tokens

# Start the server
uvicorn app.main:app --reload --port 8000
```

The backend starts at `http://localhost:8000`. API docs available at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd personal/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend starts at `http://localhost:3000`.

---

## API Endpoints

### RAG Chatbot

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/rag/upload/pdf` | Upload a PDF file |
| `POST` | `/api/rag/upload/url` | Index a web page by URL |
| `GET` | `/api/rag/documents` | List uploaded documents |
| `POST` | `/api/rag/query` | Ask a question against documents |

### Data Analyst

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyst/upload` | Upload CSV or Excel file |
| `GET` | `/api/analyst/datasets` | List uploaded datasets |
| `POST` | `/api/analyst/query` | Ask a question about data |
| `GET` | `/api/analyst/chart/{user_id}/{filename}` | Serve generated chart |

### System

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |

---

## How It Works

### RAG Chatbot Flow

```
User uploads PDF → PyMuPDF extracts text → Chunker splits into 512-char pieces
→ MiniLM-L6 creates embeddings → FAISS indexes vectors

User asks question → Embed question → FAISS finds top-5 similar chunks
→ Build prompt with context → LLM generates answer → Return with sources
```

### Data Analyst Flow

```
User uploads CSV → Pandas parses file → Store metadata in SQLite

User asks question → Generate data summary → LLM writes Python code
→ AST validates code (blocks dangerous imports/functions)
→ Execute in restricted namespace → Return result + chart URL
```

---

## Configuration

All settings are in `backend/app/config.py` and can be overridden via environment variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama` or `huggingface` |
| `HF_TOKEN` | `` | HuggingFace API token |
| `OLLAMA_MODEL` | `mistral:7b-instruct-v0.3-q4_K_M` | Ollama model name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformers model |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `RETRIEVAL_TOP_K` | `5` | Number of chunks retrieved |
| `SIMILARITY_THRESHOLD` | `0.3` | Minimum cosine similarity |
| `RATE_LIMIT_PER_HOUR` | `20` | Max queries per user per hour |
| `MAX_PDF_SIZE_MB` | `10` | Max PDF upload size |
| `MAX_CSV_SIZE_MB` | `50` | Max CSV upload size |

---

## File Storage

All data is stored locally under `backend/data/`:

```
data/
├── app.db                    ← SQLite database
└── users/
    └── {user_id}/
        ├── documents/        ← Uploaded PDFs
        ├── datasets/         ← Uploaded CSV/Excel files
        ├── indexes/          ← FAISS index + chunk metadata per document
        └── charts/           ← Generated Plotly charts (HTML)
```

---

## Security

- **Code execution sandbox**: LLM-generated code is validated with Python's AST module before execution. Blocked: `exec`, `eval`, `open`, `os`, `subprocess`, `sys`, and all non-whitelisted imports.
- **File validation**: Upload size limits enforced. Only PDF, CSV, and Excel accepted.
- **User isolation**: Each user's files, indexes, and data are stored in separate directories. All DB queries filter by `user_id`.

---

## Deployment (Free)

| Component | Platform | Free Tier |
|---|---|---|
| Frontend | Vercel | Unlimited deploys, 100GB bandwidth |
| Backend | Render.com | 750 hrs/month, 512MB RAM |
| Alternative | Railway.app | $5 credit/month |

```bash
# Deploy frontend
cd frontend
npx vercel deploy

# Deploy backend (add render.yaml or connect GitHub repo on render.com)
```

**Note**: Render free tier spins down after 15 min of inactivity (30s cold start). Use HuggingFace as LLM provider for deployment since Ollama requires persistent RAM.

---

## Limitations

- **Response time**: 5-30s per query (LLM inference)
- **Concurrent users**: 3-5 on free hosting (512MB RAM)
- **Render cold starts**: ~30s after 15 min idle
- **HuggingFace rate limits**: ~1000 requests/day on free tier
- **No auth**: Currently uses a hardcoded `demo_user` — add Supabase Auth for production
- **No streaming**: Responses are returned in full (add SSE for streaming UX)

---

## Next Steps

1. Add user authentication (Supabase Auth)
2. Add response streaming (SSE)
3. Add response caching (hash query + context)
4. Add rate limiting middleware
5. Add chat history persistence
6. Deploy to Vercel + Render
