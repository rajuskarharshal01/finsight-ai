from datetime import datetime
from typing import Dict, List, Optional, Any
import json


# ── Report Sections ────────────────────────────────────────────

def generate_header(ticker: str, company_name: str) -> str:
    """Generate the report header with timestamp."""
    now = datetime.now().strftime("%B %d, %Y %I:%M %p")
    return f"""
╔══════════════════════════════════════════════════════════════╗
║           FINSIGHT AI — INVESTMENT RESEARCH REPORT           ║
╠══════════════════════════════════════════════════════════════╣
║  Company  : {company_name:<48}║
║  Ticker   : {ticker:<48}║
║  Generated: {now:<48}║
║  Powered by: FinSight AI Research Agent                      ║
╚══════════════════════════════════════════════════════════════╝
"""


def generate_executive_summary(
    ticker: str,
    company_name: str,
    analysis: Dict,
    news_summary: str = ""
) -> str:
    """
    Generate executive summary section.
    This is the most important section — busy investors
    read this first and may not read anything else.
    """
    health = analysis.get("overall_financial_health", "N/A")
    summary = analysis.get("summary", "")
    profitability = analysis.get("profitability", {})
    valuation = analysis.get("valuation", {})

    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Overall Financial Health : {health}
  Current Price            : {valuation.get('current_price', 'N/A')}
  Market Capitalization    : {valuation.get('market_cap', 'N/A')}
  P/E Ratio                : {valuation.get('pe_ratio', 'N/A')}
  Net Profit Margin        : {profitability.get('net_margin', 'N/A')}

  {summary}

  {f"Recent Developments: {news_summary}" if news_summary else ""}
"""


def generate_financial_performance(analysis: Dict) -> str:
    """
    Generate the financial performance section.
    Presents key metrics in a clean tabular format.
    """
    prof = analysis.get("profitability", {})
    debt = analysis.get("debt_and_liquidity", {})
    cf = analysis.get("cash_flow", {})
    val = analysis.get("valuation", {})
    growth = analysis.get("growth", {})
    ratings = prof.get("ratings", {})

    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FINANCIAL PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  INCOME STATEMENT
  ┌─────────────────────────────────────────────────────┐
  │ Revenue              : {prof.get('revenue', 'N/A'):<28}│
  │ Gross Profit         : {prof.get('gross_profit', 'N/A'):<28}│
  │ Net Income           : {prof.get('net_income', 'N/A'):<28}│
  │ EBITDA               : {prof.get('ebitda', 'N/A'):<28}│
  └─────────────────────────────────────────────────────┘

  PROFITABILITY MARGINS
  ┌─────────────────────────────────────────────────────┐
  │ Gross Margin         : {prof.get('gross_margin', 'N/A'):<18} {ratings.get('gross_margin', ''):<9}│
  │ Operating Margin     : {prof.get('operating_margin', 'N/A'):<18} {'':9}│
  │ Net Margin           : {prof.get('net_margin', 'N/A'):<18} {ratings.get('net_margin', ''):<9}│
  │ EBITDA Margin        : {prof.get('ebitda_margin', 'N/A'):<18} {'':9}│
  │ Return on Equity     : {prof.get('return_on_equity', 'N/A'):<18} {ratings.get('roe', ''):<9}│
  └─────────────────────────────────────────────────────┘

  BALANCE SHEET & DEBT
  ┌─────────────────────────────────────────────────────┐
  │ Total Assets         : {debt.get('total_assets', 'N/A'):<28}│
  │ Total Debt           : {debt.get('total_debt', 'N/A'):<28}│
  │ Cash Position        : {debt.get('cash_position', 'N/A'):<28}│
  │ Net Debt             : {debt.get('net_debt', 'N/A'):<28}│
  │ Debt-to-Equity       : {str(debt.get('debt_to_equity', 'N/A')):<18} {debt.get('ratings', {}).get('leverage', ''):<9}│
  └─────────────────────────────────────────────────────┘

  CASH FLOW
  ┌─────────────────────────────────────────────────────┐
  │ Operating Cash Flow  : {cf.get('operating_cash_flow', 'N/A'):<28}│
  │ Capital Expenditure  : {cf.get('capital_expenditure', 'N/A'):<28}│
  │ Free Cash Flow       : {cf.get('free_cash_flow', 'N/A'):<28}│
  │ FCF Conversion Rate  : {cf.get('fcf_conversion_rate', 'N/A'):<18} {cf.get('cash_flow_health', ''):<9}│
  └─────────────────────────────────────────────────────┘

  VALUATION
  ┌─────────────────────────────────────────────────────┐
  │ Enterprise Value     : {val.get('enterprise_value', 'N/A'):<28}│
  │ P/E Ratio            : {str(val.get('pe_ratio', 'N/A')):<28}│
  │ P/S Ratio            : {str(val.get('ps_ratio', 'N/A')):<28}│
  │ EV/EBITDA            : {str(val.get('ev_to_ebitda', 'N/A')):<28}│
  │ Valuation            : {val.get('pe_assessment', 'N/A'):<28}│
  └─────────────────────────────────────────────────────┘

  GROWTH (Year-over-Year)
  ┌─────────────────────────────────────────────────────┐
  │ Revenue Growth       : {growth.get('revenue_growth_yoy', 'N/A'):<18} {growth.get('revenue_growth_rating', ''):<9}│
  │ Earnings Growth      : {growth.get('earnings_growth_yoy', 'N/A'):<18} {growth.get('earnings_growth_rating', ''):<9}│
  └─────────────────────────────────────────────────────┘
"""


