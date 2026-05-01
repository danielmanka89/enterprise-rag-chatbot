# 🧭 Livingstone - My Enterprise RAG Chatbot

I built a system that reads your documents and answers questions about them. You ask "How many vacation days do I get?" and it tells you. But unlike ChatGPT, it does not guess from the internet. It only uses your documents. And it shows you exactly which document the answer came from.

I named it Livingstone. Like a helpful guide through your documents.

---

## What This Project Is

Every company has thousands of documents. HR policies. Expense rules. Remote work guidelines. Employees waste hours searching. Or they ask ChatGPT and get a confident but wrong answer.

Livingstone fixes this. You feed it documents. It learns from them. Anyone can ask questions and get verifiable answers with sources.

---

## How It Works

1. Documents are loaded and split into smaller chunks.
2. Each chunk is converted into numbers (embeddings) using OpenAI.
3. These numbers are stored in a vector database called ChromaDB.
4. When you ask a question, the system finds the most similar document chunks.
5. GPT reads only those chunks and generates an answer.
6. The answer includes the source document name.

---

## AI Technology Stack

| AI Component | Technology | What It Does |
|--------------|------------|---------------|
| Large Language Model | OpenAI GPT-3.5-turbo | Generates human-like answers |
| Embeddings Model | OpenAI text-embedding-3-small | Converts text to 1536 vectors |
| Vector Database | ChromaDB | Stores and searches embeddings |
| Semantic Search | Cosine similarity | Finds meaning, not keywords |
| Web Interface | FastAPI | Serves the AI to users |

---

## ⚙️ How The AI Works

**Step 1 - Document Ingestion**
Documents are loaded and split into chunks. Each chunk is sent to OpenAI's embedding model, which converts it into 1536 numbers (vectors).

**Step 2 - Vector Storage**
These vectors are stored in ChromaDB, a vector database optimized for similarity search.

**Step 3 - Question Processing**
When you ask a question, the same embedding model converts your question into a vector.

**Step 4 - Semantic Search**
ChromaDB finds the most similar document vectors using cosine similarity. This is semantic search. "Vacations" finds "vacation" automatically.

**Step 5 - RAG Generation**
The relevant documents are sent to GPT-3.5-turbo with a system prompt that forces the model to answer ONLY from those documents.

**Step 6 - Source Citations**
The AI response includes the exact document names that were used.

---

## Day 1 - Basic RAG with Keyword Search

### What I needed to do

I wanted to understand RAG from the ground up. No shortcuts. No copying complicated code I did not understand. So I started simple.

I needed to build a system that could read documents, search through them, find relevant information, and answer questions using GPT. The answer had to come only from my documents. No internet guessing. And I wanted to see exactly which document each answer came from.

I created four sample policies. A vacation policy that says employees get 20 days. A remote work policy that says only Mondays and Fridays. An expense policy with a $50 meal limit. A sick leave policy with 10 days and a doctor note rule.

Each policy was just one or two sentences. Nothing fancy. Just enough to test the concept.

Then I wrote code to load these documents, search for keywords from the user's question, and send matching documents to GPT with a strict instruction. "Answer based ONLY on these documents."

The whole system ran in the terminal. No web interface yet. Just me typing questions and the bot answering.

### Tools I used in Day 1

| Tool | What I used it for |
|------|---------------------|
| Python | The entire system logic |
| OpenAI GPT-3.5-turbo | Generating answers from documents |
| OpenAI API | Connecting to GPT |
| python-dotenv | Keeping my API key secure in a .env file |
| RecursiveCharacterTextSplitter | Splitting documents into smaller chunks |
| Terminal | Running the chatbot |

### What I achieved in Day 1

| What I achieved | Description |
|-----------------|-------------|
| Working RAG system | Built from scratch. Every line written and understood. |
| Document loading | Four policies loaded as a Python dictionary. |
| Keyword search | Finds documents that contain words from your question. Ignores small words like "the" and "and". |
| GPT integration | Connects to OpenAI and sends prompts that force document-only answers. |
| Source citations | Every answer shows which document it came from. |
| Interactive chat loop | Type questions. Get answers. Type "quit" to exit. |
| No hallucinations | GPT never uses outside knowledge. Only my policies. |

### The limitation I found

Keyword search is strict. When I asked "How many vacations?" with an S at the end, the system failed. My document said "vacation" without an S. No match. No answer.

This showed me exactly what to fix in Day 2. Semantic search through embeddings.

---

## Day 2 - ChromaDB + Semantic Search

### What I needed to do

Day 1 worked but had a clear weakness. Keyword search could not handle plurals. "Vacations" did not find "vacation". Different words with the same meaning also failed.

I needed a smarter way to search. A way that understands meaning, not just exact letters.

I also wanted to store document information permanently. Day 1 reloaded everything every time you ran the program. Not efficient for real use.

So I learned about embeddings. Embeddings convert sentences into long lists of numbers. Similar sentences get similar numbers. "Vacations" and "vacation" become almost identical numbers.

I chose ChromaDB as my vector database. It stores these number lists and can find the most similar ones in milliseconds.

### Tools I used in Day 2

| Tool | What I used it for |
|------|---------------------|
| ChromaDB | Vector database to store embeddings permanently |
| OpenAI text-embedding-3-small | Converting text to 1536 numbers (vectors) |
| LangChain | Better document chunking and loading |
| pypdf | Reading PDF files (preparation for real documents) |
| tiktoken | Counting tokens to determine optimal chunk size |

### What I achieved in Day 2

