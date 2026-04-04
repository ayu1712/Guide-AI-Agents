# Project 01 — ReAct Agent from Scratch

> *"A common mistake that people make when trying to design something completely foolproof is to underestimate the ingenuity of complete fools."*
> — Douglas Adams

This is the simplest possible AI agent that actually works. No frameworks, no magic — just Python, a local LLM, and the ReAct loop.

## What you'll learn

- What the **ReAct (Reasoning + Acting) loop** actually is under the hood
- How to give an LLM **tools** it can call
- How to **parse** the model's output and route it to the right function
- Why this feels hard, and why frameworks like LangGraph exist to make it easier

## The agent loop (visualised)

```
User Question
      │
      ▼
  ┌─────────┐
  │ Thought │  ← LLM reasons about what to do next
  └────┬────┘
       │
  ┌────▼────┐
  │  Action │  ← LLM picks a tool and an input
  └────┬────┘
       │
  ┌────▼──────────┐
  │  Observation  │  ← We run the tool and feed the result back
  └────┬──────────┘
       │
       └──► repeat until...
  ┌──────────────┐
  │ Final Answer │  ← LLM decides it has enough to answer
  └──────────────┘
```

## Tools in this agent

| Tool | What it does |
|------|-------------|
| `wikipedia_search` | Fetches the summary of a Wikipedia page |
| `calculator` | Evaluates a Python math expression safely |

## Setup

```bash
# 1. Install Ollama (free, runs locally)
#    → https://ollama.com

# 2. Pull the model (one-time, ~2GB)
ollama pull llama3.2

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run the agent
python agent.py
```

## Usage

```bash
# Interactive demo (pick from example questions)
python agent.py

# Pass your own question directly
python agent.py "What is the population of Berlin, and how many people is that per square kilometre?"
```

## Example output

```
━━━━━━━━━━━━━━━ Starting ReAct Agent ━━━━━━━━━━━━━━━
Question: What is the speed of light, and how many times could it
          circle the Earth in one second?

━━━━━━━━━━━━━━━ Step 1 ━━━━━━━━━━━━━━━
╭─ Thought ─────────────────────────────────╮
│ I need to find the speed of light and the │
│ circumference of the Earth, then divide.  │
╰───────────────────────────────────────────╯
Action:       wikipedia_search
Action Input: speed of light

╭─ Observation ─────────────────────────────────────────╮
│ [Wikipedia: Speed of light]                           │
│ The speed of light in vacuum is 299,792,458 metres... │
╰───────────────────────────────────────────────────────╯

━━━━━━━━━━━━━━━ Step 2 ━━━━━━━━━━━━━━━
Action:       calculator
Action Input: 299792458 / 40075000

╭─ Final Answer ────────────────────────────────────────╮
│ The speed of light is 299,792,458 m/s. Light could   │
│ circle the Earth approximately 7.5 times per second. │
╰───────────────────────────────────────────────────────╯
```

## How to add your own tool

Adding a new tool takes 5 lines:

```python
def my_tool(input: str) -> str:
    # do something with input
    return "result"

TOOLS["my_tool"] = {
    "fn": my_tool,
    "description": "What this tool does and what input it expects.",
}
```

That's it. The agent will automatically learn to use it from the system prompt.

## What's next

Once you understand this loop, the next projects build on it:

- **Project 02** — Same agent, now with LangGraph (see how a framework simplifies this)
- **Project 03** — Add memory so the agent remembers past conversations
- **Project 04** — Multi-agent: two agents collaborating on a task

---

*Part of [The Hitchhiker's Guide to AI Agents](../../README.md)*
