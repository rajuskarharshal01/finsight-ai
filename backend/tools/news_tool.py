import requests
from langchain_core.tools import tool
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import yfinance as yf

@tool
def get_company_news(ticker: str) -> str:
    """
    Get the latest news specifically for a company using its stock ticker.
    Use this when you need news about a specific publicly traded company.

    Args:
        ticker: Stock ticker symbol like TSLA, AAPL, NVDA

    Returns:
        JSON string with recent company news articles
    """
    try:
        time.sleep(1)
        # Use Google News RSS — reliable and no API key needed
        url = f"https://news.google.com/rss/search?q={ticker}+stock+financial&hl=en-US&gl=US&ceid=US:en"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.findAll("item")[:5]

        articles = []
        for item in items:
            articles.append({
                "title": item.title.text if item.title else "N/A",
                "source": item.source.text if item.source else "N/A",
                "link": item.link.text if item.link else "N/A",
                "published": item.pubDate.text if item.pubDate else "N/A"
            })

        return json.dumps({
            "ticker": ticker.upper(),
            "total_results": len(articles),
            "articles": articles
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Could not fetch news for {ticker}: {str(e)}"})


@tool
def search_financial_news(query: str, max_results: int = 5) -> str:
    """
    Search for recent financial news articles about a company or topic.
    Use this when you need current news, recent events, or market sentiment.

    Args:
        query: Search query like "Tesla earnings 2024" or "NVIDIA AI chips"
        max_results: Number of articles to return (default 5)

    Returns:
        JSON string with list of news articles including title and summary
    """
    try:
        time.sleep(1)
        formatted_query = query.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={formatted_query}+finance&hl=en-US&gl=US&ceid=US:en"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.findAll("item")[:max_results]

        articles = []
        for item in items:
            articles.append({
                "title": item.title.text if item.title else "N/A",
                "source": item.source.text if item.source else "N/A",
                "link": item.link.text if item.link else "N/A",
                "published": item.pubDate.text if item.pubDate else "N/A"
            })

        return json.dumps({
            "query": query,
            "total_results": len(articles),
            "articles": articles
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Could not search news for '{query}': {str(e)}"})