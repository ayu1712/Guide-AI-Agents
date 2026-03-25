# 🔧 No Framework

> "The best framework is the one you don't need."

Before reaching for LangGraph or CrewAI, ask yourself: do I actually need a framework? A staggering number of "agent" use cases are just a while loop around an API call. That's not a bad thing. That's clarity.

This section shows you how to build a working agent from scratch — no dependencies beyond your LLM SDK — and when that's the right call.

---

## The Core Idea

An agent loop is:

1. Get input
2. Ask the LLM what to do
3. If it wants to call a tool → call the tool → go to step 2
4. If it's done → return the output

That's it. You don't need a library for that. You need a loop, a tool dispatcher, and a message history list.

```python
messages = [{"role": "user", "content": user_input}]

while True:
    response = llm.call(messages, tools=available_tools)
    
    if response.has_tool_calls:
        tool_results = execute_tools(response.tool_calls)
        messages.append(response)
        messages.append(tool_results)
    else:
        return response.content   # Done
```

---

## When No Framework Wins

**Use the raw approach when:**

- **You have one agent with a few tools** — adding a framework adds complexity without benefit
- **You need full control** — no magic, no hidden prompts, no framework-injected system messages
- **You're learning** — building your own loop teaches you exactly how agents work; frameworks hide that
- **You're building something custom** — if your requirements don't fit the framework's model, you'll fight it constantly
- **Startup speed matters** — one file, no install, no versioning conflicts

The uncomfortable truth: the framework matters far less than most developers think. What will determine if an agent is reliable or not is the infrastructure around it — state persistence, how to handle retries, how to deploy and monitor it. A raw agent with good infrastructure beats a fancy framework with poor infrastructure every time.

---

## Quickstart

See [`quickstart.py`](./quickstart.py) for a complete agent loop from scratch — no frameworks, ~70 lines of plain Python.

Install:
```bash
pip install anthropic   # or openai — pick your LLM
```

---

## What You Give Up (and How to Add It Back)

| Framework feature | DIY equivalent |
|---|---|
| State management | A dict or dataclass you pass around |
| Tool dispatch | A simple `if/elif` or `match` on tool name |
| Memory | Append to a list; slice when too long |
| Checkpointing | `json.dump(state, f)` to a file |
| Observability | `logging.info(...)` around each step |
| Retries | `try/except` with `time.sleep(backoff)` |
| Multi-agent | Call another function that runs the same loop |

None of these require a framework. They require five minutes.

---

## When to Graduate to a Framework

Add a framework when the raw approach starts hurting:

- **The control flow is getting complex** — lots of conditional branches, parallel calls → LangGraph
- **You have 3+ agents coordinating** — their interactions are getting hard to manage manually → CrewAI or AutoGen
- **You need production observability** — tracing, replay, monitoring → LangSmith / LangGraph
- **State is becoming a mess** — shared mutable state between agents is a nightmare to debug manually → any framework with explicit state

The rule: **start raw, add scaffolding when the pain is real, not anticipated.**

---

## The One Thing to Remember

A framework is a trade: you give up flexibility and transparency in exchange for structure and solved problems. That trade is worth it at a certain scale and complexity. It is not worth it at the start.

Build the simplest thing. Feel the pain points. Let them guide which framework, if any, you actually need.
