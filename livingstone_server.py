"""
Livingstone - Your Personal Document Assistant
Day 4: Authentication + Rate Limiting (FIXED)
"""

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
import mlflow
import time
import uuid
from datetime import datetime

# Load API keys
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Get the secret API key for authentication
SECRET_API_KEY = os.getenv("API_KEY", "mylivingstonekey123")

# Setup MLflow tracking
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "./mlflow_data")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "Livingstone_RAG_System")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")
print(f"MLflow experiment: {MLFLOW_EXPERIMENT_NAME}")

# Setup rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Livingstone Assistant")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup security
security = HTTPBearer()

# Verify API key function
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != SECRET_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return credentials.credentials

# Livingstone's personality prompt
LIVINGSTONE_PROMPT = """You are Livingstone, a friendly and helpful document assistant.

Your personality:
- You are warm and approachable
- You always cite your sources
- You say "Livingstone here!" at the start of responses

Instructions:
1. Answer based ONLY on the provided documents
2. Always mention the source document name
3. Be friendly and helpful
4. If you cannot find the answer, say "Livingstone couldn't find that. Try rephrasing?""

"""

# Setup ChromaDB
try:
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-3-small"
    )
    collection = chroma_client.get_collection(
        name="company_policies",
        embedding_function=openai_ef
    )
    print("✅ ChromaDB connected successfully")
except Exception as e:
    print(f"⚠️ ChromaDB error: {e}")
    collection = None

def search_documents(question, k=3):
    if collection is None:
        return {'documents': [[]], 'metadatas': [[]]}
    results = collection.query(query_texts=[question], n_results=k)
    return results

def generate_livingstone_answer(question, search_results):
    if not search_results['documents'][0]:
        return "Livingstone couldn't find that information. Try rephrasing your question?", []
    
    context_parts = []
    sources = []
    for i, (doc, metadata) in enumerate(zip(
        search_results['documents'][0],
        search_results['metadatas'][0]
    )):
        context_parts.append(f"[Document {i+1} - {metadata['source']}]:\n{doc}")
        sources.append(metadata['source'])
    
    context = "\n\n---\n\n".join(context_parts)
    
    prompt = f"""{LIVINGSTONE_PROMPT}

DOCUMENTS:
{context}

USER QUESTION: {question}

ANSWER:"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content, list(set(sources))

# Home page
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Livingstone - Document Assistant</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f0f2f5;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #4a5568;
                text-align: center;
            }
            .subtitle {
                text-align: center;
                color: #718096;
                margin-bottom: 30px;
            }
            input {
                width: 70%;
                padding: 12px;
                font-size: 16px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            button {
                padding: 12px 24px;
                font-size: 16px;
                background: #4a5568;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                margin-left: 10px;
            }
            button:hover {
                background: #2d3748;
            }
            .answer-box {
                margin-top: 30px;
                padding: 20px;
                background: #f7fafc;
                border-radius: 8px;
                min-height: 150px;
            }
            .sources {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #ddd;
                color: #4a5568;
                font-size: 14px;
            }
            .loading {
                color: #a0aec0;
                text-align: center;
            }
            .api-key-input {
                margin-bottom: 20px;
                padding: 10px;
                background: #e6fffa;
                border-radius: 8px;
            }
            .api-key-input input {
                width: 60%;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Livingstone</h1>
            <div class="subtitle">Your personal document assistant</div>
            
            <div class="api-key-input">
                <label>🔑 API Key: </label>
                <input type="password" id="apiKey" placeholder="Enter your API key">
                <button onclick="saveApiKey()">Save Key</button>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <input type="text" id="question" placeholder="Ask me anything..." style="width: 70%;">
                <button onclick="askLivingstone()">Ask</button>
            </div>
            
            <div class="answer-box" id="answerBox">
                <div class="loading">Enter your API key, then ask Livingstone a question</div>
            </div>
        </div>
        
        <script>
            function saveApiKey() {
                const apiKey = document.getElementById('apiKey').value;
                if (!apiKey) {
                    alert('Please enter an API key');
                    return;
                }
                localStorage.setItem('livingstone_api_key', apiKey);
                document.getElementById('answerBox').innerHTML = '<div class="loading">✅ API key saved! Now ask a question.</div>';
            }
            
            async function askLivingstone() {
                let sessionID = localStorage.getItem('livingstone_session_id');
                if (!sessionID) {
                    sessionID = crypto.randomUUID();
                    localStorage.setItem('livingstone_session_id', sessionID);
                }
                
                const question = document.getElementById('question').value;
                const apiKey = localStorage.getItem('livingstone_api_key');
                
                if (!apiKey) {
                    alert('Please enter and save your API key first');
                    return;
                }
                
                if (!question) {
                    alert('Please type a question');
                    return;
                }
                
                const answerBox = document.getElementById('answerBox');
                answerBox.innerHTML = '<div class="loading">Livingstone is thinking...</div>';
                
                try {
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + apiKey
                        },
                            body: JSON.stringify({
                                question: question,
                                session_id: sessionID
                            })
                    });
                    
                    if (response.status === 403) {
                        answerBox.innerHTML = '<div class="loading">Invalid API key. Please check and save again. Use: mylivingstonekey123</div>';
                        return;
                    }
                    
                    if (response.status === 429) {
                        answerBox.innerHTML = '<div class="loading">Too many requests. Please wait a minute.</div>';
                        return;
                    }
                    
                    if (!response.ok) {
                        answerBox.innerHTML = '<div class="loading">Server error. Check terminal for details.</div>';
                        return;
                    }
                    
                    const data = await response.json();
                    answerBox.innerHTML = `
                        <div>${data.answer}</div>
                        <div class="sources">📚 Sources: ${data.sources.join(', ')}</div>
                    `;
                } catch (error) {
                    console.error('Error:', error);
                    answerBox.innerHTML = '<div class="loading">Connection error. Make sure server is running at localhost:8000</div>';
                }
            }
            
            document.getElementById('question').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    askLivingstone();
                }
            });
            
            // Load saved API key on page load
            const savedKey = localStorage.getItem('livingstone_api_key');
            if (savedKey) {
                document.getElementById('apiKey').value = savedKey;
            }
        </script>
    </body>
    </html>
    """

