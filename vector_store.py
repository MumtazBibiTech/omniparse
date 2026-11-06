
from typing import List, Dict
import os
import uuid

class VectorStore:
    def __init__(self, collection="omniparse_code"):
        self.collection = collection
        self.use_qdrant = False
        self.client = None
        self.chroma_client = None
        
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_key = os.getenv("QDRANT_API_KEY")
        
        if qdrant_url and qdrant_key:
            try:
                from qdrant_client import QdrantClient
                self.client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
                self.use_qdrant = True
                print(f"[VectorStore] Using Qdrant Cloud: {qdrant_url}")
                # Create collection if not exists
                try:
                    from qdrant_client.models import Distance, VectorParams
                    self.client.create_collection(
                        collection_name=collection,
                        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
                    )
                except: pass
            except Exception as e:
                print(f"[VectorStore] Qdrant failed, fallback to Chroma: {e}")
        
        if not self.use_qdrant:
            try:
                import chromadb
                self.chroma_client = chromadb.Client()
                self.collection_obj = self.chroma_client.get_or_create_collection(name=collection)
                print("[VectorStore] Using ChromaDB local (no API key needed)")
            except:
                print("[VectorStore] Using in-memory fallback")
                self.store = {}
    
    async def upsert(self, repo_id: str, chunks: List[Dict], embeddings):
        if self.use_qdrant and self.client:
            from qdrant_client.models import PointStruct
            points = []
            for i, chunk in enumerate(chunks):
                points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embeddings[i].tolist() if hasattr(embeddings[i], 'tolist') else embeddings[i],
                    payload={
                        "file": chunk["file"],
                        "name": chunk["name"],
                        "type": chunk["type"],
                        "content": chunk["content"][:2000],
                        "repo_id": repo_id,
                        "language": chunk["language"]
                    }
                ))
            self.client.upsert(collection_name=self.collection, points=points)
        elif self.chroma_client:
            ids = [f"{repo_id}_{i}" for i in range(len(chunks))]
            self.collection_obj.add(
                ids=ids,
                embeddings=[e.tolist() if hasattr(e, 'tolist') else e for e in embeddings],
                metadatas=[{"file": c["file"], "name": c["name"], "repo_id": repo_id} for c in chunks],
                documents=[c["content"][:1000] for c in chunks]
            )
        else:
            self.store[repo_id] = chunks
        print(f"[VectorStore] Indexed {len(chunks)} chunks for {repo_id}")
    
    async def search(self, repo_id: str, query_embedding, top_k=5):
        if self.use_qdrant and self.client:
            results = self.client.search(
                collection_name=self.collection,
                query_vector=query_embedding.tolist() if hasattr(query_embedding, 'tolist') else query_embedding,
                query_filter={"must": [{"key": "repo_id", "match": {"value": repo_id}}]},
                limit=top_k
            )
            return [{"file": r.payload["file"], "name": r.payload["name"], "content": r.payload["content"], "score": r.score} for r in results]
        elif self.chroma_client:
            res = self.collection_obj.query(query_embeddings=[query_embedding.tolist()], n_results=top_k, where={"repo_id": repo_id})
            return [{"file": m["file"], "name": m["name"], "content": doc, "score": 0.9} for m, doc in zip(res["metadatas"][0], res["documents"][0])]
        else:
            # Fallback uses in-memory
            return self.store.get(repo_id, [])[:top_k]
