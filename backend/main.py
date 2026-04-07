import os
import json
import time
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from backend.tools.stock_tool import get_stock_price, get_financial_statements, get_stock_history
from backend.tools.news_tool import get_company_news, search_financial_news
from backend.tools.sec_tool import get_company_facts, get_sec_filings
from backend.pipeline.loader import process_document
from backend.pipeline.embeddings import store_documents, search_documents
from backend.analysis import run_full_analysis
from backend.report_gen import generate_report, report_to_dict
from backend.agents.research_agent import get_agent

load_dotenv()


# ── Simple In-Memory Cache ─────────────────────────────────────
# Stores API results temporarily to avoid hitting rate limits
# Key: "function_ticker", Value: (timestamp, data)
_cache = {}
CACHE_DURATION_HOURS = 6


def get_cached(key: str):
    """
    Get cached data if it exists and is not expired.
    Returns None if no cache or cache is older than 6 hours.
    """
    if key in _cache:
        timestamp, data = _cache[key]
        if datetime.now() - timestamp < timedelta(hours=CACHE_DURATION_HOURS):
            print(f"✅ Cache hit: {key}")
            return data
        else:
            del _cache[key]
    return None


def set_cached(key: str, data: dict):
    """Store data in cache with current timestamp"""
    _cache[key] = (datetime.now(), data)
    print(f"💾 Cached: {key}")


# ── App Setup ──────────────────────────────────────────────────

app = FastAPI(
    title="FinSight AI API",
    description="AI-powered financial research agent API",
    version="1.0.0"
)

# CORS — allows React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:80",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response Models ────────────────────────────────────

class AgentQuery(BaseModel):
    query: str
    ticker: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Analyze Tesla's financial performance",
                "ticker": "TSLA"
            }
        }


class CompanyAnalysisRequest(BaseModel):
    ticker: str

    class Config:
        json_schema_extra = {
            "example": {"ticker": "AAPL"}
        }


class StoreDocumentRequest(BaseModel):
    content: str
    source_name: str
    ticker: Optional[str] = ""
    doc_type: Optional[str] = "financial_insight"


class SearchRequest(BaseModel):
    query: str
    k: Optional[int] = 4


class HealthResponse(BaseModel):
    status: str
    version: str
    message: str


class AgentResponse(BaseModel):
    query: str
    answer: str
    tools_used: list
    steps_count: int


class StockResponse(BaseModel):
    ticker: str
    data: dict


class NewsResponse(BaseModel):
    ticker: str
    articles: list
    total: int


class AnalysisResponse(BaseModel):
    ticker: str
    report: dict


