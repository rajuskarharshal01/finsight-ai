import requests
import json
import time
import os
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

TWELVE_KEY = os.getenv("TWELVE_DATA_KEY")
TWELVE_BASE = "https://api.twelvedata.com"


def twelve_request(endpoint: str, params: dict = {}) -> dict:
    """Make request to Twelve Data API — 800 free requests/day"""
    params["apikey"] = TWELVE_KEY
    try:
        response = requests.get(
            f"{TWELVE_BASE}/{endpoint}",
            params=params,
            timeout=15
        )
        data = response.json()
        if data.get("status") == "error":
            return {"error": data.get("message", "Unknown error")}
        return data
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(ticker: str) -> str:
    """
    Get the current stock price and basic market data for a company.
    Use this when you need current price, market cap, volume, or
    52-week high/low for a stock.

    Args:
        ticker: Stock ticker symbol like TSLA, AAPL, NVDA, MSFT

    Returns:
        JSON string with current price and market data
    """
    try:
        # Get real-time price
        price_data = twelve_request("price", {
            "symbol": ticker.upper(),
            "outputsize": 1
        })

        if "error" in price_data:
            return json.dumps(price_data)

        time.sleep(1)

        # Get quote for more details
        quote_data = twelve_request("quote", {
            "symbol": ticker.upper()
        })

        result = {
            "ticker": ticker.upper(),
            "company_name": quote_data.get("name", ticker.upper()),
            "current_price": price_data.get("price", "N/A"),
            "change": quote_data.get("change", "N/A"),
            "change_percent": quote_data.get("percent_change", "N/A"),
            "open": quote_data.get("open", "N/A"),
            "high": quote_data.get("high", "N/A"),
            "low": quote_data.get("low", "N/A"),
            "volume": quote_data.get("volume", "N/A"),
            "previous_close": quote_data.get("previous_close", "N/A"),
            "52_week_high": quote_data.get("fifty_two_week", {}).get("high", "N/A"),
            "52_week_low": quote_data.get("fifty_two_week", {}).get("low", "N/A"),
            "latest_trading_day": quote_data.get("datetime", "N/A"),
            "exchange": quote_data.get("exchange", "N/A"),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Could not fetch data for {ticker}: {str(e)}"})


@tool
def get_stock_history(ticker: str, period: str = "1y") -> str:
    """
    Get historical price data for a stock to analyze trends.

    Args:
        ticker: Stock ticker symbol like TSLA, AAPL
        period: Time period - options are 1mo, 3mo, 6mo, 1y

    Returns:
        JSON string with price history summary
    """
    try:
        period_days = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}
        outputsize = period_days.get(period, 365)

        data = twelve_request("time_series", {
            "symbol": ticker.upper(),
            "interval": "1day",
            "outputsize": outputsize
        })

        if "error" in data:
            return json.dumps(data)

        values = data.get("values", [])
        if not values:
            return json.dumps({"error": f"No history found for {ticker}"})

        # Twelve Data returns newest first
        values = list(reversed(values))
        prices = [float(v["close"]) for v in values]

        result = {
            "ticker": ticker.upper(),
            "period": period,
            "start_date": values[0]["datetime"],
            "end_date": values[-1]["datetime"],
            "start_price": round(prices[0], 2),
            "end_price": round(prices[-1], 2),
            "highest_price": round(max(float(v["high"]) for v in values), 2),
            "lowest_price": round(min(float(v["low"]) for v in values), 2),
            "price_change_pct": round(
                ((prices[-1] - prices[0]) / prices[0]) * 100, 2
            ),
            "data_points": len(prices)
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Could not fetch history for {ticker}: {str(e)}"})


@tool
def get_financial_statements(ticker: str) -> str:
    """
    Get financial statements for a company.

    Args:
        ticker: Stock ticker symbol like TSLA, AAPL, NVDA, MSFT

    Returns:
        JSON string with key financial metrics
    """
    try:
        # Income statement
        income = twelve_request("income_statement", {
            "symbol": ticker.upper(),
            "period": "annual",
            "outputsize": 1
        })
        time.sleep(1)

        # Balance sheet
        balance = twelve_request("balance_sheet", {
            "symbol": ticker.upper(),
            "period": "annual",
            "outputsize": 1
        })
        time.sleep(1)

        # Cash flow
        cashflow = twelve_request("cash_flow_statement", {
            "symbol": ticker.upper(),
            "period": "annual",
            "outputsize": 1
        })

        def safe_get(data, key):
            try:
                items = data.get("income_statement",
                        data.get("balance_sheet",
                        data.get("cash_flow_statement",
                        data.get("data", []))))
                if items and len(items) > 0:
                    return items[0].get(key, "N/A")
                return "N/A"
            except:
                return "N/A"

        result = {
            "ticker": ticker.upper(),
            "income_statement": {
                "total_revenue": safe_get(income, "revenue"),
                "gross_profit": safe_get(income, "gross_profit"),
                "operating_income": safe_get(income, "operating_income"),
                "net_income": safe_get(income, "net_income"),
                "ebitda": safe_get(income, "ebitda"),
                "eps": safe_get(income, "eps_diluted"),
            },
            "balance_sheet": {
                "total_assets": safe_get(balance, "total_assets"),
                "total_liabilities": safe_get(balance, "total_liabilities"),
                "total_debt": safe_get(balance, "total_debt"),
                "cash": safe_get(balance, "cash_and_equivalents"),
                "stockholders_equity": safe_get(balance, "total_equity"),
            },
            "cash_flow": {
                "operating_cash_flow": safe_get(cashflow, "cash_from_operating_activities"),
                "capital_expenditure": safe_get(cashflow, "capital_expenditures"),
                "free_cash_flow": safe_get(cashflow, "free_cash_flow"),
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Could not fetch financials for {ticker}: {str(e)}"})