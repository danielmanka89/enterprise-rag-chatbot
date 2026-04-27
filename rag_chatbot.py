import os
from openai import OpenAI

# Load API key from .env file
def load_api_key():
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=")[1].strip()
    except:
        pass
    return input("Paste your OpenAI API key: ")

api_key = load_api_key()
client = OpenAI(api_key=api_key)

# Company policies (our knowledge base)
policies = {
    "HR_Policy.pdf": "Employees receive 20 paid vacation days per year. Requests need 2 weeks notice.",
    "Remote_Policy.pdf": "Remote work allowed on Mondays and Fridays. Core hours 10am-3pm.",
    "Expense_Policy.pdf": "Meal expenses up to $50/day reimbursed. Receipts within 30 days.",
    "Sick_Policy.pdf": "10 paid sick days per year. Doctor's note for 3+ days."
}

print("\n" + "="*50)
print("📚 RAG CHATBOT - Answer questions with citations")
print("="*50)
print("\nLoaded documents:")
for doc in policies:
    print(f"  ✓ {doc}")

# Search function
def search(query):
    found = []
    query_lower = query.lower()
    for name, content in policies.items():
        if any(word in content.lower() for word in query_lower.split() if len(word) > 3):
            found.append({"name": name, "content": content})
    return found

# Main chat loop
print("\n💡 Try asking: 'How many vacation days?' or 'Can I work remote on Wednesday?'")
print("Type 'quit' to exit\n")

while True:
    question = input("❓ Your question: ").strip()
    if question.lower() in ['quit', 'exit', 'bye']:
        print("👋 Goodbye!")
        break
    if not question:
        continue
    
    # Search for relevant documents
    relevant = search(question)
    
    if not relevant:
        print("❌ No relevant documents found.\n")
        continue
    
    # Build context
    context = "\n\n".join([f"[{doc['name']}]: {doc['content']}" for doc in relevant])
    
    # Ask GPT to answer
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Answer based ONLY on the provided documents. Always cite the document name."},
            {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0
    )
    
    answer = response.choices[0].message.content
    sources = [doc['name'] for doc in relevant]
    
    print(f"\n✅ Answer: {answer}")
    print(f"📚 Sources: {', '.join(sources)}\n")
