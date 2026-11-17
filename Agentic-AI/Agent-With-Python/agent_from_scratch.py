"""
The same research agent as main.py, but WITHOUT LangChain.

Here we write the agent loop ourselves using only Google's Gemini SDK
(google-genai), so you can see exactly what `create_agent` was doing behind
the scenes.

The whole idea fits in a few lines:

    messages = [user question]
    while True:
        response = ask the model(messages, tools)
        if the model didn't ask for a tool:  -> done, print the answer
        else: run the tool(s), append the results to messages, loop again

Run it:
    uv run python Agentic-AI/Agent-With-Python/agent_from_scratch.py
Needs GOOGLE_API_KEY in your environment or in a .env file.
"""

import json
from datetime import datetime

import wikipedia
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()  # reads GOOGLE_API_KEY from the environment
MODEL = "gemini-3.7-flash"
MAX_TURNS = 1  # safety limit so a confused agent can't loop forever


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


GEMINI_TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters_json_schema=t["input_schema"],
            )
            for t in TOOLS
        ]
    )
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
    # Settings that stay the same every turn: system prompt, tools, output limit.
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=GEMINI_TOOLS,
        max_output_tokens=16000,
    )

    # The conversation so far. The API is stateless: we resend ALL of it every turn.
    # Gemini calls each message a "Content", made of one or more "Part"s.
    messages = [types.Content(role="user", parts=[types.Part(text=question)])]

    for turn in range(1, MAX_TURNS + 1):
        print(f"\n--- Turn {turn}: asking Gemini ---")

        # (a) Ask Gemini what to do next.
        response = client.models.generate_content(
            model=MODEL,
            contents=messages,
            config=config,
        )

        # No candidates means Gemini blocked the whole prompt (e.g. for safety).
        if not response.candidates or response.candidates[0].content is None:
            return f"Gemini returned no answer (finish reason: {response.candidates[0].finish_reason if response.candidates else 'blocked'})."

        # (b) Save Gemini's reply into the history. Append the WHOLE Content
        #     (role="model"), not just the text: it carries hidden "thought
        #     signatures" that Gemini needs to see again on the next turn.
        messages.append(response.candidates[0].content)

        # (c) Did Gemini ask for a tool? Gemini has no "tool_use" stop reason -
        #     finish_reason is STOP either way - so we check for function calls.
        if not response.function_calls:
            # No tool requested -> Gemini is done.
            return response.text or "Gemini finished without any text."

        # (d) Gemini asked for one or more tools. Run each one.
        result_parts = []
        for call in response.function_calls:
            args = dict(call.args or {})
            print(f"[model -> tool] {call.name}({json.dumps(args)})")

            func = TOOL_FUNCTIONS.get(call.name)
            if func is None:
                output = f"Error: unknown tool '{call.name}'"
            else:
                try:
                    output = func(**args)
                except Exception as e:
                    output = f"Error: tool crashed: {e}"

            print(f"[tool -> model] {output[:150]}...")

            # Gemini wants the result as a dictionary, matched to the call by name.
            # (There's no is_error flag - an error is just described in the text.)
            result_parts.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={"result": output},
                )
            )

        # (e) Send ALL the results back in ONE message, then loop again.
        messages.append(types.Content(role="user", parts=result_parts))

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
