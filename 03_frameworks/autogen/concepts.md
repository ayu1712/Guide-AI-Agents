# AutoGen — Core Concepts

How AutoGen actually works, and the key ideas behind its conversational model.

---

## The Mental Model

AutoGen treats problem-solving as **dialogue**. Instead of defining a graph of steps or a roster of tasks, you define participants in a conversation and let the dialogue produce the result.

This is powerful when the solution path isn't known upfront. Two agents debating a coding problem will often find a better solution than a single agent following a prescribed plan — because the back-and-forth surfaces errors, alternatives, and edge cases.

The trade-off: conversation is inherently non-deterministic. You can't predict exactly what path the agents will take, how many turns it will take, or how many tokens it will use.

---

## ConversableAgent

Every AutoGen agent is a `ConversableAgent` or a subclass. It's the base class for everything.

```python
from autogen import ConversableAgent

agent = ConversableAgent(
    name="assistant",
    system_message="You are a helpful Python expert.",
    llm_config={
        "config_list": [{"model": "gpt-4o", "api_key": "..."}],
        "temperature": 0,
    },
    human_input_mode="NEVER",      # NEVER | TERMINATE | ALWAYS
    max_consecutive_auto_reply=5,  # Prevents infinite loops
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
)
```

### human_input_mode

Controls when AutoGen pauses and waits for a human:

- `"NEVER"` — fully automated, no human involvement
- `"TERMINATE"` — runs automatically, asks human when a termination condition is met
- `"ALWAYS"` — asks human after every agent response (useful for debugging)

### is_termination_msg

A function that receives a message dict and returns `True` if the conversation should stop. The most common pattern is checking for a keyword like `"TERMINATE"` in the message content.

```python
# Simple keyword check
is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", "")

# More robust: check only in non-empty messages
is_termination_msg=lambda msg: bool(msg.get("content")) and "TERMINATE" in msg["content"]
```

Termination is checked on every message. The conversation ends when *either* agent's `is_termination_msg` returns True.

---

## UserProxyAgent

A special subclass of `ConversableAgent` that represents the human or the "executor" side of a conversation. Its main superpower: **it can run code**.

```python
from autogen import UserProxyAgent

user_proxy = UserProxyAgent(
    name="executor",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "agent_workspace",  # Code runs here
        "use_docker": False,            # True = safer sandbox in production
        "timeout": 30,                  # Seconds before code execution times out
    },
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
)
```

When the `AssistantAgent` produces a message with a Python code block, `UserProxyAgent` automatically extracts and executes it, then returns the output as its next message. This creates the natural write → run → fix → run loop.

### Code Execution Safety

In production, always use Docker:

```python
code_execution_config={
    "use_docker": "python:3.11-slim",  # Docker image to use
    "work_dir": "workspace",
}
```

Without Docker, the agent executes code in your Python environment with your permissions. That's fine for local experiments, not for anything that touches external input.

---

## AssistantAgent

A pre-configured `ConversableAgent` tuned for writing and explaining code. It's just a `ConversableAgent` with a specific system message — you can replicate it manually.

```python
from autogen import AssistantAgent

assistant = AssistantAgent(
    name="coder",
    llm_config=llm_config,
    # system_message is pre-set to something like:
    # "You are a helpful AI assistant. Solve tasks using your coding and language skills.
    #  When you finish all tasks, reply TERMINATE."
)
```

---

## Two-Agent Conversation

The simplest AutoGen pattern: one agent initiates, they take turns.

```python
user_proxy.initiate_chat(
    assistant,                           # Who to talk to
    message="Fix this buggy code: ...",  # Opening message
    max_turns=10,                        # Hard limit on turns
)
```

`initiate_chat` is synchronous and blocks until the conversation terminates.

The conversation history is stored in `user_proxy.chat_messages[assistant]`.

---

## GroupChat

Multiple agents in a shared conversation. A `GroupChatManager` (itself an LLM) decides who speaks next.

```python
from autogen import GroupChat, GroupChatManager

researcher = ConversableAgent(name="researcher", ...)
writer = ConversableAgent(name="writer", ...)
critic = ConversableAgent(name="critic", ...)

group_chat = GroupChat(
    agents=[researcher, writer, critic],
    messages=[],
    max_round=15,                         # Max total turns across all agents
    speaker_selection_method="auto",      # LLM picks next speaker
    allow_repeat_speaker=False,           # Prevent the same agent twice in a row
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
)

# Initiate from a user proxy — it joins the group chat
user_proxy.initiate_chat(manager, message="Research and write a report on X")
```

### Speaker Selection Methods

- `"auto"` — the manager LLM decides who speaks next (most flexible, most expensive)
- `"round_robin"` — agents take turns in order (deterministic, ignores context)
- `"random"` — random selection (rarely useful)
- Custom function — you write the selection logic

For most use cases, `"auto"` works best. `"round_robin"` is useful when you have a fixed pipeline (researcher → writer → editor) and want predictable execution.

---

## Nested Chats

An agent can initiate a sub-conversation with another agent as part of handling a message. Useful for delegation patterns.

```python
from autogen import register_nested_chats

register_nested_chats(
    trigger=writer,              # When this agent receives a message...
    chat_queue=[{
        "recipient": researcher,  # ...it first consults this agent
        "message": "What are the key facts I need for this report?",
        "max_turns": 3,
    }]
)
```

---

## LLM Config

AutoGen uses a `config_list` pattern that allows fallback across multiple models/API keys:

```python
config_list = [
    {"model": "gpt-4o", "api_key": os.environ["OPENAI_API_KEY"]},
    {"model": "gpt-4o-mini", "api_key": os.environ["OPENAI_API_KEY"]},  # Fallback
]

llm_config = {
    "config_list": config_list,
    "temperature": 0,
    "timeout": 60,
    "cache_seed": 42,   # Cache LLM responses for reproducibility during dev
}
```

`cache_seed` is genuinely useful during development — same inputs return cached responses, saving money and time. Set to `None` in production.

---

## Common Patterns

### Code Writing + Execution
```
UserProxy ←→ AssistantAgent
```
Assistant writes code. UserProxy runs it. Loops until correct or max_turns reached.

### Debate and Consensus
```
UserProxy → GroupChat[AgentA, AgentB, AgentC]
```
Agents argue different perspectives. Manager LLM synthesises consensus.

### Critic Loop
```
UserProxy ←→ Writer
              ↕ (nested chat)
           Critic
```
Writer produces draft. Critic reviews. Writer revises. Repeat until critic approves.

---

## Common Pitfalls

**Infinite loops.** Always set `max_consecutive_auto_reply` and `max_turns`. Without these, a conversation with no clear termination condition will run forever.

**Token costs spiral in GroupChat.** Every agent receives the full conversation history. With 5 agents and 20 rounds, you're paying for the full history 100 times. Use `max_round` aggressively.

**Code execution without Docker.** In any environment where the input isn't fully trusted, always use Docker. The agent will run whatever code the LLM produces.

**Termination keyword in the middle of a message.** If an agent says "this is not TERMINATE" mid-sentence, the conversation ends. Make your termination check specific:
```python
is_termination_msg=lambda msg: msg.get("content", "").strip().endswith("TERMINATE")
```

---

## What to Read Next

- [AutoGen docs](https://microsoft.github.io/autogen/)
- [AutoGen conversation patterns](https://microsoft.github.io/autogen/docs/topics/conversation-patterns)
- [AutoGen code execution](https://microsoft.github.io/autogen/docs/topics/code-execution)
