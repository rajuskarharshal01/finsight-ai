from typing import Dict, Any, Optional
import json


# ── Helper Functions ───────────────────────────────────────────

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert any value to float.

    Financial data comes in messy formats:
    - "281724000000"  (string from API)
    - 281724000000    (int)
    - 281724000000.0  (float)
    - "N/A"           (missing data)
    - None            (null)

    This function handles all cases gracefully.
    """
    if value is None or value == "N/A" or value == "None":
        return default
    try:
        return float(str(value).replace(",", "").replace("%", ""))
    except (ValueError, TypeError):
        return default


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers — avoids ZeroDivisionError.
    Returns default if denominator is zero or either value is invalid.
    """
    if denominator == 0 or denominator is None:
        return default
    try:
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def format_number(value: float) -> str:
    """
    Format large numbers into human readable strings.

    281724000000  →  "$281.72B"
    9870000000    →  "$9.87B"
    542000000     →  "$542.00M"
    1234567       →  "$1.23M"
    """
    if value == 0:
        return "N/A"
    abs_val = abs(value)
    sign = "-" if value < 0 else ""
    if abs_val >= 1_000_000_000_000:
        return f"{sign}${abs_val/1_000_000_000_000:.2f}T"
    elif abs_val >= 1_000_000_000:
        return f"{sign}${abs_val/1_000_000_000:.2f}B"
    elif abs_val >= 1_000_000:
        return f"{sign}${abs_val/1_000_000:.2f}M"
    else:
        return f"{sign}${abs_val:,.2f}"


def format_percent(value: float) -> str:
    """Format a decimal ratio as percentage string: 0.361 → '36.1%'"""
    if value == 0:
        return "N/A"
    return f"{value * 100:.1f}%"


def rate_metric(value: float, thresholds: Dict) -> str:
    """
    Rate a metric as Excellent/Good/Fair/Poor based on thresholds.

    Example thresholds for profit margin:
    {"excellent": 0.20, "good": 0.10, "fair": 0.05}
    means:
    - > 20%  → Excellent
    - > 10%  → Good
    - > 5%   → Fair
    - else   → Poor
    """
    if value >= thresholds.get("excellent", float("inf")):
        return "Excellent"
    elif value >= thresholds.get("good", float("inf")):
        return "Good"
    elif value >= thresholds.get("fair", float("inf")):
        return "Fair"
    else:
        return "Poor"


# ── Profitability Analysis ─────────────────────────────────────

def analyze_profitability(financial_data: Dict) -> Dict:
    """
    Compute profitability ratios from financial statement data.

    Profitability ratios answer: "How efficiently does the company
    convert revenue into profit?"

    Args:
        financial_data: Dict from get_financial_statements tool

    Returns:
        Dict with computed ratios and ratings
    """
    income = financial_data.get("income_statement", {})

    revenue = safe_float(income.get("total_revenue"))
    gross_profit = safe_float(income.get("gross_profit"))
    operating_income = safe_float(income.get("operating_income"))
    net_income = safe_float(income.get("net_income"))
    ebitda = safe_float(income.get("ebitda"))

    # Compute margins — all expressed as ratios (0.0 to 1.0)
    gross_margin = safe_divide(gross_profit, revenue)
    operating_margin = safe_divide(operating_income, revenue)
    net_margin = safe_divide(net_income, revenue)
    ebitda_margin = safe_divide(ebitda, revenue)

    # Return on equity
    balance = financial_data.get("balance_sheet", {})
    equity = safe_float(balance.get("stockholders_equity"))
    roe = safe_divide(net_income, equity)

    return {
        "revenue": format_number(revenue),
        "gross_profit": format_number(gross_profit),
        "net_income": format_number(net_income),
        "ebitda": format_number(ebitda),
        "gross_margin": format_percent(gross_margin),
        "operating_margin": format_percent(operating_margin),
        "net_margin": format_percent(net_margin),
        "ebitda_margin": format_percent(ebitda_margin),
        "return_on_equity": format_percent(roe),
        "ratings": {
            "gross_margin": rate_metric(gross_margin, {
                "excellent": 0.50, "good": 0.30, "fair": 0.15
            }),
            "net_margin": rate_metric(net_margin, {
                "excellent": 0.20, "good": 0.10, "fair": 0.05
            }),
            "roe": rate_metric(roe, {
                "excellent": 0.20, "good": 0.12, "fair": 0.06
            })
        }
    }


# ── Debt & Liquidity Analysis ──────────────────────────────────

