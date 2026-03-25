# ⚡ OpenAI Agents SDK

> "If you're already in the OpenAI ecosystem, this is the lowest-friction path to a real agent."

The OpenAI Agents SDK is a lightweight, official library for building agents on top of OpenAI models. It gives you tool use, agent handoffs, and structured output with minimal setup. No graph theory, no crew metaphors — just agents, tools, and the concept of handing work from one agent to another.

---

## The Core Idea

An agent is an LLM + a set of tools + instructions. When a task is complex, one agent can hand off to another specialist. The SDK handles the execution loop, tool calls, and handoff mechanics.

```
Triage Agent → (detects math question) → hands off to → Math Agent
Triage Agent → (detects coding question) → hands off to → Code Agent
```

It's the simplest multi-agent model: **routing**. Great for customer support, task classification, and domain-specialist systems.

---

## Key Concepts

### Agent
An LLM with instructions and tools.

```python
from agents import Agent

math_agent = Agent(
    name="Math Tutor",
    instructions="You solve mathematical problems step by step. Always show your working.",
    tools=[calculator_tool],
)
```

### Tool
A Python function decorated to be callable by an agent.

```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is 22°C and sunny."
```

### Handoff
An agent can transfer control to another agent.

```python
from agents import Agent

triage_agent = Agent(
    name="Triage",
    instructions="Route questions to the right specialist.",
    handoffs=[math_agent, coding_agent],   # Other agents this can hand off to
)
```

### Runner
Executes an agent on a task.

```python
from agents import Runner

result = Runner.run_sync(triage_agent, "What is the derivative of x²?")
print(result.final_output)
```

---

## Quickstart

See [`quickstart.py`](./quickstart.py) for a working triage agent with handoffs.

Install:
```bash
pip install openai-agents
```

---

## When OpenAI Agents SDK Wins

- **You're using OpenAI models** — designed specifically for GPT-4o and later, all features work out of the box
- **Simple to medium complexity** — you want an agent quickly without framework overhead
- **Routing workflows** — multiple specialists and a triage agent is the SDK's sweet spot
- **Official support** — it's maintained by OpenAI, so it always works with the latest models and APIs
- **Streaming + structured output** — both are first-class, requiring minimal configuration

---

## When OpenAI Agents SDK Loses

- **Non-OpenAI models** — it's built for OpenAI; Anthropic/Gemini support is limited or requires wrappers
- **Complex stateful workflows** — no native equivalent to LangGraph's checkpointing or stateful graph
- **Role-based team patterns** — CrewAI's agent + task + crew abstraction is cleaner for this
- **Deep control over execution flow** — you're working within the SDK's execution model, not defining your own graph

---

## Honest Trade-offs

| Strength | Weakness |
|---|---|
| Lowest setup friction | OpenAI ecosystem lock-in |
| Official, always up-to-date with GPT APIs | Limited stateful workflow support |
| Handoffs are elegant and simple | Less flexible than LangGraph |
| Great for routing/triage patterns | Smaller community than LangGraph/CrewAI |

---

## The One Thing to Remember

The OpenAI Agents SDK is the **official on-ramp**. If you're starting fresh, using OpenAI models, and want something working in an hour — this is it. When you outgrow it (complex state, cross-provider, production observability), migrate to LangGraph.

---

## Further Reading

- [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/)
- [OpenAI Agents SDK GitHub](https://github.com/openai/openai-agents-python)
- [Agents cookbook](https://cookbook.openai.com)