| What I achieved | Description |
|-----------------|-------------|
| Vector embeddings | Each document chunk converts to 1536 numbers using OpenAI text-embedding-3-small. |
| ChromaDB storage | Embeddings saved permanently to a folder called chroma_db. No recomputation on restart. |
| Semantic search | Searches by meaning, not keywords. "Vacations" finds "vacation". |
| Plural handling | Words with S at the end now match the singular version. |
| Persistent database | Close the program. Open it again. ChromaDB remembers everything. |
| Better chunking | Documents split into overlapping chunks so no context is lost. |

### How I proved it worked

| Question | Day 1 Result | Day 2 Result |
|----------|--------------|--------------|
| "How many **vacations**?" | Not found | 20 days from HR_Policy.txt |
| "What's the **food** limit?" | Not found | $50 from Expense_Policy.txt |
| "**Doctor note** needed?" | Found | Found with better context |

---

## Day 3 - Livingstone Web Interface

### What I needed to do

The terminal worked for me. But no real user wants to open a terminal and type python commands. I needed a web interface. Something anyone could open in a browser. Type a question. Click a button. Get an answer.

I also wanted to give my assistant a personality. Something friendly. Approachable. Not a boring robot that just prints text.

I chose FastAPI for the web server. It is simple, fast, and perfect for this type of project. Uvicorn runs the server. HTML, CSS, and JavaScript handle the frontend.

I named the assistant Livingstone. Like a helpful guide through your documents. I wrote a custom system prompt that gives him personality. He starts responses with "Livingstone here!" He is warm and friendly. But he never compromises on accuracy. Every answer still comes with a source citation.

### Tools I used in Day 3

| Tool | What I used it for |
|------|---------------------|
| FastAPI | Web framework for creating the server and API endpoints |
| Uvicorn | Server that runs FastAPI and keeps it alive |
| HTML | Structure of the web page |
| CSS | Styling to make the page look clean and professional |
| JavaScript | Handling form submission and making API calls without page reload |
| Jinja2 | Templating (later simplified to plain HTML) |

### What I achieved in Day 3

| What I achieved | Description |
|-----------------|-------------|
| Web server | Livingstone runs on localhost:8000. Anyone on your network can access it. |
| Clean web page | Input box, ask button, answer display, source citations. Works on desktop and mobile. |
| API endpoint | `/ask` receives questions and returns JSON with answer and sources. |
| Livingstone personality | Custom prompt makes him say "Livingstone here!" and speak warmly. |
| Persistent ChromaDB connection | Web server connects to your existing chroma_db folder. No re-embedding needed. |
| Enter key support | Press Enter to ask. No need to click the button. |
| Error handling | Friendly messages when something goes wrong. |

### Example conversation with Livingstone

| Who | What was said |
|-----|---------------|
| **User** | "How many vacation days do I get?" |
| **Livingstone** | "Livingstone here! According to HR_Policy.txt, employees receive 20 paid vacation days per calendar year." |
| **User** | "Can I work from home on Wednesdays?" |
| **Livingstone** | "Let me check that for you. Looking at Remote_Policy.txt, remote work is only allowed on Mondays and Fridays. No mention of Wednesdays." |

---

## Day 4 - Authentication + Rate Limiting ✅ COMPLETE

### What I needed to do

Right now, anyone who knows my computer address can use Livingstone. No password. No limits. That is fine for testing at home. But not for real use. I needed authentication and rate limiting.

I wanted only authorized people to access Livingstone. And I wanted to prevent anyone from sending too many requests and abusing the system.

### Tools I used in Day 4

| Tool | What I used it for |
|------|---------------------|
| FastAPI Security | Built-in API key validation |
| HTTPBearer | Extracts API key from request headers |
| SlowAPI | Rate limiting middleware |
| secrets module | Generate secure random API keys |
| LocalStorage | Save API key in browser |

### What I achieved in Day 4

| What I achieved | Description |
|-----------------|-------------|
| API key authentication | Users must provide a valid key. No key = no access. |
| 403 error messages | Clear message when API key is invalid |
| Rate limiting | 100 requests per minute maximum |
| 429 error messages | Clear message when rate limit exceeded |
| Browser key storage | API key saved locally. Enter once, use forever. |
| CORS middleware | Allows web page to talk to server |
| Error handling | Graceful failures with helpful messages |

### How authentication works
User sends request with API key in header
↓
FastAPI checks if key matches SECRET_API_KEY
↓
If no match → 403 Forbidden
↓
If match → Process request
↓
Check rate limit → Under 100/min → Return answer
↓
Over 100/min → 429 Too Many Requests

### The API key I created
API_KEY = ASK ME FOR IT

---

## Day 5 - MLflow Tracking + Analytics ✅ COMPLETE

### What I needed to do

Livingstone was working perfectly. But I had no idea how well it was performing. How long does each question take? Which questions are people asking? Which documents are most useful? I needed answers to these questions.

I wanted to track every single interaction. Response times. Sources found. Questions asked. Answers given. Everything.

### Tools I used in Day 5

| Tool | What I used it for |
|------|---------------------|
| MLflow | Tracking every question and answer |
| time module | Measuring response time |
| uuid module | Generating unique session IDs |
| datetime | Recording timestamps |

### What I achieved in Day 5

| What I achieved | Description |
|-----------------|-------------|
| MLflow installed | Tracking system ready |
| Session tracking | Each user gets a unique ID |
| Response time tracking | Every question's speed is measured |
| Question logging | Every question saved |
| Answer logging | Every answer saved as artifact |
| Source tracking | Number of sources found recorded |
| Analytics button | One-click access to MLflow dashboard |

### How tracking works

Every time someone asks a question, Livingstone records:

| Data Tracked | How It's Used |
|--------------|---------------|
| Question text | Know what users are asking |
| Answer text | Verify quality |
| Response time | Measure performance |
| Number of sources | See retrieval quality |
| Session ID | Group questions by user |
| Timestamp | Track usage patterns |