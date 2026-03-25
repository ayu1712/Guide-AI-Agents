# 👥 CrewAI

> "What if your agents had job titles, business cards, and a shared Slack workspace?"

CrewAI models multi-agent collaboration as a **team of role-playing specialists**. You define each agent's role, goal, and backstory — then assemble them into a crew with tasks. CrewAI figures out who does what and in what order.

It's the fastest framework to go from idea to working multi-agent system.

---

## The Core Idea

Humans solve hard problems by dividing work between specialists. A good research report needs a researcher who finds information, a writer who structures it, and an editor who sharpens it. CrewAI lets you do exactly that with agents.

```
Crew: "Write a market analysis report"
├── Researcher (goal: find accurate market data)
├── Writer (goal: structure findings into clear prose)
└── Editor (goal: fact-check and improve clarity)
```

Each agent has tools it can use. Tasks flow between agents either sequentially or in parallel. The crew produces a final output.

---

## Key Concepts

### Agent
An autonomous entity with a role, goal, backstory, and (optionally) tools. The role and backstory are prompts — they shape how the LLM behaves when acting as that agent.

```python
from crewai import Agent

researcher = Agent(
    role="Senior Research Analyst",
    goal="Uncover accurate and insightful data about AI trends",
    backstory="You've spent 10 years tracking the AI industry...",
    tools=[search_tool],
    verbose=True,
)
```

### Task
A unit of work assigned to an agent. Describes what needs to be done and what good output looks like.

```python
from crewai import Task

research_task = Task(
    description="Research the top 5 AI agent frameworks in 2026 and their trade-offs",
    expected_output="A structured summary with framework name, use case, and honest limitations",
    agent=researcher,
)
```

### Crew
The team. Assembles agents and tasks, then executes.

```python
from crewai import Crew, Process

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,  # or Process.hierarchical
    verbose=True,
)

result = crew.kickoff()
```

### Process
- `Process.sequential` — tasks run one after another, each output feeds the next
- `Process.hierarchical` — a manager agent delegates tasks and checks quality

---

## Quickstart

See [`quickstart.py`](./quickstart.py) for a complete working two-agent crew (~50 lines).

Install:
```bash
pip install crewai crewai-tools
```

---

## When CrewAI Wins

- **Role-based workflows** — if you naturally think "I need a researcher and a writer", CrewAI maps directly to that mental model
- **Rapid prototyping** — lowest setup time of any multi-agent framework, fastest from idea to demo
- **Business process automation** — sales intelligence, content pipelines, report generation
- **Non-engineers on your team** — YAML config mode makes agents readable to non-Python people

---

## When CrewAI Loses

- **Unpredictable control flow** — if you need exact branching logic ("only call the validator if the confidence score is below 0.7"), CrewAI is awkward; use LangGraph
- **Debugging complex failures** — when a crew goes wrong, tracing *why* is harder than in LangGraph's explicit graph
- **High-frequency production systems** — monitoring tooling is less mature than LangGraph/LangSmith
- **You need structured outputs reliably** — add Pydantic `output_pydantic` on tasks, or you'll get free-form text

---

## Honest Trade-offs

| Strength | Weakness |
|---|---|
| Fastest setup of any framework | Less control over execution flow |
| Intuitive role metaphor | Debugging is harder than LangGraph |
| Good built-in tools ecosystem | Output consistency needs Pydantic enforcement |
| Active development, growing fast | Younger than LangGraph in production |

---

## The One Thing to Remember

CrewAI's superpower is the **role abstraction**. When you can describe your workflow as "I need a [role] who [does X]", CrewAI is the right tool. When you need to control *exactly* when and how each step happens, reach for LangGraph.

---

## Further Reading

- [CrewAI docs](https://docs.crewai.com)
- [CrewAI tools](https://docs.crewai.com/concepts/tools)
- [CrewAI GitHub](https://github.com/crewAIInc/crewAI)
