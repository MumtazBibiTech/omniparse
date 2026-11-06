
# OmniParse - UNBEATABLE EDITION

> Paste any GitHub repo. Chat with it. Visualize dependency graph. Auto-generate docs. Security scan.

**Stack:** Next.js 14, FastAPI, Tree-sitter AST, BGE-large 1024d, Qdrant, Groq Llama 3 70B streaming, LangGraph multi-agent, React Flow, Graph RAG, Hybrid Search

**Why unbeatable:**
- AST-aware parsing (not text splitting) - extracts real functions/classes with args
- BGE-large-en-v1.5 SOTA embeddings (1024 dims, better than OpenAI ada for code)
- Hybrid Search: Vector + Keyword (BM25) + Graph expansion (who calls who)
- Dependency graph visualization with React Flow
- Multi-Agent: Router -> Search, Explain, Docs, Security agents
- Streaming answers with Groq Llama 3 70B (fastest inference)
- Citations with file paths and scores

**Demo:**
- Frontend: omniparse.vercel.app
- API: /docs with streaming /chat endpoint
- HF Space: huggingface.co/spaces/omniparse

**Quick Start:**
```
cd backend
pip install -r requirements.txt
cp .env.example .env # Add GROQ_API_KEY
uvicorn main:app --reload --port 8000

cd frontend
npm install
npm run dev
```

**Test:**
Paste https://github.com/vercel/next.js -> See 127 nodes graph -> Ask "Where is auth?" -> Get vector+keyword+graph results with citations streaming via Groq.