def analyze_debt(financial_data: Dict) -> Dict:
    """
    Compute debt and liquidity ratios.

    These answer: "Can the company pay its debts?
    Is it overleveraged?"

    Key ratios:
    - Debt-to-equity: how much debt vs shareholder money
      < 1.0 = conservative, > 2.0 = risky
    - Debt-to-assets: what % of assets are debt-funded
      < 0.4 = healthy, > 0.6 = concerning
    """
    balance = financial_data.get("balance_sheet", {})

    total_debt = safe_float(balance.get("total_debt"))
    equity = safe_float(balance.get("stockholders_equity"))
    total_assets = safe_float(balance.get("total_assets"))
    cash = safe_float(balance.get("cash"))
    total_liabilities = safe_float(balance.get("total_liabilities"))

    # Key debt ratios
    debt_to_equity = safe_divide(total_debt, equity)
    debt_to_assets = safe_divide(total_debt, total_assets)
    net_debt = total_debt - cash  # negative = more cash than debt (great!)

    # Interest coverage from income statement
    income = financial_data.get("income_statement", {})
    ebitda = safe_float(income.get("ebitda"))

    return {
        "total_debt": format_number(total_debt),
        "total_assets": format_number(total_assets),
        "cash_position": format_number(cash),
        "net_debt": format_number(net_debt),
        "stockholders_equity": format_number(equity),
        "debt_to_equity": round(debt_to_equity, 2),
        "debt_to_assets": format_percent(debt_to_assets),
        "ratings": {
            "debt_to_equity": rate_metric(
                # Lower is better so we invert the rating
                1 - min(debt_to_equity / 3, 1),
                {"excellent": 0.67, "good": 0.33, "fair": 0.1}
            ),
            "leverage": "Low" if debt_to_equity < 0.5 else
                       "Moderate" if debt_to_equity < 1.5 else
                       "High" if debt_to_equity < 3.0 else "Very High"
        }
    }


# ── Cash Flow Analysis ─────────────────────────────────────────

def analyze_cash_flow(financial_data: Dict) -> Dict:
    """
    Analyze cash flow health.

    Free Cash Flow (FCF) is arguably the most important metric —
    it's the actual cash the business generates after maintaining
    and growing its asset base. A company can show accounting
    profit but have negative FCF — that's a red flag.

    FCF = Operating Cash Flow - Capital Expenditure
    """
    cash_flow = financial_data.get("cash_flow", {})
    income = financial_data.get("income_statement", {})

    operating_cf = safe_float(cash_flow.get("operating_cash_flow"))
    capex = safe_float(cash_flow.get("capital_expenditure"))
    free_cf = safe_float(cash_flow.get("free_cash_flow"))
    net_income = safe_float(income.get("net_income"))

    # FCF conversion — what % of net income becomes free cash
    # > 100% means company generates more cash than accounting profit
    fcf_conversion = safe_divide(free_cf, net_income)

    # If free_cash_flow not directly available, compute it
    if free_cf == 0 and operating_cf != 0:
        free_cf = operating_cf + capex  # capex is usually negative
        fcf_conversion = safe_divide(free_cf, net_income)

    return {
        "operating_cash_flow": format_number(operating_cf),
        "capital_expenditure": format_number(abs(capex)),
        "free_cash_flow": format_number(free_cf),
        "fcf_conversion_rate": format_percent(fcf_conversion),
        "cash_flow_health": (
            "Strong" if free_cf > 0 and fcf_conversion > 0.8 else
            "Good" if free_cf > 0 else
            "Weak" if free_cf < 0 else
            "N/A"
        )
    }


# ── Valuation Analysis ─────────────────────────────────────────

def analyze_valuation(
    stock_data: Dict,
    financial_data: Dict
) -> Dict:
    """
    Compute valuation metrics.

    Valuation answers: "Is the stock cheap or expensive
    relative to what the company earns?"

    P/E Ratio = Price / Earnings Per Share
    - < 15: potentially undervalued
    - 15-25: fairly valued
    - > 25: growth premium or overvalued

    P/S Ratio = Market Cap / Revenue
    - Useful when company has no earnings yet
    """
    # From stock price tool
    price = safe_float(stock_data.get("current_price"))
    market_cap = safe_float(stock_data.get("market_cap"))

    # From financial statements
    income = financial_data.get("income_statement", {})
    revenue = safe_float(income.get("total_revenue"))
    net_income = safe_float(income.get("net_income"))
    ebitda = safe_float(income.get("ebitda"))

    balance = financial_data.get("balance_sheet", {})
    equity = safe_float(balance.get("stockholders_equity"))
    total_debt = safe_float(balance.get("total_debt"))
    cash = safe_float(balance.get("cash"))

    # Enterprise Value = Market Cap + Debt - Cash
    # Represents total company value including debt
    enterprise_value = market_cap + total_debt - cash

    # Key valuation ratios
    pe_ratio = safe_divide(market_cap, net_income)
    ps_ratio = safe_divide(market_cap, revenue)
    pb_ratio = safe_divide(market_cap, equity)
    ev_ebitda = safe_divide(enterprise_value, ebitda)

    def rate_pe(pe):
        if pe <= 0: return "N/A (negative earnings)"
        if pe < 15: return "Potentially undervalued"
        if pe < 25: return "Fairly valued"
        if pe < 40: return "Growth premium"
        return "Expensive"

    return {
        "current_price": f"${price:.2f}" if price else "N/A",
        "market_cap": format_number(market_cap),
        "enterprise_value": format_number(enterprise_value),
        "pe_ratio": round(pe_ratio, 1) if pe_ratio else "N/A",
        "ps_ratio": round(ps_ratio, 2) if ps_ratio else "N/A",
        "pb_ratio": round(pb_ratio, 2) if pb_ratio else "N/A",
        "ev_to_ebitda": round(ev_ebitda, 1) if ev_ebitda else "N/A",
        "pe_assessment": rate_pe(pe_ratio)
    }


