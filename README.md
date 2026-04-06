# FinSight AI — Financial Research Agent

An agentic AI system that autonomously researches companies, analyzes 
financial data, and generates structured investment research reports.

## What It Does

Ask any financial question in natural language:
- *"Analyze Tesla's financial performance"*
- *"What are Apple's risk factors?"*
- *"Compare NVIDIA vs AMD"*

The AI agent autonomously fetches real stock data, news, SEC filings,
computes financial ratios, and generates a structured research report.

## Tech Stack

| Layer | Technology |
|---|---|
| AI Framework | LangChain + Gemini 2.0 |
| Backend | FastAPI + Python 3.11 |
| Frontend | React + Vite |
| Database | PostgreSQL + pgvector |
| Financial Data | Twelve Data API |
| Deployment | Docker + Render + Vercel |

## Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/finsight-ai.git
cd finsight-ai
cp .env.example .env
# Edit .env with your API keys
docker-compose up --build
```

Open http://localhost in your browser.

## Project built in 11 phases — see commit history for full progression.