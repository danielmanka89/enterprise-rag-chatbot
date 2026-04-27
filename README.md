# 🤖 Enterprise RAG Chatbot

A question-answering system I built that reads documents and answers questions with source citations. No hallucinations. Every answer is verifiable.

## The Problem I'm Solving

Companies have thousands of documents (policies, manuals, contracts). Employees waste hours searching. Generic AI like ChatGPT makes up answers. 

This system solves both problems.

## How It Works

1. You upload documents (policies, PDFs, manuals)
2. You ask a question
3. The system searches for relevant information
4. GPT-4 answers based ONLY on what it finds
5. You see the answer AND which document it came from

## Real Examples From Today

**Me:** Can I work from home on Wednesdays?

**System:** No. According to Remote_Policy.pdf, remote work is only allowed on Mondays and Fridays.

**Me:** What's the meal expense limit?

**System:** $50 per day according to Expense_Policy.pdf.

**Me:** Do I need a doctor's note for sick leave?

**System:** Yes, for sick leave longer than 3 days according to Sick_Policy.pdf.

## What Makes This Different

| Other AI | This System |
|----------|-------------|
| Guesses based on internet data | Answers based on YOUR documents |
| No sources shown | Shows exact document name |
| Can't verify accuracy | Every answer is verifiable |
| Hallucinates false information | Only says what's in your documents |

## Technology I Used

- **OpenAI GPT-3.5-turbo** - Generates accurate answers
- **Python** - Runs the entire system
- **Keyword Search** - Finds relevant documents (Day 1 version)

## What I Learned Building This

The core insight: RAG is simple. Search for relevant documents. Give them to GPT. Show the sources. Everything else is just making it faster or handling more documents.

## Current Limitations (Being Fixed)

- Can only search by exact keywords (not meaning)
- Documents are hardcoded (not loading real PDFs)
- Terminal only (no web interface)

## What's Coming Tomorrow

- Load real PDF files
- Semantic search (understands meaning, not just keywords)
- ChromaDB vector database
- Fix plural word problems ("vacations" finds "vacation")

## Why I Built This

Every company needs this. Healthcare, law firms, banks, tech companies - they all have documents their employees need to search. This is the foundation of enterprise AI.

## Try It Yourself

```bash
git clone https://github.com/danielmanka89/enterprise-rag-chatbot.git
cd enterprise-rag-chatbot
python3 -m venv venv
source venv/bin/activate
pip install openai python-dotenv
echo "OPENAI_API_KEY=your_key_here" > .env
python3 rag_chatbot.py