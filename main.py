
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
from core.cloner import clone_repo
from core.parser import CodeParser
from core.rag_engine import RAGEngine
from core.agents import RouterAgent
import uuid
import json

app = FastAPI(title="OmniParse API - Unbeatable", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

parser = CodeParser()
rag = RAGEngine()
router = RouterAgent()

class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl

class ChatRequest(BaseModel):
    repo_id: str
    question: str
    mode: str = "explain"

@app.post("/analyze")
async def analyze_repo(req: AnalyzeRequest):
    job_id = str(uuid.uuid4())[:8]
    print(f"[API] Analyzing {req.repo_url}")
    path = await clone_repo(str(req.repo_url), job_id)
    chunks = await parser.parse_codebase(path)
    await rag.index_repo(job_id, chunks)
    graph = rag.get_graph(job_id)
    return {
        "job_id": job_id,
        "status": "ready",
        "files_indexed": len(chunks),
        "graph": graph,
        "stats": {
            "nodes": len(graph["nodes"]),
            "edges": len(graph["edges"]),
            "chunks": len(chunks)
        }
    }

@app.post("/chat")
async def chat(req: ChatRequest):
    agent_type = await router.route(req.question, req.mode)
    context = await rag.hybrid_search(req.repo_id, req.question, top_k=5)
    
    async def generate():
        # Stream real Groq response
        async for token in router.generate_answer_stream(req.question, context, agent_type):
            yield f"data: {json.dumps({'token': token, 'agent': agent_type})}\n\n"
        # Send final sources
        yield f"data: {json.dumps({'done': True, 'sources': context[:3], 'graph': rag.get_graph(req.repo_id)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/health")
def health():
    return {"status": "OmniParse Unbeatable running", "version": "2.0.0", "features": ["BGE-large", "Graph RAG", "Hybrid Search", "Groq Streaming", "Multi-Agent"]}
