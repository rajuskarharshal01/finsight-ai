import requests
import re
import os
from typing import List, Dict
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()


# ── Text Cleaning ──────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Clean raw text extracted from documents or web pages.
    Removes extra whitespace, special characters, and noise.
    
    This runs on every document before chunking — dirty text
    produces bad embeddings which produces bad search results.
    """
    if not text:
        return ""

    # Remove HTML tags if any slipped through
    text = re.sub(r'<[^>]+>', ' ', text)

    # Replace multiple whitespace/newlines with single space
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\$\%]', ' ', text)

    # Strip leading and trailing whitespace
    text = text.strip()

    return text


# ── Document Loaders ───────────────────────────────────────────

def load_url(url: str, source_name: str = "") -> List[Document]:
    """
    Load and extract text content from a web URL.
    Used for loading news articles and web pages.
    
    Returns a list of LangChain Document objects.
    Each Document has:
      - page_content: the actual text
      - metadata: info about where the text came from
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove navigation, scripts, styles — we only want article text
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Extract main text content
        text = soup.get_text(separator=" ")
        text = clean_text(text)

        if not text:
            return []

        # Create a LangChain Document object
        # metadata is crucial — it tells us WHERE each chunk came from
        doc = Document(
            page_content=text,
            metadata={
                "source": url,
                "source_name": source_name or url,
                "type": "web_article"
            }
        )

        return [doc]

    except Exception as e:
        print(f"Error loading URL {url}: {e}")
        return []


def load_text(text: str, source_name: str, doc_type: str = "text") -> List[Document]:
    """
    Load plain text directly into a Document.
    Used when we already have text (from our tools)
    and want to store it in the vector database.
    """
    cleaned = clean_text(text)

    if not cleaned:
        return []

    doc = Document(
        page_content=cleaned,
        metadata={
            "source": source_name,
            "source_name": source_name,
            "type": doc_type
        }
    )

    return [doc]


def load_sec_filing(ticker: str, filing_text: str) -> List[Document]:
    """
    Load an SEC filing text into Documents with proper metadata.
    SEC filings are long — they'll be chunked properly downstream.
    """
    cleaned = clean_text(filing_text)

    if not cleaned:
        return []

    doc = Document(
        page_content=cleaned,
        metadata={
            "source": f"SEC EDGAR - {ticker}",
            "source_name": f"{ticker} SEC Filing",
            "type": "sec_filing",
            "ticker": ticker
        }
    )

    return [doc]


# ── Text Splitter ──────────────────────────────────────────────

def create_splitter(
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> RecursiveCharacterTextSplitter:
    """
    Create a text splitter that breaks documents into chunks.

    chunk_size: how many characters per chunk (roughly 200-250 words)
    chunk_overlap: how many characters to repeat between chunks

    Why overlap? Imagine this sentence spans two chunks:
    "Tesla's revenue was $97 billion, | representing 19% growth"
                          chunk 1 end | chunk 2 start

    Without overlap, neither chunk has the complete fact.
    With overlap, both chunks contain the key information.

    RecursiveCharacterTextSplitter tries to split at:
    1. Paragraph breaks first (\n\n)
    2. Then line breaks (\n)
    3. Then sentences (. ! ?)
    4. Then words (spaces)
    5. Then characters (last resort)

    This keeps sentences and paragraphs together as much as possible.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )


def split_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Split a list of Documents into smaller chunks.

    Each chunk inherits the metadata from its parent document
    plus gets a chunk_index so we know which chunk it was.

    Example:
    Input:  1 document with 5000 characters
    Output: ~6 chunks of ~1000 characters with 200 overlap
    """
    splitter = create_splitter(chunk_size, chunk_overlap)
    chunks = splitter.split_documents(documents)

    # Add chunk index to metadata for debugging
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
        chunk.metadata["total_chunks"] = len(chunks)

    return chunks


# ── Pipeline Entry Point ───────────────────────────────────────

def process_document(
    content: str,
    source_name: str,
    doc_type: str = "text",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Main entry point for the document pipeline.
    Takes raw text and returns ready-to-embed chunks.

    This is what other parts of the system call — they
    don't need to know about cleaning or splitting internals.

    Usage:
        chunks = process_document(
            content="Tesla reported revenue of...",
            source_name="Tesla Q4 2024 Earnings",
            doc_type="earnings_report"
        )
    """
    # Step 1 — load into Document object
    docs = load_text(content, source_name, doc_type)

    if not docs:
        return []

    # Step 2 — split into chunks
    chunks = split_documents(docs, chunk_size, chunk_overlap)

    print(f"Processed '{source_name}': {len(chunks)} chunks created")

    return chunks


def process_url(url: str, source_name: str = "") -> List[Document]:
    """
    Convenience function to process a URL directly.
    Loads, cleans, and splits in one call.
    """
    docs = load_url(url, source_name)

    if not docs:
        return []

    chunks = split_documents(docs)

    print(f"Processed URL '{url}': {len(chunks)} chunks created")

    return chunks