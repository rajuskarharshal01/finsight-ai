import requests
import json
import time
from langchain_core.tools import tool
from bs4 import BeautifulSoup


@tool
def get_sec_filings(ticker: str, filing_type: str = "10-K") -> str:
    """
    Retrieve SEC filings for a company from the SEC EDGAR database.
    Use this when you need official financial reports, annual reports (10-K),
    quarterly reports (10-Q), or other regulatory filings.

    Args:
        ticker: Stock ticker symbol like TSLA, AAPL, NVDA
        filing_type: Type of filing - 10-K (annual), 10-Q (quarterly), 8-K (current events)

    Returns:
        JSON string with list of recent SEC filings and their details
    """
    try:
        headers = {
            "User-Agent": "FinSight AI research@finsight.com",
            "Accept-Encoding": "gzip, deflate"
        }

        company_url = (
            f"https://www.sec.gov/cgi-bin/browse-edgar"
            f"?company=&CIK={ticker.upper()}&type={filing_type}"
            f"&dateb=&owner=include&count=5&search_text=&action=getcompany&output=atom"
        )

        response = requests.get(company_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "xml")
        entries = soup.findAll("entry")[:5]

        filings = []
        for entry in entries:
            filings.append({
                "title": entry.title.text if entry.title else "N/A",
                "filing_date": entry.updated.text[:10] if entry.updated else "N/A",
                "filing_type": filing_type,
                "link": entry.id.text if entry.id else "N/A",
            })

        return json.dumps({
            "ticker": ticker.upper(),
            "filing_type": filing_type,
            "total_filings": len(filings),
            "filings": filings
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Could not fetch SEC filings for {ticker}: {str(e)}"})


@tool
def get_company_facts(ticker: str) -> str:
    """
    Get key company facts and business description.
    Use this for company overview, business description, and basic facts.

    Args:
        ticker: Stock ticker symbol like TSLA, AAPL

    Returns:
        JSON string with company facts and description
    """
    try:
        import yfinance as yf
        import time
        time.sleep(2)
        stock = yf.Ticker(ticker.upper())

        try:
            info = stock.info
            facts = {
                "ticker": ticker.upper(),
                "company_name": info.get("longName", ticker.upper()),
                "business_summary": info.get("longBusinessSummary", "N/A")[:400],
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "country": info.get("country", "N/A"),
                "employees": info.get("fullTimeEmployees", "N/A"),
                "website": info.get("website", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
            }
        except:
            fast = stock.fast_info
            facts = {
                "ticker": ticker.upper(),
                "company_name": ticker.upper(),
                "current_price": round(float(fast.last_price), 2) if fast.last_price else "N/A",
                "market_cap": int(fast.market_cap) if fast.market_cap else "N/A",
                "note": "Limited data available"
            }

        return json.dumps(facts, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Could not fetch facts for {ticker}: {str(e)}"})