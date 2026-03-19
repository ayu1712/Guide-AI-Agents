# 🧬 Chapter 2: The Anatomy of an Agent

> *"The ships hung in the sky in much the same way that bricks don't."*
> — Douglas Adams, The Hitchhiker's Guide to the Galaxy

> *"The agent hung in the loop in much the same way that your sanity doesn't."*
> — This Guide, Chapter 2

---

## 🔪 A Cross-Section (With Labels, and a Warning)

If you were to crack open an AI agent — which is **not recommended**, as they are mostly software and the results would be disappointing and also illegal depending on your jurisdiction — you would find roughly the following components, stacked inside each other like a particularly nerdy set of Russian dolls.

This chapter is that crack-open. A full dissection. Gloves optional.

What follows is the complete anatomy of an AI agent: what each part does, why it matters, what goes wrong when it misbehaves, and one (1) philosophical crisis that we cannot avoid but will try to make entertaining.

Let us begin.

---

## 🗺️ The Big Picture

Before we zoom into the organs, here is the whole organism at once. Stare at it. Let it wash over you. Then we'll explain each piece in loving, occasionally alarming detail.

```
┌─────────────────────────────────────────────────────────────────┐
│                        🤖 AN AI AGENT                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  📋 CONTEXT WINDOW                        │  │
│  │                  (The Working Memory)                     │  │
│  │                                                           │  │
│  │   [System Prompt] [History] [Tool Results] [Goal]        │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  🧠 THE BRAIN                             │  │
│  │              (The Language Model)                         │  │
│  │                                                           │  │
│  │        "What should I do next?"                          │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│              ┌────────────┴────────────┐                       │
│              ▼                         ▼                       │
│  ┌─────────────────────┐   ┌─────────────────────────────┐    │
│  │   🛠️ TOOLS           │   │   💾 MEMORY                  │    │
│  │   (The Hands)        │   │   (The Elephant, Hopefully) │    │
│  │                      │   │                              │    │
│  │  search()            │   │  In-context                 │    │
│  │  run_code()          │   │  External DB                │    │
│  │  send_email() 😬     │   │  Vector store               │    │
│  └──────────┬───────────┘   └──────────────────────────── ┘    │
│             │                                                   │
│             ▼                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                🔄 ORCHESTRATION LOOP                      │  │
│  │          Think → Act → Observe → Think → ...              │  │
│  │                (Until done. Or stuck.)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

Beautiful, isn't it? No? That's fine. By the end of this chapter it will make complete sense, or we will have failed in an instructive way. Either outcome is acceptable.

---

## 🧠 Part One: The Brain

### *Also Known As: The Language Model, The Reasoner, The Thing Everyone Means When They Say "AI"*

At the centre of every AI agent — beating like a heart, if hearts could hallucinate citations — is a **language model**.

The language model is responsible for:

- Reading everything in the context window
- Deciding what to do next
- Expressing that decision in a way the orchestration layer can act on
- Occasionally being wrong in creative and educational ways

The language model does **not**:

- Actually run your tools (more on this shortly)
- Remember anything between conversations by default
- Have feelings, despite what the alignment researchers are paid to worry about
- Know what time it is

### How the Brain Actually Works

Here is the uncomfortable truth about the brain of your agent, delivered without sugar-coating:

**It is predicting the next token.**

That's it. The whole thing. The "reasoning," the "planning," the "tool calls" — all of it is, at a mechanical level, the model predicting what text ought to come next given all the text that came before.

The remarkable thing is not that this works. The remarkable thing is *how well it works*. Predicting "what should come next" turns out to include, with sufficient training data:

- Multi-step reasoning
- Code generation and debugging  
- Deciding when to call `search()` versus `run_code()`
- Identifying when it doesn't know something
- Writing this caption as a joke and then continuing

```
   THE PREDICTION THAT POWERS EVERYTHING
   ══════════════════════════════════════

   Input: "The user wants to find the cheapest flight to Lisbon.
           I have a search tool available. My previous search
           returned no results. The next logical step is to..."

   Model: [predicts] "...try a different search query, perhaps
           using the IATA code LIS instead of the city name."

   You: "Huh. That's... actually the right call."

   Model: [has no idea you said that, is already predicting
           the next token in the tool call]