# ── Startup Event ──────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """
    Runs when FastAPI server starts.
    Pre-loads the agent so first request is not slow.
    """
    print("FinSight AI API starting...")
    print("✅ FinSight AI API ready!")


# ── Health Check ───────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Simple health check — always returns 200 if server is up."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        message="FinSight AI API is running"
    )


# ── Company Search Endpoint ────────────────────────────────────

@app.get("/search-company")
async def search_company(q: str):
    """Search for companies by name using yfinance search"""
    try:
        cache_key = f"search_{q.lower().strip()}"
        cached = get_cached(cache_key)
        if cached:
            return {"query": q, "results": cached}

        import yfinance as yf

        # yfinance search
        results = yf.Search(q, max_results=8)
        quotes = results.quotes

        companies = []
        for match in quotes[:8]:
            symbol = match.get("symbol", "")
            name = match.get("longname") or match.get("shortname", "")
            exchange = match.get("exchange", "")
            quote_type = match.get("quoteType", "")

            if symbol and name:
                companies.append({
                    "ticker": symbol,
                    "name": name,
                    "type": quote_type,
                    "region": exchange,
                    "currency": match.get("currency", "USD")
                })

        set_cached(cache_key, companies)
        return {"query": q, "results": companies}

    except Exception as e:
        # Fallback — return empty results gracefully
        return {"query": q, "results": [], "error": str(e)}


# ── Main Agent Endpoint ────────────────────────────────────────

@app.post("/ask-research-agent")
async def ask_research_agent(request: AgentQuery):
    """
    Main endpoint — sends query to LangChain agent.
    Agent autonomously decides which tools to call.
    """
    try:
        query = request.query
        if request.ticker:
            query = f"{query} (ticker: {request.ticker.upper()})"

        agent = get_agent()
        result = agent.research(query)

        return AgentResponse(
            query=request.query,
            answer=result["answer"],
            tools_used=result["tools_used"],
            steps_count=len(result["steps"])
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


# ── Stock Data Endpoint ────────────────────────────────────────

@app.get("/stock/{ticker}")
async def get_stock_data(ticker: str):
    """
    Get current stock price and market data.
    Cached for 6 hours to save API quota.
    """
    try:
        cache_key = f"stock_{ticker.upper()}"
        cached = get_cached(cache_key)
        if cached:
            return StockResponse(ticker=ticker.upper(), data=cached)

        result = get_stock_price.invoke({"ticker": ticker.upper()})
        data = json.loads(result)

        if "error" in data:
            raise HTTPException(
                status_code=404,
                detail=f"Stock data not found: {data['error']}"
            )

        # Don't cache rate limit responses
        if "Information" not in data:
            set_cached(cache_key, data)

        return StockResponse(ticker=ticker.upper(), data=data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stock data: {str(e)}"
        )


# ── Stock History Endpoint ─────────────────────────────────────

@app.get("/stock/{ticker}/history")
async def get_stock_history_endpoint(ticker: str, period: str = "1y"):
    """
    Get historical price data. Cached for 6 hours.
    period options: 1mo, 3mo, 6mo, 1y
    """
    try:
        cache_key = f"history_{ticker.upper()}_{period}"
        cached = get_cached(cache_key)
        if cached:
            return {"ticker": ticker.upper(), "period": period, "data": cached}

        result = get_stock_history.invoke({
            "ticker": ticker.upper(),
            "period": period
        })
        data = json.loads(result)

        if "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])

        if "Information" not in data:
            set_cached(cache_key, data)

        return {"ticker": ticker.upper(), "period": period, "data": data}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── News Endpoint ──────────────────────────────────────────────

@app.get("/news/{ticker}")
async def get_news(ticker: str):
    """
    Get latest news for a company.
    Uses Google News RSS — no API quota used.
    """
    try:
        result = get_company_news.invoke({"ticker": ticker.upper()})
        data = json.loads(result)
        articles = data.get("articles", [])

        return NewsResponse(
            ticker=ticker.upper(),
            articles=articles,
            total=len(articles)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch news: {str(e)}"
        )


# ── Company Analysis Endpoint ──────────────────────────────────

@app.post("/company-analysis")
async def company_analysis(request: CompanyAnalysisRequest):
    """
    Run complete financial analysis for a company.
    Cached for 6 hours — repeat requests use zero API quota.
    """
    ticker = request.ticker.upper()

    try:
        # Check cache first — saves API calls
        cache_key = f"analysis_{ticker}"
        cached = get_cached(cache_key)
        if cached:
            print(f"Returning cached analysis for {ticker}")
            return AnalysisResponse(ticker=ticker, report=cached)

        # Step 1 — fetch stock price
        stock_result = get_stock_price.invoke({"ticker": ticker})
        stock_data = json.loads(stock_result)

        # Check for rate limiting
        if "Information" in stock_data:
            raise HTTPException(
                status_code=429,
                detail="Alpha Vantage API rate limit reached. Please wait 24 hours or use a new API key."
            )

        if "error" in stock_data:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find stock: {ticker}"
            )

        # Step 2 — fetch financial statements
        time.sleep(15)
        financials_result = get_financial_statements.invoke({"ticker": ticker})
        financial_data = json.loads(financials_result)

        # Step 3 — fetch company facts
        time.sleep(15)
        facts_result = get_company_facts.invoke({"ticker": ticker})
        facts_data = json.loads(facts_result)
        company_name = facts_data.get("company_name", ticker)

        # Step 4 — fetch news (Google RSS — no quota)
        news_result = get_company_news.invoke({"ticker": ticker})
        news_data = json.loads(news_result)
        articles = news_data.get("articles", [])

        # Step 5 — run financial analysis
        analysis = run_full_analysis(
            ticker=ticker,
            stock_data=stock_data,
            financial_data=financial_data
        )

        # Step 6 — generate report dict
        report = report_to_dict(
            ticker=ticker,
            company_name=company_name,
            analysis=analysis,
            news_articles=articles
        )

        # Cache the result — next request is instant
        set_cached(cache_key, report)

        return AnalysisResponse(ticker=ticker, report=report)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# ── Full Report Endpoint ───────────────────────────────────────

@app.get("/report/{ticker}")
async def get_full_report(ticker: str):
    """
    Generate complete formatted text report for a company.
    Cached for 6 hours.
    """
    ticker = ticker.upper()

    try:
        cache_key = f"report_{ticker}"
        cached = get_cached(cache_key)
        if cached:
            return cached

        stock_data = json.loads(get_stock_price.invoke({"ticker": ticker}))
        time.sleep(1)
        financial_data = json.loads(get_financial_statements.invoke({"ticker": ticker}))
        time.sleep(1)
        facts_data = json.loads(get_company_facts.invoke({"ticker": ticker}))
        company_name = facts_data.get("company_name", ticker)
        news_data = json.loads(get_company_news.invoke({"ticker": ticker}))
        articles = news_data.get("articles", [])

        analysis = run_full_analysis(
            ticker=ticker,
            stock_data=stock_data,
            financial_data=financial_data
        )

        report_text = generate_report(
            ticker=ticker,
            company_name=company_name,
            stock_data=stock_data,
            financial_data=financial_data,
            analysis=analysis,
            news_articles=articles,
            sources=[
                "Alpha Vantage Financial API",
                "Google News RSS Feed",
                "SEC EDGAR Database",
                "FinSight AI Knowledge Base"
            ]
        )

        result = {
            "ticker": ticker,
            "company_name": company_name,
            "report": report_text
        }

        set_cached(cache_key, result)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )


# ── SEC Filings Endpoin