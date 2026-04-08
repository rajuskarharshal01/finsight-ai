import json
import os
from langchain_core.tools import tool
from langchain_core.documents import Document
from typing import List
from dotenv import load_dotenv

load_dotenv()


def format_docs_for_agent(docs: List[Document]) -> str:
    """
    Format retrieved documents into a clean string the agent can read.

    The agent receives tool results as text. We format each chunk
    clearly so the agent knows:
    - WHERE the information came from (source)
    - WHAT the information says (content)

    This formatting directly affects answer quality — if the agent
    can't clearly read the context, it gives worse answers.
    """
    if not docs:
        return json.dumps({
            "found": False,
            "message": "No relevant documents found in knowledge base",
            "chunks": []
        })

    formatted_chunks = []
    for i, doc in enumerate(docs):
        formatted_chunks.append({
            "chunk_index": i + 1,
            "source": doc.metadata.get("source_name", "Unknown"),
            "doc_type": doc.metadata.get("type", "unknown"),
            "content": doc.page_content,
            "ticker": doc.metadata.get("ticker", "")
        })

    return json.dumps({
        "found": True,
        "total_chunks": len(formatted_chunks),
        "chunks": formatted_chunks
    }, indent=2)


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the internal knowledge base for relevant financial documents.
    Use this when you need information from previously stored financial
    reports, earnings documents, SEC filings, or research notes that
    may have been saved to the database.

    This uses semantic search — searching by meaning not keywords.
    For example searching 'company profits' will also find documents
    about 'net income' and 'earnings'.

    Args:
        query: Natural language search query like
               'Tesla risk factors' or 'Apple revenue growth'

    Returns:
        JSON string with relevant document chunks and their sources
    """
    # Import here to avoid circular imports
    from backend.pipeline.embeddings import search_documents

    docs = search_documents(query, k=4)
    return format_docs_for_agent(docs)


@tool
def search_knowledge_base_by_ticker(ticker: str) -> str:
    """
    Search the knowledge base for all stored documents about
    a specific company using its ticker symbol.
    Use this when you want everything we know about a specific company.

    Args:
        ticker: Stock ticker symbol like TSLA, AAPL, NVDA

    Returns:
        JSON string with all stored chunks related to that company
    """
    from backend.pipeline.embeddings import search_documents

    # Search using company name patterns
    query = f"{ticker.upper()} financial performance earnings revenue"
    docs = search_documents(query, k=6)

    # Filter for ticker-specific docs if metadata has ticker field
    ticker_docs = [
        doc for doc in docs
        if doc.metadata.get("ticker", "").upper() == ticker.upper()
        or ticker.upper() in doc.page_content.upper()
    ]

    # Fall back to all results if no ticker-specific ones
    final_docs = ticker_docs if ticker_docs else docs

    return format_docs_for_agent(final_docs)


@tool
def store_financial_insight(content: str, source_name: str, ticker: str = "") -> str:
    """
    Store a financial insight or analysis result in the knowledge base
    for future reference. Use this to save important findings so they
    can be retrieved in future research sessions.

    Args:
        content: The financial insight or analysis text to store
        source_name: Name describing the source of this insight
        ticker: Optional stock ticker this insight relates to

    Returns:
        JSON string confirming storage success or failure
    """
    from backend.pipeline.loader import process_document
    from backend.pipeline.embeddings import store_documents

    try:
        # Add ticker to source if provided
        full_source = f"{source_name} ({ticker.upper()})" if ticker else source_name

        chunks = process_document(
            content=content,
            source_name=full_source,
            doc_type="financial_insight",
            chunk_size=500,
            chunk_overlap=100
        )

        if not chunks:
            return json.dumps({
                "success": False,
                "message": "No content to store"
            })

        # Add ticker to metadata
        for chunk in chunks:
            if ticker:
                chunk.metadata["ticker"] = ticker.upper()

        stored = store_documents(chunks)

        return json.dumps({
            "success": True,
            "message": f"Stored {stored} chunks for '{full_source}'",
            "chunks_stored": stored
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Storage failed: {str(e)}"
        })