# When NOT to Use CrewAI

CrewAI is the fastest way to get a multi-agent system running. That speed comes with trade-offs. Here's when those trade-offs matter enough to pick something else.

---

## Don't Use CrewAI When...

### 1. You need a single agent

CrewAI is a multi-agent framework. Using it for a single agent with a few tools is like hiring a project manager, a researcher, and a writer to answer one email. The overhead is real — setup time, token costs from role prompting, task coordination.

**Signal:** You have one agent doing one job.

**Better choice:** [No framework](../no-framework/) or [OpenAI Agents SDK](../openai-agents-sdk/).

---

### 2. You need precise control over execution flow

CrewAI's sequential process runs tasks in order, and hierarchical process uses a manager LLM to coordinate. Neither gives you the fine-grained control of "run A, then if the result meets condition X run B, otherwise run C with a retry limit of 3."

If your workflow has complex branching, conditional loops, or retry logic that depends on specific output values, you'll be fighting CrewAI's abstractions to get there.

**Signal:** You're trying to add `if/else` logic between CrewAI tasks and it keeps getting messy.

**Better choice:** [LangGraph](../langgraph/) — conditional edges and state-based routing are its core strength.

---

### 3. You need reliable structured outputs at every step

CrewAI agents produce free-form text by default. You can enforce structure with `output_pydantic` on tasks, but it's not always reliable — especially for complex nested schemas or when the agent decides it knows better than your spec.

If every step of your pipeline needs to produce machine-readable structured data that feeds into downstream code, you'll spend a lot of time coaxing CrewAI into compliance.

**Signal:** You're checking `isinstance(result, YourModel)` and it's failing more than it should.

**Better choice:** LangGraph with explicit Pydantic output nodes, or direct API calls with structured output mode.

---

### 4. You need to debug a failure in production

When a CrewAI run fails or produces bad output, tracing why is harder than it should be. You see the final output and some verbose logs, but reconstructing exactly what each agent reasoned and why is not straightforward. CrewAI's observability story is improving but lags behind LangGraph + LangSmith.

**Signal:** You've spent more than an hour trying to figure out why a crew produced a bad result.

**Better choice:** [LangGraph](../langgraph/) with LangSmith — every node execution is traced and replayable.

---

### 5. You're building a conversational multi-agent system

CrewAI agents are task executors, not conversationalists. They do their job and pass the baton. If you want agents that argue, debate, revise each other's work in dialogue, and arrive at solutions through back-and-forth conversation, CrewAI's task model gets in the way.

**Signal:** You want agents to talk *to* each other, not just pass outputs *between* each other.

**Better choice:** [AutoGen](../autogen/) — conversation is its native mode.

---

### 6. Token costs are a primary concern

Every agent in a crew carries its full role + goal + backstory in its system prompt. Every task description gets repeated on every API call that agent makes. In a large crew running many tasks, you're paying for a lot of repeated context.

**Signal:** Your CrewAI runs are costing 3-5x what you expected based on task complexity alone.

**Better choice:** No framework, or LangGraph with minimal system prompts.

---

### 7. You're building a long-running workflow with pause/resume

CrewAI runs synchronously from `kickoff()` to completion. There's no native mechanism to pause a crew mid-run, wait for an external event, persist state, and resume later. If you need human approval gates, webhook triggers, or multi-day workflows, you'll need to engineer around CrewAI's execution model.

**Signal:** You need your agent to pause and wait for a human to approve something before continuing.

**Better choice:** [LangGraph](../langgraph/) with checkpointing and `interrupt_before`.

---

## The Honest Summary

CrewAI's sweet spot is **quick multi-agent prototypes with role-based workflows** where the output is prose or structured content and the execution path is roughly linear. Outside that zone — complex branching, strict structured outputs, production observability, pause/resume — the abstractions start costing more than they save.

The role metaphor is genuinely powerful when it fits. When it doesn't fit, forcing it makes everything harder.

---

## If You're Already Invested in CrewAI

You don't have to abandon it. For the most common pain point (brittle outputs), adding `output_pydantic` on every task and bumping `max_iter` up usually helps. For observability, CrewAI has Agentops integration that provides basic tracing.

The cases where a full migration makes sense: you've hit the branching/state management wall, or you're going to production and need replay-level debugging. At that point, LangGraph is worth the rewrite.
