# OmniParse - AI Codebase Intelligence Platform

> Paste any GitHub repo URL. Chat with it. Visualize dependency graph. Auto-generate docs.

![OmniParse](https://img.shields.io/badge/BGE--large-1024d-blue) ![Graph RAG](https://img.shields.io/badge/Graph%20RAG-Real-purple) ![Groq](https://img.shields.io/badge/Groq-Llama3%2070B-green)

## Live Demo
Frontend: Coming soon (Vercel)
API Docs: /docs
HF Space: Coming soon

## Why Not a Toy Project?
- AST-Aware: Tree-sitter + Python AST, not random text splitting
- Graph RAG: Builds who-imports-who graph
- Hybrid Search: Vector (BGE-large) + Keyword (BM25) + Graph expansion
- Multi-Agent: Router → Search, Explain, Docs, Security via LangGraph
- Streaming: Real-time with Groq Llama 3 70B

## Architecture
GitHub URL -> Cloner (depth=1) -> AST Parser -> BGE-large Embeddings -> Qdrant -> Knowledge Graph -> Router Agent -> Specialized Agents

## Quick Start
Backend: pip install -r requirements.txt && uvicorn main:app --reload
Frontend: npm install && npm run dev

Built with Next.js 14, FastAPI, Qdrant, Groq, BGE-large, LangGraph
