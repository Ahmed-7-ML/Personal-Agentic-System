import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings


# Define the function to ingest data
def ingest_data(file_path: str):
    print(f"Loading {file_path}...")
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print(f"Loaded {len(docs)} pages. Splitting text...")

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks. Ingesting to Pinecone...")

    # Embed and upload to Pinecone
    index_name = os.environ.get("PINECONE_INDEX")
    if not index_name:
        raise ValueError("Missing PINECONE_INDEX environment variable")

    # Ingest directly into Pinecone. PineconeVectorStore will handle batches automatically.
    embeddings = PineconeEmbeddings(model="llama-text-embed-v2")
    PineconeVectorStore.from_documents(chunks, embeddings, index_name=index_name)
    print("Uploaded to Pinecone")
    