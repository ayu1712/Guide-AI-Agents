# LangGraph — Core Concepts

A deep dive into the building blocks. Read this after the quickstart, when you want to understand *why* things work the way they do.

---

## The Mental Model

LangGraph treats your agent as a **state machine**. State machines are everywhere — traffic lights, vending machines, TCP connections. They work because:

- There's a finite set of states the system can be in
- Transitions between states are explicit and controlled
- The current state determines what actions are valid

Your agent is no different. It's in one of a handful of states at any time: gathering context, reasoning, calling a tool, waiting for human input, done. LangGraph makes you write that down explicitly. That explicitness is the whole point.

---

## State

State is the single shared object that flows through your entire graph. Every node reads from it and writes to it. Think of it as your agent's working memory for a given run.

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # Conversation history
    plan: str                                  # Current plan
    steps_taken: int                          # Counter
    final_answer: str                         # Where we store the result
```

### Reducers

Notice `Annotated[list, add_messages]` on the messages field. That `add_messages` is a **reducer** — it tells LangGraph how to merge updates to that field.

By default, returning `{"messages": new_message}` from a node would *replace* the whole messages list. The `add_messages` reducer changes that: it *appends* instead of replacing.

You can write your own reducers for custom merge logic:

```python
def keep_latest(existing: str, new: str) -> str:
    return new  # Default behaviour — just replace

def accumulate(existing: list, new: list) -> list:
    return existing + new  # Append behaviour

class State(TypedDict):
    logs: Annotated[list, accumulate]
```

---

## Nodes

Nodes are just Python functions. They take the current state, do something, and return a partial update to state. LangGraph merges the update back in.

```python
def my_node(state: AgentState) -> dict:
    # Read from state
    last_message = state["messages"][-1]
    
    # Do something
    result = some_computation(last_message)
    
    # Return ONLY what changed — not the whole state
    return {"steps_taken": state["steps_taken"] + 1, "plan": result}
```

Key rule: **return only the fields you changed**. LangGraph handles the merge.

### Async Nodes

Nodes can be async — useful for parallel tool calls or non-blocking I/O:

```python
async def async_node(state: AgentState) -> dict:
    result = await some_async_api_call()
    return {"messages": [result]}
```

---

## Edges

Edges define how the graph flows from node to node.

### Static Edges

Always go from A to B:

```python
graph.add_edge("node_a", "node_b")
graph.add_edge(START, "first_node")    # Entry point
graph.add_edge("last_node", END)       # Exit point
```

### Conditional Edges

Go to B or C depending on state. This is where the intelligence lives:

```python
def route(state: AgentState) -> str:
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"   # LLM wants to use a tool
    else:
        return "end"     # LLM is done

graph.add_conditional_edges(
    "llm_node",          # From this node
    route,               # Call this function to decide
    {
        "tools": "tool_node",   # If route() returns "tools" → go here
        "end": END,             # If route() returns "end" → finish
    }
)
```

The routing function receives the current state and returns a string key. That key maps to the next node.

---

## The Graph Builder

You construct the graph with a `StateGraph`, then compile it:

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(AgentState)

# Add nodes
builder.add_node("llm", call_llm)
builder.add_node("tools", run_tools)

# Add edges
builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", route, {"tools": "tools", "end": END})
builder.add_edge("tools", "llm")   # After tools, always back to LLM

# Compile validates the graph and returns a runnable
graph = builder.compile()
```

Compilation validates that:
- Every node has at least one outgoing edge (no dead ends)
- Every edge target exists
- The graph has a valid entry point

---

## Checkpointing

Checkpointing is LangGraph's killer feature. It persists the entire graph state to storage after every node execution. This enables:

- **Long-running workflows** — pause overnight, resume tomorrow
- **Human-in-the-loop** — interrupt mid-graph, wait for human approval, continue
- **Fault tolerance** — if a node crashes, restart from the last checkpoint
- **Debugging** — replay any run from any point in history

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver  # For production

# In-memory (testing)
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# SQLite (local dev)
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# Postgres (production)
checkpointer = PostgresSaver.from_conn_string(os.environ["DATABASE_URL"])

graph = builder.compile(checkpointer=checkpointer)
```

### Thread IDs

Each independent conversation gets a `thread_id`. The checkpointer stores state per thread:

```python
config = {"configurable": {"thread_id": "user-123-session-456"}}

# Run resumes from where this thread left off
result = graph.invoke({"messages": [("user", "continue")]}, config=config)
```

---

## Human-in-the-Loop

Use `interrupt_before` or `interrupt_after` to pause execution at a node and wait for human input:

```python
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["dangerous_action_node"],   # Pause BEFORE this node runs
)

# Run until the interrupt
graph.invoke(inputs, config)

# Human reviews, then resumes
graph.invoke(None, config)   # None = no new input, just continue
```

This is how you build approval workflows: the graph runs up to a checkpoint, emails a human, and resumes when they click "Approve".

---

## Parallel Execution

Use `Send` to fan out work to multiple nodes in parallel:

```python
from langgraph.types import Send

def fan_out(state: AgentState):
    # Dispatch the same task to multiple workers in parallel
    return [
        Send("worker_node", {"task": task})
        for task in state["tasks"]
    ]

graph.add_conditional_edges("coordinator", fan_out)
```

Each `Send` creates an independent branch. Results are collected and merged back into state by the reducer.

---

## Subgraphs

Complex graphs can be composed from smaller graphs. A subgraph is just another compiled graph used as a node:

```python
subgraph = build_research_subgraph()  # Returns a compiled graph

builder.add_node("research", subgraph)  # Use subgraph as a node
```

This keeps large systems manageable and allows reuse across different parent graphs.

---

## Visualising Your Graph

One of LangGraph's best features — see exactly what you built:

```python
# Print as ASCII
print(graph.get_graph().draw_ascii())

# Export as PNG (requires graphviz)
graph.get_graph().draw_png("my_agent.png")

# In a Jupyter notebook
from IPython.display import Image
Image(graph.get_graph().draw_mermaid_png())
```

If your graph looks more complicated than you expected, it probably is.

---

## Common Patterns

### ReAct Loop
```
START → llm → (tool calls?) → tools → llm → ... → END
```

### Plan-and-Execute
```
START → planner → executor → (done?) → END
                     ↑_________|
```

### Reflection
```
START → generator → critic → (good enough?) → END
              ↑_______________|
```

### Human Approval
```
START → agent → [INTERRUPT] → human_review → agent → END
```

---

## What to Read Next

- [LangGraph official concepts](https://langchain-ai.github.io/langgraph/concepts/)
- [LangGraph how-to guides](https://langchain-ai.github.io/langgraph/how-tos/)
- [LangSmith for observability](https://smith.langchain.com)
