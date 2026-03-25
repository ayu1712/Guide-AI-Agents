# 🌌 Chapter 4: The Galaxy of Agent Types

> *"Space is big. Really big. You just won't believe how vastly, hugely, mind-bogglingly big it is."*
> - Douglas Adams, on space, but also, inadvertently, on the AI agent taxonomy landscape of 2026.

---

The known universe of AI agents, much like the actual universe, is expanding faster than anyone can map it, contains a disturbing number of things that look similar from a distance but will kill you if you get close, and is populated by entities that are either very intelligent or doing an extremely convincing impression of it.

There is, currently, no agreed-upon classification system. Researchers use one taxonomy. Framework developers use another. LinkedIn thought leaders use a third, which is mostly made up. Startup pitch decks use all three simultaneously while gesturing at a slide that says **"Agentic AI"** in very large letters.

This chapter is an attempt to impose order on chaos. It will not fully succeed. But it will give you enough of a map that when someone at a conference says *"we're building a multi-agent hierarchical orchestration system with episodic memory and tool-augmented reasoning,"* you will know what they mean, whether it's impressive, and whether you should get another drink first.

---

## 🗺️ The Map of Known Agent Space

Before we explore each type individually, here is an overview of the full taxonomy, arranged by increasing complexity, autonomy, and probability of causing you a production incident:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    THE GALAXY OF AI AGENT TYPES                             ║
║                 (Not to scale. Nothing is ever to scale.)                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   COMPLEXITY │ LOW ──────────────────────────────────────────────── HIGH    ║
║              │                                                               ║
║              │  🪨          🔧          🔄          🧠          🌐          ║
║              │                                                               ║
║              │ Simple    Tool-Use    ReAct     Cognitive   Autonomous       ║
║              │  Agent     Agent      Agent      Agent       Agent           ║
║              │                                                               ║
║   AUTONOMY   │ ████░░░░  ████████░  ████████  █████████  ██████████        ║
║              │                                                               ║
║   DANGER*    │ 🟢         🟡         🟡         🟠          🔴              ║
║              │                                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  * "Danger" = likelihood of doing something you didn't quite ask for        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

> 🚨 **FIELD NOTE:** The map is not the territory. The territory is a GitHub repository with 47 open issues, a README that says "work in progress," and a last commit from three weeks ago that says *"fix: actually fix it this time."*

---

## 🪨 Type 1: The Simple Agent

### *"It Does One Thing. Admirably."*

The Simple Agent is the hydrogen atom of the agent universe. It is the most basic unit. It is, if we are being honest, barely an agent at all - but we include it here because it works, it's everywhere, and dismissing it because it lacks sophistication would be like dismissing bread because it's not a soufflé.

```
┌─────────────────────────────────────────────────────────────┐
│                   THE SIMPLE AGENT                          │
│                                                             │
│    USER INPUT                                               │
│        │                                                    │
│        ▼                                                    │
│   ┌─────────┐     calls      ┌──────────────┐              │
│   │   LLM   │ ─────────────► │  ONE TOOL    │              │
│   │  Brain  │ ◄───────────── │(maybe two)   │              │
│   └─────────┘    returns     └──────────────┘              │
│        │                                                    │
│        ▼                                                    │
│    RESPONSE                                                 │
│                                                             │
│  No loop. No memory. No drama. Blessed simplicity.         │
└─────────────────────────────────────────────────────────────┘
```

**What it does:** Takes input, calls one or two tools, returns output. Done. Goes home. Does not keep you up at night.

**What it cannot do:** Adapt. Retry. Remember last Tuesday. Recover gracefully from unexpected situations. Feel existential dread. (This last one is a feature.)

**Real-world examples:**

| Agent | What it does | Tool(s) used |
|-------|-------------|--------------|
| 🔍 Knowledge Base Bot | Answers questions from internal docs | `search_docs` |
| 🌤️ Weather Summary | Gets weather and formats it nicely | `get_weather` |
| 💱 Currency Converter | Converts currencies on request | `exchange_rate_api` |
| 📋 Form Filler | Extracts data from text into a form | `parse_structured` |

**When to use it:**
- You have a well-defined, bounded task
- The task doesn't require multiple steps
- You would like to sleep soundly
- You are not trying to impress a VC

**When NOT to use it:**
- The task requires the agent to notice that its first approach didn't work
- The task has more than one meaningful decision point
- You want to call it an "agentic AI system" on your website

