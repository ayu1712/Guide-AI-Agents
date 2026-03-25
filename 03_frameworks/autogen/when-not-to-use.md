# When NOT to Use AutoGen

AutoGen's conversational model is genuinely powerful for certain problems. It's also a poor fit for many others — and given its 2026 maintenance status, the threshold for choosing it should be higher than it once was.

---

## Don't Use AutoGen When...

### 1. You're starting a new production system

AutoGen is in maintenance mode as of 2026. Microsoft has shifted investment toward newer agent infrastructure. It still works, still receives security patches, and has a large community — but you're building on a framework whose best days of active development are behind it.

For a new system you'll be maintaining for years, this matters.

**Signal:** You're writing a project that will run in production for 12+ months.

**Better choice:** [LangGraph](../langgraph/) for complex workflows, [CrewAI](../crewai/) for multi-agent teams, [OpenAI Agents SDK](../openai-agents-sdk/) for simpler routing.

---

### 2. You need predictable, auditable execution

AutoGen conversations are emergent. Agents decide what to say next based on what was said before. Two runs with identical inputs can produce different execution paths, different numbers of turns, and different outputs. That non-determinism is a feature for exploratory tasks and a liability for anything that needs to be auditable.

**Signal:** Someone asks "why did the agent do that?" and you need to give a precise answer.

**Better choice:** [LangGraph](../langgraph/) — every node transition is logged, traceable, and replayable.

---

### 3. You're optimising for token costs

AutoGen's GroupChat sends the full conversation history to every agent on every turn. With 4 agents and 20 rounds, you're paying for 80 full-history API calls. Complex group chats can cost 10-20x more in tokens than an equivalent LangGraph workflow.

**Signal:** You've run a few GroupChat tests and the token counts made you wince.

**Better choice:** LangGraph with selective state passing — nodes only receive the parts of state they need.

---

### 4. You need structured, machine-readable output

AutoGen agents produce conversational text. Extracting a reliable JSON object or Pydantic model from a multi-agent conversation requires post-processing and validation that you have to write yourself. The conversation format doesn't naturally produce structured outputs.

**Signal:** Your downstream code needs to parse the agent's output into a data structure.

**Better choice:** LangGraph with Pydantic-typed state, or CrewAI with `output_pydantic`.

---

### 5. You don't need agents to actually converse

AutoGen's value is in the back-and-forth. If your workflow is really "agent A does X, then agent B does Y with A's output," you don't need conversation — you need a pipeline. Forcing a pipeline into AutoGen's conversation model adds turns, tokens, and unpredictability without benefit.

**Signal:** Your agents aren't really responding to each other — they're just executing in sequence.

**Better choice:** [CrewAI](../crewai/) with `Process.sequential` or LangGraph with chained nodes.

---

### 6. Code execution safety is non-negotiable

AutoGen's `UserProxyAgent` can execute code. Without Docker, that means arbitrary Python running with your process permissions. In any environment where the input isn't fully controlled — user-facing apps, untrusted data sources — this is a significant security risk.

Docker mitigates it, but adds operational complexity. If your team isn't ready to run and maintain Docker-based code sandboxes, AutoGen's code execution is a liability.

**Signal:** Your system processes untrusted input and executes code. You don't have a Docker setup.

**Better choice:** Any framework without automatic code execution, or AutoGen with Docker strictly enforced.

---

### 7. You need good observability tooling

AutoGen's observability story is basic compared to LangGraph + LangSmith or CrewAI + AgentOps. You get verbose console logging, but production-grade tracing, replay, and monitoring require significant custom work.

**Signal:** You need to debug failures in a deployed system, not just in local development.

**Better choice:** LangGraph with LangSmith.

---

## When AutoGen Still Makes Sense

Despite all the above, there are cases where AutoGen remains the right call:

- **Learning and experimentation** — it's still an excellent way to understand multi-agent patterns. The conversation model makes agent reasoning transparent.
- **Code generation + execution loops** — the `UserProxyAgent` + code executor pattern is still one of the cleanest implementations of this workflow anywhere.
- **Academic or research contexts** — AutoGen has a large body of published research and community work around it. If you're building on or comparing to prior art, AutoGen is the right baseline.
- **Existing AutoGen codebases** — if you're maintaining a system already built on AutoGen, staying on it is often the pragmatic choice.

---

## The Honest Summary

AutoGen was the right answer in 2023. In 2026, the landscape has matured and better-maintained alternatives exist for most of its use cases. Use it when its unique conversational model is genuinely what you need, and when you're comfortable building on a framework in maintenance mode. Otherwise, one of the actively developed alternatives is likely a better long-term bet.
