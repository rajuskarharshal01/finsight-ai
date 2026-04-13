import React from 'react';

const StockCard = ({ data }) => {
    if (!data) return null;

    const isPositive = parseFloat(data.change_percent) >= 0;
    const changeColor = isPositive ? '#00d4aa' : '#ff4757';
    const changeSymbol = isPositive ? '▲' : '▼';

    return (
        <div style={styles.card}>
            <div style={styles.header}>
                <span style={styles.ticker}>{data.ticker}</span>
                <span style={styles.badge}>LIVE</span>
            </div>
            <div style={styles.price}>
                ${parseFloat(data.current_price).toFixed(2)}
            </div>
            <div style={{ ...styles.change, color: changeColor }}>
                {changeSymbol} {data.change} ({data.change_percent})
            </div>
            <div style={styles.divider} />
            <div style={styles.grid}>
                <div style={styles.metric}>
                    <span style={styles.label}>Open</span>
                    <span style={styles.value}>${data.open}</span>
                </div>
                <div style={styles.metric}>
                    <span style={styles.label}>High</span>
                    <span style={styles.value}>${data.high}</span>
                </div>
                <div style={styles.metric}>
                    <span style={styles.label}>Low</span>
                    <span style={styles.value}>${data.low}</span>
                </div>
                <div style={styles.metric}>
                    <span style={styles.label}>Volume</span>
                    <span style={styles.value}>
                        {parseInt(data.volume).toLocaleString()}
                    </span>
                </div>
                <div style={styles.metric}>
                    <span style={styles.label}>Prev Close</span>
                    <span style={styles.value}>${data.previous_close}</span>
                </div>
                <div style={styles.metric}>
                    <span style={styles.label}>As of</span>
                    <span style={styles.value}>{data.latest_trading_day}</span>
                </div>
            </div>
        </div>
    );
};

const styles = {
    card: {
        background: '#16213e',
        border: '1px solid #0f3460',
        borderRadius: '12px',
        padding: '24px',
        minWidth: '280px',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '12px',
    },
    ticker: {
        color: '#ccd6f6',
        fontSize: '20px',
        fontWeight: '700',
    },
    badge: {
        background: '#00d4aa22',
        color: '#00d4aa',
        fontSize: '11px',
        padding: '2px 8px',
        borderRadius: '20px',
        border: '1px solid #00d4aa44',
    },
    price: {
        color: '#e6f1ff',
        fontSize: '36px',
        fontWeight: '700',
        marginBottom: '4px',
    },
    change: {
        fontSize: '15px',
        fontWeight: '600',
        marginBottom: '16px',
    },
    divider: {
        height: '1px',
        background: '#0f3460',
        marginBottom: '16px',
    },
    grid: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
    },
    metric: {
        display: 'flex',
        flexDirection: 'column',
        gap: '2px',
    },
    label: {
        color: '#8892b0',
        fontSize: '11px',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
    },
    value: {
        color: '#ccd6f6',
        fontSize: '14px',
        fontWeight: '600',
    },
};

export default StockCard;