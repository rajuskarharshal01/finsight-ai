import json
import os
import time
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

TWELVE_KEY = os.getenv("TWELVE_DATA_KEY")
TWELVE_BASE = "https://api.twelvedata.com"

REQUEST_TIMEOUT = 15


def twelve_request(
    endpoint: str,
    params: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """
    Make a request to Twelve Data API.

    Returns a normalized dictionary. API errors are returned as
    {"error": "..."} instead of raising exceptions.
    """

    if not TWELVE_KEY:
        return {
            "error": "TWELVE_DATA_KEY is not configured in the environment."
        }

    request_params = dict(params or {})
    request_params["apikey"] = TWELVE_KEY

    try:
        response = requests.get(
            f"{TWELVE_BASE}/{endpoint}",
            params=request_params,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            return {
                "error": "Unexpected response format from Twelve Data."
            }

        if data.get("status") == "error":
            return {
                "error": data.get(
                    "message",
                    "Unknown Twelve Data API error."
                )
            }

        return data

    except requests.RequestException as exc:
        return {
            "error": f"Twelve Data request failed: {str(exc)}"
        }

    except ValueError as exc:
        return {
            "error": f"Invalid JSON response from Twelve Data: {str(exc)}"
        }

    except Exception as exc:
        return {
            "error": f"Unexpected Twelve Data error: {str(exc)}"
        }


def _json(data: Dict[str, Any]) -> str:
    """Convert dictionary to readable JSON."""
    return json.dumps(data, indent=2, default=str)


# ---------------------------------------------------------------------
# CURRENT STOCK PRICE
# ---------------------------------------------------------------------

@tool
def get_stock_price(ticker: str) -> str:
    """
    Get current stock price and basic market data.

    Use this tool when the user asks for:
    - Current stock price
    - Daily change
    - Trading range
    - Volume
    - Previous close
    - 52-week high/low

    Args:
        ticker: Stock ticker such as TSLA, AAPL, NVDA, MSFT.

    Returns:
        JSON string containing current market data.
    """

    ticker = ticker.upper().strip()

    if not ticker:
        return _json({
            "status": "error",
            "message": "Ticker symbol is required."
        })

    try:
        # -------------------------------------------------------------
        # 1. Current price
        # -------------------------------------------------------------

        price_data = twelve_request(
            "price",
            {
                "symbol": ticker
            }
        )

        if "error" in price_data:
            return _json({
                "ticker": ticker,
                "status": "error",
                "message": price_data["error"]
            })

        time.sleep(1)

        # -------------------------------------------------------------
        # 2. Quote information
        # -------------------------------------------------------------

        quote_data = twelve_request(
            "quote",
            {
                "symbol": ticker
            }
        )

        if "error" in quote_data:
            return _json({
                "ticker": ticker,
                "status": "partial",
                "current_price": price_data.get("price", "N/A"),
                "message": quote_data["error"]
            })

        fifty_two_week = quote_data.get("fifty_two_week", {})

        if not isinstance(fifty_two_week, dict):
            fifty_two_week = {}

        result = {
            "ticker": ticker,
            "status": "success",

            "company_name": quote_data.get(
                "name",
                ticker
            ),

            "current_price": price_data.get(
                "price",
                "N/A"
            ),

            "change": quote_data.get(
                "change",
                "N/A"
            ),

            "change_percent": quote_data.get(
                "percent_change",
                "N/A"
            ),

            "open": quote_data.get(
                "open",
                "N/A"
            ),

            "high": quote_data.get(
                "high",
                "N/A"
            ),

            "low": quote_data.get(
                "low",
                "N/A"
            ),

            "volume": quote_data.get(
                "volume",
                "N/A"
            ),

            "previous_close": quote_data.get(
                "previous_close",
                "N/A"
            ),

            "52_week_high": fifty_two_week.get(
                "high",
                "N/A"
            ),

            "52_week_low": fifty_two_week.get(
                "low",
                "N/A"
            ),

            "latest_trading_day": quote_data.get(
                "datetime",
                "N/A"
            ),

            "exchange": quote_data.get(
                "exchange",
                "N/A"
            ),

            "source": "Twelve Data"
        }

        return _json(result)

    except Exception as exc:
        return _json({
            "ticker": ticker,
            "status": "error",
            "message": f"Could not fetch stock price: {str(exc)}"
        })


# ---------------------------------------------------------------------
# STOCK HISTORY
# ---------------------------------------------------------------------

@tool
def get_stock_history(
    ticker: str,
    period: str = "1y"
) -> str:
    """
    Get historical daily price data and trend summary.

    Args:
        ticker: Stock ticker symbol.
        period: 1mo, 3mo, 6mo, or 1y.

    Returns:
        JSON string containing historical price summary.
    """

    ticker = ticker.upper().strip()

    allowed_periods = {
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365
    }

    if period not in allowed_periods:
        return _json({
            "ticker": ticker,
            "status": "error",
            "message": (
                f"Invalid period '{period}'. "
                f"Use one of: {', '.join(allowed_periods.keys())}."
            )
        })

    try:
        data = twelve_request(
            "time_series",
            {
                "symbol": ticker,
                "interval": "1day",
                "outputsize": allowed_periods[period]
            }
        )

        if "error" in data:
            return _json({
                "ticker": ticker,
                "status": "error",
                "message": data["error"]
            })

        values = data.get("values", [])

        if not values:
            return _json({
                "ticker": ticker,
                "status": "error",
                "message": f"No historical data found for {ticker}."
            })

        # Twelve Data normally returns newest first.
        values = list(reversed(values))

        prices = []

        for value in values:
            try:
                prices.append(float(value["close"]))
            except (KeyError, TypeError, ValueError):
                continue

        if not prices:
            return _json({
                "ticker": ticker,
                "status": "error",
                "message": f"No valid price data found for {ticker}."
            })

        start_price = prices[0]
        end_price = prices[-1]

        if start_price != 0:
            price_change_pct = (
                (end_price - start_price) / start_price
            ) * 100
        else:
            price_change_pct = 0

        result = {
            "ticker": ticker,
            "status": "success",
            "period": period,

            "start_date": values[0].get(
                "datetime",
                "N/A"
            ),

            "end_date": values[-1].get(
                "datetime",
                "N/A"
            ),

            "start_price": round(
                start_price,
                2
            ),

            "end_price": round(
                end_price,
                2
            ),

            "highest_price": round(
                max(
                    float(v["high"])
                    for v in values
                    if v.get("high") is not None
                ),
                2
            ),

            "lowest_price": round(
                min(
                    float(v["low"])
                    for v in values
                    if v.get("low") is not None
                ),
                2
            ),

            "price_change_pct": round(
                price_change_pct,
                2
            ),

            "data_points": len(prices),

            "source": "Twelve Data"
        }

        return _json(result)

    except Exception as exc:
        return _json({
            "ticker": ticker,
            "status": "error",
            "message": f"Could not fetch history: {str(exc)}"
        })


# ---------------------------------------------------------------------
# FINANCIAL STATEMENTS
# ---------------------------------------------------------------------

@tool
def get_financial_statements(ticker: str) -> str:
    """
    Get annual financial statements using official SEC company facts.

    Twelve Data requires a paid plan for financial statement endpoints,
    so FinSight uses SEC EDGAR data instead.

    Args:
        ticker: Stock ticker symbol like TSLA, AAPL, NVDA, MSFT

    Returns:
        JSON string with annual revenue, net income, and other
        available financial metrics.
    """
    try:
        import json
        from backend.tools.sec_tool import get_company_facts

        ticker = ticker.upper().strip()

        # Get official SEC company facts
        raw_data = get_company_facts.invoke({"ticker": ticker})
        data = json.loads(raw_data)

        if data.get("status") != "success":
            return json.dumps({
                "ticker": ticker,
                "status": "error",
                "message": "Unable to retrieve SEC financial data.",
                "details": data.get("message", "Unknown SEC error")
            }, indent=2)

        financials = data.get("financials", {})

        revenue_data = financials.get("revenue", [])
        net_income_data = financials.get("net_income", [])

        # ---------------------------------------------------------
        # Helper: keep only annual FY records and remove duplicates
        # ---------------------------------------------------------
        def clean_annual_records(records):
            annual = []

            for record in records:
                if record.get("fp") != "FY":
                    continue

                start = record.get("start")
                end = record.get("end")

                if not start or not end:
                    continue

                # Ignore periods that are not approximately one year
                try:
                    from datetime import date

                    start_date = date.fromisoformat(start)
                    end_date = date.fromisoformat(end)
                    days = (end_date - start_date).days

                    if days < 300:
                        continue

                except Exception:
                    continue

                annual.append(record)

            # Deduplicate by actual reporting period.
            # SEC may contain the same year's number in multiple filings.
            unique = {}

            for record in annual:
                key = (
                    record.get("start"),
                    record.get("end")
                )

                # Prefer the most recently filed record
                if key not in unique:
                    unique[key] = record
                else:
                    existing_filed = unique[key].get("filed", "")
                    current_filed = record.get("filed", "")

                    if current_filed > existing_filed:
                        unique[key] = record

            # Sort newest year first
            return sorted(
                unique.values(),
                key=lambda x: x.get("end", ""),
                reverse=True
            )

        revenue_records = clean_annual_records(revenue_data)
        net_income_records = clean_annual_records(net_income_data)

        # ---------------------------------------------------------
        # Build clean financial history
        # ---------------------------------------------------------
        revenue_by_year = {}
        for record in revenue_records:
            year = record.get("end", "")[:4]

            if year:
                revenue_by_year[year] = {
                    "fiscal_year": int(year),
                    "revenue": record.get("value"),
                    "period_start": record.get("start"),
                    "period_end": record.get("end"),
                    "filed": record.get("filed"),
                    "form": record.get("form"),
                    "accession_number": record.get("accn")
                }

        net_income_by_year = {}
        for record in net_income_records:
            year = record.get("end", "")[:4]

            if year:
                net_income_by_year[year] = {
                    "fiscal_year": int(year),
                    "net_income": record.get("value"),
                    "period_start": record.get("start"),
                    "period_end": record.get("end"),
                    "filed": record.get("filed"),
                    "form": record.get("form"),
                    "accession_number": record.get("accn")
                }

        # ---------------------------------------------------------
        # Combine revenue + net income by fiscal year
        # ---------------------------------------------------------
        years = sorted(
            set(revenue_by_year.keys()) |
            set(net_income_by_year.keys()),
            reverse=True
        )

        annual_financials = []

        for year in years[:5]:
            revenue = revenue_by_year.get(year, {})
            net_income = net_income_by_year.get(year, {})

            annual_financials.append({
                "fiscal_year": int(year),
                "revenue": revenue.get("revenue", "N/A"),
                "net_income": net_income.get("net_income", "N/A"),
                "revenue_billions": (
                    round(revenue["revenue"] / 1_000_000_000, 2)
                    if isinstance(revenue.get("revenue"), (int, float))
                    else "N/A"
                ),
                "net_income_billions": (
                    round(net_income["net_income"] / 1_000_000_000, 2)
                    if isinstance(net_income.get("net_income"), (int, float))
                    else "N/A"
                ),
                "filing_date": (
                    revenue.get("filed")
                    or net_income.get("filed")
                    or "N/A"
                ),
                "form": (
                    revenue.get("form")
                    or net_income.get("form")
                    or "N/A"
                )
            })

        if not annual_financials:
            return json.dumps({
                "ticker": ticker,
                "status": "unavailable",
                "message": "No annual financial data found in SEC company facts.",
                "source": "SEC EDGAR"
            }, indent=2)

        return json.dumps({
            "ticker": ticker,
            "status": "success",
            "company_name": data.get("company_name", ticker),
            "annual_financials": annual_financials,
            "source": "SEC EDGAR",
            "note": (
                "Revenue and net income are sourced from official SEC "
                "company facts. Values are reported in USD."
            )
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "ticker": ticker if "ticker" in locals() else ticker,
            "status": "error",
            "message": f"Could not fetch financial statements for {ticker}: {str(e)}"
        }, indent=2)