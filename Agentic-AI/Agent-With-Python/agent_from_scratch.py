"""
The same research agent as main.py, but WITHOUT LangChain.

Here we write the agent loop ourselves using only the Anthropic SDK, so you can
see exactly what `create_agent` was doing behind the scenes.

The whole idea fits in a few lines:

    messages = [user question]
    while True:
        response = ask Claude(messages, tools)
        if Claude didn't ask for a tool:  -> done, print the answer
        else: run the tool(s), append the results to messages, loop again

Run it:
    uv run python Agentic-AI/Agent-With-Python/agent_from_scratch.py
Needs ANTHROPIC_API_KEY in your environment or in a .env file.
"""

import json
from datetime import datetime

import anthropic
import wikipedia
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = "claude-opus-5-5"
MAX_TURNS = 10  # safety limit so a confused agent can't loop forever


# ---------------------------------------------------------------------------
# 1. THE TOOL FUNCTIONS
# Plain Python. Nothing special about them - Claude never runs these itself.
# Claude only *asks* us to run them; our loop does the actual calling.
# ---------------------------------------------------------------------------

def search_wikipedia(query: str) -> str:
    try:
        return wikipedia.summary(query, sentences=5, auto_suggest=False)
    except wikipedia.DisambiguationError as e:
        return f"Ambiguous query. Try one of: {e.options[:5]}"
    except wikipedia.PageError:
        return f"No Wikipedia page found for '{query}'."


def calculator(expression: str) -> str:
    if not set(expression) <= set("0123456789+-*/(). "):
        return "Error: only numbers and + - * / ( ) are allowed."
    try:
        return str(eval(expression))  # characters are whitelisted above
    except Exception as e:
        return f"Error: {e}"


def save_notes(text: str) -> str:
    with open("research_notes.txt", "a") as f:
        f.write(f"--- {datetime.now():%Y-%m-%d %H:%M} ---\n{text}\n\n")
    return "Saved to research_notes.txt"


# A lookup table: tool name (what Claude says) -> Python function (what we run)
TOOL_FUNCTIONS = {
    "search_wikipedia": search_wikipedia,
    "calculator": calculator,
    "save_notes": save_notes,
}


# ---------------------------------------------------------------------------
# 2. THE TOOL DESCRIPTIONS (what Claude sees)
# LangChain's @tool built these for you from the function signature and
# docstring. Without LangChain we write the JSON Schema by hand.
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "search_wikipedia",
        "description": "Search Wikipedia and return a short summary of the best-matching "
                       "article. Use this for facts about people, places, events, and concepts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression, e.g. '2026 - 1969'. "
                       "Only numbers and + - * / ( ) . are allowed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "The math expression"},
            },
            "required": ["expression"],
        },
    },
    {
        "name": "save_notes",
        "description": "Append research notes to research_notes.txt. "
                       "Only use this when the user asks to save results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The notes to save"},
            },
            "required": ["text"],
        },
    },
]

SYSTEM_PROMPT = (
    "You are a helpful research assistant. "
    "Use tools to look up facts instead of guessing, and use the calculator for math. "
    "Only save notes if the user asks you to. "
    "End with a short final answer and list your sources."
)


# ---------------------------------------------------------------------------
# 3. THE AGENT LOOP  <- this is the important part
# ---------------------------------------------------------------------------

def run_agent(question: str) -> str:
    # The conversation so far. The API is stateless: we resend ALL of it every turn.
    messages = [{"role": "user", "content": question}]

    for turn in range(1, MAX_TURNS + 1):
        print(f"\n--- Turn {turn}: asking Claude ---")

        # (a) Ask Claude what to do next.
        #     `fallbacks="default"`: if Claude Opus 5.5 declines a request for safety
        #     reasons, the API automatically retries it on a fallback model.
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )

        # (b) Save Claude's reply into the history. We append the WHOLE content
        #     list (text + tool calls + thinking), not just the text, so Claude
        #     remembers exactly what it asked for.
        messages.append({"role": "assistant", "content": response.content})

        # (c) Why did Claude stop talking? This decides what we do next.
        if response.stop_reason == "end_turn":
            # No tool requested -> Claude is done. Collect its text and return it.
            return "".join(b.text for b in response.content if b.type == "text")

        if response.stop_reason == "refusal":
            return "Claude declined to answer this request."

        if response.stop_reason == "max_tokens":
            return "Ran out of output tokens before finishing."

        if response.stop_reason != "tool_use":
            return f"Stopped unexpectedly: {response.stop_reason}"

        # (d) Claude asked for one or more tools. Run each one.
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue  # skip text / thinking blocks

            print(f"[model -> tool] {block.name}({json.dumps(block.input)})")

            func = TOOL_FUNCTIONS.get(block.name)
            if func is None:
                output, is_error = f"Unknown tool: {block.name}", True
            else:
                try:
                    output, is_error = func(**block.input), False
                except Exception as e:
                    output, is_error = f"Tool crashed: {e}", True

            print(f"[tool -> model] {output[:150]}...")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,  # links this result to the request it answers
                "content": output,
                "is_error": is_error,     # tells Claude the tool failed so it can adapt
            })

        # (e) Send ALL the results back in ONE user message, then loop again.
        messages.append({"role": "user", "content": tool_results})

    return f"Gave up after {MAX_TURNS} turns."


# ---------------------------------------------------------------------------
# 4. RUN IT
# ---------------------------------------------------------------------------

def main() -> None:
    question = input("What do you want to research? ")
    answer = run_agent(question)
    print("\n===== Final answer =====")
    print(answer)


if __name__ == "__main__":
    main()
