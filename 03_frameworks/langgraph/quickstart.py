"""
LangGraph Quickstart — A minimal ReAct agent

What this builds:
  A simple agent that can search the web and answer questions.
  It loops: think → call tool → observe → think → answer.

Install:
  pip install langgraph langchain-anthropic

Run:
  python quickstart.py
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool


# ── 1. Define your state ────────────────────────────────────────────────────
# This TypedDict flows through every node in the graph.
# `add_messages` is a reducer — it appends new messages instead of replacing.

class State(TypedDict):
    messages: Annotated[list, add_messages]


# ── 2. Define tools ─────────────────────────────────────────────────────────
# These are the actions the agent can take.
# In production, these would hit real APIs. Here we fake them.

@tool
def search_web(query: str) -> str:
    """Search the web for information about a topic."""
    # Replace with real search (Tavily, SerpAPI, etc.)
    return f"[Fake search result for '{query}']: The answer is 42, and also the capital of France is Paris."

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

tools = [search_web, calculate]


# ── 3. Set up the LLM ───────────────────────────────────────────────────────

llm = ChatAnthropic(model="claude-sonnet-4-5")
llm_with_tools = llm.bind_tools(tools)


# ── 4. Define nodes ─────────────────────────────────────────────────────────
# Each node is a plain function: takes State in, returns partial State out.

def call_llm(state: State) -> State:
    """The reasoning node — asks the LLM what to do next."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# ── 5. Build the graph ──────────────────────────────────────────────────────

builder = StateGraph(State)

# Add nodes
builder.add_node("llm", call_llm)
builder.add_node("tools", ToolNode(tools))

# Add edges
builder.add_edge(START, "llm")

# Conditional edge: after LLM, either call a tool or finish
# `tools_condition` is a prebuilt helper that checks if the LLM made tool calls
builder.add_conditional_edges("llm", tools_condition)

# After tools run, always go back to LLM to reason about the result
builder.add_edge("tools", "llm")

# Compile — this validates the graph and returns a runnable
graph = builder.compile()


# ── 6. Run it ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("LangGraph ReAct Agent")
    print("=" * 40)
    
    question = "What is 25 * 4, and what is the capital of France?"
    print(f"Question: {question}\n")
    
    # Stream events so we can see each step
    for event in graph.stream(
        {"messages": [("user", question)]},
        stream_mode="values"
    ):
        last_message = event["messages"][-1]
        last_message.pretty_print()
        print()


# ── What's happening ────────────────────────────────────────────────────────
#
# Graph structure:
#
#   START → [llm] → (tools_condition) → [tools] → [llm] → ... → END
#                          ↓
#                    (no tool calls)
#                          ↓
#                         END
#
# The LLM sees the question, decides to call `calculate` and `search_web`,
# ToolNode executes both, results go back to the LLM as tool messages,
# the LLM synthesizes a final answer, and since it makes no more tool calls,
# tools_condition routes to END.
