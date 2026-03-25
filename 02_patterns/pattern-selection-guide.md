## 🗺️ Pattern Selection Guide

*With great patterns come great architectural decisions. This guide will not make them for you, but it will tell you which questions to ask.*

```mermaid
flowchart TD
    START([🎯 I need to build an agent]) --> Q1

    Q1{"Single step or
    multi-step task?"}
    Q1 -->|Single step| SIMPLE["Simple LLM call
    Maybe one tool.
    No loop needed."]
    Q1 -->|Multi-step| Q2

    Q2{"Is the path
    known in advance?"}
    Q2 -->|"Yes - clear structure"| Q3
    Q2 -->|"No - discover as you go"| REACT["⚡ ReAct Pattern
    Think → Act → Observe"]

    Q3{"Can steps run
    in parallel?"}
    Q3 -->|Yes| MULTI["🤝 Multi-Agent
    Specialised agents.
    Orchestrator manages."]
    Q3 -->|No| PAE["📋 Plan-and-Execute
    Make plan first.
    Execute sequentially."]

    REACT --> Q4
    PAE --> Q4

    Q4{"Does output
    quality matter a lot?"}
    Q4 -->|Yes| REFLECT["🪞 Add Reflection
    Critique + Revise"]
    Q4 -->|"Good enough is fine"| Q5

    REFLECT --> Q5
    Q5{"Multiple sessions
    or long-running tasks?"}
    Q5 -->|Yes| MEM["🧠 Add Memory
    Vector store or summarisation."]
    Q5 -->|No| DONE([✅ You have your pattern])
    MEM --> DONE

    style START fill:#4A90D9,color:#fff,stroke:#2171b5
    style DONE fill:#27AE60,color:#fff,stroke:#1a8a4a
    style SIMPLE fill:#BDC3C7,stroke:#95a5a6
    style REACT fill:#8E44AD,color:#fff,stroke:#6c3483
    style MULTI fill:#E67E22,color:#fff,stroke:#ca6f1e
    style PAE fill:#2980B9,color:#fff,stroke:#1a5276
    style REFLECT fill:#C0392B,color:#fff,stroke:#922b21
    style MEM fill:#16A085,color:#fff,stroke:#0e6b5e
```

---

## 📚 Pattern Quick Reference

```
┌──────────────────────────────────────────────────────────────────────┐
│                         PATTERN CHEAT SHEET                          │
├──────────────────┬──────────────────────────┬────────────────────────┤
│  PATTERN         │  USE WHEN                │  WATCH OUT FOR         │
├──────────────────┼──────────────────────────┼────────────────────────┤
│  🔄 ReAct         │  Path unknown upfront    │  Infinite loops       │
│                  │  General-purpose tasks   │  Context filling up    │
│                  │  Iterative discovery     │  Hallucinated results  │
├──────────────────┼──────────────────────────┼────────────────────────┤
│  🔗 Chain-of-     │  Maths and reasoning     │  More tokens, slower  │
│     Thought      │  Multi-constraint probs  │  Overkill for simple   │
│                  │  Accuracy over speed     │  lookups               │
├──────────────────┼──────────────────────────┼────────────────────────┤
│  🛠️  Tool Use     │  Needs external data     │  Over-permissioned    │
│                  │  World-affecting actions │  agents                │
│                  │  Anything beyond context │  Hallucinated calls    │
├──────────────────┼──────────────────────────┼────────────────────────┤
│  🪞 Reflection    │  Quality matters a lot   │  Latency and cost     │
│                  │  High-stakes outputs     │  Model may be lenient  │
│                  │  Complex writing or code │  with its own work     │
├──────────────────┼──────────────────────────┼────────────────────────┤
│  📋 Plan-and-     │  Known structure         │  Plans go stale fast  │
│     Execute      │  Parallelisable steps    │  Need replanning logic │
│                  │  Delegation needed       │  Reality differs from  │
│                  │                          │  the original plan     │
├──────────────────┼──────────────────────────┼────────────────────────┤
│  🤝 Multi-Agent   │  Genuinely large tasks   │ Exponential complexity│
│                  │  Specialisation needed   │  Silent failures       │
│                  │  Parallel execution      │  3–5× higher cost      │
├──────────────────┼──────────────────────────┼────────────────────────┤
│  🧠 Memory        │  Multi-session work      │ What to forget is as  │
│                  │  Personalisation         │  hard as what to store │
│                  │  Long-running agents     │  Retrieval strategy    │
│                  │                          │  matters enormously    │
└──────────────────┴──────────────────────────┴────────────────────────┘
```

---

## 🚀 What's Next

You now have the patterns. The vocabulary. The failure modes. The decision tree. The cheat sheet for the wall above your monitor.

What you don't have yet is working code that uses a real framework - the scaffolding that manages the loop, owns the state, routes tool calls, handles retries, produces traces you can actually debug, and requires configuring several things before anything runs.

That's Section 03.

> *"Section 03 covers the major agent frameworks: LangGraph, CrewAI, the OpenAI Agents SDK, and MCP. These frameworks are, in the words of a senior engineer who shall remain anonymous, 'like democracy - the worst possible solution except for all the other ones that were tried before them.'"*

---

<div align="center">

```
──────────────────────────────────────────────────────────────────
  Section 02 complete.   7 patterns.   No panicking.
──────────────────────────────────────────────────────────────────
```

*github.com/ayu1712/Guide-AI-Agents*

</div>