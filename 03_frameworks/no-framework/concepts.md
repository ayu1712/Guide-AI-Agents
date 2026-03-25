# No Framework — Core Concepts

What every framework is doing under the hood. These are the concepts that transfer regardless of which tool you eventually pick up.

---

## The Agent Loop

Every AI agent, regardless of framework, is a loop over this structure:

```
1. Receive input
2. Add to message history
3. Call LLM with history + tools
4. If LLM returns tool calls:
     a. Execute each tool
     b. Add results to history
     c. Go to step 3
5. If LLM returns final text:
     a. Return it
```

That's it. Every framework — LangGraph, CrewAI, AutoGen, all of them — is this loop with different abstractions layered on top.

Knowing this loop intimately makes you better at using frameworks, because you understand what they're doing for you (and when they're getting in your way).

---

## Message History

The message history is the agent's working memory. It's a list of dictionaries in the format your LLM expects. The LLM has no memory between calls — the history *is* the context.

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant with tools."},
    {"role": "user", "content": "What is 2 + 2?"},
    # After LLM calls calculate tool:
    {"role": "assistant", "content": None, "tool_calls": [...]},
    # After tool runs:
    {"role": "tool", "content": "4", "tool_call_id": "..."},
    # LLM sees the result and responds:
    # {"role": "assistant", "content": "2 + 2 = 4."}
]
```

### The History Growth Problem

History only grows. A long-running agent accumulates thousands of tokens of history. This causes two problems:

1. **Cost** — you pay for every token in the history on every call
2. **Context window limits** — even the largest models have limits

Solutions, in order of complexity:

**Sliding window** — keep only the last N messages:
```python
MAX_HISTORY = 20
messages = messages[-MAX_HISTORY:]  # Keep system message separately
```

**Summarisation** — when history gets long, ask the LLM to summarise it:
```python
if len(messages) > THRESHOLD:
    summary = llm.summarise(messages[:-5])
    messages = [system_message, {"role": "assistant", "content": summary}] + messages[-5:]
```

**Selective retention** — keep only tool results and final answers, discard reasoning steps.

---

## Tool Definition

Tools are defined as JSON schemas that tell the LLM what's available, what parameters each tool takes, and when to use it.

```python
tools = [
    {
        "name": "search_web",
        "description": (
            "Search the web for current information. "
            "Use this when you need facts you don't know or that may have changed recently."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific for better results."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return. Default 5.",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
]
```

### Tool Descriptions Are Prompts

The `description` field is what the LLM reads to decide whether to call this tool. Write it from the LLM's perspective:

- What does this tool do?
- When should I call it?
- What should I expect back?

A vague description like `"search the web"` performs worse than a specific one like `"Search the web for current information. Use this when you need facts you don't know or that may have changed recently."`

---

## Tool Dispatch

The simplest tool dispatcher is a dictionary lookup:

```python
# Registry: name → function
TOOLS = {
    "search_web": search_web,
    "calculate": calculate,
    "get_weather": get_weather,
}

def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name not in TOOLS:
        return f"Error: unknown tool '{tool_name}'"
    
    try:
        result = TOOLS[tool_name](**tool_input)
        return str(result)
    except TypeError as e:
        return f"Error: invalid arguments — {e}"
    except Exception as e:
        return f"Error: tool execution failed — {e}"
```

Always wrap tool execution in try/except. A tool that raises an unhandled exception kills the agent loop. Return the error as a string — the LLM can read it, understand what went wrong, and try a different approach.

---

## State

For simple agents, state is just the message history. For more complex agents, you need additional state: what plan is being followed, what tools have been called, what partial results have been collected.

### Minimal State

```python
from dataclasses import dataclass, field

@dataclass
class AgentState:
    messages: list = field(default_factory=list)
    tool_calls_made: int = 0
    errors: list = field(default_factory=list)
    result: str = ""
```

Pass this through your loop and update it as you go. No magic, no framework.

### When State Gets Complex

If you find your state object growing large and hard to reason about, that's the signal to consider a framework with explicit state management (LangGraph). Until then, keep it simple.

---

## Retries and Error Handling

Production agents need to handle failures gracefully. Three levels of retry:

**Tool-level retry** — retry a specific tool call that failed:
```python
import time

def execute_tool_with_retry(tool_name, tool_input, max_retries=3):
    for attempt in range(max_retries):
        try:
            return TOOLS[tool_name](**tool_input)
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Tool failed after {max_retries} attempts: {e}"
            time.sleep(2 ** attempt)   # Exponential backoff: 1s, 2s, 4s
```

**LLM-level retry** — retry the API call if it fails:
```python
def call_llm_with_retry(messages, tools, max_retries=3):
    for attempt in range(max_retries):
        try:
            return llm.create(messages=messages, tools=tools)
        except RateLimitError:
            time.sleep(60)   # Wait for rate limit to reset
        except APIError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

**Loop-level guard** — the `max_iterations` parameter in your outer loop:
```python
for iteration in range(max_iterations):
    ...
    
return "Max iterations reached — no final answer produced."
```

Always have all three. The loop guard is your last line of defence against runaway agents.

---

## Memory Beyond the Context Window

Context window memory disappears when the conversation ends. For persistent memory, you need external storage.

### Simple File-Based Memory

```python
import json
from pathlib import Path

def save_memory(user_id: str, memory: dict):
    Path(f"memory/{user_id}.json").write_text(json.dumps(memory))

def load_memory(user_id: str) -> dict:
    path = Path(f"memory/{user_id}.json")
    return json.loads(path.read_text()) if path.exists() else {}
```

### Vector Memory

For semantic recall ("what did the user say about X last time?"):

```python
from your_vector_db import VectorStore

store = VectorStore()

# After each conversation
store.upsert(user_id, conversation_summary, embedding)

# At the start of a new conversation
relevant_memories = store.query(user_id, current_message, top_k=3)
```

Most agent memory use cases don't need vector search. Start with a simple JSON file. Add complexity when you have a concrete reason to.

---

## Observability Without a Framework

You don't need LangSmith to observe your agent. Standard Python logging is often enough:

```python
import logging
import time

logger = logging.getLogger("agent")

def run_agent(user_message: str) -> str:
    start = time.time()
    messages = [{"role": "user", "content": user_message}]
    
    for iteration in range(max_iterations):
        response = call_llm(messages)
        
        logger.info(f"Iteration {iteration}: stop_reason={response.stop_reason}")
        
        if response.has_tool_calls:
            for tool_call in response.tool_calls:
                tool_start = time.time()
                result = execute_tool(tool_call.name, tool_call.input)
                logger.info(f"Tool {tool_call.name}: {time.time() - tool_start:.2f}s")
        else:
            logger.info(f"Total: {time.time() - start:.2f}s, iterations: {iteration + 1}")
            return response.content
```

Log: iteration count, tool names and durations, total elapsed time, stop reason. That's 80% of what you need for production debugging.

---

## The Upgrade Path

Start raw. Add complexity only when you hit a specific pain point:

| Pain point | Add this |
|---|---|
| Control flow is getting messy | LangGraph |
| Multiple agents are hard to coordinate | CrewAI or AutoGen |
| You need persistent checkpointing | LangGraph checkpointer |
| Debugging is impossible | LangSmith or structured logging |
| You need human approval steps | LangGraph interrupt |
| You need parallel agent execution | asyncio + LangGraph Send |

Don't solve problems you don't have yet.
