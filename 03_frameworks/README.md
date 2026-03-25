# 🛸 03 - Frameworks

> "Don't panic. There are only five frameworks you need to know. Well, four. Maybe three. It depends."

The AI agent framework ecosystem moves fast. This section gives you an honest map of the landscape - what each framework actually is, what it's best at, and crucially, **when to skip a framework entirely**.

---

## The Big Picture

A framework is just scaffolding. It handles the plumbing - tool calling, state management, agent loops, memory - so you can focus on what your agent actually does. The trap is thinking the framework *is* the agent. It isn't. The framework is the stage. Your prompts, tools, and logic are the show.

The second trap: framework FOMO. New ones appear weekly. Most are wrappers around the same ideas. The ones in this section have real production usage, real communities, and real staying power as of 2026.

---

## Framework Comparison at a Glance

| Framework | Mental model | Best for | Learning curve | Production-ready |
|---|---|---|---|---|
| **LangGraph** | Graph of nodes + state | Complex stateful workflows | ★★★★☆ | ✅ Battle-tested |
| **CrewAI** | Team of role-playing agents | Quick multi-agent prototypes | ★★☆☆☆ | ✅ Yes |
| **AutoGen** | Agents talking to each other | Conversational multi-agent | ★★★☆☆ | ⚠️ Maintenance mode |
| **OpenAI Agents SDK** | Simple agent + tools + handoffs | OpenAI-stack projects | ★★☆☆☆ | ✅ Yes |
| **No framework** | Raw LLM calls + your own loop | Full control, simple agents | ★☆☆☆☆ | ✅ Often best |

---

## How to Choose

Answer these questions in order:

**1. Do you need multiple agents collaborating?**
- No → Start with [No Framework](./no-framework/) or [OpenAI Agents SDK](./openai-agents-sdk/)
- Yes → Keep going

**2. Do you need explicit, debuggable control over execution flow?**
- Yes → [LangGraph](./langgraph/) - it's a state machine, you define every transition
- No → Keep going

**3. Do you want role-based agents (Researcher, Writer, QA) with task delegation?**
- Yes → [CrewAI](./crewai/) - fastest path to a working crew
- No → [AutoGen](./autogen/) if you want agents that talk through problems conversationally

**4. Are you already deep in the OpenAI ecosystem?**
- Yes → [OpenAI Agents SDK](./openai-agents-sdk/) - minimal overhead, native tool use

---

## The Uncomfortable Truth

From a senior engineer who's shipped real agent systems:

> "Framework selection is a 2-hour decision. Infrastructure building is a 2-month journey. Spend your time where it matters."

The patterns - ReAct loops, tool use, state management, retries, observability - are the same across every framework. If you understand those (see [02_patterns](../02_patterns/)), switching frameworks is annoying, not hard.

**Start with the simplest thing that could work. Add a framework when the plumbing gets painful.**

---

## What's in Each Folder

Each framework folder contains:

```
langgraph/
├── README.md         ← What it is, when to use it, honest trade-offs
├── quickstart.py     ← Working example in ~50 lines
├── concepts.md       ← Key concepts explained (nodes, state, edges, etc.)
└── when-not-to-use.md ← When to pick something else
```

---

## Sections

- [LangGraph](./langgraph/) - Graph-based stateful workflows
- [CrewAI](./crewai/) - Role-based agent teams
- [AutoGen](./autogen/) - Conversational multi-agent systems
- [OpenAI Agents SDK](./openai-agents-sdk/) - Lightweight agents for the OpenAI stack
- [No Framework](./no-framework/) - When the best framework is no framework

---

*Last updated: March 2026*
