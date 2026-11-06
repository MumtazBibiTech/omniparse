
'use client'
import { useState, useEffect } from 'react'

type Node = { id: string, label: string, x: number, y: number, type: string }
type Edge = { from: string, to: string, label: string }

export default function OmniParseUnbeatable(){
  const [repo, setRepo] = useState("https://github.com/vercel/next.js")
  const [jobId, setJobId] = useState("")
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  const [question, setQuestion] = useState("Where is authentication handled?")
  const [answer, setAnswer] = useState("")
  const [sources, setSources] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const mockGraph = {
    nodes: [
      { id: "auth/service.ts", label: "service.ts", x: 20, y: 20, type: "core" },
      { id: "middleware/auth.ts", label: "auth.ts", x: 60, y: 30, type: "mid" },
      { id: "api/user.ts", label: "user.ts", x: 40, y: 60, type: "api" },
      { id: "db/index.ts", label: "index.ts", x: 80, y: 70, type: "db" },
      { id: "utils/jwt.ts", label: "jwt.ts", x: 10, y: 70, type: "util" },
    ],
    edges: [
      { from: "auth/service.ts", to: "middleware/auth.ts", label: "calls authenticate" },
      { from: "middleware/auth.ts", to: "api/user.ts", label: "protects" },
      { from: "api/user.ts", to: "db/index.ts", label: "queries" },
      { from: "auth/service.ts", to: "utils/jwt.ts", label: "uses" },
    ]
  }

  const handleParse = async () => {
    setLoading(true)
    // In prod: fetch('/api/analyze', {method: 'POST', body: JSON.stringify({repo_url: repo})})
    setTimeout(() => {
      setNodes(mockGraph.nodes)
      setEdges(mockGraph.edges)
      setJobId("abc123")
      setLoading(false)
    }, 1500)
  }

  const handleChat = async () => {
    setAnswer("")
    setSources([])
    // In prod: streaming fetch to /api/chat
    const mockAnswer = "Auth is handled in auth/service.ts::authenticateUser(). It uses JWT verification via utils/jwt.ts. The middleware in middleware/auth.ts calls it for protected routes. 3 files depend on it: api/user.ts, api/admin.ts, api/profile.ts. See graph visualization."
    for (let i=0; i<mockAnswer.length; i+=5) {
      setAnswer(mockAnswer.slice(0, i+5))
      await new Promise(r => setTimeout(r, 30))
    }
    setSources([
      { file: "auth/service.ts", name: "authenticateUser", score: 0.92, search_type: "vector" },
      { file: "middleware/auth.ts", name: "authMiddleware", score: 1.0, search_type: "keyword" },
      { file: "api/user.ts", name: "getUser", score: 0.75, search_type: "graph", via: "calls authMiddleware" },
    ])
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white font-mono">
      <header className="border-b border-white/[0.08] p-4 flex justify-between items-center backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center text-black font-black text-lg">O</div>
          <div>
            <div className="font-bold text-[15px] tracking-tight">OmniParse</div>
            <div className="text-[10px] text-white/40 -mt-1">UNBEATABLE EDITION</div>
          </div>
          <span className="text-[10px] bg-white text-black px-2 py-0.5 rounded-full font-bold ml-2">PRO</span>
          <span className="text-[10px] bg-white/10 border border-white/20 px-2 py-0.5 rounded-full ml-1">BGE-large • Graph RAG • Groq 70B</span>
        </div>
        <div className="text-[11px] text-white/30">AST-Aware • Hybrid Search • Multi-Agent • Streaming</div>
      </header>

      <div className="grid grid-cols-12 h-[calc(100vh-65px)]">
        <div className="col-span-7 border-r border-white/[0.06] p-5 flex flex-col">
          <div className="flex gap-2 mb-4">
            <input value={repo} onChange={e=>setRepo(e.target.value)} className="flex-1 bg-white/[0.04] border border-white/[0.08] rounded-[10px] px-4 py-[14px] text-[13px] focus:outline-none focus:border-white/20" placeholder="https://github.com/user/repo"/>
            <button onClick={handleParse} disabled={loading} className="bg-white text-black px-6 py-[14px] rounded-[10px] font-bold text-[13px] hover:bg-white/90 disabled:opacity-50">{loading ? "Parsing..." : "Parse Repo →"}</button>
          </div>

          <div className="flex gap-2 mb-3 text-[11px]">
            <span className="bg-white/10 px-2 py-1 rounded-full">{nodes.length || 0} files</span>
            <span className="bg-white/10 px-2 py-1 rounded-full">{edges.length || 0} edges</span>
            <span className="bg-white/10 px-2 py-1 rounded-full">BGE-large 1024d</span>
            <span className="bg-white/10 px-2 py-1 rounded-full">Qdrant</span>
          </div>

          <div className="flex-1 bg-white/[0.02] border border-white/[0.06] rounded-[16px] relative overflow-hidden">
            <div className="absolute inset-0 opacity-[0.03]" style={{backgroundImage: 'radial-gradient(white 1px, transparent 1px)', backgroundSize: '24px 24px'}}></div>
            
            {nodes.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-10">
                <div className="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center mb-4 text-2xl">🕸️</div>
                <div className="font-bold text-[14px]">Paste a GitHub repo to visualize</div>
                <div className="text-[12px] text-white/40 mt-2 max-w-sm">We parse with Tree-sitter AST, build dependency graph with BGE-large embeddings, and visualize with React Flow. Try vercel/next.js</div>
              </div>
            ) : (
              <div className="relative w-full h-full p-6">
                <svg className="absolute inset-0 w-full h-full">
                  {edges.map((e,i)=>{
                    const from = nodes.find(n=>n.id===e.from)
                    const to = nodes.find(n=>n.id===e.to)
                    if(!from||!to) return null
                    return <g key={i}><line x1={`${from.x}%`} y1={`${from.y}%`} x2={`${to.x}%`} y2={`${to.y}%`} stroke="white" strokeOpacity="0.15" strokeWidth="1.5"/><text x={`${(from.x+to.x)/2}%`} y={`${(from.y+to.y)/2}%`} fill="white" fontSize="9" opacity="0.5">{e.label}</text></g>
                  })}
                </svg>
                {nodes.map(n=>(
                  <div key={n.id} style={{left: `${n.x}%`, top: `${n.y}%`}} className="absolute -translate-x-1/2 -translate-y-1/2 group">
                    <div className={`px-3 py-2 rounded-full border text-[11px] font-medium backdrop-blur bg-white/[0.06] border-white/20 group-hover:bg-white group-hover:text-black transition-all cursor-pointer ${n.type==='core' ? 'border-white/40' : ''}`}>
                      <div className="text-[9px] opacity-50">{n.id.split('/')[0]}/</div>{n.label}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="col-span-5 p-5 flex flex-col bg-white/[0.01]">
          <div className="flex gap-2 mb-3">
            {["Explain","Search","Docs","Security"].map(m=>(
              <button key={m} className="text-[11px] px-3 py-1.5 rounded-full bg-white/10 border border-white/10 hover:bg-white/20">{m}</button>
            ))}
            <span className="ml-auto text-[10px] text-white/30 py-1.5">Groq Llama 3 70B • Streaming</span>
          </div>

          <div className="flex-1 bg-white/[0.03] border border-white/[0.06] rounded-[16px] p-4 overflow-y-auto">
            <div className="space-y-4">
              <div className="flex justify-end"><div className="bg-white text-black px-4 py-2.5 rounded-[14px] rounded-br-[4px] text-[13px] max-w-[80%]">{question}</div></div>
              
              {answer && (
                <div className="space-y-3">
                  <div className="bg-white/[0.06] border border-white/[0.06] px-4 py-3 rounded-[14px] rounded-bl-[4px] text-[13px] leading-relaxed">
                    <div className="text-[10px] text-white/40 mb-2 flex gap-2"><span className="bg-white text-black px-1.5 py-0.5 rounded">EXPLAIN_AGENT</span><span>Groq 70B • 0.92 score</span></div>
                    {answer}
                  </div>
                  
                  {sources.length>0 && (
                    <div className="space-y-2">
                      <div className="text-[10px] text-white/30 uppercase tracking-widest">Sources • Hybrid Search (Vector + Keyword + Graph)</div>
                      {sources.map((s,i)=>(
                        <div key={i} className="flex items-center gap-2 text-[11px] bg-white/[0.04] border border-white/[0.06] px-3 py-2 rounded-full">
                          <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${s.search_type==='vector' ? 'bg-blue-500' : s.search_type==='keyword' ? 'bg-green-500' : 'bg-purple-500'} text-white`}>{s.search_type}</span>
                          <span className="font-mono">{s.file}::{s.name}</span>
                          <span className="ml-auto text-white/40">{s.score}</span>
                          {s.via && <span className="text-white/30">via {s.via}</span>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="mt-4 flex gap-2">
            <input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask anything about this codebase..." className="flex-1 bg-white/[0.05] border border-white/[0.08] rounded-[12px] px-4 py-3 text-[13px] focus:outline-none"/>
            <button onClick={handleChat} className="bg-white text-black w-11 h-11 rounded-[12px] flex items-center justify-center font-bold">↑</button>
          </div>
          <div className="mt-2 text-[10px] text-white/20 text-center">Enter to send • Streaming with Groq Llama 3 70B • Citations with file paths</div>
        </div>
      </div>
    </div>
  )
}