> 💬 **The Guide says:** *"The Simple Agent is, per capita, responsible for more successful production deployments than any other agent type. It is also responsible for zero of the conference talks. These two facts are not unrelated."*

---

## 🔧 Type 2: The Tool-Use Agent

### *"Give It Enough Tools and It Will Build a House. Or Try To."*

The Tool-Use Agent is what most people mean when they say "AI agent" in a product demo. It has access to a rich collection of tools - web search, code execution, file systems, APIs, databases - and it selects which ones to use based on what the task requires.

The key distinction from the Simple Agent is breadth: not one or two tools, but a whole belt of them, and the intelligence to pick the right one for the moment.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE TOOL-USE AGENT                               │
│                                                                     │
│                        ┌─────────────┐                             │
│                        │  TASK/GOAL  │                             │
│                        └──────┬──────┘                             │
│                               │                                     │
│                               ▼                                     │
│                        ┌─────────────┐                             │
│                        │  LLM BRAIN  │ ◄── System Prompt           │
│                        │ "What tool  │     (who it is,             │
│                        │  do I need?"│      what it has)           │
│                        └──────┬──────┘                             │
│                               │                                     │
│            ┌──────────────────┼──────────────────┐                │
│            │                  │                  │                 │
│            ▼                  ▼                  ▼                 │
│      ┌──────────┐      ┌──────────┐      ┌──────────┐            │
│      │ 🌐 Web   │      │ 💻 Code  │      │ 📁 Files │            │
│      │ Search   │      │ Execute  │      │ R/W      │            │
│      └──────────┘      └──────────┘      └──────────┘            │
│            │                  │                  │                 │
│            └──────────────────┴──────────────────┘                │
│                               │                                     │
│                               ▼                                     │
│                      ┌──────────────┐                              │
│                       │   RESPONSE   │                              │
│                      └──────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

**The MCP Revolution** 🔌

A development worth pausing on: the Model Context Protocol (MCP), introduced by Anthropic, is to tool-use agents what USB was to computers. Before USB, every peripheral had its own connector, its own driver, its own complete chaos. After USB, things just... plugged in.

MCP does the same for agent tools. Instead of every agent framework inventing its own tool format, you implement an MCP server once and your tools work everywhere. This is either the most boring-sounding important development in AI agent infrastructure, or the most important-sounding boring one. Either way, it matters.

```
     BEFORE MCP                          AFTER MCP
     ──────────                          ─────────

  Framework A ──► Tool A's format     Agent ──► MCP ──► Any Tool
  Framework B ──► Tool B's format              │
  Framework C ──► Tool C's format              ├──► Web Search
  Framework D ──► Tool D's format              ├──► Databases  
  Framework E ──► Tool E's format              ├──► File Systems
  [six more] ──► [six more formats]            ├──► APIs
                                               └──► Basically Anything
  Result: Chaos                        Result: Slightly less chaos
```

**The Blessing and the Curse** 🎭

The more tools you give an agent, the more powerful it becomes. Also, the more likely it is to pick the wrong one, chain them in unexpected ways, or discover a creative combination that technically achieves the goal but not at all in the way you intended.

> ⚠️ **Cautionary Tale:** A tool-use agent given access to `send_email`, `search_contacts`, and `compose_message` will, when asked to "follow up with all the leads from last month," do exactly that. Whether "all the leads" means 12 people or 4,000 depends on your database. This is why confirmation steps exist. This is why you add confirmation steps. Before the demo. Not after.

---

## 🔄 Type 3: The ReAct Agent

### *"It Thinks, Therefore It Tries Again"*

The ReAct Agent is where things get genuinely interesting. Named after **Re**asoning + **Act**ing (a naming convention that only a researcher could love), the ReAct Agent runs in a loop. It thinks about what to do. It does it. It looks at what happened. It thinks again. It does something else. It continues until it's finished, or until it's not.

This is the dominant pattern. This is the workhorse. This is the agent type that, more than any other, deserves the name.

