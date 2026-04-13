import React, { useState, useEffect, useRef } from 'react';
import StockCard from '../components/StockCard';
import NewsCard from '../components/NewsCard';
import ReportDisplay from '../components/ReportDisplay';
import LoadingSpinner from '../components/LoadingSpinner';
import { api } from '../api/client';

const Analysis = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [selectedTicker, setSelectedTicker] = useState('');
    const [selectedName, setSelectedName] = useState('');
    const [loading, setLoading] = useState(false);
    const [searching, setSearching] = useState(false);
    const [stockData, setStockData] = useState(null);
    const [newsData, setNewsData] = useState(null);
    const [reportData, setReportData] = useState(null);
    const [error, setError] = useState(null);
    const searchTimeout = useRef(null);
    const wrapperRef = useRef(null);

    const popularCompanies = [
        { name: 'Apple', ticker: 'AAPL' },
        { name: 'Microsoft', ticker: 'MSFT' },
        { name: 'NVIDIA', ticker: 'NVDA' },
        { name: 'Tesla', ticker: 'TSLA' },
        { name: 'JP Morgan', ticker: 'JPM' },
        { name: 'Google', ticker: 'GOOGL' },
        { name: 'Amazon', ticker: 'AMZN' },
        { name: 'Meta', ticker: 'META' },
        { name: 'Goldman Sachs', ticker: 'GS' },
        { name: 'Netflix', ticker: 'NFLX' },
        { name: 'Visa', ticker: 'V' },
        { name: 'Johnson & Johnson', ticker: 'JNJ' },
    ];

    // Close suggestions when clicking outside
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
                setShowSuggestions(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Search as user types — debounced 400ms
    const handleSearchInput = (value) => {
        setSearchQuery(value);
        setSelectedTicker('');

        if (searchTimeout.current) clearTimeout(searchTimeout.current);

        if (value.length < 2) {
            setSuggestions([]);
            setShowSuggestions(false);
            return;
        }

        setSearching(true);
        searchTimeout.current = setTimeout(async () => {
            try {
                const res = await api.searchCompany(value);
                setSuggestions(res.data.results || []);
                setShowSuggestions(true);
            } catch {
                setSuggestions([]);
            } finally {
                setSearching(false);
            }
        }, 400);
    };

    // User picks a suggestion
    const handleSelectCompany = (company) => {
        setSearchQuery(company.name);
        setSelectedTicker(company.ticker);
        setSelectedName(company.name);
        setShowSuggestions(false);
        setSuggestions([]);
        // Auto-analyze when selected
        handleAnalyze(company.ticker, company.name);
    };

    // Run analysis
    const handleAnalyze = async (ticker, name) => {
        const symbol = ticker || selectedTicker || searchQuery.toUpperCase().trim();
        if (!symbol) {
            setError('Please type a company name or ticker symbol');
            return;
        }

        setLoading(true);
        setError(null);
        setStockData(null);
        setNewsData(null);
        setReportData(null);

        try {
            const [stockRes, newsRes, analysisRes] = await Promise.allSettled([
                api.getStock(symbol),
                api.getNews(symbol),
                api.analyzeCompany(symbol),
            ]);

            if (stockRes.status === 'fulfilled') {
                setStockData(stockRes.value.data.data);
            }
            if (newsRes.status === 'fulfilled') {
                setNewsData(newsRes.value.data.articles);
            }
            if (analysisRes.status === 'fulfilled') {
                setReportData(analysisRes.value.data.report);
            } else {
                setError('Analysis partially failed — showing available data');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Analysis failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.page}>

            {/* Search Box */}
            <div style={styles.searchBar}>
                <h2 style={styles.heading}>Company Analysis</h2>
                <p style={styles.subheading}>
                    Search by company name — no need to know the ticker symbol
                </p>

                {/* Search Input with Autocomplete */}
                <div ref={wrapperRef} style={styles.searchWrapper}>
                    <div style={styles.inputRow}>
                        <div style={styles.inputContainer}>
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => handleSearchInput(e.target.value)}
                                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                                placeholder="Search company name e.g. Apple, Tesla, JP Morgan..."
                                style={styles.input}
                                disabled={loading}
                            />
                            {searching && (
                                <span style={styles.searchingIndicator}>Searching...</span>
                            )}
                            {selectedTicker && (
                                <span style={styles.tickerBadge}>{selectedTicker}</span>
                            )}
                        </div>
                        <button
                            onClick={() => handleAnalyze()}
                            disabled={loading || (!selectedTicker && searchQuery.length < 2)}
                            style={{
                                ...styles.button,
                                opacity: loading || (!selectedTicker && searchQuery.length < 2) ? 0.5 : 1,
                                cursor: loading || (!selectedTicker && searchQuery.length < 2) ? 'not-allowed' : 'pointer'
                            }}
                        >
                            {loading ? 'Analyzing...' : 'Analyze'}
                        </button>
                    </div>

                    {/* Autocomplete Dropdown */}
                    {showSuggestions && suggestions.length > 0 && (
                        <div style={styles.dropdown}>
                            {suggestions.map((company, i) => (
                                <div
                                    key={i}
                                    style={styles.dropdownItem}
                                    onClick={() => handleSelectCompany(company)}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = '#0f3460';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = 'transparent';
                                    }}
                                >
                                    <div style={styles.dropdownLeft}>
                                        <span style={styles.dropdownTicker}>{company.ticker}</span>
                                        <span style={styles.dropdownName}>{company.name}</span>
                                    </div>
                                    <div style={styles.dropdownRight}>
                                        <span style={styles.dropdownType}>{company.type}</span>
                                        <span style={styles.dropdownRegion}>{company.region}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* No results message */}
                    {showSuggestions && suggestions.length === 0 && !searching && searchQuery.length >= 2 && (
                        <div style={styles.dropdown}>
                            <div style={styles.noResults}>
                                No publicly traded companies found for "{searchQuery}"
                                <br />
                                <span style={styles.noResultsSub}>
                                    Note: Private companies like OpenAI or McKinsey are not listed
                                </span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Popular Companies */}
                <div style={styles.popularSection}>
                    <span style={styles.popularLabel}>Popular:</span>
                    <div style={styles.popularChips}>
                        {popularCompanies.map(company => (
                            <button
                                key={company.ticker}
                                onClick={() => handleSelectCompany(company)}
                                style={styles.chip}
                                disabled={loading}
                                title={company.ticker}
                            >
                                {company.name}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div style={styles.error}>⚠️ {error}</div>
            )}

            {/* Loading */}
            {loading && (
                <LoadingSpinner message={`Analyzing ${selectedName || selectedTicker}...`} />
            )}

            {/* Results */}
            {!loading && (stockData || newsData || reportData) && (
                <div style={styles.results}>
                    <div style={styles.topRow}>
                        {stockData && <StockCard data={stockData} />}
                        {newsData && newsData.length > 0 && (
                            <div style={styles.newsSection}>
                                <h3 style={styles.sectionTitle}>📰 Latest News</h3>
                                <NewsCard articles={newsData} />
                            </div>
                        )}
                    </div>
                    {reportData && (
                        <div style={styles.reportSection}>
                            <h3 style={styles.sectionTitle}>📋 Financial Analysis Report</h3>
                            <ReportDisplay report={reportData} />
                        </div>
                    )}
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
    searchBar: {
        background: '#16213e',
        border: '1px solid #0f3460',
        borderRadius: '12px',
        padding: '32px',
        marginBottom: '32px',
    },
    heading: {
        color: '#e6f1ff',
        fontSize: '22px',
        fontWeight: '700',
        margin: '0 0 8px 0',
    },
    subheading: {
        color: '#8892b0',
        fontSize: '14px',
        margin: '0 0 24px 0',
    },
    searchWrapper: {
        position: 'relative',
        marginBottom: '20px',
    },
    inputRow: {
        display: 'flex',
        gap: '12px',
    },
    inputContainer: {
        flex: 1,
        position: 'relative',
    },
    input: {
        width: '100%',
        background: '#0d1b2a',
        border: '1px solid #0f3460',
        borderRadius: '8px',
        padding: '14px 16px',
        color: '#e6f1ff',
        fontSize: '15px',
        outline: 'none',
        boxSizing: 'border-box',
    },
    searchingIndicator: {
        position: 'absolute',
        right: '12px',
        top: '50%',
        transform: 'translateY(-50%)',
        color: '#8892b0',
        fontSize: '12px',
    },
    tickerBadge: {
        position: 'absolute',
        right: '12px',
        top: '50%',
        transform: 'translateY(-50%)',
        background: '#00d4aa22',
        color: '#00d4aa',
        border: '1px solid #00d4aa44',
        borderRadius: '12px',
        padding: '2px 10px',
        fontSize: '12px',
        fontWeight: '700',
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
    dropdown: {
        position: 'absolute',
        top: '100%',
        left: 0,
        right: 0,
        background: '#16213e',
        border: '1px solid #0f3460',
        borderRadius: '8px',
        marginTop: '4px',
        zIndex: 1000,
        boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        maxHeight: '320px',
        overflowY: 'auto',
    },
    dropdownItem: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '12px 16px',
        cursor: 'pointer',
        borderBottom: '1px solid #0f346022',
        transition: 'background 0.15s',
    },
    dropdownLeft: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
    },
    dropdownTicker: {
        color: '#00d4aa',
        fontSize: '14px',
        fontWeight: '700',
        minWidth: '60px',
        fontFamily: 'monospace',
    },
    dropdownName: {
        color: '#e6f1ff',
        fontSize: '14px',
    },
    dropdownRight: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-end',
        gap: '2px',
    },
    dropdownType: {
        color: '#8892b0',
        fontSize: '11px',
        textTransform: 'uppercase',
    },
    dropdownRegion: {
        color: '#8892b0',
        fontSize: '11px',
    },
    noResults: {
        padding: '20px',
        color: '#8892b0',
        fontSize: '14px',
        textAlign: 'center',
        lineHeight: '1.6',
    },
    noResultsSub: {
        fontSize: '12px',
        color: '#4a5568',
    },
    popularSection: {
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        flexWrap: 'wrap',
    },
    popularLabel: {
        color: '#8892b0',
        fontSize: '13px',
        paddingTop: '6px',
        whiteSpace: 'nowrap',
    },
    popularChips: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
    },
    chip: {
        background: '#0d1b2a',
        border: '1px solid #0f3460',
        borderRadius: '20px',
        padding: '6px 14px',
        color: '#ccd6f6',
        fontSize: '12px',
        cursor: 'pointer',
        transition: 'all 0.2s',
    },
    error: {
        background: '#FF980022',
        border: '1px solid #FF980044',
        borderRadius: '8px',
        padding: '16px',
        color: '#FF9800',
        marginBottom: '24px',
    },
    results: {
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
    },
    topRow: {
        display: 'flex',
        gap: '24px',
        flexWrap: 'wrap',
        alignItems: 'flex-start',
    },
    newsSection: {
        flex: 1,
        minWidth: '300px',
    },
    reportSection: {
        width: '100%',
    },
    sectionTitle: {
        color: '#ccd6f6',
        fontSize: '16px',
        fontWeight: '600',
        margin: '0 0 16px 0',
    },
};

export default Analysis;




