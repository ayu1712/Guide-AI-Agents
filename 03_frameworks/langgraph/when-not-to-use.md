# When NOT to Use LangGraph

LangGraph is excellent. It's also overkill in a lot of situations. Here's an honest guide to when you should reach for something else.

---

## Don't Use LangGraph When...

### 1. Your agent is simple

If your agent does one thing — calls a few tools and returns an answer — LangGraph adds ceremony without benefit. You're defining nodes, edges, state schemas, and compiling a graph just to wrap a `while` loop you could write in 20 lines.

**Signal:** Your graph has fewer than 3 nodes and no conditional edges.

**Better choice:** [No framework](../no-framework/) or [OpenAI Agents SDK](../openai-agents-sdk/).

---

### 2. You're prototyping

LangGraph's explicitness is a strength in production. In a 2-hour prototype, it's friction. You want to iterate fast, change the agent's behaviour on the fly, and not spend 30 minutes debugging why your conditional edge isn't routing correctly.

**Signal:** You don't know yet if the idea works. You're in exploration mode.

**Better choice:** [CrewAI](../crewai/) for multi-agent prototypes. Raw calls for single agents.

---

### 3. Your team doesn't think in graphs

Graph theory is intuitive to some engineers and genuinely confusing to others. If your team struggles with nodes, edges, reducers, and state schemas, you'll spend more time explaining the framework than building the product.

**Signal:** You've had to explain what a "reducer" is more than twice this week.

**Better choice:** CrewAI's role-based model is more intuitive for most people. AutoGen's conversation model is even more natural.

---

### 4. You need role-based agent teams fast

LangGraph can absolutely model multi-agent teams. But you have to wire everything manually — each agent is a node, the routing logic is conditional edges, state passes between them explicitly. It's powerful and verbose.

**Signal:** You're thinking "I need a Researcher, a Writer, and an Editor" not "I need a graph with three nodes."

**Better choice:** [CrewAI](../crewai/) — that's exactly its mental model.

---

### 5. You're fully committed to a non-LangChain stack

LangGraph works with any LLM via direct API calls. But its observability tooling (LangSmith), its integrations, and most of its documentation examples assume the LangChain ecosystem. If you're building on raw Anthropic SDK or OpenAI SDK with no LangChain, you'll be swimming against the current.

**Signal:** Your `requirements.txt` has zero `langchain-*` packages and you want to keep it that way.

**Better choice:** OpenAI Agents SDK (if on OpenAI) or no framework (if you want zero dependencies).

---

### 6. Observability cost is a concern

LangSmith — LangGraph's companion observability platform — is the best way to debug and monitor LangGraph agents. It's also a paid SaaS product. For hobbyist projects, indie developers, or cost-sensitive teams, this is a real factor.

**Signal:** You're watching your infrastructure budget carefully.

**Better choice:** No framework with structured logging, or CrewAI with a self-hosted observability stack.

---

### 7. You need agents to have free-form conversations

LangGraph's strength is explicit, controlled flow. If you want agents to reason through problems via open-ended dialogue — debate, critique, explore — you're fighting LangGraph's model. It wants you to define the flow upfront.

**Signal:** You can't draw the graph before you start because the path depends on what the agents discover.

**Better choice:** [AutoGen](../autogen/) — its conversational model handles emergent paths naturally.

---

## The Honest Summary

LangGraph is the right choice when you care deeply about **control, debuggability, and production reliability**. It's the wrong choice when you care more about **speed, simplicity, or team accessibility**.

A useful heuristic: if you can describe your agent's execution flow as a diagram before you write any code, LangGraph will serve you well. If the flow is too dynamic or uncertain to diagram, start somewhere else.

---

## Migration Note

Starting with a simpler approach and migrating to LangGraph later is a legitimate strategy. The patterns — tool dispatch, message history, retry logic — are the same. The migration is mostly about wrapping your existing logic in nodes and making state explicit. It's annoying, not catastrophic.

Start simple. Migrate when the pain is real.
