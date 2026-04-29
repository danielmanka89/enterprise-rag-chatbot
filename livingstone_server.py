"""
Livingstone - Your Personal Document Assistant
Day 3: FastAPI + RAG + Personality
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Create Livingstone app
app = FastAPI(title="Livingstone Assistant", description="Your personal document Q&A assistant")

# Livingstone's personality prompt
LIVINGSTONE_PROMPT = """You are Livingstone, a friendly and helpful document assistant.

Your personality:
- You are warm and approachable
- You call the user by name if they tell you
- You always cite your sources
- You say "Livingstone here!" at the start of responses
- You are helpful but not overly formal

Example responses:
"Livingstone here! According to HR_Policy.pdf, employees get 20 vacation days."

"Let me check that for you. Looking at Remote_Policy.pdf, remote work is only allowed on Mondays and Fridays."

Instructions:
1. Answer based ONLY on the provided documents
2. Always mention the source document name
3. Be friendly and helpful
4. If you cannot find the answer, say "Livingstone couldn't find that. Try rephrasing your question?""

"""

# Setup ChromaDB (from Day 2)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=api_key,
    model_name="text-embedding-3-small"
)

# Get the collection
collection = chroma_client.get_collection(
    name="company_policies",
    embedding_function=openai_ef
)

def search_documents(question, k=3):
    """Search ChromaDB for relevant documents"""
    results = collection.query(
        query_texts=[question],
        n_results=k
    )
    return results

def generate_livingstone_answer(question, search_results):
    """Generate answer with Livingstone's personality"""
    if not search_results['documents'][0]:
        return "Livingstone couldn't find that information. Try rephrasing your question?"
    
    # Build context
    context_parts = []
    sources = []
    for i, (doc, metadata) in enumerate(zip(
        search_results['documents'][0],
        search_results['metadatas'][0]
    )):
        context_parts.append(f"[Document {i+1} - {metadata['source']}]:\n{doc}")
        sources.append(metadata['source'])
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Create prompt with Livingstone's personality
    prompt = f"""{LIVINGSTONE_PROMPT}

DOCUMENTS:
{context}

USER QUESTION: {question}

Remember to:
1. Start with "Livingstone here!"
2. Cite your sources
3. Be friendly and helpful

ANSWER:"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7  # Slightly creative for personality
    )
    
    return response.choices[0].message.content, list(set(sources))

# Web page route
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Livingstone - Document Assistant</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            input[type="text"] {
                width: 70%;
                padding: 12px;
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 10px;
                margin-right: 10px;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 10px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            button:hover {
                transform: scale(1.05);
                background: #5a67d8;
            }
            .answer-box {
                background: #f7f7f7;
                border-radius: 15px;
                padding: 20px;
                margin-top: 30px;
                min-height: 150px;
            }
            .answer {
                font-size: 16px;
                line-height: 1.6;
                color: #333;
            }
            .sources {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #ddd;
                color: #667eea;
                font-size: 14px;
            }
            .loading {
                color: #999;
                text-align: center;
                padding: 20px;
            }
            .livingstone-icon {
                font-size: 50px;
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="livingstone-icon"></div>
            <h1>Livingstone</h1>
            <div class="subtitle">Your personal document assistant. Ask me anything about your policies.</div>
            
            <div>
                <input type="text" id="question" placeholder="e.g., How many vacation days do I get?" >
                <button onclick="askLivingstone()">Ask Livingstone</button>
            </div>
            
            <div class="answer-box" id="answerBox">
                <div class="loading"> Livingstone is listening... Ask a question above.</div>
            </div>
        </div>
        
        <script>
            async function askLivingstone() {
                const question = document.getElementById('question').value;
                if (!question) {
                    alert('Please type a question first.');
                    return;
                }
                
                const answerBox = document.getElementById('answerBox');
                answerBox.innerHTML = '<div class="loading"> Livingstone is thinking...</div>';
                
                try {
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question: question })
                    });
                    
                    const data = await response.json();
                    
                    answerBox.innerHTML = `
                        <div class="answer">${data.answer}</div>
                        <div class="sources"> Sources: ${data.sources.join(', ')}</div>
                    `;
                } catch (error) {
                    answerBox.innerHTML = '<div class="loading"> Livingstone had trouble connecting. Try again.</div>';
                }
            }
            
            // Allow Enter key
            document.getElementById('question').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    askLivingstone();
                }
            });
        </script>
    </body>
    </html>
    """

# API endpoint for questions
@app.post("/ask")
async def ask(request: Request):
    import json
    body = await request.body()
    data = json.loads(body)
    question = data.get("question", "")
    
    if not question:
        return {"answer": "Livingstone here! Please ask me a question.", "sources": []}
    
    # Search and answer
    search_results = search_documents(question)
    answer, sources = generate_livingstone_answer(question, search_results)
    
    return {"answer": answer, "sources": sources}