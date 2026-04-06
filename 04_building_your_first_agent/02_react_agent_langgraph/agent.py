"""
The Hitchhiker's Guide to AI Agents
=====================================
Project 02: ReAct Agent with LangGraph
 
The same agent as Project 01 — same tools, same job — but now built with
LangGraph instead of raw Python.
 
Compare the two side-by-side:
 
  Project 01 (scratch)          Project 02 (LangGraph)
  ─────────────────────         ──────────────────────
  ~150 lines                    ~80 lines (logic only)
  Manual prompt engineering     Framework handles ReAct format
  Hand-rolled parser (regex)    Framework parses tool calls
  Manual message history        State managed automatically
  You own every edge case       LangGraph owns the loop
 
The big insight: LangGraph is not magic — it IS the loop from Project 01,
packaged so you don't have to re-implement it every time.
 
Run:
  ollama pull llama3.2        # if you haven't already
  python agent.py
 
Author: The Hitchhiker's Guide to AI Agents
"""
 
import json
import math
import urllib.parse
import urllib.request
 
import wikipediaapi
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
 
from langgraph.prebuilt import create_react_agent
 
console = Console()
 
# ─────────────────────────────────────────────
# 1. TOOLS
#
# Same two tools as Project 01.
# The only difference: the @tool decorator.
#
# That decorator does three things automatically:
#   - Extracts the function name as the tool name
#   - Reads the docstring as the tool description
#   - Generates a JSON schema from the type hints
#
# In Project 01, we registered all of that manually in the TOOLS dict.
# Here: one decorator = done.
# ─────────────────────────────────────────────
 
