# 🚀 Section 02: Patterns
### *The Hitchhiker's Guide to AI Agents*

> *"In the beginning, the Universe was created.*
> *This has made a lot of people very angry and been widely regarded as a bad move.*
> *Similarly, in the beginning, AI agents had no patterns. Someone eventually wrote a `while` loop.*
> *This has made a lot of things possible and a lot of production systems very unstable."*

---

<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    Don't Panic.                                                  ║
║                                                                  ║
║    This section contains seven patterns.                         ║
║    All seven are variations of the same idea.                    ║
║    That idea is: let the model think, then do something,         ║
║    then think about what it did.                                 ║
║                                                                  ║
║    Everything else is commentary.                                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

</div>

---

## 📖 Table of Contents

| # | Pattern | Difficulty | The Vibe |
|:---:|:--------|:----------:|:---------|
| [01](#01-the-react-loop) | 🔄 The ReAct Loop | 🟢 Beginner | *Think. Act. Observe. Repeat until done or defeated.* |
| [02](#02-chain-of-thought) | 🔗 Chain-of-Thought | 🟢 Beginner | *Talk to yourself. It helps. Seriously.* |
| [03](#-pattern-03-tool-use) | 🛠️ Tool Use | 🟡 Intermediate | *Give it hands. Then hide the delete button.* |
| [04](#04-reflection--self-critique) | 🪞 Reflection & Self-Critique | 🟡 Intermediate | *The agent argues with itself and somehow wins.* |
| [05](#05-plan-and-execute) | 📋 Plan-and-Execute | 🟡 Intermediate | *Ready. Aim. Discover the plan was wrong. Adapt.* |
| [06](#06-multi-agent-systems) | 🤝 Multi-Agent Systems | 🔴 Advanced | *It takes a village. The village has a bug tracker.* |
| [07](#07-memory-patterns) | 🧠 Memory Patterns | 🔴 Advanced | *Remembering is engineering. Forgetting is an architectural choice.* |

---

## 🌌 Preface: Why Patterns?

You would not build a house by randomly stacking bricks and hoping for the best. You might get *something*, but it probably wouldn't have a roof where you wanted one, and it would collapse at an inconvenient moment — probably during a demo in front of the very people whose funding you were hoping to secure.

Patterns are the architectural blueprints of agent design. They represent the accumulated wisdom of many engineers who built things, watched them collapse, rebuilt them slightly differently, and eventually wrote a blog post titled *"What We Learned Building Agents at Scale"* — which got 47,000 views and fourteen comments saying *"but have you considered LangGraph?"*

The remarkable thing about agent patterns is that there are not very many of them. The field, for all its noise and activity and competing frameworks and conference talks, has converged on roughly **seven** fundamental patterns, recombined endlessly in ways that are either clever or unnecessarily complicated depending on who you ask and whether they maintain one of the frameworks being discussed.

This section covers all seven. By the end, you will be able to look at any agent system — no matter how elaborate its architecture diagram, no matter how many nodes its state graph has, no matter how much YAML was required to configure it — and identify which patterns it's using.

That's the superpower on offer here. It's not glamorous. But it's real.

> 💡 **A gentle reminder before we begin:** Every pattern in this section is, at its core, a variation on the same idea — *let the model decide what to do next, check if it worked, and go again*. The variations are in the details. The details, however, matter enormously. This is true of most things.

---

<br>