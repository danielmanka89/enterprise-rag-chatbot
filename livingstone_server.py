from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
SECRET_API_KEY = os.getenv("API_KEY", "mylivingstonekey123")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Livingstone Assistant")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != SECRET_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return credentials.credentials

LIVINGSTONE_PROMPT = """You are Livingstone, a friendly and helpful document assistant. You say "Livingstone here!" at the start of responses. Answer based ONLY on the provided documents. Always mention the source document name. Be friendly and helpful."""

# Setup ChromaDB
print("Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=api_key,
    model_name="text-embedding-3-small"
)
collection = chroma_client.get_collection(
    name="company_policies",
    embedding_function=openai_ef
)
print(f"✅ ChromaDB connected with {collection.count()} documents")

def search_documents(question, k=3):
    results = collection.query(query_texts=[question], n_results=k)
    return results

def generate_livingstone_answer(question, search_results):
    if not search_results['documents'][0]:
        return "Livingstone couldn't find that information. Try rephrasing your question?", []
    
    context_parts = []
    sources = []
    for i, (doc, metadata) in enumerate(zip(search_results['documents'][0], search_results['metadatas'][0])):
        context_parts.append(f"[Document {i+1} - {metadata['source']}]:\n{doc}")
        sources.append(metadata['source'])
    
    context = "\n\n---\n\n".join(context_parts)
    prompt = f"{LIVINGSTONE_PROMPT}\n\nDOCUMENTS:\n{context}\n\nUSER QUESTION: {question}\n\nANSWER:"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content, list(set(sources))

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Livingstone</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; background: #f0f2f5; }
            .container { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            input { width: 70%; padding: 12px; margin: 5px; }
            button { padding: 12px 24px; background: #4a5568; color: white; border: none; border-radius: 8px; cursor: pointer; }
            .answer-box { margin-top: 30px; padding: 20px; background: #f7fafc; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧭 Livingstone</h1>
            <p>Your personal document assistant</p>
            <div><input type="password" id="apiKey" placeholder="API Key"><button onclick="saveKey()">Save Key</button></div>
            <div><input type="text" id="question" placeholder="Ask me anything..."><button onclick="ask()">Ask</button></div>
            <div class="answer-box" id="answer">💬 Enter API key, then ask Livingstone a question</div>
        </div>
        <script>
            function saveKey() { localStorage.setItem('api_key', document.getElementById('apiKey').value); document.getElementById('answer').innerHTML = '✅ Key saved! Now ask a question.'; }
            async function ask() {
                const apiKey = localStorage.getItem('api_key');
                if(!apiKey){ alert('Save API key first'); return; }
                const question = document.getElementById('question').value;
                if(!question){ alert('Type a question'); return; }
                document.getElementById('answer').innerHTML = '🤔 Livingstone is thinking...';
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + apiKey },
                    body: JSON.stringify({question: question})
                });
                const data = await response.json();
                document.getElementById('answer').innerHTML = `<div>${data.answer}</div><div style="margin-top:15px; color:#4a5568;">📚 Sources: ${data.sources.join(', ')}</div>`;
            }
            document.getElementById('question').addEventListener('keypress', function(e) { if(e.key === 'Enter') ask(); });
        </script>
    </body>
    </html>
    """

@app.post("/ask")
@limiter.limit("100/minute")
async def ask(request: Request, api_key: str = Depends(verify_api_key)):
    data = await request.json()
    question = data.get("question", "")
    if not question:
        return {"answer": "Please ask a question.", "sources": []}
    search_results = search_documents(question)
    answer, sources = generate_livingstone_answer(question, search_results)
    return {"answer": answer, "sources": sources}
