"""
The Hitchhiker's Guide to AI Agents
=====================================
Project 03: Agent with Memory

Same agent as Project 02. One new concept: memory.

In Projects 01 and 02, every run started fresh — the agent had no
recollection of previous conversations. Ask it "What did I just ask you?"
and it would be genuinely baffled.

This project adds two kinds of memory:

  ┌─────────────────────────────────────────────────────────────┐
  │  Within-conversation (short-term)                           │
  │  The agent remembers everything said earlier in this chat.  │
  │  "You asked about Berlin. Now you're asking about its wall."│
  └─────────────────────────────────────────────────────────────┘
  ┌─────────────────────────────────────────────────────────────┐
  │  Across-conversation (long-term)                            │
  │  The agent remembers past sessions saved to disk.           │
  │  Restart the script. It still knows what you discussed.     │
  └─────────────────────────────────────────────────────────────┘

The mechanism: LangGraph's checkpointer.

  Project 02: graph.stream(input, config)
                                  ↑
                            just a thread id

  Project 03: graph.stream(input, config)          ← same call
              + SqliteSaver(conn)                  ← one new argument
                                                     at graph build time

That's the entire diff. One argument. The checkpointer intercepts every
state update and writes it to SQLite. On the next turn, it reads it back.

Run:
  ollama pull llama3.2        # if you haven't already
  python agent.py

Author: The Hitchhiker's Guide to AI Agents
"""

import json
import math
import sqlite3
import urllib.parse
import urllib.request
from pathlib import Path

import wikipediaapi
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.text import Text

console = Console()

# ─────────────────────────────────────────────
# 1. TOOLS  (identical to Project 02)
# ─────────────────────────────────────────────

wiki = wikipediaapi.Wikipedia(user_agent="hitchhikers-guide-ai-agents/1.0", language="en")


