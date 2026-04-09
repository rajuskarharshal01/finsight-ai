import os
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector

load_dotenv()

# ── Configuration ──────────────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Collection name — like a table name for our vectors
# All financial documents go into this one collection
COLLECTION_NAME = "financial_documents"


# ── Embedding Model ────────────────────────────────────────────

def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """
    Create and return the Gemini embedding model.

    This model converts text into vectors (lists of numbers).
    We use Gemini's embedding model — the same provider as our LLM
    which means consistent vector space for queries and documents.

    models/gemini-embedding-001 produces 768-dimensional vectors —
    each piece of text becomes a list of 768 numbers.
    """
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GEMINI_API_KEY
    )


# ── Vector Store ───────────────────────────────────────────────

def get_vector_store() -> PGVector:
    """
    Create and return the pgvector vector store.

    PGVector connects LangChain to our PostgreSQL database
    with the pgvector extension. It handles:
    - Creating the table structure automatically
    - Storing vectors alongside their text and metadata
    - Similarity search queries

    pre_delete_collection=False means we keep existing data
    when reconnecting — we don't wipe the database each time.
    """
    embeddings = get_embedding_model()

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True
    )

    return vector_store


# ── Store Documents ────────────────────────────────────────────

def store_documents(documents: List[Document]) -> int:
    """
    Embed and store a list of document chunks in pgvector.

    This is the core function of the pipeline:
    1. Takes chunked Document objects from loader.py
    2. Sends each chunk's text to Gemini embedding model
    3. Gets back 768-dimensional vectors
    4. Stores text + vector + metadata in PostgreSQL

    Returns the number of documents successfully stored.

    Example usage:
        chunks = process_document("Tesla revenue grew...", "Tesla Report")
        stored = store_documents(chunks)
        print(f"Stored {stored} chunks")
    """
    if not documents:
        print("No documents to store")
        return 0

    try:
        vector_store = get_vector_store()

        # add_documents handles embedding + storing in one call
        # LangChain calls the embedding model for each chunk
        # then stores (text, vector, metadata) in pgvector
        vector_store.add_documents(documents)

        print(f"✅ Stored {len(documents)} chunks in vector database")
        return len(documents)

    except Exception as e:
        print(f"❌ Error storing documents: {e}")
        return 0


# ── Search Documents ───────────────────────────────────────────

def search_documents(query: str, k: int = 5) -> List[Document]:
    """
    Search the vector database for documents relevant to a query.

    This is semantic search — not keyword matching.
    "Tesla profit" will also find chunks about "Tesla earnings"
    and "Tesla net income" because they have similar meaning.

    How it works:
    1. Convert query text to a vector using Gemini
    2. Ask pgvector to find the k most similar vectors
    3. Return the corresponding Document chunks

    Args:
        query: Natural language question or search text
        k: Number of results to return (default 5)

    Returns:
        List of most relevant Document chunks with metadata
    """
    try:
        vector_store = get_vector_store()

        # similarity_search converts query to vector
        # then finds k nearest vectors in the database
        results = vector_store.similarity_search(query, k=k)

        print(f"Found {len(results)} relevant chunks for: '{query}'")
        return results

    except Exception as e:
        print(f"❌ Search error: {e}")
        return []


def search_with_score(query: str, k: int = 5) -> List[tuple]:
    """
    Search with similarity scores — useful for debugging.
    Returns (Document, score) pairs.
    Score closer to 0 = more similar (cosine distance).
    Score closer to 1 = less similar.
    """
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search_with_score(query, k=k)
        return results

    except Exception as e:
        print(f"❌ Search error: {e}")
        return []


def get_retriever(k: int = 4):
    """
    Return a LangChain retriever object.

    A retriever is LangChain's standard interface for
    fetching relevant documents. The agent can use this
    directly without going through our tool wrapper.

    This is used in Phase 6 when we build the agent with
    a built-in retrieval chain.

    Args:
        k: Number of documents to retrieve per query

    Returns:
        LangChain retriever object
    """
    vector_store = get_vector_store()
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )