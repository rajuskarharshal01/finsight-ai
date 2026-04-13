import React from 'react';

const MetricRow = ({ label, value, rating }) => (
    <div style={styles.metricRow}>
        <span style={styles.metricLabel}>{label}</span>
        <div style={styles.metricRight}>
            <span style={styles.metricValue}>{value}</span>
            {rating && (
                <span style={{
                    ...styles.ratingBadge,
                    background: rating === 'Excellent' ? '#00d4aa22' :
                        rating === 'Good' ? '#4CAF5022' :
                            rating === 'Fair' ? '#FF980022' : '#ff475722',
                    color: rating === 'Excellent' ? '#00d4aa' :
                        rating === 'Good' ? '#4CAF50' :
                            rating === 'Fair' ? '#FF9800' : '#ff4757',
                    border: `1px solid ${rating === 'Excellent' ? '#00d4aa44' :
                            rating === 'Good' ? '#4CAF5044' :
                                rating === 'Fair' ? '#FF980044' : '#ff475744'}`
                }}>
                    {rating}
                </span>
            )}
        </div>
    </div>
);

const Section = ({ title, children }) => (
    <div style={styles.section}>
        <h3 style={styles.sectionTitle}>{title}</h3>
        {children}
    </div>
);

const ReportDisplay = ({ report, agentAnswer }) => {
    if (!report && !agentAnswer) return null;

    // Show agent answer if available
    if (agentAnswer) {
        return (
            <div style={styles.container}>
                <div style={styles.header}>
                    <h2 style={styles.companyName}>Research Results</h2>
                    <span style={styles.healthBadge}>AI Analysis</span>
                </div>
                <div style={styles.agentAnswer}>
                    <h3 style={styles.sectionTitle}>Agent Response</h3>
                    <p style={styles.answerText}>{agentAnswer}</p>
                </div>
            </div>
        );
    }

    const {
        ticker,
        company_name,
        overall_health,
        summary,
        profitability,
        debt_and_liquidity,
        cash_flow,
        valuation,
        growth,
        recent_news,
        generated_at
    } = report;

    const healthColor = overall_health === 'Strong' ? '#00d4aa' :
        overall_health === 'Good' ? '#4CAF50' :
            overall_health === 'Fair' ? '#FF9800' : '#ff4757';

    return (
        <div style={styles.container}>

            {/* Header */}
            <div style={styles.header}>
                <div>
                    <h2 style={styles.companyName}>{company_name}</h2>
                    <span style={styles.tickerLabel}>{ticker}</span>
                </div>
                <div style={styles.headerRight}>
                    <span style={{
                        ...styles.healthBadge,
                        background: `${healthColor}22`,
                        color: healthColor,
                        border: `1px solid ${healthColor}44`
                    }}>
                        {overall_health} Financial Health
                    </span>
                    <span style={styles.timestamp}>
                        {new Date(generated_at).toLocaleString()}
                    </span>
                </div>
            </div>

            {/* Summary */}
            <div style={styles.summary}>
                <p style={styles.summaryText}>{summary}</p>
            </div>

            <div style={styles.grid}>

                {/* Profitability */}
                <Section title="📊 Profitability">
                    <MetricRow
                        label="Revenue"
                        value={profitability?.revenue}
                    />
                    <MetricRow
                        label="Net Income"
                        value={profitability?.net_income}
                    />
                    <MetricRow
                        label="Gross Margin"
                        value={profitability?.gross_margin}
                        rating={profitability?.ratings?.gross_margin}
                    />
                    <MetricRow
                        label="Net Margin"
                        value={profitability?.net_margin}
                        rating={profitability?.ratings?.net_margin}
                    />
                    <MetricRow
                        label="Return on Equity"
                        value={profitability?.return_on_equity}
                        rating={profitability?.ratings?.roe}
                    />
                </Section>

                {/* Valuation */}
                <Section title="💰 Valuation">
                    <MetricRow
                        label="Current Price"
                        value={valuation?.current_price}
                    />
                    <MetricRow
                        label="Market Cap"
                        value={valuation?.market_cap}
                    />
                    <MetricRow
                        label="P/E Ratio"
                        value={valuation?.pe_ratio}
                    />
                    <MetricRow
                        label="EV/EBITDA"
                        value={valuation?.ev_to_ebitda}
                    />
                    <MetricRow
                        label="Assessment"
                        value={valuation?.pe_assessment}
                    />
                </Section>

                {/* Debt */}
                <Section title="🏦 Debt & Liquidity">
                    <MetricRow
                        label="Total Debt"
                        value={debt_and_liquidity?.total_debt}
                    />
                    <MetricRow
                        label="Cash Position"
                        value={debt_and_liquidity?.cash_position}
                    />
                    <MetricRow
                        label="Net Debt"
                        value={debt_and_liquidity?.net_debt}
                    />
                    <MetricRow
                        label="Debt-to-Equity"
                        value={debt_and_liquidity?.debt_to_equity}
                    />
                    <MetricRow
                        label="Leverage"
                        value={debt_and_liquidity?.ratings?.leverage}
                    />
                </Section>

                {/* Cash Flow */}
                <Section title="💵 Cash Flow">
                    <MetricRow
                        label="Operating CF"
                        value={cash_flow?.operating_cash_flow}
                    />
                    <MetricRow
                        label="Capital Expenditure"
                        value={cash_flow?.capital_expenditure}
                    />
                    <MetricRow
                        label="Free Cash Flow"
                        value={cash_flow?.free_cash_flow}
                    />
                    <MetricRow
                        label="FCF Conversion"
                        value={cash_flow?.fcf_conversion_rate}
                    />
                    <MetricRow
                        label="Health"
                        value={cash_flow?.cash_flow_health}
                    />
                </Section>

                {/* Growth */}
                <Section title="📈 Growth (YoY)">
                    <MetricRow
                        label="Revenue Growth"
                        value={growth?.revenue_growth_yoy}
                    />
                    <MetricRow
                        label="Earnings Growth"
                        value={growth?.earnings_growth_yoy}
                    />
                    <MetricRow
                        label="Revenue Rating"
                        value={growth?.revenue_growth_rating}
                    />
                </Section>

                {/* News */}
                {recent_news && recent_news.length > 0 && (
                    <Section title="📰 Recent News">
                        {recent_news.slice(0, 3).map((article, i) => (
                            <div key={i} style={styles.newsItem}>
                                <span style={styles.newsSource}>
                                    {article.source}
                                </span>
                                <p style={styles.newsTitle}>{article.title}</p>
                            </div>
                        ))}
                    </Section>
                )}

            </div>

            {/* Disclaimer */}
            <div style={styles.disclaimer}>
                ⚠️ This report is generated by AI for informational purposes
                only and does NOT constitute financial advice.
            </div>

        </div>
    );
};

