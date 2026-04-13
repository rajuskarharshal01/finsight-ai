import React, { useState } from 'react';

const QueryInput = ({ onSubmit, isLoading }) => {
    const [query, setQuery] = useState('');
    const [ticker, setTicker] = useState('');

    const suggestions = [
        'Analyze Tesla financial performance',
        'What are Apple risk factors?',
        'Compare NVIDIA vs AMD',
        'Summarize Microsoft earnings',
        'Is Google stock overvalued?',
    ];

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSubmit(query.trim(), ticker.trim() || null);
        }
    };

    const handleSuggestion = (text) => {
        setQuery(text);
    };

    return (
        <div style={styles.container}>
            <h2 style={styles.heading}>Ask FinSight AI</h2>
            <p style={styles.subheading}>
                Ask any financial research question — the AI agent will
                gather real data and generate a structured analysis
            </p>
            <form onSubmit={handleSubmit} style={styles.form}>
                <div style={styles.inputRow}>
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="e.g. Analyze Tesla's financial performance..."
                        style={styles.queryInput}
                        disabled={isLoading}
                    />
                    <input
                        type="text"
                        value={ticker}
                        onChange={(e) => setTicker(e.target.value.toUpperCase())}
                        placeholder="Ticker (optional)"
                        style={styles.tickerInput}
                        disabled={isLoading}
                        maxLength={5}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !query.trim()}
                        style={{
                            ...styles.button,
                            ...(isLoading || !query.trim() ? styles.buttonDisabled : {})
                        }}
                    >
                        {isLoading ? 'Researching...' : 'Research →'}
                    </button>
                </div>
            </form>
            <div style={styles.suggestions}>
                <span style={styles.suggestionsLabel}>Try:</span>
                {suggestions.map((s, i) => (
                    <button
                        key={i}
                        onClick={() => handleSuggestion(s)}
                        style={styles.chip}
                        disabled={isLoading}
                    >
                        {s}
                    </button>
                ))}
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
        marginBottom: '32px',
    },
    heading: {
        color: '#e6f1ff',
        fontSize: '24px',
        fontWeight: '700',
        margin: '0 0 8px 0',
    },
    subheading: {
        color: '#8892b0',
        fontSize: '14px',
        margin: '0 0 24px 0',
        lineHeight: '1.5',
    },
    form: {
        marginBottom: '16px',
    },
    inputRow: {
        display: 'flex',
        gap: '12px',
        flexWrap: 'wrap',
    },
    queryInput: {
        flex: '1',
        minWidth: '300px',
        background: '#0d1b2a',
        border: '1px solid #0f3460',
        borderRadius: '8px',
        padding: '14px 16px',
        color: '#e6f1ff',
        fontSize: '15px',
        outline: 'none',
    },
    tickerInput: {
        width: '120px',
        background: '#0d1b2a',
        border: '1px solid #0f3460',
        borderRadius: '8px',
        padding: '14px 16px',
        color: '#e6f1ff',
        fontSize: '15px',
        outline: 'none',
        textTransform: 'uppercase',
    },
    button: {
        background: 'linear-gradient(135deg, #00d4aa, #00a884)',
        border: 'none',
        borderRadius: '8px',
        padding: '14px 28px',
        color: '#0d1b2a',
        fontSize: '15px',
        fontWeight: '700',
        cursor: 'pointer',
        whiteSpace: 'nowrap',
    },
    buttonDisabled: {
        opacity: '0.5',
        cursor: 'not-allowed',
    },
    suggestions: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        alignItems: 'center',
    },
    suggestionsLabel: {
        color: '#8892b0',
        fontSize: '13px',
    },
    chip: {
        background: '#0d1b2a',
        border: '1px solid #0f3460',
        borderRadius: '20px',
        padding: '6px 14px',
        color: '#8892b0',
        fontSize: '12px',
        cursor: 'pointer',
    },
};

export default QueryInput;