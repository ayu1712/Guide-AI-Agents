"""
The Hitchhiker's Guide to AI Agents
=====================================
Project 01: ReAct Agent from Scratch

A minimal but complete ReAct (Reasoning + Acting) agent built with:
  - Ollama (free, runs locally — no API key needed)
  - Two tools: Wikipedia search + a calculator
  - Full reasoning trace printed to terminal

The ReAct loop:
  Thought → Action → Observation → Thought → ... → Final Answer

Run:
  ollama pull llama3.2        # one-time setup
  python agent.py

Author: The Hitchhiker's Guide to AI Agents
"""

import json
import math
import re
import textwrap
from typing import Any

import wikipediaapi
from ollama import chat
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

console = Console()

# ─────────────────────────────────────────────
# 1. TOOLS
# Each tool is just a plain Python function.
# The agent decides when to call them.
# ─────────────────────────────────────────────

wiki = wikipediaapi.Wikipedia(user_agent="hitchhikers-guide-ai-agents/1.0", language="en")


def wikipedia_search(query: str) -> str:
    """Search Wikipedia and return the opening summary of the best matching page."""
    page = wiki.page(query)
    if not page.exists():
        return f"No Wikipedia page found for '{query}'. Try a different search term."
    # Return first ~800 chars — enough context without blowing the context window
    summary = page.summary[:800]
    return f"[Wikipedia: {page.title}]\n{summary}"


def calculator(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    Supports: +, -, *, /, **, sqrt(), log(), sin(), cos(), pi, e
    Example: '2 ** 10', 'sqrt(144)', 'pi * 5 ** 2'
    """
    allowed = {
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "abs": abs, "round": round,
        "pi": math.pi, "e": math.e,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed)  # noqa: S307
        return str(result)
    except Exception as exc:
        return f"Calculator error: {exc}"


# Tool registry — the agent sees this as its action menu
TOOLS: dict[str, dict[str, Any]] = {
    "wikipedia_search": {
        "fn": wikipedia_search,
        "description": (
            "Search Wikipedia for factual information about a topic. "
            "Input: a search query string. "
            "Output: the opening summary of the most relevant Wikipedia page."
        ),
    },
    "calculator": {
        "fn": calculator,
        "description": (
            "Evaluate a mathematical expression. "
            "Input: a valid Python math expression as a string (e.g. '2**10', 'sqrt(144)', 'pi * 5**2'). "
            "Output: the numeric result."
        ),
    },
}


# ─────────────────────────────────────────────
# 2. SYSTEM PROMPT
# This is what teaches the model the ReAct format.
# ─────────────────────────────────────────────

def build_system_prompt() -> str:
    tool_descriptions = "\n".join(
        f"- {name}: {meta['description']}"
        for name, meta in TOOLS.items()
    )
    return textwrap.dedent(f"""
        You are a helpful reasoning agent. You solve problems step-by-step using tools.

        You have access to these tools:
        {tool_descriptions}

        Always respond in this exact format:

        Thought: <your reasoning about what to do next>
        Action: <tool_name>
        Action Input: <the input to pass to the tool>

        After you receive an Observation, continue with another Thought/Action/Action Input,
        OR if you have enough information to answer, respond with:

        Thought: I now have enough information to answer.
        Final Answer: <your complete answer to the user's question>

        Rules:
        - Never make up facts. Use tools to look things up.
        - For calculations, always use the calculator tool — don't compute in your head.
        - Be concise in your thoughts.
        - Action must be one of: {list(TOOLS.keys())}
        - Action Input must be a plain string, not JSON.
    """).strip()


# ─────────────────────────────────────────────
# 3. PARSING
# Extract the agent's intended action from its text output.
# ─────────────────────────────────────────────

def parse_action(text: str) -> tuple[str | None, str | None, str | None]:
    """
    Parse a ReAct-formatted response.
    Returns: (thought, action, action_input)
    Returns (thought, None, None) if it's a Final Answer.
    """
    thought_match = re.search(r"Thought:\s*(.+?)(?=Action:|Final Answer:|$)", text, re.S)
    action_match = re.search(r"Action:\s*(.+?)(?=Action Input:|$)", text, re.S)
    input_match = re.search(r"Action Input:\s*(.+?)(?=Observation:|Thought:|$)", text, re.S)
    final_match = re.search(r"Final Answer:\s*(.+)", text, re.S)

    thought = thought_match.group(1).strip() if thought_match else ""

    if final_match:
        return thought, None, final_match.group(1).strip()

    action = action_match.group(1).strip() if action_match else None
    action_input = input_match.group(1).strip() if input_match else None
    return thought, action, action_input


# ─────────────────────────────────────────────
# 4. THE AGENT LOOP
# Thought → Action → Observation → repeat
# ─────────────────────────────────────────────

def run_agent(question: str, model: str = "llama3.2", max_steps: int = 8) -> str:
    """
    Run the ReAct agent loop until it produces a Final Answer or hits max_steps.
    Returns the final answer string.
    """
    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": question},
    ]

    console.print(Rule("[bold]Starting ReAct Agent[/bold]", style="dim"))
    console.print(f"[bold cyan]Question:[/bold cyan] {question}\n")

    for step in range(1, max_steps + 1):
        console.print(Rule(f"Step {step}", style="dim"))

        # ── LLM call ──
        response = chat(model=model, messages=messages)
        agent_text = response.message.content.strip()

        # ── Parse the response ──
        thought, action, action_input = parse_action(agent_text)

        # Show thought
        if thought:
            console.print(Panel(thought, title="[yellow]Thought[/yellow]", border_style="yellow"))

        # ── Final answer? ──
        if action is None:
            # action_input holds the final answer when action is None
            final = action_input or agent_text
            console.print(Panel(final, title="[bold green]Final Answer[/bold green]", border_style="green"))
            return final

        # ── Execute tool ──
        console.print(f"[cyan]Action:[/cyan]      {action}")
        console.print(f"[cyan]Action Input:[/cyan] {action_input}")

        if action not in TOOLS:
            observation = f"Unknown tool '{action}'. Available tools: {list(TOOLS.keys())}"
        else:
            observation = TOOLS[action]["fn"](action_input)

        console.print(Panel(
            Text(observation[:600] + ("…" if len(observation) > 600 else ""), style="dim"),
            title="[blue]Observation[/blue]",
            border_style="blue",
        ))

        # Feed the full exchange back into context
        messages.append({"role": "assistant", "content": agent_text})
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    return "Agent reached max steps without a final answer."


# ─────────────────────────────────────────────
# 5. ENTRY POINT
# ─────────────────────────────────────────────

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
        console.print("\n[bold]Demo questions:[/bold]")
        for i, q in enumerate(DEMO_QUESTIONS, 1):
            console.print(f"  {i}. {q}")
        console.print("\nPick a number, or type your own question:")
        user_input = input("> ").strip()
        if user_input.isdigit() and 1 <= int(user_input) <= len(DEMO_QUESTIONS):
            question = DEMO_QUESTIONS[int(user_input) - 1]
        else:
            question = user_input

    run_agent(question)