def _coerce_str(value: object) -> str:
    """Normalize tool inputs — llama3.2 sometimes passes schema dicts instead of values."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if "value" in value:
            return str(value["value"])
        for key in ("query", "expression", "input", "text", "search"):
            if key in value:
                return str(value[key])
        parts = [str(v) for v in value.values() if isinstance(v, (str, int, float))]
        return " ".join(parts) if parts else str(value)
    return str(value)


def _strip_quotes(s: str) -> str:
    return s.strip().strip("\"'").strip()


def _wikipedia_resolve_title(query: str) -> str | None:
    params = urllib.parse.urlencode({
        "action": "query", "list": "search",
        "srsearch": query, "format": "json", "srlimit": 1,
    })
    req = urllib.request.Request(
        f"https://en.wikipedia.org/w/api.php?{params}",
        headers={"User-Agent": "hitchhikers-guide-ai-agents/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            hits = json.loads(resp.read()).get("query", {}).get("search", [])
            return hits[0]["title"] if hits else None
    except Exception:
        return None


@tool
def wikipedia_search(query: object) -> str:
    """
    Search Wikipedia for factual information about a topic.
    Works with fuzzy queries — 'berlin wall history' will find 'Berlin Wall'.
    """
    query = _strip_quotes(_coerce_str(query))
    title = _wikipedia_resolve_title(query)
    page = wiki.page(title or query)
    if not page.exists():
        return f"No Wikipedia page found for '{query}'. Try a different search term."
    return f"[Wikipedia: {page.title}]\n{page.summary[:800]}"


@tool
def calculator(expression: object) -> str:
    """
    Evaluate a math expression. Example: 2 ** 10, sqrt(144), pi * 5 ** 2
    Do NOT wrap the expression in quotes.
    """
    expression = _strip_quotes(_coerce_str(expression))
    allowed = {
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "abs": abs, "round": round, "pi": math.pi, "e": math.e,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed)  # noqa: S307
        if isinstance(result, str):
            result = eval(result, {"__builtins__": {}}, allowed)  # noqa: S307
        return str(result)
    except Exception as exc:
        return f"Calculator error: {exc}"


TOOLS = [wikipedia_search, calculator]


# ─────────────────────────────────────────────
# 2. THE GRAPH  (Project 02 + one argument)
#
# The only difference from Project 02 is the `checkpointer=` argument.
# Everything else — the model, the tools, the prompt — is identical.
#
# SqliteSaver writes the full message state to a local .db file after
# every node execution. On the next turn, it reads it back using the
# thread_id as the lookup key.
# ─────────────────────────────────────────────

DB_PATH = Path(__file__).parent / "memory.db"


def build_agent(model: str = "llama3.2"):
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    llm = ChatOllama(model=model, temperature=0)

    graph = create_react_agent(
        model=llm,
        tools=TOOLS,
        checkpointer=checkpointer,      # ← the only new line vs Project 02
        prompt=(
            "You are a helpful reasoning agent with memory. "
            "You remember everything said earlier in this conversation. "
            "Use tools to look up facts and do calculations. "
            "If the user refers to something mentioned earlier, use that context."
        ),
    )
    return graph


# ─────────────────────────────────────────────
# 3. DISPLAY HELPERS
# ─────────────────────────────────────────────

def print_agent_response(update: dict) -> str | None:
    """Print one graph update event. Returns final answer text if present."""
    for node_name, node_output in update.items():
        for msg in node_output.get("messages", []):

            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    args_str = ", ".join(f"{k}={v!r}" for k, v in tc["args"].items())
                    console.print(f"  [cyan]→ {tc['name']}[/cyan]({args_str})")

            elif isinstance(msg, ToolMessage):
                console.print(Panel(
                    Text(str(msg.content)[:400], style="dim"),
                    title="[blue]Observation[/blue]",
                    border_style="blue",
                    padding=(0, 1),
                ))

            elif isinstance(msg, AIMessage) and not msg.tool_calls and msg.content:
                console.print(Panel(
                    str(msg.content),
                    title="[bold green]Answer[/bold green]",
                    border_style="green",
                ))
                return str(msg.content)

    return None


def show_memory_snapshot(graph, thread_id: str) -> None:
    """Print how many messages are stored for this thread."""
    config = {"configurable": {"thread_id": thread_id}}
    state = graph.get_state(config)
    msgs = state.values.get("messages", [])
    human = sum(1 for m in msgs if isinstance(m, HumanMessage))
    ai = sum(1 for m in msgs if isinstance(m, AIMessage))
    console.print(
        f"\n[dim]  Memory snapshot — thread '{thread_id}': "
        f"{len(msgs)} messages stored ({human} human, {ai} AI)[/dim]\n"
    )


# ─────────────────────────────────────────────
# 4. THE CHAT LOOP
#
# thread_id is the key concept here.
# Every conversation gets one. The checkpointer uses it to store
# and retrieve that conversation's message history independently.
#
# Same thread_id  → agent remembers previous turns
# New thread_id   → fresh conversation, no memory of the old one
# ─────────────────────────────────────────────

def run_chat(thread_id: str, model: str = "llama3.2") -> None:
    graph = build_agent(model)
    config = {"configurable": {"thread_id": thread_id}}

    console.print(Rule(f"[bold]Session — thread '{thread_id}'[/bold]", style="dim"))
    console.print(
        f"[dim]Memory stored at:[/dim] [yellow]{DB_PATH}[/yellow]\n"
        f"[dim]Restart the script with the same thread ID to resume this conversation.[/dim]\n"
    )

    # Show existing memory if resuming a previous session
    state = graph.get_state(config)
    prior_msgs = state.values.get("messages", [])
    if prior_msgs:
        console.print(
            f"[bold yellow]Resuming conversation[/bold yellow] — "
            f"{len(prior_msgs)} messages loaded from memory.\n"
        )
        # Print the last exchange so the user remembers where they left off
        for msg in prior_msgs[-2:]:
            if isinstance(msg, HumanMessage):
                console.print(f"[dim]  You (previously):[/dim] {msg.content}")
            elif isinstance(msg, AIMessage) and not msg.tool_calls:
                content = str(msg.content)
                console.print(f"[dim]  Agent (previously):[/dim] {content[:200]}{'…' if len(content) > 200 else ''}")
        console.print()

    console.print("[dim]Type your question, 'memory' to inspect state, or 'quit' to exit.[/dim]\n")

    turn = 0
    while True:
        try:
            question = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break
        if question.lower() == "memory":
            show_memory_snapshot(graph, thread_id)
            continue

        turn += 1
        console.print(Rule(f"Turn {turn}", style="dim"))

        for update in graph.stream(
            {"messages": [HumanMessage(content=question)]},
            config=config,
            stream_mode="updates",
        ):
            print_agent_response(update)

        console.print()

    console.print(Rule("[dim]Session ended[/dim]", style="dim"))
    show_memory_snapshot(graph, thread_id)


# ─────────────────────────────────────────────
# 5. ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    console.print()
    console.print("[bold]The Hitchhiker's Guide to AI Agents[/bold]")
    console.print("[dim]Project 03 — Agent with Memory[/dim]\n")

    if len(sys.argv) > 1:
        thread_id = sys.argv[1]
        console.print(f"[dim]Using thread ID from argument: '{thread_id}'[/dim]")
    else:
        console.print(
            "Each conversation gets a [bold]thread ID[/bold]. "
            "Use the same ID to resume. Use a new one for a fresh start.\n"
        )
        thread_id = Prompt.ask(
            "[bold]Thread ID[/bold]",
            default="default",
        )

    run_chat(thread_id)
