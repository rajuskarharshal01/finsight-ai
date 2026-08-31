
import requests
import json
from langchain_core.tools import tool


# ============================================================
# SEC EDGAR API CONFIGURATION
# ============================================================

SEC_BASE = "https://data.sec.gov"

# SEC requires a descriptive User-Agent for automated requests.
# Replace the email with your actual project/contact email.
SEC_HEADERS = {
    "User-Agent": "FinSight AI research@finsight.com",
    "Accept-Encoding": "gzip, deflate",
}


# ============================================================
# COMMON SEC REQUEST
# ============================================================

def sec_request(endpoint: str) -> dict:
    """
    Make a request to the SEC API.

    Supports both:
    - relative endpoints
    - full SEC URLs
    """
    try:
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            url = endpoint
        else:
            url = f"{SEC_BASE}/{endpoint.lstrip('/')}"

        response = requests.get(
            url,
            headers=SEC_HEADERS,
            timeout=20
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as e:
        return {
            "error": f"SEC HTTP error: {e}",
            "status_code": getattr(e.response, "status_code", None)
        }

    except requests.exceptions.RequestException as e:
        return {
            "error": f"SEC request failed: {str(e)}"
        }

    except ValueError as e:
        return {
            "error": f"SEC returned invalid JSON: {str(e)}"
        }

    except Exception as e:
        return {
            "error": f"Unexpected SEC error: {str(e)}"
        }


def get_cik_from_ticker(ticker: str) -> str | None:
    """
    Convert a stock ticker to its SEC CIK number.
    """

    ticker = ticker.upper().strip()

    # SEC ticker mapping endpoint
    url = "https://www.sec.gov/files/company_tickers.json"

    data = sec_request(url)

    if "error" in data:
        print("SEC ticker lookup error:", data)
        return None

    for company in data.values():

        company_ticker = str(
            company.get("ticker", "")
        ).upper().strip()

        if company_ticker == ticker:

            cik = company.get("cik_str")

            if cik is not None:
                return str(cik).zfill(10)

    return None

# ============================================================
# SEC FILINGS
# ============================================================

@tool
def get_sec_filings(
    ticker: str,
    filing_type: str = "10-K"
) -> str:
    """
    Retrieve recent SEC filings for a company.

    Uses the official SEC EDGAR submissions API.

    Args:
        ticker:
            Stock ticker symbol such as TSLA, AAPL, NVDA.

        filing_type:
            SEC filing type:
            10-K = Annual Report
            10-Q = Quarterly Report
            8-K  = Current Report

    Returns:
        JSON string containing recent filings.
    """

    try:
        ticker = ticker.upper().strip()

        cik = get_cik_from_ticker(ticker)

        if not cik:
            return json.dumps({
                "ticker": ticker,
                "status": "error",
                "message": f"Could not find SEC CIK for ticker {ticker}."
            }, indent=2)

        submissions = sec_request(
            f"submissions/CIK{cik}.json"
        )

        if "error" in submissions:
            return json.dumps({
                "ticker": ticker,
                "status": "error",
                "message": submissions["error"]
            }, indent=2)

        recent = submissions.get(
            "filings",
            {}
        ).get(
            "recent",
            {}
        )

        forms = recent.get("form", [])
        accession_numbers = recent.get(
            "accessionNumber",
            []
        )
        filing_dates = recent.get(
            "filingDate",
            []
        )
        report_dates = recent.get(
            "reportDate",
            []
        )
        primary_documents = recent.get(
            "primaryDocument",
            []
        )

        filings = []

        for i, form in enumerate(forms):

            if form != filing_type:
                continue

            accession = (
                accession_numbers[i]
                if i < len(accession_numbers)
                else "N/A"
            )

            accession_no_dash = accession.replace(
                "-", ""
            )

            primary_document = (
                primary_documents[i]
                if i < len(primary_documents)
                else ""
            )

            filing_date = (
                filing_dates[i]
                if i < len(filing_dates)
                else "N/A"
            )

            report_date = (
                report_dates[i]
                if i < len(report_dates)
                else "N/A"
            )

            filing_url = (
                f"https://www.sec.gov/Archives/edgar/data/"
                f"{int(cik)}/"
                f"{accession_no_dash}/"
                f"{primary_document}"
            )

            filings.append({
                "form": form,
                "filing_date": filing_date,
                "report_date": report_date,
                "accession_number": accession,
                "primary_document": primary_document,
                "url": filing_url
            })

            if len(filings) >= 5:
                break

        return json.dumps({
            "ticker": ticker,
            "cik": cik,
            "status": "success",
            "filing_type": filing_type,
            "total_filings": len(filings),
            "filings": filings,
            "source": "SEC EDGAR"
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "ticker": ticker,
            "status": "error",
            "message": f"Could not fetch SEC filings: {str(e)}"
        }, indent=2)


# ============================================================
# COMPANY FACTS / FINANCIAL DATA
# ============================================================

@tool
def get_company_facts(ticker: str) -> str:
    """
    Retrieve official company facts and financial metrics
    from the SEC XBRL Company Facts API.

    This replaces yfinance for SEC/company financial data.

    Useful for:
    - Revenue
    - Net income
    - Assets
    - Liabilities
    - Equity
    - Cash
    - Operating cash flow
    - Capital expenditure
    - EPS
    - Shares outstanding

    Args:
        ticker:
            Stock ticker symbol such as TSLA, AAPL, NVDA.

    Returns:
        JSON string containing company information and
        selected annual financial metrics.
    """

    try:
        ticker = ticker.upper().strip()

        cik = get_cik_from_ticker(ticker)

        if not cik:
            return json.dumps({
                "ticker": ticker,
                "status": "error",
                "message": f"Could not find SEC CIK for ticker {ticker}."
            }, indent=2)

        # ----------------------------------------------------
        # Get company submissions
        # ----------------------------------------------------

        submissions = sec_request(
            f"submissions/CIK{cik}.json"
        )

        if "error" in submissions:
            return json.dumps({
                "ticker": ticker,
                "status": "error",
                "message": submissions["error"]
            }, indent=2)

        company_name = submissions.get(
            "name",
            ticker
        )

        tickers = submissions.get(
            "tickers",
            []
        )

        exchanges = submissions.get(
            "exchanges",
            []
        )

        sic = submissions.get(
            "sic",
            "N/A"
        )

        sic_description = submissions.get(
            "sicDescription",
            "N/A"
        )

        # ----------------------------------------------------
        # Get XBRL Company Facts
        # ----------------------------------------------------

        facts = sec_request(
            f"api/xbrl/companyfacts/CIK{cik}.json"
        )

        if "error" in facts:
            return json.dumps({
                "ticker": ticker,
                "cik": cik,
                "status": "error",
                "message": facts["error"]
            }, indent=2)

        us_gaap = facts.get(
            "facts",
            {}
        ).get(
            "us-gaap",
            {}
        )

        # ----------------------------------------------------
        # Helper to retrieve annual facts
        # ----------------------------------------------------

        def get_annual_fact(
            possible_tags: list[str],
            limit: int = 5
        ):
            """
            Find the first available XBRL tag and return
            annual 10-K values.
            """

            for tag in possible_tags:

                concept = us_gaap.get(tag)

                if not concept:
                    continue

                units = concept.get(
                    "units",
                    {}
                )

                # Most financial statement values are USD.
                values = (
                    units.get("USD")
                    or units.get("USD/shares")
                    or units.get("shares")
                )

                if not values:
                    continue

                annual_values = []

                for item in values:

                    form = item.get("form")

                    # We primarily want annual 10-K data.
                    if form != "10-K":
                        continue

                    if "fy" not in item:
                        continue

                    annual_values.append({
                        "fy": item.get("fy"),
                        "fp": item.get("fp"),
                        "filed": item.get("filed"),
                        "start": item.get("start"),
                        "end": item.get("end"),
                        "value": item.get("val"),
                        "form": form,
                        "accn": item.get("accn")
                    })

                if annual_values:

                    # Newest first
                    annual_values.sort(
                        key=lambda x: (
                            x.get("end") or "",
                            x.get("filed") or ""
                        ),
                        reverse=True
                    )

                    return annual_values[:limit]

            return []

        # ----------------------------------------------------
        # Financial metrics
        # ----------------------------------------------------

        revenue = get_annual_fact([
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet"
        ])

        net_income = get_annual_fact([
            "NetIncomeLoss",
            "ProfitLoss"
        ])

        gross_profit = get_annual_fact([
            "GrossProfit"
        ])

        operating_income = get_annual_fact([
            "OperatingIncomeLoss"
        ])

        total_assets = get_annual_fact([
            "Assets"
        ])

        total_liabilities = get_annual_fact([
            "Liabilities"
        ])

        equity = get_annual_fact([
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
        ])

        cash = get_annual_fact([
            "CashAndCashEquivalentsAtCarryingValue"
        ])

        operating_cash_flow = get_annual_fact([
            "NetCashProvidedByUsedInOperatingActivities"
        ])

        capex = get_annual_fact([
            "PaymentsToAcquirePropertyPlantAndEquipment"
        ])

        diluted_eps = get_annual_fact([
            "EarningsPerShareDiluted"
        ])

        # ----------------------------------------------------
        # Build result
        # ----------------------------------------------------

        result = {
            "ticker": ticker,
            "cik": cik,
            "status": "success",
            "company_name": company_name,
            "tickers": tickers,
            "exchanges": exchanges,
            "sic": sic,
            "sic_description": sic_description,

            "financials": {
                "revenue": revenue,
                "net_income": net_income,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "stockholders_equity": equity,
                "cash_and_equivalents": cash,
                "operating_cash_flow": operating_cash_flow,
                "capital_expenditure": capex,
                "diluted_eps": diluted_eps
            },

            "source": "SEC EDGAR XBRL Company Facts API"
        }

        return json.dumps(
            result,
            indent=2
        )

    except Exception as e:

        return json.dumps({
            "ticker": ticker,
            "status": "error",
            "message": f"Could not fetch company facts: {str(e)}"
        }, indent=2)

