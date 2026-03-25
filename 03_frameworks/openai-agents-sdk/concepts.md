# OpenAI Agents SDK — Core Concepts

The building blocks of the SDK, and how the execution model actually works.

---

## The Mental Model

The OpenAI Agents SDK is built around one insight: most real-world tasks require **routing**, not monolithic reasoning. A customer support system doesn't need one giant agent that knows everything — it needs a triage agent that recognises the problem type and hands off to a specialist who handles it well.

The SDK's primitives — agents, tools, and handoffs — map directly to this pattern. It's deliberately simple. That simplicity is a feature.

---

## Agent

An agent is an LLM with instructions, a set of tools, and a list of agents it can hand off to.

```python
from agents import Agent

agent = Agent(
    name="Support Agent",
    instructions=(
        "You handle customer support for Acme Corp. "
        "Be concise and friendly. "
        "If the issue is technical, hand off to the technical specialist. "
        "If the issue is billing, hand off to the billing specialist."
    ),
    tools=[search_knowledge_base],
    handoffs=[technical_agent, billing_agent],
    model="gpt-4o",                  # Defaults to gpt-4o
    model_settings=ModelSettings(
        temperature=0.2,
        max_tokens=1024,
    ),
)
```

### Instructions Are the Whole Game

Unlike frameworks that split behaviour across role/goal/backstory, the SDK keeps everything in `instructions`. This is just the system prompt. Write it like you're writing a precise system prompt — because you are.

Good instructions specify:
- What the agent is responsible for (and not responsible for)
- When to use each tool
- When to hand off (and to whom)
- Output format requirements

---

## Tools

Tools are Python functions the agent can call. The SDK infers the schema from the function signature and docstring.

```python
from agents import function_tool

@function_tool
def get_order_status(order_id: str) -> str:
    """
    Look up the current status of a customer order.
    
    Args:
        order_id: The order ID from the customer's confirmation email.
    
    Returns:
        A string describing the order status and estimated delivery.
    """
    order = db.get_order(order_id)
    return f"Order {order_id}: {order.status}. Estimated delivery: {order.eta}"
```

The docstring becomes the tool description that the LLM sees. Write it from the LLM's perspective: what does this tool do, when should I call it, what does it return?

### Tool Type Annotations Matter

The SDK uses type annotations to build the JSON schema:

```python
@function_tool
def search(query: str, max_results: int = 5) -> list[str]:
    """Search the knowledge base."""
    ...
```

This generates:
```json
{
  "name": "search",
  "parameters": {
    "query": {"type": "string"},
    "max_results": {"type": "integer", "default": 5}
  },
  "required": ["query"]
}
```

Use Pydantic models for complex input schemas:

```python
from pydantic import BaseModel

class FilterParams(BaseModel):
    date_range: tuple[str, str]
    categories: list[str]
    min_amount: float = 0.0

@function_tool
def search_transactions(filters: FilterParams) -> str:
    """Search transactions with optional filters."""
    ...
```

---

## Handoffs

Handoffs let one agent transfer control to another. When the LLM decides to hand off, the SDK switches context to the target agent and the conversation continues there.

```python
billing_agent = Agent(
    name="Billing Specialist",
    instructions="You handle all billing and payment questions...",
    tools=[lookup_invoice, process_refund],
)

triage_agent = Agent(
    name="Triage",
    instructions="Route to the right specialist.",
    handoffs=[billing_agent, technical_agent],
)
```

Under the hood, each handoff target is exposed to the LLM as a tool — a special tool that transfers control instead of returning data. The LLM calls it like any other tool.

### Customising Handoff Behaviour

```python
from agents import handoff

# Custom handoff with a different name/description the LLM sees
billing_handoff = handoff(
    agent=billing_agent,
    tool_name_override="escalate_to_billing",
    tool_description_override="Transfer to billing when the customer has invoice or payment questions",
    on_handoff=lambda ctx: log_handoff_event(ctx),  # Callback on handoff
)

triage_agent = Agent(
    ...,
    handoffs=[billing_handoff, technical_agent],
)
```

---

## Runner

The `Runner` executes an agent loop — it handles the repeated cycle of calling the LLM, executing tools, and processing results until the agent is done.

