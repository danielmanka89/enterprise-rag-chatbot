# Enterprise RAG Chatbot

## What Is This Project?

This is a document question-answering system I built.  
You give it documents. You ask a question. It gives you an answer and tells you exactly which document the answer came from.

Unlike ChatGPT, this system does not guess. It does not use internet data. It only uses the documents you provide. Every answer is verifiable.

---

## Why I Built This

In every company, critical information lives inside PDFs, policies, and internal documents. Employees waste hours searching. Generic AI tools hallucinate because they were never trained on company data.

I built this to solve both problems: fast search and trustworthy answers.

---

## How It Works

1. Documents are loaded and split into smaller chunks.
2. Each chunk is converted into numbers (embeddings) using OpenAI.
3. These numbers are stored in a vector database called ChromaDB.
4. When you ask a question, the system finds the most similar document chunks.
5. GPT reads only those chunks and generates an answer.
6. The answer includes the source document name.

---

## Technology Stack

- Python – core language
- OpenAI GPT-3.5-turbo – generates answers
- OpenAI embeddings – converts text to numbers
- ChromaDB – vector database for semantic search
- LangChain – document loading and splitting
- Git & GitHub – version control

---

# Day 1 – Basic RAG with Keyword Search

## What I Needed to Do

I started simple. I wanted to understand the core RAG flow before adding complexity.

I loaded a few policy documents directly in code. Then I used keyword matching to find relevant information. Finally, I asked GPT to answer based only on what was found, and I showed the source document.

## Tools I Used in Day 1

- Python
- OpenAI GPT-3.5-turbo
- RecursiveCharacterTextSplitter for chunking
- Dotenv for API key management

## What I Achieved in Day 1

The system was able to answer questions like:

> "Can I work from home on Wednesdays?"

And it responded correctly using only my documents, not internet knowledge. It also showed the source file name.

However, I found a clear limitation. Keyword search is strict. When I asked "How many vacations do I get?" it failed because the document said "vacation" not "vacations."

That limitation led me to Day 2.

---

# Day 2 – Semantic Search with ChromaDB

## What I Needed to Do

I needed to move from keyword matching to meaning-based search. The system should understand that "vacations" and "vacation" mean the same thing.

I also wanted to store document embeddings permanently so the system does not recompute everything every time.

## Tools I Added in Day 2

- ChromaDB – persistent vector database
- OpenAI text-embedding-3-small – converts text to 1536 numbers
- LangChain – better document handling
- pypdf – for future PDF support

## What I Achieved in Day 2

The system now uses semantic search. It converts every document chunk into numbers and stores them in ChromaDB.

When I ask "How many vacations do I get?" it finds the chunk about "vacation" because their number patterns are almost identical.

The answer still includes the source document name. The database is persistent, so I do not need to re-embed documents every time I restart the program.

---

## How to Run Day 1

```bash
git clone https://github.com/danielmanka89/enterprise-rag-chatbot.git
cd enterprise-rag-chatbot
python3 -m venv venv
source venv/bin/activate
pip install openai python-dotenv
echo "OPENAI_API_KEY=your_key_here" > .env
python3 rag_chatbot.py

## How to Run Day 2

pip install chromadb langchain pypdf tiktoken
python3 rag_day2.py