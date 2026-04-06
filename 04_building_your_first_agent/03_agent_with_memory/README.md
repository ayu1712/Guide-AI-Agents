# Project 03 — Agent with Memory

> *"I may not have gone where I intended to go, but I think I have ended up where I needed to be."*
> — Douglas Adams

This is the same agent as [Project 02](../02_react_agent_langgraph/). Same tools. Same model. Same graph structure.

The new concept: **memory**. The agent now remembers what you talked about — both within a conversation and across restarts.

Read Projects 01 and 02 first. This builds directly on them.

---

## The problem memory solves

Run the Project 02 agent and ask it two questions:

```
You: Who is Tim Berners-Lee?
Agent: Tim Berners-Lee is a British computer scientist who invented...

You: What year was he born?
Agent: I'm sorry, I don't know who you're referring to.
```

Every turn in Project 02 is stateless. The agent has no idea what "he" refers to because it never saw the previous exchange. Each `graph.stream()` call starts from zero.

Project 03 fixes this at both timescales:

| Timescale | Project 02 | Project 03 |
|-----------|-----------|-----------|
| Within a conversation | ❌ Forgets each turn | ✅ Remembers full history |
| Across restarts | ❌ Fresh start every time | ✅ Resumes from disk |

---

## The mechanism: checkpointers

A **checkpointer** is an object you attach to a LangGraph graph. After every node execution, it serialises the entire graph state and writes it to a storage backend. On the next turn, it reads the state back using a **thread ID** as the lookup key.

```
Turn 1                          Turn 2
──────                          ──────
graph.stream(Q1, thread="a")    graph.stream(Q2, thread="a")
       │                                │
       │ state after turn 1             │ reads state from turn 1
       └──────────────────► SQLite ────►┘
                              memory.db
```

The thread ID is what separates conversations. Same ID = same memory. New ID = fresh start.

---

## The diff from Project 02

This is the entire change. Everything else — tools, prompt, streaming display — is identical.

```python
# Project 02
graph = create_react_agent(
    model=llm,
    tools=TOOLS,
    prompt="...",
)

# Project 03
conn = sqlite3.connect("memory.db")
checkpointer = SqliteSaver(conn)

graph = create_react_agent(
    model=llm,
    tools=TOOLS,
    prompt="...",
    checkpointer=checkpointer,   # ← this line
)
```

And when running:

```python
# Project 02
graph.stream({"messages": [HumanMessage(question)]})

# Project 03
config = {"configurable": {"thread_id": "my-conversation"}}
graph.stream({"messages": [HumanMessage(question)]}, config=config)
```

That's it. Two additions — one argument at build time, one config at run time — and the agent gains persistent memory across turns and restarts.

---

## What the SQLite file contains

After a conversation, `memory.db` is created in the project directory. It stores the full message history as serialised JSON — every `HumanMessage`, `AIMessage`, and `ToolMessage` from every turn of every thread.

You can inspect it:

```bash
sqlite3 memory.db
sqlite> .tables
sqlite> SELECT thread_id, checkpoint_id FROM checkpoints;
sqlite> SELECT COUNT(*) FROM writes;
```

Or just type `memory` during a session to see a live summary.

---

## Setup

```bash
pip install -r requirements.txt

# Uses the same model as Projects 01 and 02 — no extra downloads
python agent.py
```

## Usage

```bash
# Interactive — asks you for a thread ID at startup
python agent.py

# Pass a thread ID directly to resume a specific conversation
python agent.py my-research-session
python agent.py default
```

## Try this experiment

This is the experiment that makes the memory concrete:

```
# Run 1
python agent.py experiment

You: Tell me about the Roman Empire
Agent: [answers]

You: What was its population at its peak?
Agent: [answers — it remembers "Roman Empire" from the previous question]

# Exit (Ctrl+C or type quit)

# Run 2 — same thread ID
python agent.py experiment

# Agent shows: "Resuming conversation — X messages loaded from memory"
You: What city was its capital?
Agent: [answers — it still remembers "Roman Empire" from Run 1]
```

Then try with a *different* thread ID:

```
python agent.py fresh-start
You: What city was its capital?
Agent: [has no idea what you're referring to — clean slate]
```

---

## Two kinds of memory — and what this project doesn't cover

The memory in this project is **verbatim conversation history** — every message stored and replayed. This works well for short conversations but has a ceiling: context windows are finite. A very long conversation will eventually overflow the model's context.

Production agents handle this with additional memory strategies not covered here:

| Strategy | How it works | When to use |
|----------|-------------|-------------|
| **Windowing** | Keep only the last N messages | When recency matters more than full history |
| **Summarisation** | Compress old turns into a summary | Long-running conversations |
| **Semantic memory** | Store facts in a vector DB, retrieve relevant ones | When the agent needs to recall specific facts across many sessions |
| **Entity memory** | Track known entities (people, places, topics) explicitly | Assistants that build a model of the user over time |

Project 03 is the foundation. Those strategies are layers on top of it.

---

## What's next

- **Project 04** — Multi-agent: a supervisor that delegates tasks to specialist sub-agents, using the same graph primitives you've now seen in three projects

---

*Part of [The Hitchhiker's Guide to AI Agents](../../README.md)*