```python
from agents import Runner

# Synchronous
result = Runner.run_sync(agent, "What's my order status for #12345?")

# Asynchronous
result = await Runner.run(agent, "What's my order status for #12345?")

# Streaming (for UI integration)
async for event in Runner.run_streamed(agent, "..."):
    if event.type == "text_delta":
        print(event.data, end="", flush=True)
```

### The Result Object

```python
result.final_output          # str: the agent's final response
result.new_items             # list: every event (messages, tool calls, handoffs)
result.last_agent            # Agent: which agent produced the final output
result.input_guardrail_results   # Results from input guardrails
result.output_guardrail_results  # Results from output guardrails
```

---

## Guardrails

Guardrails run checks on inputs or outputs. They're the SDK's built-in safety net.

```python
from agents import Agent, input_guardrail, output_guardrail, GuardrailFunctionOutput, RunContextWrapper
from pydantic import BaseModel

class SafetyCheck(BaseModel):
    is_safe: bool
    reason: str

@input_guardrail
async def check_for_pii(ctx: RunContextWrapper, agent: Agent, input: str) -> GuardrailFunctionOutput:
    """Block inputs that contain personally identifiable information."""
    result = await run_pii_check(input)
    return GuardrailFunctionOutput(
        output_info=result,
        tripwire_triggered=result.contains_pii,
    )

agent = Agent(
    name="Safe Agent",
    instructions="...",
    input_guardrails=[check_for_pii],
)
```

If a guardrail's `tripwire_triggered` is `True`, the SDK raises an `InputGuardrailTripwireTriggered` exception before the agent runs.

---

## Context

Context lets you pass custom data through the entire agent run — available to tools, guardrails, and lifecycle hooks without threading it through function arguments.

```python
from dataclasses import dataclass
from agents import RunContextWrapper

@dataclass
class UserContext:
    user_id: str
    account_tier: str
    session_id: str

@function_tool
def get_personalized_recommendation(wrapper: RunContextWrapper[UserContext], category: str) -> str:
    """Get a recommendation tailored to the user's account tier."""
    user = wrapper.context
    return fetch_recommendation(user.user_id, user.account_tier, category)

agent = Agent(name="...", tools=[get_personalized_recommendation])

# Pass context at runtime
result = await Runner.run(
    agent,
    "Recommend something in electronics",
    context=UserContext(user_id="u123", account_tier="premium", session_id="s456"),
)
```

---

## Tracing

The SDK has built-in tracing — every run produces a trace that records agents, tools, handoffs, and LLM calls.

```python
from agents import trace

# Wrap any code in a named trace
with trace("customer_support_flow"):
    result = await Runner.run(triage_agent, user_message)
```

Traces are sent to the OpenAI platform by default. You can disable or redirect them:

```python
from agents.tracing import set_tracing_export_api_key, set_tracing_disabled

set_tracing_disabled(True)   # Disable entirely
```

---

## Common Patterns

### Triage + Specialists
```
triage_agent → (routes to) → specialist_agent_1
                           → specialist_agent_2
                           → specialist_agent_3
```
Best for: support systems, task routing, domain-specific Q&A.

### Sequential Pipeline via Handoffs
```
agent_1 → (handoff) → agent_2 → (handoff) → agent_3
```
Each agent does its part and passes to the next. Different from LangGraph in that handoffs are decided by the LLM, not hardcoded edges.

### Parallelism with asyncio
```python
results = await asyncio.gather(
    Runner.run(research_agent, topic_1),
    Runner.run(research_agent, topic_2),
    Runner.run(research_agent, topic_3),
)
```
The SDK doesn't have native parallel agents, but you can parallelise runs with standard `asyncio.gather`.

---

## Common Pitfalls

**Instructions that are too vague about handoffs.** If you don't tell the triage agent *exactly* when to hand off to each specialist, it guesses. Be explicit: "Hand off to billing when the user mentions an invoice, charge, refund, or payment method."

**Missing context in handoffs.** When an agent hands off, the new agent sees the full conversation history — but not the original agent's instructions. Make sure specialist agents are self-contained in their instructions.

**Over-engineering with handoffs.** If you find yourself creating a chain of 5+ agents that each hand off to the next, you've probably replicated a LangGraph workflow inside the SDK. Consider LangGraph instead.

---

## What to Read Next

- [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/)
- [Agents cookbook](https://cookbook.openai.com)
- [Tracing guide](https://openai.github.io/openai-agents-python/tracing/)
