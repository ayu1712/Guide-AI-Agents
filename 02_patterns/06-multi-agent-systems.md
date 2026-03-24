## 🤝 Pattern 06 · Multi-Agent Systems

> *"No single agent can know everything.*
> *This is not a limitation. This is an excuse to build more agents."*
> *— Everyone who has ever written a multi-agent paper*

### What It Is

Multi-agent systems are collections of agents that collaborate on a task — each specialised, each with its own tools and instructions, each contributing to a goal none of them could achieve alone.

Think of it as the difference between asking one person to design, build, wire, and plumb your house versus hiring specialists who know how to coordinate. The specialists do better work. They also introduce coordination overhead, miscommunication, and the occasional wall that turns out to be load-bearing in a way the architect forgot to mention to the builder.

---

### 🏗️ The Four Multi-Agent Topologies

#### Pattern A: Orchestrator–Subagent *(The Manager)*

```
                    ┌──────────────────────────┐
                    │      🎯 ORCHESTRATOR       │
                    │   ─────────────────────   │
                    │   Receives the goal        │
                    │   Makes a plan             │
                    │   Delegates work           │
                    │   Synthesises results      │
                    └────────────┬─────────────┘
                                 │  delegates tasks
               ┌─────────────────┼─────────────────┐
               ▼                 ▼                 ▼
      ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
      │ 🔍 RESEARCH   │  │ ✍️  WRITER     │  │ ✅ CHECKER    │
      │    Agent      │  │    Agent      │  │    Agent      │
      │ ────────────  │  │ ────────────  │  │ ────────────  │
      │ web_search    │  │ draft()       │  │ verify()      │
      │ read_docs     │  │ revise()      │  │ test()        │
      └───────────────┘  └───────────────┘  └───────────────┘
```

**Best for:** Tasks that decompose into distinct specialisations. Research-write-verify is the canonical example. Everyone knows who is responsible for what. Works well until the orchestrator's context fills up, which it will.

---

#### Pattern B: Peer-to-Peer *(The Debate)*

```
    ┌─────────────────────┐              ┌─────────────────────┐
    │    🔵 AGENT A         │ ◄─ debate ─► │     🔴 AGENT B        │
    │    "The Bull"         │              │     "The Bear"        │
    │                     │              │                     │
    │  Argues FOR the      │              │  Argues AGAINST the  │
    │  proposal            │              │  proposal            │
    └─────────────────────┘              └─────────────────────┘
                │                                   │
                └─────────────────┬─────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │   ⚖️  JUDGE AGENT  │
                         │   Makes the       │
                         │   final call      │
                         └──────────────────┘
```

**Best for:** High-stakes decisions, content verification, risk analysis. Two agents arguing opposite sides produces better outcomes than one agent holding both positions simultaneously. The debate transcripts are also entertaining. Both agents will be more confident than they should be. This too mirrors human behaviour.

---

#### Pattern C: Pipeline *(The Assembly Line)*

```
    Raw Input
       │
       ▼
  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ Agent 1  │───►│ Agent 2  │───►│ Agent 3  │───►│ Agent 4  │
  │  Parse   │    │  Enrich  │    │ Analyse  │    │  Format  │
  └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                        │
                                                        ▼
                                                  Final Output
```

**Best for:** Data processing, content pipelines, document transformation. Each agent does one thing and hands off. Simple, predictable, debuggable. The failure mode is that an error in Agent 2 propagates silently through Agents 3 and 4 until it emerges as a puzzling output at the very end.

---

#### Pattern D: Hierarchical *(The Org Chart)*

```
                    ┌─────────────────┐
                    │   🏛️ CEO Agent   │
                    │  Top-level goal  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │ 👔 Mgr A │   │ 👔 Mgr B │   │ 👔 Mgr C │
       └────┬─────┘   └────┬─────┘   └────┬─────┘
            │              │              │
         Workers        Workers        Workers
```

**Best for:** Very large, complex tasks with natural team boundaries. Mirrors how human organisations scale. Also mirrors how human organisations fail — miscommunication between layers, diffused responsibility, managers who don't know what the workers are actually doing. Build this when you genuinely need it, not before.

---

### 💬 Agent Communication

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  METHOD 1: Shared Memory         METHOD 2: Direct Messages      │
│  ─────────────────────────       ─────────────────────────────  │
│                                                                  │
│  Agent A writes to store   vs    Agent A sends a structured     │
│  Agent B reads from store        message directly to Agent B    │
│                                                                  │
│  Asynchronous.                   Synchronous.                   │
│  Any agent can read.             Targeted. Point-to-point.      │
│  Good for shared state.          Good for explicit handoffs.    │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  METHOD 3: Blackboard                                            │
│  ──────────────────────                                          │
│                                                                  │
│  All agents read from and write to a shared "blackboard."       │
│  Agents post findings. Others build on them.                    │
│  No single agent owns communication; anyone can contribute.     │
│                                                                  │
│  Elegant in theory. Requires careful design in practice.        │
│  Also requires someone to decide what gets erased.              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

### ⚠️ The Multi-Agent Danger Zone

Before building a multi-agent system, answer these questions honestly:

```
❓  Could a single agent with a well-written system prompt do this?
    (The answer is yes more often than people admit.)

❓  Do I have monitoring for every agent, or will failures be silent?
    (Silent failures in multi-agent systems are silent and expensive.)

❓  What happens when Agent B produces output Agent C cannot use?
    (This will happen. What is the recovery path?)

❓  Have I budgeted for 3–5× more API costs than a single-agent solution?
    (Multi-agent systems call the model many times. This costs money.)

❓  Who is responsible when the system as a whole produces something wrong?
    (Distributed responsibility means distributed blame. Plan for this.)
```

> 🚨 **The Rule of Thumb:** Build the single-agent version first. Get it working. Then, and only then, ask whether decomposing it into specialised agents would meaningfully improve the result. Sometimes yes. Less often than the architecture diagrams suggest.
