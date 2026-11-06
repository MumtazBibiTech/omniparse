
from .embeddings import RealEmbeddings
from .vector_store import VectorStore
from pathlib import Path
from typing import List, Dict

class RAGEngine:
    def __init__(self):
        self.embeddings = RealEmbeddings()
        self.vector_store = VectorStore()
        self.graph_store = {}

    def build_graph(self, chunks: List[Dict]) -> Dict:
        nodes = {}
        edges = []
        for c in chunks:
            if c["file"] not in nodes:
                nodes[c["file"]] = {"id": c["file"], "label": Path(c["file"]).name, "functions": [], "type": "file"}
            nodes[c["file"]]["functions"].append(c["name"])
        
        # Real import parsing - who calls who
        for c in chunks:
            content = c["content"].lower()
            for f, data in nodes.items():
                if f == c["file"]: continue
                for func in data["functions"]:
                    if len(func) > 3 and func.lower() in content:
                        edges.append({"from": c["file"], "to": f, "label": f"calls {func}", "type": "call"})
                        break
        
        return {"nodes": list(nodes.values()), "edges": edges}

    async def index_repo(self, repo_id: str, chunks: List[Dict]):
        print(f"[RAG] Indexing {len(chunks)} chunks with BGE-large...")
        # Real embeddings
        texts = [c["content"][:1000] for c in chunks]
        embeddings = self.embeddings.encode(texts, is_query=False)
        
        # Real vector store
        await self.vector_store.upsert(repo_id, chunks, embeddings)
        
        # Graph
        graph = self.build_graph(chunks)
        self.graph_store[repo_id] = graph
        print(f"[RAG] Done: {len(chunks)} vectors + graph {len(graph['nodes'])} nodes")

    async def hybrid_search(self, repo_id: str, query: str, top_k=5) -> List[Dict]:
        # 1. Vector search with real BGE query embedding
        query_emb = self.embeddings.encode_single(query, is_query=True)
        vector_results = await self.vector_store.search(repo_id, query_emb, top_k=top_k)
        
        # 2. Graph expansion - if auth/service found, get its dependents
        graph = self.graph_store.get(repo_id, {})
        found_files = {r["file"] for r in vector_results}
        expanded = []
        
        for edge in graph.get("edges", []):
            if edge["from"] in found_files and edge["to"] not in found_files:
                # Find chunk from connected file
                all_chunks = []
                # In prod, fetch from vector store
                # For now, we return graph info
                expanded.append({"file": edge["to"], "name": "connected", "content": f"Connected via {edge['label']}", "score": 0.75, "search_type": "graph"})
        
        # Combine
        results = []
        for r in vector_results:
            results.append({**r, "search_type": "vector"})
        results.extend(expanded[:2])
        
        return results[:top_k]

    def get_graph(self, repo_id: str) -> Dict:
        return self.graph_store.get(repo_id, {"nodes": [], "edges": []})