def generate_news_section(articles: List[Dict]) -> str:
    """
    Generate the recent news section.
    Articles come from our news tools.
    """
    if not articles:
        return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RECENT NEWS & DEVELOPMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  No recent news available.
"""

    news_text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RECENT NEWS & DEVELOPMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for i, article in enumerate(articles[:5], 1):
        title = article.get("title", "N/A")[:70]
        source = article.get("source", "N/A")
        published = article.get("published", "N/A")[:16]
        news_text += f"""
  [{i}] {title}
       Source: {source} | {published}
"""
    return news_text


def generate_risk_section(
    ticker: str,
    analysis: Dict,
    rag_context: str = ""
) -> str:
    """
    Generate risk factors section.
    Combines quantitative risks from analysis with
    qualitative risks from RAG document search.
    """
    debt = analysis.get("debt_and_liquidity", {})
    cf = analysis.get("cash_flow", {})
    val = analysis.get("valuation", {})

    # Identify quantitative risk flags
    risks = []

    leverage = debt.get("ratings", {}).get("leverage", "")
    if leverage in ["High", "Very High"]:
        risks.append(f"High leverage — debt-to-equity ratio of "
                    f"{debt.get('debt_to_equity', 'N/A')} indicates "
                    f"significant debt burden")

    cf_health = cf.get("cash_flow_health", "")
    if cf_health == "Weak":
        risks.append(f"Negative free cash flow — company is burning "
                    f"cash which may require additional financing")

    pe = val.get("pe_ratio", 0)
    if isinstance(pe, (int, float)) and pe > 40:
        risks.append(f"High valuation — P/E ratio of {pe} leaves "
                    f"little margin for error if growth slows")

    pe_assessment = val.get("pe_assessment", "")
    if pe_assessment == "Expensive":
        risks.append("Stock appears expensive relative to earnings — "
                    "downside risk if market sentiment shifts")

    # Default risks if none identified
    if not risks:
        risks = [
            "Market and macroeconomic risks affecting all equities",
            "Competitive landscape changes in the industry",
            "Regulatory and geopolitical risk factors"
        ]

    risk_text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK FACTORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for i, risk in enumerate(risks, 1):
        risk_text += f"\n  {i}. {risk}\n"

    if rag_context:
        risk_text += f"\n  Additional context from research database:\n"
        risk_text += f"  {rag_context[:300]}...\n"

    return risk_text


def generate_investment_outlook(
    ticker: str,
    analysis: Dict
) -> str:
    """
    Generate balanced investment outlook section.
    Always presents both bull and bear cases.
    This is NOT financial advice — it's structured analysis.
    """
    health = analysis.get("overall_financial_health", "Fair")
    prof = analysis.get("profitability", {})
    debt = analysis.get("debt_and_liquidity", {})
    cf = analysis.get("cash_flow", {})
    growth = analysis.get("growth", {})
    val = analysis.get("valuation", {})

    # Bull case points
    bull_points = []
    if prof.get("ratings", {}).get("net_margin") in ["Excellent", "Good"]:
        bull_points.append(
            f"Strong profitability with {prof.get('net_margin')} net margin"
        )
    if debt.get("ratings", {}).get("leverage") in ["Low", "Moderate"]:
        bull_points.append(
            f"Conservative balance sheet with "
            f"{debt.get('debt_to_equity')} debt-to-equity"
        )
    if cf.get("cash_flow_health") in ["Strong", "Good"]:
        bull_points.append(
            f"Healthy free cash flow of {cf.get('free_cash_flow')}"
        )
    if growth.get("revenue_growth_rating") in ["Exceptional", "Strong"]:
        bull_points.append(
            f"Strong revenue growth of {growth.get('revenue_growth_yoy')}"
        )

    if not bull_points:
        bull_points = ["Company maintains operational presence in market"]

    # Bear case points
    bear_points = []
    pe = val.get("pe_ratio", 0)
    if isinstance(pe, (int, float)) and pe > 30:
        bear_points.append(
            f"Premium valuation at {pe}x earnings requires "
            f"continued strong execution"
        )
    if debt.get("ratings", {}).get("leverage") in ["High", "Very High"]:
        bear_points.append("Elevated debt levels increase financial risk")
    if cf.get("cash_flow_health") == "Weak":
        bear_points.append("Negative free cash flow raises sustainability concerns")

    if not bear_points:
        bear_points = [
            "Market volatility and macro conditions could impact performance",
            "Increased competition may pressure margins over time"
        ]

    bull_text = "\n".join([f"  + {p}" for p in bull_points])
    bear_text = "\n".join([f"  - {p}" for p in bear_points])

    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  INVESTMENT OUTLOOK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Overall Assessment: {health} Financial Position

  BULL CASE (Positive Factors):
{bull_text}

  BEAR CASE (Risk Factors):
{bear_text}

  ⚠  DISCLAIMER: This report is generated by AI for informational
     purposes only and does NOT constitute financial advice.
     Always consult a qualified financial advisor before investing.
"""


