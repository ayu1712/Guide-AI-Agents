# CrewAI — Core Concepts

A breakdown of every building block in CrewAI, and how they fit together.

---

## The Mental Model

CrewAI models work the way a consulting firm does. You hire specialists, give them a brief, and they coordinate to produce a deliverable. The key insight: agents work better when they have a **clear role identity**. A researcher who *knows* they're a researcher asks better questions than a generic assistant told to "research things".

The role, goal, and backstory aren't just labels — they're injected into the system prompt. They shape how the underlying LLM behaves.

---

## Agent

An agent is an autonomous worker with a defined identity and a set of capabilities.

```python
from crewai import Agent

analyst = Agent(
    role="Financial Data Analyst",
    goal="Extract actionable insights from financial data with rigorous accuracy",
    backstory=(
        "You have 15 years of experience analysing public markets. "
        "You distrust hype and look for evidence in the numbers. "
        "You always state confidence levels alongside conclusions."
    ),
    tools=[search_tool, calculator_tool],
    llm="claude-sonnet-4-5",       # Defaults to gpt-4o if not set
    verbose=True,                   # Print reasoning steps
    allow_delegation=False,         # Can this agent delegate to others?
    max_iter=10,                    # Max reasoning iterations before forced stop
    memory=True,                    # Enable agent-level memory
)
```

### The Backstory Is Prompt Engineering

The `backstory` field is pure prompt injection. "You distrust hype" and "You always state confidence levels" are behavioural instructions dressed up as biography. A well-crafted backstory is the difference between a generic LLM response and a response that actually feels like a specialist.

Spend real time on backstories. They matter more than most settings.

### allow_delegation

When `True`, an agent can ask other agents in the crew for help. Use carefully — it adds latency and can cause unexpected conversations between agents.

---

## Task

A task is a unit of work. It describes what needs to be done, what good output looks like, and who should do it.

```python
from crewai import Task

analysis_task = Task(
    description=(
        "Analyse the provided Q3 earnings report for {company_name}. "
        "Identify: revenue trend, margin changes, and the top 3 risks. "
        "Support every claim with a specific number from the report."
    ),
    expected_output=(
        "A structured analysis with three sections: Revenue Trend, "
        "Margin Analysis, and Top 3 Risks. Each section max 150 words. "
        "Every claim cited with a specific figure."
    ),
    agent=analyst,
    output_file="analysis.md",      # Optional: write output to a file
    output_pydantic=AnalysisReport, # Optional: enforce structured output
    context=[prior_task],           # Optional: include outputs from other tasks
)
```

### expected_output Is a Quality Spec

The `expected_output` field sets the bar for what "done" looks like. Be specific — length constraints, format requirements, citation requirements. Vague expected output → vague agent output.

### Pydantic Output Enforcement

If you need reliable structured data (not free-form prose), use `output_pydantic`:

```python
from pydantic import BaseModel
from typing import List

class Risk(BaseModel):
    description: str
    severity: str  # "high", "medium", "low"
    evidence: str

class AnalysisReport(BaseModel):
    revenue_trend: str
    margin_analysis: str
    risks: List[Risk]

analysis_task = Task(
    ...,
    output_pydantic=AnalysisReport,
)

result = crew.kickoff()
report: AnalysisReport = result.pydantic  # Typed output
```

This is the most reliable way to get structured data out of CrewAI.

---

## Tools

Tools are functions agents can call. CrewAI ships a tools library, or you can write your own.

### Built-in Tools

```python
from crewai_tools import (
    SerperDevTool,       # Web search via Serper
    WebsiteSearchTool,   # RAG over a website
    FileReadTool,        # Read local files
    CodeInterpreterTool, # Execute Python code
    PDFSearchTool,       # RAG over a PDF
)

search = SerperDevTool()
file_reader = FileReadTool()
```

### Custom Tools

```python
from crewai.tools import BaseTool

class DatabaseQueryTool(BaseTool):
    name: str = "Query Database"
    description: str = "Query the internal database for customer records"
    
    def _run(self, query: str) -> str:
        # Your implementation
        return run_sql_query(query)
```

Or use the decorator shorthand:

```python
from crewai import tool

@tool("Fetch Stock Price")
def get_stock_price(ticker: str) -> str:
    """Fetch the current price for a stock ticker symbol."""
    return fetch_from_api(ticker)
```

---

## Crew

The crew assembles agents and tasks into a runnable team.

```python
from crewai import Crew, Process

crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.sequential,
    verbose=True,
    memory=True,           # Shared memory across agents
    max_rpm=10,            # Rate limit API calls
    output_log_file="run.log",
)

# Basic run
result = crew.kickoff()

# With input variables (used in task descriptions via {variable})
result = crew.kickoff(inputs={"company_name": "Anthropic", "quarter": "Q3 2025"})
```

---

## Process

Process controls how tasks are executed.

### Sequential (default)

Tasks run one after another. Each task's output is available to subsequent tasks via `context`.

```
Task 1 → Task 2 → Task 3 → Done
```

Good for: linear workflows where each step depends on the previous.

### Hierarchical

A manager LLM oversees the crew. It assigns tasks, reviews outputs, and can request revisions before accepting.

```python
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.hierarchical,
    manager_llm="claude-opus-4-5",   # Use a capable model as manager
)
```

Good for: quality-sensitive workflows where you want automatic revision loops.

---

## Memory

CrewAI supports three types of memory, all optional.

| Type | What it stores | Scope |
|---|---|---|
| Short-term | Recent interactions in the run | Current crew execution |
| Long-term | Learnings across multiple runs (SQLite) | Persistent across runs |
| Entity | Facts about people, companies, concepts | Persistent across runs |

Enable all three with `memory=True` on the Crew. Enable per-agent with `memory=True` on the Agent.

---

## Kickoff Variants

```python
# Synchronous
result = crew.kickoff()

# Asynchronous
result = await crew.kickoff_async()

# Process multiple input sets
results = crew.kickoff_for_each(inputs=[
    {"company": "Apple"},
    {"company": "Google"},
    {"company": "Microsoft"},
])

# Async parallel processing of multiple inputs
results = await crew.kickoff_for_each_async(inputs=[...])
```

`kickoff_for_each` is powerful for batch jobs — e.g. analysing 20 companies with the same crew.

---

## The Output Object

`crew.kickoff()` returns a `CrewOutput` object:

```python
result = crew.kickoff()

result.raw           # String: the final task's raw output
result.pydantic      # Pydantic model: if output_pydantic was set on the last task
result.json_dict     # Dict: if output_json was set on the last task
result.tasks_output  # List[TaskOutput]: output from every task
result.token_usage   # Token counts for the run
```

---

## Common Pitfalls

**Agents hallucinate without constraints.** Set `max_iter`, use `output_pydantic`, and write specific `expected_output`. Vague tasks produce vague results.

**Sequential tasks without context don't share information.** If Task 2 needs Task 1's output, set `context=[task_1]` on Task 2. Without it, Task 2 doesn't know what Task 1 found.

**allow_delegation=True in sequential flows creates loops.** Agents delegating to each other in a sequential process can spin. Keep `allow_delegation=False` unless you specifically need it.

**Backstories get long and expensive.** Every agent's backstory is in every API call that agent makes. Keep backstories under 100 words.

---

## What to Read Next

- [CrewAI agents docs](https://docs.crewai.com/concepts/agents)
- [CrewAI tasks docs](https://docs.crewai.com/concepts/tasks)
- [CrewAI tools library](https://docs.crewai.com/concepts/tools)
- [CrewAI memory](https://docs.crewai.com/concepts/memory)
