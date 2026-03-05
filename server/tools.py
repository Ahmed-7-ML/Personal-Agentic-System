import os
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from langchain_core.tools import tool

# Get Vector Store
def get_vector_store():
    index_name = os.environ.get("PINECONE_INDEX")
    if not index_name:
        raise ValueError("PINECONE_INDEX environment variable is not set")
    
    # This MUST match the embedding model used during ingestion
    embeddings = PineconeEmbeddings(
        model="llama-text-embed-v2"
    )

    vectorstore = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings
    )
    return vectorstore

# Search Knowledge Base Tool
@tool
def search_knowledge_base(query: str) -> str:
    """Searches the internal knowledge base for technical info and documentation.
    Use this when you need to find information from uploaded PDF documents."""
    
    print(f"Agent is searching Pinecone for: '{query}'")
    store = get_vector_store()

    # Fetch the top 10 most similar chunks
    results = store.similarity_search(query, k=10)

    for i, r in enumerate(results):
        print(f"Result {i + 1}: {r.page_content[:200]}")

    if not results:
        return "No relevant information found in the knowledge base."

    # Join the chunks so the LLM can read them as one context block
    return "\n\n---\n\n".join([doc.page_content for doc in results])
