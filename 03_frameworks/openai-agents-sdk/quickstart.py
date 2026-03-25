"""
OpenAI Agents SDK Quickstart — Triage agent with handoffs

What this builds:
  A triage agent that routes questions to specialist agents.
  Math questions → Math Agent. Coding questions → Code Agent.

Install:
  pip install openai-agents

Run:
  python quickstart.py
"""

import asyncio
from agents import Agent, Runner, function_tool


# ── 1. Define tools ────────────────────────────────────────────────────────────

@function_tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        # In production, use a proper math library instead of eval
        result = eval(expression, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

@function_tool
def run_python(code: str) -> str:
    """Execute a Python code snippet and return the output."""
    # In production, run this in a sandbox (Docker, subprocess with limits)
    import io, contextlib
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {"__builtins__": {"print": print, "range": range, "len": len}})
        return output.getvalue() or "Code executed with no output."
    except Exception as e:
        return f"Error: {e}"


# ── 2. Define specialist agents ─────────────────────────────────────────────────

math_agent = Agent(
    name="Math Specialist",
    instructions=(
        "You are an expert mathematician. "
        "Solve problems step by step, showing all working. "
        "Use the calculate tool for arithmetic. "
        "Always verify your answer makes sense."
    ),
    tools=[calculate],
)

code_agent = Agent(
    name="Code Specialist",
    instructions=(
        "You are an expert Python developer. "
        "Write clean, well-commented code. "
        "Use run_python to test your solutions. "
        "If the code has an error, debug and retry."
    ),
    tools=[run_python],
)


# ── 3. Define the triage agent ──────────────────────────────────────────────────
# This agent routes to specialists. It has no tools of its own —
# it just decides who should handle the task.

triage_agent = Agent(
    name="Triage",
    instructions=(
        "You are a routing agent. Analyze the user's question and hand off to the right specialist.\n"
        "- Math questions (calculations, equations, proofs) → Math Specialist\n"
        "- Coding questions (write code, debug, algorithms) → Code Specialist\n"
        "- If unclear, ask one clarifying question before routing."
    ),
    handoffs=[math_agent, code_agent],
)


# ── 4. Run it ────────────────────────────────────────────────────────────────────

async def ask(question: str):
    print(f"\nQ: {question}")
    print("-" * 40)
    result = await Runner.run(triage_agent, question)
    print(f"A: {result.final_output}")


async def main():
    print("OpenAI Agents SDK — Triage + Handoff Demo")
    print("=" * 40)
    
    await ask("What is 347 × 892?")
    await ask("Write a Python function that reverses a linked list.")


if __name__ == "__main__":
    asyncio.run(main())


# ── What's happening ─────────────────────────────────────────────────────────────
#
# For a math question:
#   user → triage_agent → (detects math) → handoff to math_agent
#   math_agent → uses calculate tool → returns answer
#
# For a coding question:
#   user → triage_agent → (detects code) → handoff to code_agent
#   code_agent → writes code → uses run_python → debugs if needed → returns
#
# The SDK's Runner handles:
#   - The agent loop (calling LLM → executing tools → calling LLM again)
#   - Handoff mechanics (switching context to the specialist agent)
#   - Structured output collection
#
# result.final_output is the last text response from whichever agent handled it.
# result.new_items contains every event (tool calls, handoffs, messages) if you need them.