wiki = wikipediaapi.Wikipedia(user_agent="hitchhikers-guide-ai-agents/1.0", language="en")
 
 
def _coerce_str(value: object) -> str:
    """
    Normalize tool inputs to a plain string.
 
    llama3.2 sometimes passes the JSON schema object instead of the actual value:
        {'type': 'string', 'value': 'Mughal Empire'}   ← schema echo
        {'query': 'Mughal Empire'}                      ← wrong nesting
        'Mughal Empire'                                 ← correct
 
    This helper extracts the real string from any of those forms.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        # Schema echo: {'type': 'string', 'value': 'Mughal Empire'}
        if "value" in value:
            return str(value["value"])
        # Wrong nesting: {'query': 'Mughal Empire'} or {'expression': '2+2'}
        for key in ("query", "expression", "input", "text", "search"):
            if key in value:
                return str(value[key])
        # Last resort: join all string values
        parts = [str(v) for v in value.values() if isinstance(v, (str, int, float))]
        return " ".join(parts) if parts else str(value)
    return str(value)
 
 
def _strip_quotes(s: str) -> str:
    """Strip surrounding quotes that LLMs sometimes add to tool inputs."""
    return s.strip().strip("\"'").strip()
 
 
def _wikipedia_resolve_title(query: str) -> str | None:
    """
    Use Wikipedia's search API to resolve a fuzzy query to an exact page title.
    wiki.page() requires an exact title — this finds the closest match first.
    """
    params = urllib.parse.urlencode({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 1,
    })
    url = f"https://en.wikipedia.org/w/api.php?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "hitchhikers-guide-ai-agents/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
            hits = data.get("query", {}).get("search", [])
            return hits[0]["title"] if hits else None
    except Exception:
        return None
 
 
@tool
def wikipedia_search(query: object) -> str:
    """
    Search Wikipedia for factual information about a topic.
    Returns the opening summary of the most relevant Wikipedia page.
    Works with fuzzy queries — 'berlin wall history' will find 'Berlin Wall'.
    """
    query = _strip_quotes(_coerce_str(query))
    title = _wikipedia_resolve_title(query)
    page = wiki.page(title or query)
    if not page.exists():
        return (
            f"No Wikipedia page found for '{query}'. "
            "Try a different search term."
        )
    return f"[Wikipedia: {page.title}]\n{page.summary[:800]}"
 
 
@tool
def calculator(expression: object) -> str:
    """
    Evaluate a mathematical expression. Do NOT wrap the expression in quotes.
    Good: 299792458 / 40075000  |  Bad: '299792458 / 40075000'
    Supports: +, -, *, /, **, sqrt(), log(), sin(), cos(), pi, e
    """
    # Coerce dict/schema inputs, then strip quotes
    expression = _strip_quotes(_coerce_str(expression))
    allowed = {
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "sin": math.sin,   "cos": math.cos, "tan": math.tan,
        "abs": abs,        "round": round,
        "pi": math.pi,     "e": math.e,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed)  # noqa: S307
        # Guard: if result is still a string, the LLM passed a double-quoted expression
        if isinstance(result, str):
            result = eval(result, {"__builtins__": {}}, allowed)  # noqa: S307
        return str(result)
    except Exception as exc:
        return f"Calculator error: {exc}"
 
 
TOOLS = [wikipedia_search, calculator]
 
 
# ─────────────────────────────────────────────
# 2. THE GRAPH
#
# In Project 01, the agent loop was a for-loop we wrote ourselves:
#   while not done:
#       response = llm(messages)
#       action = parse(response)
#       observation = run_tool(action)
#       messages.append(observation)
#
# Here, create_react_agent() builds that same loop as a LangGraph graph.
# Under the hood it creates two nodes:
#   - "agent"  → calls the LLM
#   - "tools"  → runs whichever tool the LLM chose
# And two edges:
#   - agent → tools  (when the LLM wants to use a tool)
#   - tools → agent  (feed the observation back)
#   - agent → END    (when the LLM produces a final answer)
#
# We don't write any of that — we just configure it.
# ─────────────────────────────────────────────
 
def build_agent(model: str = "llama3.2"):
    llm = ChatOllama(model=model, temperature=0)
 
    # This one line replaces ~60 lines from Project 01
    # (the loop, the parser, the message management, the routing logic)
    graph = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=(
            "You are a helpful reasoning agent. "
            "Use tools to look up facts and do calculations. "
            "Never make up numbers — always use the calculator tool for math."
        ),
    )
    return graph
 
 
# ─────────────────────────────────────────────
# 3. PRETTY PRINTING
#
# LangGraph streams events as the graph executes.
# We intercept them to show the same Thought/Action/Observation
# display as Project 01, so you can compare the experience.
# ─────────────────────────────────────────────
 
def run_agent(question: str, model: str = "llama3.2") -> str:
    graph = build_agent(model)
 
    console.print(Rule("[bold]Starting ReAct Agent (LangGraph)[/bold]", style="dim"))
    console.print(f"[bold cyan]Question:[/bold cyan] {question}\n")
 
    step = 0
    final_answer = ""
 
    # stream_mode="updates" gives us one dict per node execution
    for update in graph.stream(
        {"messages": [HumanMessage(content=question)]},
        stream_mode="updates",
    ):
        for node_name, node_output in update.items():
            messages = node_output.get("messages", [])
 
            for msg in messages:
                # ── Agent node: LLM decided to call a tool ──
                if isinstance(msg, AIMessage) and msg.tool_calls:
                    step += 1
                    console.print(Rule(f"Step {step}", style="dim"))
 
                    # Show the model's reasoning (content before tool call)
                    if msg.content:
                        console.print(Panel(
                            str(msg.content),
                            title="[yellow]Thought[/yellow]",
                            border_style="yellow",
                        ))
 
                    for tc in msg.tool_calls:
                        args_str = ", ".join(f"{k}={v!r}" for k, v in tc["args"].items())
                        console.print(f"[cyan]Action:[/cyan]       {tc['name']}")
                        console.print(f"[cyan]Action Input:[/cyan] {args_str}")
 
                # ── Tools node: tool result came back ──
                elif isinstance(msg, ToolMessage):
                    console.print(Panel(
                        Text(str(msg.content)[:600], style="dim"),
                        title="[blue]Observation[/blue]",
                        border_style="blue",
                    ))
 
                # ── Agent node: final answer (no more tool calls) ──
                elif isinstance(msg, AIMessage) and not msg.tool_calls and msg.content:
                    final_answer = str(msg.content)
                    console.print(Panel(
                        final_answer,
                        title="[bold green]Final Answer[/bold green]",
                        border_style="green",
                    ))
 
    return final_answer
 
 
# ─────────────────────────────────────────────
# 4. ENTRY POINT
# ─────────────────────────────────────────────
 
# Same demo questions as Project 01 — run both and compare the output
DEMO_QUESTIONS = [
    "What is the speed of light, and how many times could it circle the Earth in one second?",
    "Who invented the World Wide Web, and what year was it proposed?",
    "What is the area of a circle with a radius equal to the number of planets in our solar system?",
]
 
if __name__ == "__main__":
    import sys
 
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        console.print("\n[bold]Demo questions (same as Project 01 — try both!):[/bold]")
        for i, q in enumerate(DEMO_QUESTIONS, 1):
            console.print(f"  {i}. {q}")
        console.print("\nPick a number, or type your own question:")
        user_input = input("> ").strip()
        if user_input.isdigit() and 1 <= int(user_input) <= len(DEMO_QUESTIONS):
            question = DEMO_QUESTIONS[int(user_input) - 1]
        else:
            question = user_input
 
    run_agent(question)