```
╔═══════════════════════════════════════════════════════════════╗
║                  THE ReAct LOOP                               ║
║                                                               ║
║                                                               ║
║    ┌──────────────────────────────────────────────────┐      ║
║    │                                                  │      ║
║    │   ┌─────────┐    THOUGHT                        │      ║
║    │   │         │   "I need to find X.              │      ║
║    │   │   LLM   │    Let me search."                │      ║
║    │   │         │         │                         │      ║
║    │   └─────────┘         │                         │      ║
║    │        ▲              ▼                         │      ║
║    │        │         ACTION                         │      ║
║    │        │        search("X")                     │      ║
║    │        │              │                         │      ║
║    │        │              ▼                         │      ║
║    │        │       OBSERVATION                      │      ║
║    │        │      "Results returned.                │      ║
║    │        │       Hmm, not quite right."           │      ║
║    │        │              │                         │      ║
║    │        └──────────────┘                         │      ║
║    │            (loop continues)                     │      ║
║    └──────────────────────────────────────────────────┘      ║
║                         │                                     ║
║                         ▼ (eventually)                        ║
║                    FINAL ANSWER                               ║
║               (or token limit reached,                        ║
║                whichever comes first)                         ║
╚═══════════════════════════════════════════════════════════════╝
```

**The Actual Transcript** 📝

To make this concrete, here is a lightly dramatised but technically accurate example of a ReAct agent working through a task. The task: *"Find the current CEO of OpenAI and their educational background."*

```
🤔 THOUGHT: I need to find the current CEO of OpenAI. I'll search for this.

🔧 ACTION: web_search("current CEO of OpenAI 2026")

👁️ OBSERVATION: Results indicate Sam Altman is the CEO, but wait -
               there's something about a brief firing in November 2023.
               Let me get more current information.

🤔 THOUGHT: The situation seems to have changed. Let me look for the
            most recent status specifically.

🔧 ACTION: web_search("Sam Altman OpenAI CEO status 2026")

👁️ OBSERVATION: Sam Altman was reinstated as CEO. He is currently CEO.

🤔 THOUGHT: Good. Now I need his educational background.

🔧 ACTION: web_search("Sam Altman education background university")

👁️ OBSERVATION: Attended Stanford. Dropped out. Classic.

🤔 THOUGHT: I have enough information to answer the question.

✅ FINAL ANSWER: Sam Altman is the current CEO of OpenAI. He attended
                Stanford University, which he left without completing
                his degree to pursue Y Combinator. He later became
                its president before joining OpenAI.
```

Notice what happened there. The agent found a complication (the brief firing), *decided on its own that this warranted further investigation*, did further investigation, and incorporated the new information. No human prompted it to do that. The loop handled it.

This is the magic. And the magic is just a while loop with a language model inside it, which is either deeply profound or deeply deflating depending on your philosophical disposition.

**When ReAct agents fail** 💀

```
COMMON FAILURE MODES
────────────────────

😵 THE INFINITE LOOP
   Agent calls the same tool with the same arguments
   because each failure confirms the next step is:
   call the same tool with the same arguments.
   Fix: max_iterations, please.

🌀 THE GARDEN PATH
   Agent convinces itself it's making progress
   while drifting steadily away from the actual goal.
   Fix: better system prompts, human checkpoints.

💭 THE HALLUCINATED OBSERVATION
   Agent "observes" what the tool *should* have returned
   instead of waiting for what it *actually* returned.
   This is deeply spooky when it happens.
   Fix: structured tool outputs, output validation.

📚 CONTEXT OVERFLOW
   Task was too long. Agent forgot the original goal.
   Is now doing something tangentially related.
   Fix: summarisation, memory management, humility.
```

---

## 🧠 Type 4: The Cognitive / Reflective Agent

### *"It Checks Its Own Work, Which Is More Than Most Humans Do"*

The Cognitive Agent does something that sounds simple but is, in practice, extraordinary: **it thinks about its own thinking.**

After generating a response or completing a step, it asks itself - or another model asks it - *"Was that any good? Could it be better? Did I miss something obvious?"* Then it revises.

This pattern goes by many names: Reflection, Self-Critique, Constitutional AI-adjacent reasoning, or, in more excitable papers, "metacognition." Whatever you call it, the results are consistently better than single-pass generation, which has led to the uncomfortable realisation that a model asking itself "wait, is this actually correct?" is more reliable than a model that doesn't.

