import axios from 'axios';

// In Docker: requests go through nginx proxy at /api/
// In development: requests go directly to localhost:8000
const API_BASE = import.meta.env.PROD
    ? '/api'
    : 'http://localhost:8000';

const client = axios.create({
    baseURL: API_BASE,
    timeout: 60000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    checkHealth: () =>
        client.get('/health'),
    askAgent: (query, ticker = null) =>
        client.post('/ask-research-agent', { query, ticker }),
    getStock: (ticker) =>
        client.get(`/stock/${ticker}`),
    getStockHistory: (ticker, period = '3mo') =>
        client.get(`/stock/${ticker}/history?period=${period}`),
    getNews: (ticker) =>
        client.get(`/news/${ticker}`),
    searchNews: (query, maxResults = 5) =>
        client.get(`/news/search/${query}?max_results=${maxResults}`),
    analyzeCompany: (ticker) =>
        client.post('/company-analysis', { ticker }),
    getReport: (ticker) =>
        client.get(`/report/${ticker}`),
    getSecFilings: (ticker, filingType = '10-K') =>
        client.get(`/sec/${ticker}?filing_type=${filingType}`),
    searchKnowledge: (query, k = 4) =>
        client.post('/knowledge/search', { query, k }),
    searchCompany: (query) =>
        client.get(`/search-company?q=${encodeURIComponent(query)}`),
};

export default client;