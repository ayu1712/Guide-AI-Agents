# 🤝 AutoGen

> "What if agents just... talked to each other until they figured it out?"

AutoGen, from Microsoft Research, models multi-agent collaboration as **conversation**. Agents take turns speaking in a group chat, and the emergent dialogue produces the solution. It's the most natural framework for tasks where you want agents to debate, critique, and refine.

**⚠️ 2026 note:** Microsoft has shifted strategic focus from AutoGen to the broader Microsoft Agent Framework. AutoGen receives bug fixes and security patches, but major new feature development has slowed. It's still usable and has a large community, but consider this when planning long-term projects.

---

## The Core Idea

Humans solve problems through dialogue. A developer, a code reviewer, and a tester can work together by just... talking. AutoGen models this literally: each agent is a participant in a conversation, with a role defined by its system prompt and a set of tools it can use.

```
User Proxy → "Write me a sorting algorithm and test it"
    ↓
Assistant → "Here's quicksort in Python..." [writes code]
    ↓
Code Executor → [runs the code] "Tests pass. Output: [1, 2, 3]"
    ↓
Assistant → "The implementation is complete."
```

The conversation continues until a termination condition is met (a keyword like "TERMINATE", a max turn limit, or a custom function).

---

## Key Concepts

### ConversableAgent
The base agent class. Every AutoGen agent is a `ConversableAgent` or a subclass.

```python
from autogen import ConversableAgent

agent = ConversableAgent(
    name="assistant",
    system_message="You are a helpful assistant that writes clean Python code.",
    llm_config={"model": "claude-sonnet-4-5", "api_key": "..."},
)
```

### UserProxyAgent
A special agent that can execute code and represent the human in the conversation. Often used as the "task initiator".

```python
from autogen import UserProxyAgent

user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="NEVER",   # NEVER=fully automated, ALWAYS=human in loop, TERMINATE=ask at end
    code_execution_config={"work_dir": "output", "use_docker": False},
    max_consecutive_auto_reply=5,
)
```

### GroupChat
Multiple agents in a shared conversation. A `GroupChatManager` decides who speaks next.

```python
from autogen import GroupChat, GroupChatManager

group_chat = GroupChat(
    agents=[researcher, writer, critic],
    messages=[],
    max_round=10,
)

manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
user_proxy.initiate_chat(manager, message="Research and write a report on AI agents")
```

---

## Quickstart

See [`quickstart.py`](./quickstart.py) for a working two-agent code-writing and execution example.

Install:
```bash
pip install pyautogen
```

---

## When AutoGen Wins

- **Agents that need to debate** — consensus-building, code review, adversarial fact-checking
- **Code generation + execution loops** — the UserProxyAgent + code executor pattern is excellent for iterative coding tasks
- **Exploratory tasks** — when you don't know the exact steps upfront and want agents to figure it out conversationally
- **Multi-party dialogues** — GroupChat handles complex turn-taking that other frameworks don't model naturally

---

## When AutoGen Loses

- **Predictable production workflows** — emergent conversation means unpredictable token usage and execution paths
- **You need explicit control flow** — "this runs then that runs" is hard to enforce in conversation
- **Long-term project investment** — AutoGen is in maintenance mode; consider LangGraph or CrewAI for greenfield projects
- **Structured outputs** — free-form conversation makes it harder to get consistent JSON/Pydantic outputs

---

## Honest Trade-offs

| Strength | Weakness |
|---|---|
| Most natural multi-agent model | Non-deterministic, hard to predict |
| Excellent code generation + execution | In maintenance mode as of 2026 |
| GroupChat handles complex turn-taking | Token costs can spiral in long chats |
| AutoGen Studio for no-code prototyping | Debugging conversation chains is painful |

---

## The One Thing to Remember

AutoGen is the **conversation framework**. If your problem naturally involves agents that need to talk through something — debate, critique, revise, re-examine — AutoGen's model fits. If you need predictable steps and structured outputs, it doesn't.

Given its 2026 maintenance status, prefer AutoGen for experimentation and learning over new production systems.

---

## Further Reading

- [AutoGen docs](https://microsoft.github.io/autogen/)
- [AutoGen GitHub](https://github.com/microsoft/autogen)
- [AutoGen Studio (no-code)](https://microsoft.github.io/autogen/docs/autogen-studio/getting-started)
