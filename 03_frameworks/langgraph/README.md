# 🔗 LangGraph

> "If you want to know exactly which node your agent is stuck in at 2am, LangGraph is the answer."

LangGraph is a library from the LangChain team for building **stateful, graph-based agent workflows**. Every agent is modeled as a directed graph: nodes are functions, edges are control flow, and shared state flows through the whole thing.

It's the most battle-tested framework for production agent systems as of 2026.

---

## The Core Idea

Most agents are secretly state machines. They gather info, decide what to do, call a tool, look at the result, decide again. LangGraph makes that state machine **explicit and visible**.

```
[START] → [gather_context] → [decide_action] → [call_tool] → [check_result]
                                    ↑                               |
                                    └───────── (loop back) ─────────┘
```

You define the graph. LangGraph executes it, manages the shared state at each node, and lets you add checkpointing, human-in-the-loop pauses, and conditional edges.

---

## Key Concepts

### State
A typed dictionary (usually a `TypedDict` or Pydantic model) that every node can read and write. This is the agent's memory within a run.

```python
from typing import TypedDict, Annotated
from langgraph.graph import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    tool_calls_made: int
    final_answer: str
```

### Nodes
Plain Python functions that take state in, return updated state.

```python
def call_llm(state: AgentState) -> AgentState:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}
```

### Edges
Define how nodes connect. Can be static (`A → B always`) or conditional (`A → B or C depending on state`).

```python
graph.add_conditional_edges(
    "call_llm",
    route_based_on_output,   # your function returns "tools" or "end"
    {"tools": "call_tools", "end": END}
)
```

### Checkpointing
Persist the entire graph state to a database between steps. Allows long-running workflows, human approval gates, and resuming after failures.

```python
from langgraph.checkpoint.sqlite import SqliteSaver
memory = SqliteSaver.from_conn_string(":memory:")
graph = builder.compile(checkpointer=memory)
```

---

## Quickstart

See [`quickstart.py`](./quickstart.py) for a complete working ReAct agent in LangGraph (~60 lines).

Install:
```bash
pip install langgraph langchain-anthropic
```

The quickstart builds an agent that:
1. Receives a user message
2. Calls an LLM with tools available
3. Executes any tool calls
4. Loops back until the LLM is done
5. Returns the final answer

---

## When LangGraph Wins

- **Complex branching logic** - conditional paths, loops, retry on failure, human approval gates
- **You need to debug execution** - LangGraph's graph visualization in LangSmith shows exactly which node ran and why
- **Long-running workflows** - checkpointing lets you pause, resume, and recover without restarting
- **Production systems** - explicit state makes it easy to add monitoring, retries, and error handling
- **You care about determinism** - same graph, same inputs → same execution path

---

## When LangGraph Loses

- **Simple single-agent tasks** - overkill if you just need one LLM call with some tools
- **Quick prototyping** - the graph-think overhead slows you down vs. CrewAI or raw calls
- **Non-LangChain stacks** - it works with any LLM, but ecosystem is LangChain-flavored
- **Your team doesn't know graph theory** - `nodes`, `edges`, `state`, `conditional edges` is a real learning curve

---

## Honest Trade-offs

| Strength | Weakness |
|---|---|
| Most debuggable of any framework | Steepest learning curve |
| True stateful persistence | Verbose setup for simple tasks |
| Human-in-the-loop is first-class | LangSmith observability is paid |
| Production-proven at scale | LangChain ecosystem lock-in |

---

## The One Thing to Remember

LangGraph makes your agent's control flow a **first-class artifact**. You can draw it, inspect it, test it, and reason about it. If that visibility matters to you - pick LangGraph. If you just want something running fast - start somewhere simpler.

---

## Further Reading

- [LangGraph docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph conceptual guide](https://langchain-ai.github.io/langgraph/concepts/)
- [LangSmith observability](https://smith.langchain.com)