# ── Growth Analysis ────────────────────────────────────────────

def analyze_growth(
    current_data: Dict,
    previous_data: Optional[Dict] = None
) -> Dict:
    """
    Calculate year-over-year growth rates.

    Growth rates tell us if the company is expanding or contracting.
    We compare current year vs previous year for key metrics.

    If previous_data is not available, we return estimated
    growth based on available context.
    """
    current_income = current_data.get("income_statement", {})

    current_revenue = safe_float(current_income.get("total_revenue"))
    current_net_income = safe_float(current_income.get("net_income"))
    current_ebitda = safe_float(current_income.get("ebitda"))

    if previous_data:
        prev_income = previous_data.get("income_statement", {})
        prev_revenue = safe_float(prev_income.get("total_revenue"))
        prev_net_income = safe_float(prev_income.get("net_income"))
        prev_ebitda = safe_float(prev_income.get("ebitda"))

        revenue_growth = safe_divide(
            current_revenue - prev_revenue, prev_revenue
        )
        earnings_growth = safe_divide(
            current_net_income - prev_net_income, abs(prev_net_income)
        )
        ebitda_growth = safe_divide(
            current_ebitda - prev_ebitda, abs(prev_ebitda)
        )

        def rate_growth(g):
            if g > 0.30: return "Exceptional"
            if g > 0.15: return "Strong"
            if g > 0.05: return "Moderate"
            if g > 0: return "Slow"
            return "Declining"

        return {
            "revenue_growth_yoy": format_percent(revenue_growth),
            "earnings_growth_yoy": format_percent(earnings_growth),
            "ebitda_growth_yoy": format_percent(ebitda_growth),
            "revenue_growth_rating": rate_growth(revenue_growth),
            "earnings_growth_rating": rate_growth(earnings_growth)
        }

    return {
        "note": "Previous year data not provided — growth rates unavailable",
        "current_revenue": format_number(current_revenue),
        "current_net_income": format_number(current_net_income)
    }


# ── Master Analysis Function ───────────────────────────────────

def run_full_analysis(
    ticker: str,
    stock_data: Dict,
    financial_data: Dict,
    previous_financial_data: Optional[Dict] = None
) -> Dict:
    """
    Run complete financial analysis for a company.

    This is the main entry point — combines all individual
    analysis functions into one comprehensive report dict.

    Args:
        ticker: Stock symbol e.g. "AAPL"
        stock_data: Output from get_stock_price tool
        financial_data: Output from get_financial_statements tool
        previous_financial_data: Previous year data for growth calc

    Returns:
        Complete analysis dict with all metrics and ratings
    """
    print(f"Running full analysis for {ticker}...")

    profitability = analyze_profitability(financial_data)
    debt = analyze_debt(financial_data)
    cash_flow = analyze_cash_flow(financial_data)
    valuation = analyze_valuation(stock_data, financial_data)
    growth = analyze_growth(financial_data, previous_financial_data)

    # Overall health score — weighted average of key ratings
    rating_map = {"Excellent": 4, "Good": 3, "Fair": 2, "Poor": 1}
    scores = []

    gm_score = rating_map.get(
        profitability["ratings"]["gross_margin"], 2
    )
    nm_score = rating_map.get(
        profitability["ratings"]["net_margin"], 2
    )
    scores.extend([gm_score, nm_score])

    avg_score = sum(scores) / len(scores) if scores else 2

    overall = (
        "Strong" if avg_score >= 3.5 else
        "Good" if avg_score >= 2.5 else
        "Fair" if avg_score >= 1.5 else
        "Weak"
    )

    return {
        "ticker": ticker.upper(),
        "overall_financial_health": overall,
        "profitability": profitability,
        "debt_and_liquidity": debt,
        "cash_flow": cash_flow,
        "valuation": valuation,
        "growth": growth,
        "summary": (
            f"{ticker.upper()} shows {overall.lower()} financial health. "
            f"Net margin: {profitability['net_margin']}, "
            f"Debt-to-equity: {debt['debt_to_equity']}, "
            f"Free cash flow: {cash_flow['free_cash_flow']}."
        )
    }