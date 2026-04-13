import React, { useState } from 'react';
import QueryInput from '../components/QueryInput';
import ReportDisplay from '../components/ReportDisplay';
import StockCard from '../components/StockCard';
import NewsCard from '../components/NewsCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { api } from '../api/client';

const Home = () => {
    const [loading, setLoading] = useState(false);
    const [agentResult, setAgentResult] = useState(null);
    const [error, setError] = useState(null);

    const handleQuery = async (query, ticker) => {
        setLoading(true);
        setError(null);
        setAgentResult(null);

        try {
            const response = await api.askAgent(query, ticker);
            setAgentResult(response.data);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                'Research failed. Please check if the API server is running.'
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.page}>
            <QueryInput onSubmit={handleQuery} isLoading={loading} />

            {error && (
                <div style={styles.error}>
                    ❌ {error}
                </div>
            )}

            {loading && (
                <LoadingSpinner message="AI Agent is researching..." />
            )}

            {agentResult && !loading && (
                <div style={styles.results}>
                    <div style={styles.resultHeader}>
                        <h3 style={styles.resultTitle}>Research Results</h3>
                        <div style={styles.toolsUsed}>
                            <span style={styles.toolsLabel}>Tools used:</span>
                            {agentResult.tools_used?.map((tool, i) => (
                                <span key={i} style={styles.toolBadge}>{tool}</span>
                            ))}
                        </div>
                    </div>
                    <ReportDisplay agentAnswer={agentResult.answer} />
                </div>
            )}
        </div>
    );
};

const styles = {
    page: {
        padding: '32px',
        maxWidth: '1200px',
        margin: '0 auto',
    },
    error: {
        background: '#ff475722',
        border: '1px solid #ff475744',
        borderRadius: '8px',
        padding: '16px',
        color: '#ff4757',
        marginBottom: '24px',
    },
    results: {
        marginTop: '24px',
    },
    resultHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
        flexWrap: 'wrap',
        gap: '12px',
    },
    resultTitle: {
        color: '#e6f1ff',
        fontSize: '18px',
        fontWeight: '600',
        margin: 0,
    },
    toolsUsed: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        flexWrap: 'wrap',
    },
    toolsLabel: {
        color: '#8892b0',
        fontSize: '13px',
    },
    toolBadge: {
        background: '#00d4aa22',
        color: '#00d4aa',
        border: '1px solid #00d4aa44',
        borderRadius: '12px',
        padding: '2px 10px',
        fontSize: '12px',
    },
};

export default Home;