def generate_sources_section(sources: List[str]) -> str:
    """Generate the data sources and citations section."""
    if not sources:
        sources = [
            "Alpha Vantage Financial API",
            "Google News RSS Feed",
            "SEC EDGAR Database",
            "FinSight AI Knowledge Base"
        ]

    sources_text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DATA SOURCES & CITATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for i, source in enumerate(sources, 1):
        sources_text += f"\n  [{i}] {source}"

    sources_text += "\n"
    return sources_text


# ── Master Report Generator ────────────────────────────────────

def generate_report(
    ticker: str,
    company_name: str,
    stock_data: Dict,
    financial_data: Dict,
    analysis: Dict,
    news_articles: Optional[List[Dict]] = None,
    rag_context: str = "",
    sources: Optional[List[str]] = None,
    previous_financial_data: Optional[Dict] = None
) -> str:
    """
    Generate a complete investment research report.

    This is the main entry point — combines all sections
    into one formatted report string.

    Args:
        ticker: Stock symbol e.g. "MSFT"
        company_name: Full company name
        stock_data: From get_stock_price tool
        financial_data: From get_financial_statements tool
        analysis: From run_full_analysis()
        news_articles: List of news dicts from news tools
        rag_context: Relevant text from knowledge base
        sources: List of data source names for citations
        previous_financial_data: For growth calculations

    Returns:
        Complete formatted report as string
    """
    print(f"Generating report for {ticker}...")

    # Build news summary for executive summary
    news_summary = ""
    if news_articles:
        titles = [a.get("title", "")[:60] for a in news_articles[:2]]
        news_summary = " | ".join(titles)

    # Combine all sections
    report = ""
    report += generate_header(ticker, company_name)
    report += generate_executive_summary(
        ticker, company_name, analysis, news_summary
    )
    report += generate_financial_performance(analysis)
    report += generate_news_section(news_articles or [])
    report += generate_risk_section(ticker, analysis, rag_context)
    report += generate_investment_outlook(ticker, analysis)
    report += generate_sources_section(sources or [])

    # Footer
    report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  END OF REPORT — FinSight AI | {datetime.now().strftime("%Y")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return report


def save_report(report: str, ticker: str) -> str:
    """
    Save report to a file.
    Returns the filename.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{ticker}_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report saved to {filename}")
    return filename


def report_to_dict(
    ticker: str,
    company_name: str,
    analysis: Dict,
    news_articles: Optional[List[Dict]] = None,
) -> Dict:
    """
    Convert report data to a clean dictionary.
    Used by the FastAPI endpoint to return JSON to the frontend.
    """
    return {
        "ticker": ticker.upper(),
        "company_name": company_name,
        "generated_at": datetime.now().isoformat(),
        "overall_health": analysis.get("overall_financial_health"),
        "summary": analysis.get("summary"),
        "profitability": analysis.get("profitability"),
        "debt_and_liquidity": analysis.get("debt_and_liquidity"),
        "cash_flow": analysis.get("cash_flow"),
        "valuation": analysis.get("valuation"),
        "growth": analysis.get("growth"),
        "recent_news": news_articles[:5] if news_articles else [],
        "disclaimer": "This report is for informational purposes only "
                     "and does not constitute financial advice."
    }