const styles = {
    container: {
        background: '#16213e',
        border: '1px solid #0f3460',
        borderRadius: '12px',
        padding: '32px',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '12px',
    },
    companyName: {
        color: '#e6f1ff',
        fontSize: '24px',
        fontWeight: '700',
        margin: '0 0 4px 0',
    },
    tickerLabel: {
        color: '#00d4aa',
        fontSize: '14px',
        fontWeight: '600',
    },
    headerRight: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-end',
        gap: '8px',
    },
    healthBadge: {
        padding: '6px 16px',
        borderRadius: '20px',
        fontSize: '13px',
        fontWeight: '600',
    },
    timestamp: {
        color: '#8892b0',
        fontSize: '12px',
    },
    summary: {
        background: '#0d1b2a',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '24px',
        borderLeft: '3px solid #00d4aa',
    },
    summaryText: {
        color: '#ccd6f6',
        fontSize: '15px',
        lineHeight: '1.6',
        margin: 0,
    },
    grid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '20px',
        marginBottom: '24px',
    },
    section: {
        background: '#0d1b2a',
        borderRadius: '8px',
        padding: '20px',
    },
    sectionTitle: {
        color: '#ccd6f6',
        fontSize: '15px',
        fontWeight: '600',
        margin: '0 0 16px 0',
        paddingBottom: '8px',
        borderBottom: '1px solid #0f3460',
    },
    metricRow: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 0',
        borderBottom: '1px solid #0f346022',
    },
    metricLabel: {
        color: '#8892b0',
        fontSize: '13px',
    },
    metricRight: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
    },
    metricValue: {
        color: '#e6f1ff',
        fontSize: '14px',
        fontWeight: '600',
    },
    ratingBadge: {
        fontSize: '11px',
        padding: '2px 8px',
        borderRadius: '12px',
        fontWeight: '600',
    },
    newsItem: {
        paddingBottom: '12px',
        marginBottom: '12px',
        borderBottom: '1px solid #0f346022',
    },
    newsSource: {
        color: '#00d4aa',
        fontSize: '11px',
        fontWeight: '600',
        textTransform: 'uppercase',
    },
    newsTitle: {
        color: '#ccd6f6',
        fontSize: '13px',
        margin: '4px 0 0 0',
        lineHeight: '1.4',
    },
    agentAnswer: {
        background: '#0d1b2a',
        borderRadius: '8px',
        padding: '20px',
    },
    answerText: {
        color: '#ccd6f6',
        fontSize: '15px',
        lineHeight: '1.7',
        margin: 0,
        whiteSpace: 'pre-wrap',
    },
    disclaimer: {
        color: '#8892b0',
        fontSize: '12px',
        textAlign: 'center',
        padding: '16px',
        borderTop: '1px solid #0f3460',
    },
};

export default ReportDisplay;