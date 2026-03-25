"""
CrewAI Quickstart — A two-agent research crew

What this builds:
  A Researcher + Writer crew that investigates a topic
  and produces a structured summary.

Install:
  pip install crewai crewai-tools

Run:
  python quickstart.py
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Optional: real web search. Remove and use fake_search below if you don't have an API key.
# search_tool = SerperDevTool()

from langchain_core.tools import tool

@tool
def fake_search(query: str) -> str:
    """Search the web for information."""
    # Replace with SerperDevTool() or Tavily for real search
    return f"""
    Search results for '{query}':
    - LangGraph: graph-based stateful workflows, best for production
    - CrewAI: role-based teams, best for quick prototyping
    - AutoGen: conversational agents, best for multi-party dialogues
    - OpenAI Agents SDK: lightweight, best for OpenAI-stack projects
    """


# ── 1. Define agents ─────────────────────────────────────────────────────────
# Role, goal, and backstory shape the agent's behaviour via prompting.
# Tools define what the agent can actually do.

researcher = Agent(
    role="Senior AI Research Analyst",
    goal="Find accurate, current information about AI agent frameworks and synthesise key insights",
    backstory=(
        "You've spent years tracking the evolution of AI tooling. "
        "You cut through hype to find what actually works in production. "
        "You always cite trade-offs honestly."
    ),
    tools=[fake_search],
    verbose=True,
    allow_delegation=False,
)

writer = Agent(
    role="Technical Writer",
    goal="Transform research findings into clear, structured prose that developers can act on",
    backstory=(
        "You write for developers who are busy and skeptical. "
        "You lead with the most important point, explain trade-offs honestly, "
        "and never pad word count."
    ),
    verbose=True,
    allow_delegation=False,
)


# ── 2. Define tasks ──────────────────────────────────────────────────────────
# Each task describes the work and what good output looks like.
# context= tells CrewAI which prior task outputs to include.

research_task = Task(
    description=(
        "Research the top AI agent frameworks available in 2026. "
        "For each framework, identify: what it is, its core mental model, "
        "what it's best at, and its main limitations. "
        "Focus on: LangGraph, CrewAI, AutoGen, OpenAI Agents SDK."
    ),
    expected_output=(
        "A structured list of 4 frameworks, each with: "
        "name, core mental model (1 sentence), best use case (1 sentence), "
        "main limitation (1 sentence)."
    ),
    agent=researcher,
)

writing_task = Task(
    description=(
        "Using the research provided, write a practical guide for a developer "
        "trying to choose an AI agent framework. "
        "Lead with the decision criteria, not the framework list. "
        "End with a one-line recommendation for each of: "
        "beginners, production teams, and conversational agent builders."
    ),
    expected_output=(
        "A 300-400 word markdown guide with: "
        "a decision-criteria section, "
        "a framework summary table, "
        "and 3 one-line recommendations."
    ),
    agent=writer,
    context=[research_task],  # Writer gets the researcher's output
)


# ── 3. Assemble and run the crew ─────────────────────────────────────────────

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,  # Research happens before writing
    verbose=True,
)

if __name__ == "__main__":
    print("CrewAI — Research + Writing Crew")
    print("=" * 40)
    
    result = crew.kickoff()
    
    print("\n" + "=" * 40)
    print("FINAL OUTPUT")
    print("=" * 40)
    print(result)


# ── What's happening ─────────────────────────────────────────────────────────
#
# Flow:
#   [Researcher] searches for framework info → produces structured list
#         ↓ (output passed as context)
#   [Writer] reads research → produces developer guide
#         ↓
#   Crew returns final output
#
# Process.sequential means tasks run in order.
# context=[research_task] feeds the first task's output to the second.
#
# Try changing to Process.hierarchical to add a manager agent
# that delegates and quality-checks both agents' work.
