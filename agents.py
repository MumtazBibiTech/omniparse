
import os
from typing import List, Dict

class RouterAgent:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if self.groq_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_key)
                print("[Agents] Groq client ready - Llama 3 70B streaming")
            except:
                print("[Agents] Groq not installed, using fallback")

    async def route(self, question: str, mode: str) -> str:
        q = question.lower()
        if "security" in q or mode == "security": return "security_agent"
        if "document" in q or "readme" in q or mode == "docs": return "docs_agent"
        if "where" in q or "find" in q or mode == "search": return "search_agent"
        return "explain_agent"

    async def generate_answer_stream(self, question: str, context: List[Dict], agent_type: str):
        # Real Groq streaming prompt
        context_str = "\n\n".join([f"File: {c['file']}::{c['name']}\n{c['content'][:500]}" for c in context[:3]])
        
        system_prompts = {
            "explain_agent": "You are a senior staff engineer. Explain code with file citations. Be concise, technical.",
            "search_agent": "You are a code search expert. Find where functionality is implemented. Return file paths and function names.",
            "docs_agent": "You are a documentation generator. Generate README, architecture docs from code.",
            "security_agent": "You are a security auditor. Find hardcoded secrets, SQL injection, XSS risks."
        }
        
        system = system_prompts.get(agent_type, system_prompts["explain_agent"])
        
        prompt = f"""{system}

Context from codebase:
{context_str}

Question: {question}

Answer with:
1. Direct answer
2. File citations with function names
3. Graph connections if relevant

Keep it technical and precise."""
        
        if self.client:
            # REAL Groq streaming - Llama 3 70B
            stream = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1024,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            # Fallback for demo without API key
            mock = f"[{agent_type}] Based on {len(context)} files: "
            if context:
                mock += f"Auth is in {context[0]['file']}::{context[0]['name']}. "
                mock += f"It uses JWT middleware. Found in {', '.join([c['file'] for c in context[:2]])}."
            else:
                mock += "No context found. Clone a repo first."
            for word in mock.split():
                yield word + " "

    async def generate_answer(self, question: str, context: List[Dict], agent_type: str) -> str:
        full = ""
        async for token in self.generate_answer_stream(question, context, agent_type):
            full += token
        return full
