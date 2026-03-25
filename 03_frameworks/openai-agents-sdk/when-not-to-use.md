# When NOT to Use the OpenAI Agents SDK

The OpenAI Agents SDK is the lowest-friction entry point for agent development. That makes it easy to start with — and easy to outgrow. Here's when you've outgrown it.

---

## Don't Use the OpenAI Agents SDK When...

### 1. You're not using OpenAI models

The SDK is designed and optimised for GPT-4o and OpenAI's model family. It technically supports other providers through a compatibility layer, but the first-class experience — tool definitions, streaming, structured output, tracing — is built around OpenAI's API.

If you're using Claude, Gemini, Mistral, or local models as your primary LLM, you'll spend more time working around the SDK than benefiting from it.

**Signal:** Your primary LLM isn't from OpenAI.

**Better choice:** [LangGraph](../langgraph/) (model-agnostic) or [No framework](../no-framework/) with your provider's SDK directly.

---

### 2. You need complex stateful workflows

The SDK is great at routing — triage agent hands off to specialist, specialist uses tools, returns answer. That's the pattern it was built for.

What it doesn't model well: workflows where state needs to persist across multiple steps, where execution can branch based on intermediate results, where you need to loop back to an earlier stage based on quality checks, or where you need to pause and resume.

**Signal:** You're trying to implement "if the output quality score is below 0.7, loop back and retry with a different approach" and it keeps getting awkward.

**Better choice:** [LangGraph](../langgraph/) — that's exactly what nodes + conditional edges + state are for.

---

### 3. Your agents need to collaborate, not just hand off

The SDK's handoff model is one-directional: Agent A decides to hand to Agent B, B runs, B returns. It's clean for routing. It's not designed for agents that need to have a conversation with each other, debate a problem, or iteratively critique and improve each other's work.

**Signal:** You want two agents to go back and forth on a problem, not just pass a baton.

**Better choice:** [AutoGen](../autogen/) for conversational multi-agent patterns.

---

### 4. You need production-grade observability beyond OpenAI's platform

The SDK's built-in tracing sends data to OpenAI's platform. If you can't or won't send your agent execution data to a third-party (data residency requirements, sensitive workloads, cost), you're building your own observability layer from scratch.

**Signal:** "We can't send this data to OpenAI's servers" is a requirement on your project.

**Better choice:** LangGraph with self-hosted LangSmith or custom logging.

---

### 5. You need fine-grained parallel execution

The SDK runs agents sequentially unless you manually parallelise with `asyncio.gather`. There's no native concept of fan-out to multiple agents, collecting their results, and merging. You can build it, but you're building it yourself.

**Signal:** You need 5 agents to run simultaneously on sub-tasks and then merge results.

**Better choice:** LangGraph with `Send` for native parallel node execution.

---

### 6. Vendor lock-in is a concern

Choosing the OpenAI Agents SDK means committing to the OpenAI ecosystem for your agent infrastructure. If OpenAI changes pricing, deprecates features, or if a better model appears from another provider, migrating is a real effort.

**Signal:** Long-term infrastructure independence is important to your team or organisation.

**Better choice:** LangGraph or no framework — both are model-agnostic from day one.

---

### 7. You need multi-step memory and learning across runs

The SDK has no built-in persistent memory beyond the context window. An agent doesn't remember anything from a previous run unless you build that storage layer yourself. For stateless request-response agents, that's fine. For agents that should learn from past interactions or maintain a user model over time, it's a gap.

**Signal:** "Remember what we talked about last week" should work.

**Better choice:** No framework with your own memory layer, or CrewAI with long-term memory enabled.

---

## The Honest Summary

The OpenAI Agents SDK is the right choice when you want **the fastest path from idea to working agent** in the OpenAI ecosystem. It's the wrong choice when you need **model independence, complex state management, deep observability, or multi-agent collaboration beyond simple routing**.

It's an excellent starting point. It's not always the destination.

---

## The Upgrade Path

The most common migration is SDK → LangGraph when workflows get complex. The SDK's concepts map cleanly:

| SDK concept | LangGraph equivalent |
|---|---|
| Agent + instructions | Node with LLM call |
| Tool | Node or ToolNode |
| Handoff | Conditional edge |
| Runner loop | Graph compile + invoke |
| Result object | Final state |

The migration is mostly mechanical. The hard part is redesigning your state schema — the SDK doesn't have explicit state, so you have to decide what to track. That design work is worth doing carefully.