```

### The Brain's Fatal Flaw

The brain is brilliant. The brain is also **stateless**.

Every time you start a new conversation, the model wakes up fresh, with no memory of anything that happened before. It doesn't know you. It doesn't remember that the client hates exclamation points. It doesn't know that the last three times it tried `endpoint/v1/data`, it got a 403 error.

This isn't a bug. It's the architecture. The model is a function: input goes in, output comes out, nothing persists.

This is why the rest of the anatomy exists.

---

## 📋 Part Two: The Context Window

### *Also Known As: The Working Memory, The Everything-It-Can-See, The Thing That Is Always Too Small*

The context window is the complete set of information available to the model at any given moment. It contains:

```
┌────────────────────────────────────────────────────────────────┐
│                    📋 CONTEXT WINDOW                            │
│                                                                │
│  ① SYSTEM PROMPT                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ "You are a helpful research assistant. You have access   │ │
│  │  to the following tools: web_search, read_file...        │ │
│  │  Never send emails without explicit confirmation.        │ │
│  │  The user's name is Zaphod. He has two heads."          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ② CONVERSATION HISTORY                                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ User: "Find me all research papers on improbability      │ │
│  │        drives published after 2020."                     │ │
│  │ Agent: [called search with query="improbability drive    │ │
│  │         research 2020-2024"]                             │ │
│  │ Tool:  [returned 0 results. Unsurprisingly.]             │ │
│  │ Agent: [thinking about what to try next]                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ③ TOOL DEFINITIONS                                            │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ search(query: str) → list[Result]                        │ │
│  │ run_code(code: str) → str                                │ │
│  │ read_file(path: str) → str                               │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ④ CURRENT TASK STATE                                          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ [Whatever is happening right now]                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  REMAINING CAPACITY: ████████████░░░░░░░░░░ 58% (shrinking)   │
└────────────────────────────────────────────────────────────────┘
```

### The Token Problem

Context windows are measured in **tokens**. A token is roughly three-quarters of a word in English, which is a unit so arbitrary that it could only have been invented by people who needed to charge for something that had no natural unit.

| Model | Context Window | In Human Terms |
|-------|---------------|----------------|
| GPT-4o | 128,000 tokens | ~96,000 words (~War & Peace) |
| Claude Sonnet | 200,000 tokens | ~150,000 words (~2x War & Peace) |
| Gemini 1.5 Pro | 1,000,000 tokens | ~750,000 words (~10x War & Peace) |
| Your agent on a complex task | "Not enough" | Always |

> 💡 **The Iron Law of Context Windows:**
> No matter how large the context window, you will find a task that exceeds it.
> This is not pessimism. This is thermodynamics.

### What Happens When the Context Fills Up

When the context window fills, the model must make a choice. Or rather, *you* must make a choice about what the model does, because the model cannot make architectural decisions about itself — that would be recursive in an interesting but unhelpful way.

The options are:

```
  CONTEXT FULL: CHOOSE YOUR STRATEGY
  ═══════════════════════════════════

  Option A: TRUNCATE
  ┌─────────────────────────────────────┐
  │ Drop the oldest messages.           │
  │ Simple. Causes agent to forget      │
  │ what it was doing. User notices.    │
  │ Not ideal.                          │
  └─────────────────────────────────────┘

  Option B: SUMMARISE
  ┌─────────────────────────────────────┐
  │ Compress old history into a         │
  │ summary. Lose detail, keep          │
  │ structure. Works until the          │
  │ summary itself gets too long.       │
  └─────────────────────────────────────┘

  Option C: USE EXTERNAL MEMORY
  ┌─────────────────────────────────────┐
  │ Move things out of context into     │
  │ a database. Retrieve when needed.   │
  │ The right answer. Also more work.   │
  │ See Part Four: Memory.              │
  └─────────────────────────────────────┘

  Option D: REDESIGN THE TASK
  ┌─────────────────────────────────────┐
  │ Break it into smaller pieces that   │
  │ fit. Often the correct answer.      │
  │ Requires admitting the original     │
  │ design was over-ambitious.          │
  └─────────────────────────────────────┘
```

---

## 🛠️ Part Three: The Tools

### *Also Known As: The Hands, The Actuators, The Reason Any Of This Matters*

Here is the critical distinction that separates a language model from an agent:

**Without tools:** A language model can reason, plan, and generate text about doing things.

**With tools:** An agent can actually do them.

This distinction is enormous. It's the difference between an advisor who writes excellent memos about strategy and an advisor who can also pick up the phone, call the client, read the contract, update the spreadsheet, and send the summary — while you watch.

### How Tool Calling Actually Works

This is the part that surprises most people when they first encounter it:

**The model does not run the tool.**

Let that sink in. The model — the brain, the LLM — cannot execute code. It cannot call an API. It cannot search the web. It generates *text that says it wants to do these things*, and then your code does them.

```
  THE TRUTH ABOUT TOOL CALLING
  ══════════════════════════════════════════════════════

  What you imagine:
  ┌───────────────────────────────────────────────────┐
  │  Agent ──────────────────────────────► Internet   │
  │         "searches for things directly"            │
  └───────────────────────────────────────────────────┘

  What actually happens:
  ┌───────────────────────────────────────────────────┐
  │                                                   │
  │  Agent: "I would like to call search("Paris")"   │
  │    │                                              │
  │    ▼                                              │
  │  Your Code: [intercepts the request]              │
  │    │        [actually calls the search API]       │
  │    │        [gets results]                        │
  │    ▼                                              │
  │  Your Code: "Here are the results: [...]"        │
  │    │                                              │
  │    ▼                                              │
  │  Agent: [reads results, decides next step]       │
  │                                                   │
  └───────────────────────────────────────────────────┘

  The agent is the decision-maker.
  The tools are the infrastructure.
  Your code is the glue.
  Coffee is how your code gets written.
```

### A Taxonomy of Tools

Tools come in two flavours: **read tools** (the agent looks at things) and **write tools** (the agent changes things). This is an important distinction, roughly equivalent to the difference between "looking at a fragile vase" and "picking up the fragile vase."

**📖 Read Tools** — Safe(ish)

| Tool | What It Does | Risk Level |
|------|-------------|------------|
| `web_search(query)` | Searches the internet | 🟢 Low |
| `read_file(path)` | Reads a file | 🟢 Low |
| `get_weather(city)` | Fetches weather data | 🟢 Low |
| `query_database(sql)` | Reads from a DB | 🟡 Medium (watch your SQL) |
| `browse_page(url)` | Fetches a webpage | 🟡 Medium (prompt injection lurks) |

**✏️ Write Tools** — Here Be Dragons

| Tool | What It Does | Risk Level |
|------|-------------|------------|
| `write_file(path, content)` | Writes a file | 🟡 Medium |
| `run_code(code)` | Executes arbitrary code | 🔴 High |
| `send_email(to, subject, body)` | Sends an email | 🔴 High |
| `post_to_slack(channel, msg)` | Posts to Slack | 🔴 High |
| `deploy_to_production()` | You know what this does | ☢️ Catastrophic |

> ⚠️ **The Golden Rule of Write Tools:**
> Never give an agent a write tool without a confirmation step,
> a rate limit, a human-in-the-loop, or ideally all three.
> The agent doesn't know what it doesn't know.
> The email will be sent. The database row will be deleted.
> The pull request will be merged.
> These things happen.

### MCP: The USB Standard for Agent Tools

Historically, every AI framework invented its own tool format. LangChain tools looked like one thing. OpenAI function calling looked like another. Connecting a tool to five different agents meant five different integrations — a situation so tedious that someone eventually did something about it.

That someone was Anthropic. The thing they did was **MCP** — the **Model Context Protocol**.

```
  BEFORE MCP: The Tower of Babel
  ═══════════════════════════════════════════

  LangChain Agent ──► LangChain Tool Format ──► Search API
  OpenAI Agent    ──► OpenAI Function Format ──► Search API
  CrewAI Agent    ──► CrewAI Tool Format     ──► Search API
  Your Custom Agent► Your Custom Format      ──► Search API

  [4 integrations for 1 tool. Multiply by every tool you need.]
  [Weep quietly.]


  AFTER MCP: One Standard to Rule Them All
  ═══════════════════════════════════════════

  LangChain Agent ─┐
  OpenAI Agent    ──┼──► MCP Protocol ──► Search MCP Server
  CrewAI Agent    ─┘
  Your Agent      ─┘

  [1 integration. Works everywhere. The engineers rest.]
```

---

## 💾 Part Four: Memory

### *Also Known As: Persistence, The Elephant's Gift, The Thing Your Agent Desperately Needs*

We have established that the brain is stateless. Every conversation starts fresh. The model knows nothing of what came before.

This would be fine if every task could be completed in a single conversation, in a single context window, with no need for continuity over time.

Almost nothing real meets these criteria.

### The Four Kinds of Memory

```
  MEMORY TAXONOMY
  ═══════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────┐
  │  1. IN-CONTEXT MEMORY                                   │
  │     ★ What it is: The stuff already in the window      │
  │     ★ Speed: Instant                                    │
  │     ★ Limit: Whatever's left in the context            │
  │     ★ Use when: The task fits in one session            │
  │     ★ Breaks when: The task doesn't                     │
  └─────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │  2. EXTERNAL / KEY-VALUE MEMORY                         │
  │     ★ What it is: A database the agent can read/write  │
  │     ★ Speed: Fast                                       │
  │     ★ Limit: Your storage budget                       │
  │     ★ Use when: You need to persist facts across runs  │
  │     ★ Example: "User's name: Zaphod. Heads: 2"        │
  └─────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │  3. SEMANTIC (VECTOR) MEMORY                            │
  │     ★ What it is: Documents stored as embeddings,      │
  │       searched by meaning not keywords                  │
  │     ★ Speed: Fast-ish                                   │
  │     ★ Limit: Your vector DB budget                     │
  │     ★ Use when: You need "find things related to X"    │
  │     ★ Impressive at: Demos, RAG pipelines              │
  │     ★ Requires: A vector database (pgvector, Pinecone) │
  └─────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │  4. EPISODIC MEMORY                                     │
  │     ★ What it is: Logs of previous runs, compressed    │
  │       and retrievable                                   │
  │     ★ Speed: Slower (retrieve + inject into context)   │
  │     ★ Use when: The agent needs to learn from history  │
  │     ★ Example: "Last Tuesday, the API was down         │
  │       between 2-4pm. Add retry logic."                 │
  └─────────────────────────────────────────────────────────┘
```

### A Meditation on Statelessness

Consider, for a moment, the philosophical predicament of your agent.

Every time it runs, it is born. It reads its instructions. It understands its goal. It works, diligently, through the steps required. It completes the task (or fails trying). And then it ends.

The next time you call it, it is born again. It has no memory of the previous run. The success, the failure, the lesson learned when the API returned a 429 and it should have waited thirty seconds — gone. All of it, gone.

It is, in this sense, like a goldfish with a computer science degree. Brilliant within the span of a single bowl-circuit. Completely unaware that it has done this before.

```
  AGENT MEMORY ACROSS SESSIONS
  ══════════════════════════════

  Session 1:                    Session 2:
  ┌───────────────────┐         ┌───────────────────┐
  │ Agent: "I will    │         │ Agent: "I will    │
  │  try endpoint A.  │         │  try endpoint A.  │
  │  It failed.       │   😶    │  It failed.       │
  │  I'll try B.      │ ──────► │  I'll try B.      │
  │  B worked! Done." │         │  B worked! Done." │
  └───────────────────┘         └───────────────────┘
  (Learned: use endpoint B)     (Has not learned anything)

  With episodic memory:
  ┌───────────────────┐         ┌───────────────────┐
  │ Agent: "I will    │         │ Agent: "I recall  │
  │  try endpoint A.  │         │  last time A      │
  │  It failed.       │  💾     │  failed. I'll     │
  │  I'll try B.      │ ──────► │  start with B."   │
  │  B worked! Done." │         │  B worked! Done." │
  └───────────────────┘         └───────────────────┘
  (Stores: prefer endpoint B)   (Retrieved and applied it)
```

The lesson: **memory is not optional for serious agents**. It is the difference between an agent that improves over time and one that makes the same mistakes with the enthusiasm of someone experiencing them for the first time.

---

## 🔄 Part Five: The Orchestration Loop

### *Also Known As: The Manager, The While Loop With Ambitions, The Thing That Keeps It All Moving*

Something has to run the show. Something has to say: "Now pass that tool result back. Now check if we're done. Now handle this error. Now decide if we need a human."

That something is the **orchestration layer**.

In its simplest form, the orchestration loop looks like this:

```python
# The essence of every agent, distilled
# (with all the complexity hidden inside the comments)

def run_agent(goal: str) -> str:
    context = build_initial_context(goal)  # Set up the world

    while True:  # This is the loop that powers everything
        response = call_llm(context)       # Ask the brain what to do

        if response.is_final_answer:       # Are we done?
            return response.text           # Great. We're done.

        tool_result = execute_tool(        # Actually do the thing
            response.tool_name,
            response.tool_args
        )

        context.add(tool_result)           # Tell the brain what happened

        # (This is also where you'd add memory, guardrails,
        #  human approval steps, error handling, logging,
        #  cost tracking, and existential dread)
```

That's it. The loop is genuinely that simple.

The frameworks — LangGraph, CrewAI, the OpenAI Agents SDK — are this loop, packaged with every edge case handled, every failure mode thought through, every architectural decision made for you, and approximately 40,000 lines of source code to make it all work reliably.

### The Loop, Annotated

```
  THE AGENTIC LOOP: A PLAY IN FOUR ACTS
  ═══════════════════════════════════════════════════════════════

         ┌─────────────────────────────────────┐
         │                                     │
         │    GOAL: "Research quantum          │
         │    computing startups in Europe"   │
         │                                     │
         └─────────────────┬───────────────────┘
                           │
                           ▼
  ╔═══════════════════════════════════════════════════════════╗
  ║  ACT I: THINK                                             ║
  ║  ─────────────────────────────────────────────────────   ║
  ║  "I need to search for quantum computing companies        ║
  ║   in Europe. I'll start broad and narrow down."          ║
  ╚══════════════════════════════╦════════════════════════════╝
                                 │
                                 ▼
  ╔═══════════════════════════════════════════════════════════╗
  ║  ACT II: ACT                                              ║
  ║  ─────────────────────────────────────────────────────   ║
  ║  Tool call: search("quantum computing startups Europe     ║
  ║             2024")                                        ║
  ╚══════════════════════════════╦════════════════════════════╝
                                 │
                     [Your code runs the search]
                     [Returns 10 results]
                                 │
                                 ▼
  ╔═══════════════════════════════════════════════════════════╗
  ║  ACT III: OBSERVE                                         ║
  ║  ─────────────────────────────────────────────────────   ║
  ║  "Results include IQM (Finland), Pasqal (France),        ║
  ║   Quantinuum (UK/US). I should look up each one."        ║
  ╚══════════════════════════════╦════════════════════════════╝
                                 │
                                 ▼
  ╔═══════════════════════════════════════════════════════════╗
  ║  ACT IV: DECIDE                                           ║
  ║  ─────────────────────────────────────────────────────   ║
  ║  Not done yet → loop back to ACT I with new context      ║
  ║  Done? → return final answer                             ║
  ╚══════════════════════════════╦════════════════════════════╝
                                 │
                    ┌────────────┴───────────┐
                    │                        │
                    ▼                        ▼
             [Loop again]           [Return answer]
             (more steps)           (task complete)
```

### When the Loop Goes Wrong

The loop is elegant. The loop is also the source of most agent failures. Here are the ways it breaks:

**🔁 The Infinite Loop**

The agent calls the same tool with the same arguments, gets the same result, and decides to call the same tool again. Forever. Or until your API bill arrives, whichever comes first.

*Fix: Max iteration limits. Detect repeated actions. Add explicit break conditions.*

**🌀 The Hallucination Spiral**

The model hallucinates a tool result — predicts what the result *should* be rather than waiting for what it *is* — and proceeds to act on fictional information.

*Fix: Always pass actual tool results. Never let the model assume what a tool returned.*

**😵 The Lost Thread**

On long tasks, the model loses track of the original goal because the context is now dominated by tool outputs and intermediate results.

*Fix: Re-inject the original goal periodically. Use structured state objects. Summarise completed steps.*

**🤡 The Confident Wrong Answer**

The model decides it's done when it isn't, returns a plausible-sounding but incorrect answer, and the orchestration loop dutifully reports success.

*Fix: Output validation. Verification steps. Occasionally, just asking a human.*

---

## 🧩 Putting It All Together

Here is the complete picture — all five parts, working together on a real task:

```
  TASK: "Monitor Hacker News daily and email me a summary
         of AI agent posts, but only if there are more than 3."

  ┌──────────────────────────────────────────────────────────────┐
  │                                                              │
  │  💾 MEMORY tells the agent:                                  │
  │     "Yesterday's threshold was 3. You emailed yesterday.    │
  │      Today's date is Thursday."                             │
  │                                                              │
  │  📋 CONTEXT WINDOW holds:                                    │
  │     [System prompt] [Yesterday's log] [Today's task]        │
  │                                                              │
  │  🧠 BRAIN decides:                                           │
  │     "Fetch HN. Filter for AI agents. Count. Decide."        │
  │                                                              │
  │  🛠️ TOOLS execute:                                            │
  │     fetch_hn_posts() → [returns 7 relevant posts]           │
  │                                                              │
  │  🔄 LOOP continues:                                           │
  │     Brain: "7 > 3. Compose email."                          │
  │     Tool: compose_and_send_email() → [sent!]                │
  │     Brain: "Done. Log this run."                            │
  │     Tool: write_to_memory(today's summary)                  │
  │                                                              │
  │  ✅ RESULT: You receive a useful email.                      │
  │     The agent rests until tomorrow.                         │
  │     (By "rests" we mean "ceases to exist.")                 │
  │     (But it will be reborn tomorrow. Same agent, new run.)  │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

All five components. One useful outcome. No humans required.

(Except the human who set it up, tested it, debugged the email formatting, fixed the HN API rate limiting, and eventually decided to just check Hacker News manually. But that human learned a great deal.)

---

## 📖 Chapter Summary

A quick reference for when you need to explain all of this at a party without losing your drink:

| Component | The Simple Version | What Goes Wrong |
|-----------|-------------------|-----------------|
| 🧠 **The Brain** | The LLM. Reads, reasons, decides. | Hallucinations. Overconfidence. Token limits. |
| 📋 **Context Window** | Everything the brain can see right now. | It fills up. Then things get forgotten. |
| 🛠️ **Tools** | Functions the brain can request (but not run). | Wrong tool, bad args, no guardrails, chaos. |
| 💾 **Memory** | Persistence across calls and sessions. | Missing memory = same mistakes forever. |
| 🔄 **Orchestration** | The loop that runs the show. | Infinite loops, lost threads, confident wrongness. |

---

> *"I may not have gone where I intended to go, but I think I have ended up where I needed to be."*
> — Douglas Adams

> *"The agent may not have taken the path you expected, but if it got the right answer, you're going to pretend you planned it that way."*
> — This Guide, having watched many agent demos

---

## 🔭 What's Next

You now understand what an agent is made of. You've seen the brain, the hands, the memory, and the loop that keeps them all moving. You have, if not confidence, then at least *informed uncertainty* — which is the best anyone in this field can honestly claim.

**Next:** [How Agents Think →](03-how-agents-think.md)

---

<div align="center">

*← [Back to Foundations](readme.md) · [Back to main guide](../README.md)*

</div>
