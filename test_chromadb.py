import chromadb

print("Testing ChromaDB...")

client = chromadb.Client()

collection = client.create_collection("test")

collection.add(
    documents=["This is a test document about vacation policy"],
    ids=["1"]
)

results = collection.query(
    query_texts=["vacation"],
    n_results=1
)

print("✅ ChromaDB is working!")
print(f"Search result: {results['documents'][0][0]}")