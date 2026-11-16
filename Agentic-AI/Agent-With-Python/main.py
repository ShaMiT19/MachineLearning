"""
A simple research agent built with LangChain + Claude.

WHAT IS AN AGENT?
-----------------
A plain LLM call is: prompt in -> text out.
An *agent* is an LLM running in a loop with access to TOOLS:

    1. You send the model a question + a list of tools it may use.
    2. The model either answers directly, OR replies "please call tool X with args Y".
    3. Your code runs the tool and sends the result back to the model.
    4. Repeat steps 2-3 until the model decides it has enough info to answer.

LangChain's `create_agent` runs that loop for you. Your job is to:
    - pick a model
    - write tools (plain Python functions with good docstrings)
    - write a system prompt
    - (optionally) define the shape of the final answer

Run it:
    uv run python Agentic-AI/Agent-With-Python/main.py
Needs ANTHROPIC_API_KEY in your environment or in a .env file.
"""

from datetime import datetime

import wikipedia
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from pydantic import BaseModel, Field

load_dotenv()  # reads ANTHROPIC_API_KEY from a .env file if present


# ---------------------------------------------------------------------------
# 1. TOOLS
# The @tool decorator turns a function into something the model can call.
# The model sees the function NAME, the DOCSTRING, and the ARGUMENT TYPES,
# so write the docstring as instructions for the model.
# ---------------------------------------------------------------------------

@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia and return a short summary of the best-matching article.
    Use this for facts about people, places, events, and concepts."""
    try:
        return wikipedia.summary(query, sentences=5, auto_suggest=False)
    except wikipedia.DisambiguationError as e:
        return f"Ambiguous query. Try one of: {e.options[:5]}"
    except wikipedia.PageError:
        return f"No Wikipedia page found for '{query}'."


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '2026 - 1969' or '3.5 * 12'.
    Only numbers and + - * / ( ) . are allowed."""
    if not set(expression) <= set("0123456789+-*/(). "):
        return "Error: only numbers and + - * / ( ) are allowed."
    try:
        return str(eval(expression))  # safe-ish: we whitelisted the characters
    except Exception as e:
        return f"Error: {e}"


@tool
def save_notes(text: str) -> str:
    """Append research notes to research_notes.txt. Use this when the user asks to save results."""
    with open("research_notes.txt", "a") as f:
        f.write(f"--- {datetime.now():%Y-%m-%d %H:%M} ---\n{text}\n\n")
    return "Saved to research_notes.txt"


# ---------------------------------------------------------------------------
# 2. STRUCTURED OUTPUT (optional)
# Instead of free text, we ask the agent to return data in this exact shape.
# That makes the result easy to use from code.
# ---------------------------------------------------------------------------

class ResearchAnswer(BaseModel):
    topic: str = Field(description="The topic that was researched")
    summary: str = Field(description="A clear answer to the user's question")
    sources: list[str] = Field(description="Where the information came from")
    tools_used: list[str] = Field(description="Names of the tools that were called")


# ---------------------------------------------------------------------------
# 3. BUILD THE AGENT
# ---------------------------------------------------------------------------

agent = create_agent(
    model="anthropic:claude-sonnet-5-5",
    tools=[search_wikipedia, calculator, save_notes],
    system_prompt=(
        "You are a helpful research assistant. "
        "Use tools to look up facts instead of guessing, and use the calculator for math. "
        "Only save notes if the user asks you to."
    ),
    response_format=ResearchAnswer,
)


# ---------------------------------------------------------------------------
# 4. RUN IT
# ---------------------------------------------------------------------------

def main() -> None:
    question = input("What do you want to research? ")

    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    # Peek inside the loop: every message the agent exchanged, including tool calls.
    print("\n===== What the agent did =====")
    for msg in result["messages"]:
        if getattr(msg, "tool_calls", None):
            for call in msg.tool_calls:
                print(f"[model -> tool] {call['name']}({call['args']})")
        elif msg.type == "tool":
            print(f"[tool -> model] {msg.content[:150]}...")

    answer: ResearchAnswer = result["structured_response"]
    print("\n===== Final answer =====")
    print(f"Topic:   {answer.topic}")
    print(f"Summary: {answer.summary}")
    print(f"Sources: {', '.join(answer.sources)}")
    print(f"Tools:   {', '.join(answer.tools_used)}")


if __name__ == "__main__":
    main()
