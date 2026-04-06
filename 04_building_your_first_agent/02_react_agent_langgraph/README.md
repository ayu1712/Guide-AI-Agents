# Project 02 - ReAct Agent with LangGraph

> *"I love deadlines. I love the whooshing noise they make as they go by."*
> - Douglas Adams

This is the same agent as [Project 01](../01_react_agent_from_scratch/). Same tools. Same job. Same model.

The only difference: we replaced ~150 lines of hand-rolled loop logic with LangGraph.

Read this project *after* Project 01. The whole point is the comparison.

---

## Before you read the code - understand the graph

In Project 01, the agent loop was a `for` loop you wrote yourself. In LangGraph, that same loop is expressed as a **directed graph** with nodes and edges.

```
                    ┌──────────────┐
                    │  START / Q   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
               ┌───►│  agent node  │───────────────────┐
               │    │  (LLM call)  │                   │
               │    └──────┬───────┘                   │
               │           │                           │
               │    wants to use a tool?               │
               │           │                           │
               │        ┌──▼──┐                     ┌──▼──┐
               │        │ YES │                     │ NO  │
               │        └──┬──┘                     └──┬──┘
               │           │                           │
               │    ┌──────▼───────┐                   │
               │    │  tools node  │                   │
               │    │ (runs tool,  │                   │
               │    │  returns     │                   │
               │    │  observation)│                   │
               │    └──────┬───────┘                   │
               │           │                           │
               └───────────┘                    ┌──────▼───────┐
                    loop                        │     END      │
                                                │ (final ans.) │
                                                └──────────────┘
```

That graph is exactly what `create_react_agent()` builds for you. Two nodes, three edges.

---

## The side-by-side comparison

### Defining tools

**Project 01 - manual**
```python
def wikipedia_search(query: str) -> str:
    """..."""
    ...

TOOLS = {
    "wikipedia_search": {
        "fn": wikipedia_search,
        "description": "Search Wikipedia for factual information...",
    }
}
```

**Project 02 - LangGraph**
```python
@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for factual information about a topic..."""
    ...

TOOLS = [wikipedia_search]
```

The `@tool` decorator reads the docstring as the description and auto-generates a JSON schema from the type hints. The LLM receives that schema so it knows exactly what arguments to pass.

---

### The agent loop

**Project 01 - manual (simplified)**
```python
for step in range(max_steps):
    response = llm(messages)
    thought, action, action_input = parse_action(response)  # regex!

    if action is None:
        return action_input  # final answer

    observation = TOOLS[action]["fn"](action_input)
    messages.append({"role": "assistant", "content": response})
    messages.append({"role": "user", "content": f"Observation: {observation}"})
```

**Project 02 - LangGraph**
```python
graph = create_react_agent(model=llm, tools=TOOLS, prompt="...")
result = graph.invoke({"messages": [HumanMessage(content=question)]})
```

That's it. The loop, the parser, the message history, the routing logic - all gone. LangGraph handles it.

---

### What you gave up to get that simplicity

Nothing for the common case. But when you need custom behaviour, you pay in configuration complexity instead of code:

| Need | Project 01 | Project 02 |
|------|-----------|-----------|
| Change max steps | `max_steps=8` in your loop | `create_react_agent(..., max_iterations=8)` |
| Custom stopping condition | `if my_condition: break` | Implement a custom `should_continue` edge |
| Inspect intermediate state | Print inside the loop | Stream with `graph.stream(..., stream_mode="updates")` |
| Human-in-the-loop pause | Add `input()` anywhere | `interrupt_before=["tools"]` + checkpointer |
| Persist state to disk | Pickle `messages` manually | Built-in `MemorySaver` checkpointer |

The pattern: **simple things are simpler in LangGraph. Complex things are more structured.** Neither is unconditionally better - it depends on what you're building.

---

## Setup

```bash
# Same Ollama model as Project 01 - no extra downloads needed
pip install -r requirements.txt
python agent.py
```

## Usage

```bash
# Interactive (picks from the same 3 demo questions as Project 01)
python agent.py

# Direct question
python agent.py "What is the population of Berlin and what is its area in square kilometres?"
```

## Try this experiment

Run both agents on the same question and compare:

```bash
# Terminal 1
cd ../01_react_agent_from_scratch
python agent.py "Who invented the World Wide Web, and what year was it proposed?"

# Terminal 2
cd ../02_react_agent_langgraph
python agent.py "Who invented the World Wide Web, and what year was it proposed?"
```

What to notice:
- The **reasoning steps** are the same - ReAct is ReAct, regardless of framework
- The **output display** looks similar - we replicated it intentionally
- The **code that produces it** is radically different in size and structure

---

## How LangGraph works under the hood

When you call `create_react_agent()`, LangGraph builds a `StateGraph` like this:

```python
# What LangGraph does internally (simplified)
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode

def call_model(state):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state):
    last = state["messages"][-1]
    if last.tool_calls:
        return "tools"   # route to tool execution
    return END           # route to finish

graph = StateGraph(MessagesState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")   # always loop back
```

`create_react_agent()` is just a convenience wrapper around exactly this. In Project 04 (multi-agent), you'll write this graph yourself - because that's when you need full control over the nodes and routing.

---

## What's next

- **Project 03** - Add memory: same agent, but it remembers previous conversations using LangGraph's built-in checkpointer
- **Project 04** - Multi-agent: build a supervisor + two specialist agents using the graph primitives directly

---

*Part of [The Hitchhiker's Guide to AI Agents](../../README.md)*