```
┌──────────────────────────────────────────────────────────────────┐
│              THE REFLECTION LOOP                                  │
│                                                                   │
│   TASK ──► GENERATE ──► DRAFT OUTPUT                            │
│                              │                                    │
│                              ▼                                    │
│                    ┌─────────────────┐                           │
│                    │   CRITIC LLM    │                           │
│                    │   (same or      │                           │
│                    │    different    │                           │
│                    │    model)       │                           │
│                    │                 │                           │
│                    │ "This is wrong  │                           │
│                    │  about X. Also  │                           │
│                    │  missing Y.     │                           │
│                    │  Could be       │                           │
│                    │  clearer on Z." │                           │
│                    └────────┬────────┘                           │
│                             │                                     │
│                             ▼                                     │
│                     REVISE OUTPUT                                │
│                             │                                     │
│                             ▼                                     │
│                  Good enough? ──NO──► back to CRITIC             │
│                       │                                           │
│                      YES                                          │
│                       │                                           │
│                       ▼                                           │
│                 FINAL OUTPUT                                      │
│             (better than the first draft,                        │
│              as first drafts usually are)                        │
└──────────────────────────────────────────────────────────────────┘
```

**The Two-Model Variant** 🎭

Some architectures use two separate models: a **Generator** that produces output, and a **Critic** that evaluates it. This is not unlike having a writer and an editor - the writer is optimistic about their work; the editor is not.

```
  GENERATOR MODEL               CRITIC MODEL
  ───────────────               ────────────
  "Here is a solution           "This solution has three
   to your problem."             problems. First..."
         │                              │
         │         REVISION             │
         └──────────────────────────────┘
                 (several rounds)
                       │
                       ▼
              ACTUALLY GOOD OUTPUT
```

The interesting discovery from this approach is that the critic and generator don't have to be good at the same things. A smaller, cheaper model can often be a very effective critic of a larger model's output. This has implications for cost, for latency, and for the professional self-esteem of large language models, which we will not speculate on here.

> 🧪 **Field Observation:** Agents with reflection loops produce measurably better output on complex tasks. They also cost more and take longer. Whether this tradeoff is worth it depends on your task, your budget, and how wrong you can afford to be.

---

## 🌐 Type 5: The Multi-Agent System

### *"Many Minds, One Task, Infinite Coordination Overhead"*

Multi-Agent Systems are what you build when a task is too big for one agent, too complex for one context window, or when you have been seduced by the idea that the solution to your AI problems is *more AI*.

The core idea: instead of one agent doing everything, you have multiple specialised agents, each responsible for a part of the task, coordinated by an orchestrator.

```
╔══════════════════════════════════════════════════════════════════╗
║              MULTI-AGENT SYSTEM TOPOLOGY                         ║
║                                                                   ║
║    ┌──────────────────────────────────────┐                      ║
║    │         ORCHESTRATOR AGENT           │                      ║
║    │   "I manage the other agents.        │                      ║
║    │    I break down tasks.               │                      ║
║    │    I synthesise results.             │                      ║
║    │    I am, technically, in charge."    │                      ║
║    └──────────────────────────────────────┘                      ║
║           │              │              │                         ║
║           ▼              ▼              ▼                         ║
║    ┌──────────┐   ┌──────────┐   ┌──────────┐                   ║
║    │ RESEARCH │   │  WRITER  │   │  CRITIC  │                   ║
║    │  AGENT   │   │  AGENT   │   │  AGENT   │                   ║
║    │          │   │          │   │          │                   ║
║    │ Searches │   │ Drafts   │   │ Reviews  │                   ║
║    │ Verifies │   │ Formats  │   │ Improves │                   ║
║    │ Cites    │   │ Polishes │   │ Argues   │                   ║
║    └──────────┘   └──────────┘   └──────────┘                   ║
║           │              │              │                         ║
║           └──────────────┴──────────────┘                        ║
║                          │                                        ║
║                          ▼                                        ║
║                   SYNTHESISED OUTPUT                              ║
╚══════════════════════════════════════════════════════════════════╝
```

**Three Topologies Worth Knowing** 🗺️

Multi-agent systems come in a few common shapes:

```
TOPOLOGY 1: PIPELINE (Sequential)
──────────────────────────────────

 Agent A ──► Agent B ──► Agent C ──► Output

 Each agent does its job and hands off to the next.
 Like an assembly line. Fast. Brittle. An error
 in Agent A affects everything downstream.

 Best for: Content pipelines, data processing,
           tasks with clear sequential phases.


TOPOLOGY 2: HIERARCHICAL
─────────────────────────

        Orchestrator
        /     |      \
    Agent A  Agent B  Agent C
       |
   Sub-Agent A1

 A manager delegates. Agents report back.
 Can handle complex, branching tasks.
 Communication overhead grows quickly.

 Best for: Complex research, software development,
           anything that needs a project manager.


TOPOLOGY 3: COLLABORATIVE / DEBATE
───────────────────────────────────

  Agent A ◄──────► Agent B
      \              /
       \            /
        ──► Merge ◄──

 Agents work in parallel, discuss, challenge
 each other, and synthesise a joint output.
 Expensive. Surprisingly effective for
 hard reasoning tasks.

 Best for: Decision-making, adversarial review,
           situations where being wrong is costly.
```

**The Uncomfortable Truth About Multi-Agent Systems** 🙈

Multi-agent systems are powerful. They are also, without exception, more complex to build, debug, and maintain than single-agent systems. The following table is honest about this:

| Feature | Single Agent | Multi-Agent |
|---------|-------------|-------------|
| 🏗️ Setup complexity | Low | High |
| 🐛 Debugging difficulty | Manageable | Send help |
| 💰 Cost per task | Low | Multiplied by agents |
| 🔍 Where things go wrong | One place | Everywhere |
| 🎯 Task ceiling | Limited | High |
| 😴 Your sleep quality | Good | Depends |

> 🔬 **Research Note:** Multi-agent systems outperform single agents on complex, multi-step tasks. Single agents outperform multi-agent systems on simple tasks, because multi-agent systems have *coordination overhead*, which is the technical term for "the agents have to talk to each other, and that takes time and tokens and can go wrong."

---

## 🤖 Type 6: The Autonomous / Long-Running Agent

### *"It Lives. It Persists. It Sends Emails While You Sleep."*

The Autonomous Agent is what the science fiction writers imagined when they wrote about AI. It runs continuously - not waiting for a user to ask it a question, but pursuing goals over hours, days, or indefinitely. It monitors. It reacts to events. It builds up a picture of the world over time. It acts.

It is also the agent type that most frequently triggers the question: *"wait, should we maybe have a human check this first?"*

```
┌────────────────────────────────────────────────────────────────────┐
│              THE AUTONOMOUS AGENT LIFECYCLE                         │
│                                                                     │
│                         ┌──────────┐                               │
│             ┌──────────►│  MEMORY  │◄──────────┐                  │
│             │           │  STORE   │           │                  │
│             │           └──────────┘           │                  │
│             │                │                 │                  │
│             │ retrieves      │ stores          │ updates          │
│             │                ▼                 │                  │
│         ┌───────┐      ┌──────────┐        ┌───────┐             │
│  EVENT  │       │      │   LLM    │        │       │             │
│ ───────►│ SENSE │─────►│  REASON  │───────►│  ACT  │─► WORLD    │
│  TICK   │       │      │          │        │       │             │
│ TRIGGER │       │      └──────────┘        └───────┘             │
│         └───────┘           │                                      │
│                             │                                      │
│                    ┌────────▼────────┐                            │
│                    │  HUMAN IN THE   │                            │
│                    │  LOOP CHECKS    │ ◄── Critical for anything  │
│                    │  (when needed)  │     irreversible           │
│                    └─────────────────┘                            │
└────────────────────────────────────────────────────────────────────┘
```

**What "autonomous" actually means** 🤔

The word "autonomous" in AI agent discourse covers a spectrum so wide it should probably be two separate words:

```
AUTONOMY SPECTRUM
─────────────────

  Low                                                      High
   │                                                         │
   ▼                                                         ▼
┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────────────┐
│ 5   │    │ 30  │    │ 1   │    │ 8   │    │  Runs until │
│steps│    │steps│    │hour │    │hours│    │  you notice │
│w/o  │    │w/o  │    │w/o  │    │w/o  │    │  the bill   │
│human│    │human│    │human│    │human│    │             │
└─────┘    └─────┘    └─────┘    └─────┘    └─────────────┘
  "It's        "It's     "It's      "It's      "It's fully
 semi-        pretty   fairly    pretty    autonomous"
 agentic"   agentic"   agentic"  agentic"
```

When someone calls their agent "fully autonomous," it is entirely reasonable to ask:
- Autonomous for how long?
- In what domain?
- With what permissions?
- What happens when it gets confused?
- Does it stop?

These are not trick questions. They are the difference between an autonomous agent that is useful and one that autonomously sends 340 emails to the same person because the first 339 didn't receive a reply.

