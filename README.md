# Machine Learning

A personal learning repo for machine learning, agentic AI, and computer science topics.
It holds small runnable Python experiments alongside long-form study notes.

## Contents

| Folder | What's inside |
| --- | --- |
| `Agentic-AI/Agent-With-Python/` | A simple Wikipedia research agent written two ways, both using Google Gemini |
| `LLD/` | Low-level design practice (for example, Python decorators in `decorators.py`) |
| `Computer-Science-Topics/` | Markdown study guides on Docker, containers, and Kubernetes |
| `src/machinelearning/` | Package stub created by `uv init` |

### Research agent

- `agent_using_langchain.py` uses LangChain's `create_agent` with Gemini and structured output.
- `agent_from_scratch.py` writes the same agent loop by hand with the `google-genai` SDK, so you can see what LangChain does for you.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) and Python 3.13 or newer.

```bash
uv sync
```

The agents need a Gemini API key. Put it in a `.env` file at the repo root (it is gitignored):

```
GOOGLE_API_KEY=your-key-here
```

## Usage

```bash
uv run python Agentic-AI/Agent-With-Python/agent_using_langchain.py
uv run python Agentic-AI/Agent-With-Python/agent_from_scratch.py
uv run python LLD/decorators.py
```
