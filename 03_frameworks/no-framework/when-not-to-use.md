# When NOT to Skip Frameworks

The no-framework approach is underrated and often the right call. But there are genuine situations where the DIY loop becomes a liability. Here's an honest look at when you should stop rolling your own and pick up a framework.

---

## Stop Going Raw When...

### 1. Your control flow has more than 3 conditional branches

A simple `if tool_calls: ... else: return` is easy to follow. Three nested conditions with retries and fallbacks starts to look like spaghetti. When you catch yourself drawing flow diagrams just to understand your own code, that's the graph wanting to be declared explicitly.

**Signal:** You have more than one `if/elif/else` block inside your agent loop that routes execution differently based on state.

**Better choice:** [LangGraph](../langgraph/) — your implicit graph becomes an explicit one with named nodes and edges.

---

### 2. You have 3 or more agents that need to coordinate

One agent loop is simple. Two can be manageable. Three or more agents passing work between each other, where each agent has its own tools, prompts, and state, is coordination complexity that doesn't fit cleanly in a single file.

You'll end up building a mini-framework anyway. At that point you may as well use a real one.

**Signal:** You have three or more functions that each wrap their own agent loop and you're orchestrating calls between them.

**Better choice:** [CrewAI](../crewai/) if roles are the right model. [LangGraph](../langgraph/) if you need precise control. [AutoGen](../autogen/) if conversation between agents is what you need.

---

### 3. You need to pause mid-run and resume later

The raw loop runs to completion or fails. There's no native way to say "stop here, wait for a human to approve, then continue from this exact point." You can simulate it with checkpointing to a file, but you're building what LangGraph already built — and building it worse the first time.

**Signal:** Your agent needs to pause for human review, an external API callback, or a scheduled resume.

**Better choice:** [LangGraph](../langgraph/) with checkpointing and `interrupt_before`.

---

### 4. Production debugging is taking more than an hour per incident

With a raw loop, debugging is `print()` statements and log files. For a quick script, that's fine. For a production system where something went wrong three days ago and you need to understand exactly what the agent did and why, it's not enough.

**Signal:** You've had a production incident where you couldn't reconstruct what the agent did.

**Better choice:** LangGraph with LangSmith. Every node execution is recorded, every state transition is queryable, and you can replay any run from any point.

---

### 5. Multiple developers are working on the same agent

A raw agent loop in one file works for one developer. When two developers are touching the same code, the lack of structure creates merge conflicts and unclear ownership. Where does the prompt live? Where does the tool logic live? What's the contract between the reasoning step and the execution step?

Frameworks force a structure that makes collaboration easier, even if that structure feels like overhead when you're working alone.

**Signal:** More than one person is committing to the agent code and you're having conversations about where things should live.

**Better choice:** Any framework — the structure itself is the benefit here, not the specific framework.

---

### 6. You're building something with a compliance or audit requirement

Raw loops don't produce audit trails by default. If your agent makes decisions that need to be logged, reviewed, or explained — legal reasoning, financial recommendations, medical triage — the raw approach puts the entire audit infrastructure burden on you.

**Signal:** Someone in a legal or compliance role is asking how you'll prove what the agent did in a given run.

**Better choice:** LangGraph with LangSmith, or any framework with structured logging and execution tracing.

---

### 7. You've rewritten the same plumbing three times

If you've written `execute_tool_with_retry()` in three different projects, you're maintaining a private framework that only you understand. At some point, a well-maintained public framework is cheaper to operate than a custom one.

**Signal:** You're copy-pasting your own agent boilerplate between projects.

**Better choice:** Whichever framework's model fits your use case — you've already designed the equivalent, now just use the maintained version.

---

## The Exception: When Raw Is Always Right

Some use cases stay raw forever, not because frameworks are bad but because the problem genuinely doesn't need them:

- **Simple one-off scripts** — a 50-line agent that runs once a day and emails you a summary
- **Tightly constrained pipelines** — exactly 3 steps, no branching, runs in CI
- **Proof of concepts** — you're testing if the idea works before investing in infrastructure
- **Teaching** — showing someone how agents work requires starting from first principles

For these, adding a framework is gold-plating.

---

## The Honest Summary

Go raw when the problem is simple and the team is small. Add a framework when the complexity is real — not anticipated, not theoretical — and when the framework's abstractions map to the actual pain you're feeling.

The worst outcome is adding framework complexity to a simple problem. The second-worst is fighting a simple script's limitations on a complex problem. Know which one you're building.
