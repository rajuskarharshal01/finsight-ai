import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from backend.agents.prompts import SYSTEM_PROMPT
from backend.tools.stock_tool import (get_stock_price, get_stock_history, get_financial_statements) 
from backend.tools.news_tool import (get_company_news, search_financial_news)
from backend.tools.sec_tool import (get_company_facts, get_sec_filings)
from backend.tools.rag_tool import (search_knowledge_base, search_knowledge_base_by_ticker, store_financial_insight)

load_dotenv()


# ============================================================
# TOOL REGISTRY
# ============================================================

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


# ============================================================
# LLM
# ============================================================

def get_llm():

    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )


# ============================================================
# AGENT FACTORY
# ============================================================

def create_financial_agent():

    llm = get_llm()

    agent = create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


# ============================================================
# FINANCIAL RESEARCH AGENT
# ============================================================

class FinancialResearchAgent:
    """
    High-level wrapper around the LangChain financial agent.

    This class provides a clean interface for FastAPI,
    tests, and other application components.
    """

    def __init__(self):

        self.agent = create_financial_agent()

        self.chat_history: List = []

        print("FinSight Research Agent initialized")


    def research(self, query: str) -> Dict[str, Any]:
        """
        Run a financial research query through the LangGraph agent.

        Args:
            query: Natural language financial research question.

        Returns:
            Dict containing:
            - query: original question
            - answer: final agent response
            - steps: tools called
            - tools_used: tool names
        """
        try:
            print(f"\n{'=' * 60}")
            print(f"Query: {query}")
            print(f"{'=' * 60}")

            # Build message history using plain dictionaries.
            # No HumanMessage / AIMessage required.
            messages = list(self.chat_history)
            messages.append({
                "role": "user",
                "content": query
            })

            # Invoke LangGraph agent
            result = self.agent.invoke({
                "messages": messages
            })

            # Get the final assistant message
            final_message = result["messages"][-1]

            # Gemini 3.5 may return content as:
            # [{'type': 'text', 'text': '...'}]
            content = final_message.content

            if isinstance(content, list):
                text_parts = []

                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))

                answer = "\n".join(text_parts).strip()

            else:
                answer = str(content)

            # Extract tool usage
            steps = []

            for message in result["messages"]:
                tool_calls = getattr(message, "tool_calls", None)

                if tool_calls:
                    for tool_call in tool_calls:
                        steps.append({
                            "tool": tool_call.get("name"),
                            "input": tool_call.get("args", {})
                        })

            # Store history as plain dictionaries
            self.chat_history.append({
                "role": "user",
                "content": query
            })

            self.chat_history.append({
                "role": "assistant",
                "content": answer
            })

            return {
                "query": query,
                "answer": answer,
                "steps": steps,
                "tools_used": [
                    step["tool"]
                    for step in steps
                ]
            }

        except Exception as e:
            import traceback
            traceback.print_exc()

            return {
                "query": query,
                "answer": f"Research failed: {str(e)}",
                "steps": [],
                "tools_used": []
            }


    def clear_history(self):
        """
        Clear conversation history.
        """

        self.chat_history = []

        print("Chat history cleared")


# ============================================================
# SINGLETON
# ============================================================

_agent_instance = None


def get_agent() -> FinancialResearchAgent:
    """
    Return singleton FinancialResearchAgent instance.
    """

    global _agent_instance

    if _agent_instance is None:

        _agent_instance = FinancialResearchAgent()

    return _agent_instance