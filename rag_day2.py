"""
DAY 2: Enterprise RAG with ChromaDB + Semantic Search
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

# Load your API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

print("="*50)
print("DAY 2: Building RAG with ChromaDB")
print("="*50)
print("\nImports loaded successfully")
print(f"API key found: {api_key[:10]}...")

# --------------------------------------------
# PART 1: CREATE SAMPLE DOCUMENTS
# --------------------------------------------

print("\nStep 1: Creating sample policy documents...")

# These are our company policies (like real HR documents)
hr_policy = """
VACATION POLICY
Employees receive 20 paid vacation days per calendar year.
Vacation requests must be submitted at least 2 weeks in advance.
Unused vacation days do NOT roll over to the next year.
Part-time employees get 10 vacation days per year.
"""

remote_policy = """
REMOTE WORK POLICY
Employees can work remotely on Mondays and Fridays.
Core hours are 10:00 AM to 3:00 PM (must be available by chat).
Remote work requires manager approval for additional days.
Tuesday, Wednesday, Thursday are in-office days.
"""

expense_policy = """
EXPENSE POLICY
Meal expenses up to $50 per day are reimbursable.
Receipts must be submitted within 30 days of purchase.
Travel expenses over $500 require VP approval.
"""

sick_policy = """
SICK LEAVE POLICY
Employees get 10 paid sick days per year.
Sick days can be used for personal illness or doctor visits.
Doctor's note required for sick leave longer than 3 days.
"""

# Put all policies in a dictionary (like a phonebook)
documents = {
    "HR_Policy.txt": hr_policy,
    "Remote_Policy.txt": remote_policy,
    "Expense_Policy.txt": expense_policy,
    "Sick_Policy.txt": sick_policy,
}

print(f"Loaded {len(documents)} documents:")
for doc_name in documents:
    print(f"   - {doc_name}")

# --------------------------------------------
# PART 2: SPLIT DOCUMENTS INTO CHUNKS
# --------------------------------------------

print("\nStep 2: Splitting documents into chunks...")

def chunk_document(text, chunk_size=100, overlap=20):
    """
    Splits a document into smaller chunks.
    chunk_size = how many words per chunk
    overlap = words that appear in two chunks (preserves context)
    """
    words = text.split()  # Split text into individual words
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        # Take a slice of words from i to i+chunk_size
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks

all_chunks = []
all_metadata = []

for doc_name, doc_text in documents.items():
    chunks = chunk_document(doc_text)
    for i, chunk in enumerate(chunks):
        all_chunks.append(chunk)
        all_metadata.append({
            "source": doc_name,
            "chunk_number": i + 1,
            "total_chunks": len(chunks)
        })
    
    print(f"   {doc_name}: split into {len(chunks)} chunks")

print(f"\nTotal chunks created: {len(all_chunks)}")

# --------------------------------------------
# PART 3: CREATE EMBEDDINGS AND STORE IN CHROMADB
# --------------------------------------------

print("\nStep 3: Storing chunks in ChromaDB...")

# Create ChromaDB client (creates a database folder called "chroma_db")
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create embedding function using OpenAI
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=api_key,
    model_name="text-embedding-3-small"  # OpenAI's embedding model
)

# Create or get a collection (like a table in a database)
collection = chroma_client.get_or_create_collection(
    name="company_policies",
    embedding_function=openai_ef
)

# Add all chunks to ChromaDB
for i, (chunk, metadata) in enumerate(zip(all_chunks, all_metadata)):
    collection.add(
        documents=[chunk],
        ids=[f"chunk_{i}"],
        metadatas=[metadata]
    )

print(f"Stored {len(all_chunks)} chunks in ChromaDB")
print(f"   Database location: ./chroma_db")

# --------------------------------------------
# PART 4: SEMANTIC SEARCH FUNCTION
# --------------------------------------------

print("\nStep 4: Testing semantic search...")

def semantic_search(question, collection, k=3):
    """
    Searches for chunks that are semantically similar to the question.
    k = number of results to return
    """
    results = collection.query(
        query_texts=[question],
        n_results=k
    )
    return results

test_question = "How many vacation days do I get?"
print(f"\nTest question: '{test_question}'")

results = semantic_search(test_question, collection)

print(f"\nFound {len(results['documents'][0])} relevant chunks:")

for i, (doc, metadata, distance) in enumerate(zip(
    results['documents'][0], 
    results['metadatas'][0],
    results['distances'][0]
)):
    print(f"\nResult {i+1}:")
    print(f"   Source: {metadata['source']}")
    print(f"   Content: {doc[:150]}...")
    print(f"   Similarity score: {1 - distance:.2f}")

# --------------------------------------------
# PART 5: GENERATE ANSWER WITH GPT
# --------------------------------------------

print("\nStep 5: Generating answer with GPT...")

def generate_answer(question, search_results):
    """
    Uses GPT to generate an answer based ONLY on the retrieved documents
    """
    if not search_results['documents'][0]:
        return "I couldn't find any relevant information.", []
    
    context_parts = []
    sources = []
    
    for i, (doc, metadata) in enumerate(zip(
        search_results['documents'][0], 
        search_results['metadatas'][0]
    )):
        context_parts.append(f"[Document {i+1} - {metadata['source']}]:\n{doc}")
        sources.append(metadata['source'])
    
    context = "\n\n---\n\n".join(context_parts)
    
    prompt = f"""You are an HR assistant. Answer the question using ONLY the information from the documents below.

DOCUMENTS:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. ONLY use information from the documents above
2. Always mention which document your answer comes from
3. If the answer isn't in the documents, say "I don't have that information"
4. Be specific and helpful

ANSWER:"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You answer questions based only on provided documents. Always cite your sources."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content, sources

# ============================================
# PART 5: INTERACTIVE CHAT LOOP
# ============================================

print("\n" + "="*50)
print("DAY 2 RAG CHATBOT IS READY!")
print("="*50)

print("\nI can answer questions about:")
print("   - Vacation days")
print("   - Remote work policy")
print("   - Expense reimbursement")
print("   - Sick leave policy")

print("\nThis system uses SEMANTIC SEARCH (understands meaning)")
print("   'vacations' will find 'vacation' automatically!")

print("\nType 'quit' to exit\n")

# ============================================
# MAIN CHAT LOOP
# ============================================

while True:
    # Get question from user
    question = input("Your question: ").strip()
    
    # Check if user wants to quit
    if question.lower() in ['quit', 'exit', 'bye', 'q']:
        print("\nThank you for using Day 2 RAG Chatbot!")
        print("   This system uses ChromaDB + Semantic Search")
        break
    
    # Skip empty questions
    if not question:
        print("Please enter a question.\n")
        continue
    
    # Step 1: Semantic search
    print("\nSearching semantically...")
    search_results = semantic_search(question, collection)
    
    if not search_results['documents'][0]:
        print("No relevant documents found.\n")
        continue
    
    # Show what was found
    print(f"Found {len(search_results['documents'][0])} relevant chunks")
    
    # Step 2: Generate answer with GPT
    print("Generating answer...")
    answer, sources = generate_answer(question, search_results)
    
    # Step 3: Display results
    print("\n" + "="*50)
    print("💬 ANSWER")
    print("="*50)
    print(f"\nQuestion: {question}")
    print(f"\nAnswer: {answer}")
    print(f"\nSources: {', '.join(set(sources))}")
    print("\n" + "="*50 + "\n")