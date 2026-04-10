import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any

from backend.agents.prompts import get_agent_prompt
from backend.tools.stock_tool import (
    get_stock_price,
    get_stock_history,
    get_financial_statements
)
from backend.tools.news_tool import (
    get_company_news,
    search_financial_news
)
from backend.tools.sec_tool import (
    get_company_facts,
    get_sec_filings
)
from backend.tools.rag_tool import (
    search_knowledge_base,
    search_knowledge_base_by_ticker,
    store_financial_insight
)

load_dotenv()


# ── Tool Registry ──────────────────────────────────────────────
# All tools the agent can use — listed in order of importance.
# The agent reads each tool's docstring to know when to use it.

ALL_TOOLS = [
    get_stock_price,
    get_stock_history,
    get_financial_statements,
    get_company_news,
    search_financial_news,
    get_company_facts,
    get_sec_filings,
    search_knowledge_base,
    search_knowledge_base_by_ticker,
    store_financial_insight,
]


# ── LLM Setup ──────────────────────────────────────────────────

def get_llm():
    """
    Create and return the Gemini LLM.

    gemini-2.0-flash-lite is used because:
    - Fast response times
    - Good reasoning capability
    - Supports tool/function calling natively
    - Cost effective for development

    temperature=0 means deterministic output —
    the agent will give consistent answers for the same question.
    For creative tasks you'd use higher temperature (0.7-1.0)
    but for financial analysis we want factual consistency.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )


# ── Agent Factory ──────────────────────────────────────────────

def create_agent() -> AgentExecutor:
    """
    Create and return the complete LangChain agent.

    Three components combine to make the agent:

    1. LLM (Gemini) — the brain that reasons and decides
    2. Tools — the hands that fetch real data
    3. Prompt — the personality and instructions

    create_tool_calling_agent() connects these three.
    It's specifically designed for LLMs that support
    native function/tool calling (like Gemini and GPT-4).

    AgentExecutor wraps the agent and handles:
    - The Thought/Action/Observation loop
    - Error handling when tools fail
    - Limiting iterations to prevent infinite loops
    - Verbose logging so we can see the agent's thinking
    """
    llm = get_llm()
    prompt = get_agent_prompt()

    # Create the agent — connects LLM + tools + prompt
    agent = create_tool_calling_agent(
        llm=llm,
        tools=ALL_TOOLS,
        prompt=prompt
    )

    # Wrap in executor which runs the ReAct loop
    executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,           # prints agent's thinking process
        max_iterations=10,      # prevents infinite loops
        handle_parsing_errors=True,  # graceful error recovery
        return_intermediate_steps=True  # returns tool call history
    )

    return executor


# ── Research Agent Class ───────────────────────────────────────

class FinancialResearchAgent:
    """
    High-level wrapper around the LangChain agent.

    This class provides a clean interface for the rest of
    the system (FastAPI, tests) to interact with the agent
    without knowing LangChain internals.

    It also manages conversation history so the agent
    remembers context within a session.
    """

    def __init__(self):
        self.agent = create_agent()
        self.chat_history: List = []
        print("✅ FinSight Research Agent initialized")

    def research(self, query: str) -> Dict[str, Any]:
        """
        Run a financial research query through the agent.

        The agent will:
        1. Read the query
        2. Decide which tools to call
        3. Call tools and read results
        4. Reason about the results
        5. Generate a structured response

        Args:
            query: Natural language financial research question

        Returns:
            Dict with:
            - answer: the agent's final response
            - steps: list of tools called and their results
            - query: the original question
        """
        try:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"{'='*60}")

            result = self.agent.invoke({
                "input": query,
                "chat_history": self.chat_history
            })

            # Extract the answer
            answer = result.get("output", "No response generated")

            # Extract intermediate steps (tool calls)
            steps = []
            for action, observation in result.get("intermediate_steps", []):
                steps.append({
                    "tool": action.tool,
                    "input": action.tool_input,
                    "output": str(observation)[:200]  # truncate for readability
                })

            # Update conversation history for next turn
            self.chat_history.append(HumanMessage(content=query))
            self.chat_history.append(AIMessage(content=answer))

            return {
                "query": query,
                "answer": answer,
                "steps": steps,
                "tools_used": [s["tool"] for s in steps]
            }

        except Exception as e:
            return {
                "query": query,
                "answer": f"Research failed: {str(e)}",
                "steps": [],
                "tools_used": []
            }

    def clear_history(self):
        """Clear conversation history to start fresh session"""
        self.chat_history = []
        print("Chat history cleared")


# ── Singleton Pattern ──────────────────────────────────────────
# We create one agent instance and reuse it.
# Creating a new agent for every request is wasteful —
# it reloads all tools and reconnects to the LLM each time.

_agent_instance = None

def get_agent() -> FinancialResearchAgent:
    """
    Return the singleton agent instance.
    Creates it on first call, reuses on subsequent calls.
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = FinancialResearchAgent()
    return _agent_instance