import os
import chromadb
from chromadb.utils import embedding_functions

# Get API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')

print(f"API key found: {api_key is not None}")
print(f"API key first 10 chars: {api_key[:10] if api_key else 'None'}")

if not api_key:
    print("ERROR: OPENAI_API_KEY environment variable not set")
    print("Available environment variables:")
    for key in os.environ.keys():
        print(f"  - {key}")
    raise ValueError("OPENAI_API_KEY environment variable not set")

documents = {
    'HR_Policy.txt': 'Employees get 20 paid vacation days per year.',
    'Remote_Policy.txt': 'Remote work allowed on Mondays and Fridays.',
    'Expense_Policy.txt': 'Meal expenses up to $50 per day.',
    'Sick_Policy.txt': '10 sick days per year. Doctor note for 3+ days.'
}

print("Connecting to ChromaDB...")
client = chromadb.PersistentClient(path='/app/chroma_db')
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=api_key,
    model_name='text-embedding-3-small'
)

print("Creating collection...")
collection = client.create_collection(
    name='company_policies',
    embedding_function=openai_ef
)

print("Adding documents...")
for name, content in documents.items():
    collection.add(
        documents=[content],
        ids=[name],
        metadatas=[{'source': name}]
    )
    print(f'  Added {name}')

print(f'✅ ChromaDB ready with {collection.count()} documents')