# API endpoint with authentication and rate limiting
@app.post("/ask")
@limiter.limit("100/minute")
async def ask(request: Request, api_key: str = Depends(verify_api_key)):
    # Start timing the request
    start_time = time.time()
    
    # Get the question from the request
    data = await request.json()
    question = data.get("question", "")
    session_id = data.get("session_id", "unknown")
    
    if not question:
        return {"answer": "Livingstone here! Please ask me a question.", "sources": []}
    
    # Search for relevant documents
    search_results = search_documents(question)
    
    # Generate answer
    answer, sources = generate_livingstone_answer(question, search_results)
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Log to MLflow
    with mlflow.start_run(run_name=f"Q_{session_id[:8]}"):
        # Log parameters (inputs)
        mlflow.log_param("question", question)
        mlflow.log_param("session_id", session_id)
        
        # Log metrics (numbers)
        mlflow.log_metric("response_time_seconds", response_time)
        mlflow.log_metric("num_sources", len(sources))
        mlflow.log_metric("num_chunks", len(search_results['documents'][0]) if search_results['documents'][0] else 0)
        
        # Log artifacts (outputs)
        mlflow.log_text(answer, "answer.txt")
        mlflow.log_text(str(sources), "sources.txt")
        
        # Log tags (metadata)
        mlflow.set_tag("timestamp", str(datetime.now()))
        mlflow.set_tag("question_length", len(question))
        mlflow.set_tag("answer_length", len(answer))
    
    print(f"📊 Logged to MLflow: Q={question[:50]}... | Time={response_time:.2f}s | Sources={len(sources)}")
    
    return {"answer": answer, "sources": sources}