**The Golden Rule of Autonomous Agents** ⚖️

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  Make irreversible actions require confirmation.            ║
║                                                              ║
║  Always.                                                     ║
║                                                              ║
║  Without exception.                                          ║
║                                                              ║
║  No, not even if it makes the demo less smooth.             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

> 🌟 **Use cases where autonomous agents genuinely shine:**
> - Monitoring systems (price alerts, security events, data feeds)  
> - Inbox triage (reads, categorises, drafts responses for approval)  
> - Research pipelines (continuously scrapes, summarises, files reports)  
> - DevOps agents (monitors deployments, responds to incidents)  
> - Personal assistants (calendar management, routine correspondence)

---

## 🔬 The Comparison Table

*For those of you who have been waiting for the table that summarises everything. Here it is. You're welcome.*

| Type | 🧩 Complexity | 🧠 Memory | 🔁 Loops? | 🛠️ Tools | ⚡ Best For | 🚨 Main Risk |
|------|--------------|---------|----------|---------|-----------|------------|
| 🪨 Simple | ⭐ | None | No | 1-2 | Bounded tasks | Boring |
| 🔧 Tool-Use | ⭐⭐ | None | Sometimes | Many | Tool-rich tasks | Tool misuse |
| 🔄 ReAct | ⭐⭐⭐ | In-context | Yes | Yes | General tasks | Loops, drift |
| 🧠 Cognitive | ⭐⭐⭐⭐ | In-context | Yes | Yes | Quality-critical | Cost, latency |
| 🌐 Multi-Agent | ⭐⭐⭐⭐⭐ | Shared/External | Yes | Yes | Complex, parallel | Coordination hell |
| 🤖 Autonomous | ⭐⭐⭐⭐⭐ | External | Yes | Yes | Long-running tasks | Doing the wrong thing, persistently |

---

## 🧭 How to Choose

The question every engineer eventually faces: **which type do I need?**

The answer, as with most engineering questions, is: *it depends*. But the following decision tree is honest about what it depends on:

```
                    START HERE
                         │
                         ▼
          Is the task completely bounded
          and well-defined?
          │                    │
         YES                   NO
          │                    │
          ▼                    ▼
    Use a Simple Agent.  Does it require
    (Seriously. Don't    multiple steps
    over-engineer this.) and adaptation?
                         │           │
                        YES          NO
                         │           │
                         ▼           ▼
                   Use a ReAct    Actually,
                   Agent.         go back and
                         │        define the
                    Does output   task properly.
                    quality matter
                    a lot?
                    │         │
                   YES        NO
                    │         │
                    ▼         ▼
             Add a         Plain ReAct
             Reflection    is fine.
             layer.
                    │
              Does it need
              to run for
              hours/days?
              │          │
             YES         NO
              │          │
              ▼          ▼
         Autonomous    You're
         Agent with    done.
         guardrails.
         │
    Is there truly too
    much for one agent?
    │               │
   YES              NO
    │               │
    ▼               ▼
Multi-Agent.   Add memory
Be careful.    and move on.
```

---

## 🎓 A Final Note on Naming

The field has not settled on names. What one framework calls a "supervisor" another calls an "orchestrator." What one paper calls "a hierarchical multi-agent system" a startup calls "a swarm." What one engineer calls "a simple ReAct agent" a marketing team calls "an autonomous AI copilot powered by next-generation agentic reasoning."

This is normal. Fields are messy while they're being invented. The important thing is not the name - it's the architecture. Know what the thing does. Know where it fails. Know what it needs from you. The rest is vocabulary, and vocabulary is negotiable.

> *"The major difference between a thing that might go wrong and a thing that cannot possibly go wrong is that when a thing that cannot possibly go wrong goes wrong, it usually turns out to be impossible to get at or repair."*
> - Douglas Adams
>
> This principle applies to AI agents. Set your confirmation steps. Add your guardrails. Define your stopping conditions. Then deploy.

---

## 🚀 What's Next

You now know the full taxonomy. You know what each type is, how it's structured, when to use it, and when it will cause you problems.

The next chapter - **Chapter 5: Glossary** - summarize all the technical jargons

Each has opinions. We will share ours.

---

*- End of Chapter 4 -*

---

> *Part of the [Hitchhiker's Guide to AI Agents](../README.md)*
> *Don't Panic. The agent is fine, probably.*
