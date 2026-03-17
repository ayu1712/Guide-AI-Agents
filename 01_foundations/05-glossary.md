\# Glossary



\*Chapter 05 of \[Foundations](./README.md)\*



---



> \*"The Guide is definitive. Reality is frequently inaccurate."\*



The field of AI agents has a jargon problem. Terms are used confidently, inconsistently, and sometimes in direct contradiction with how the same term was used in the paper published last Tuesday.



The following are the most honest definitions available as of the time of writing.



---



\## A



\*\*Agent\*\*

An AI system that pursues goals, uses tools, and adapts based on observations. See \[Chapter 01](./01-what-is-an-agent.md) for the full treatment. Sometimes also used to mean "any AI that does more than one thing in sequence," which is less useful but extremely common.



\*\*Agentic loop\*\*

The cycle of think → act → observe that powers most agents. Also called the "agent loop," the "reasoning loop," or, by engineers debugging a stuck agent at 2am, various other things.



\*\*Autonomy\*\*

The degree to which an agent operates without human input. A spectrum, not a binary. See the note at the end of Chapter 01.



\## C



\*\*Chain-of-Thought (CoT)\*\*

Prompting a model to reason step-by-step before answering. Dramatically improves performance on reasoning tasks. Famous for working so well that it seemed like cheating.



\*\*Context window\*\*

The maximum amount of text (in tokens) a model can process at once. Everything the agent knows about its current task must fit here. When it doesn't fit, you have an architecture problem.



\## F



\*\*Function calling\*\*

See \*Tool use\*. Same thing, different name used by different providers.



\*\*Guardrails\*\*

Constraints on what an agent can do. Implemented in the system prompt, in tools themselves, in the orchestration layer, or all three if you are wise.



\## H



\*\*Hallucination\*\*

When a model generates confident, fluent, plausible-sounding nonsense. In a chatbot, annoying. In an agent that acts on its outputs, a production incident. Understanding when hallucinations occur is foundational to building trustworthy agents.



\## M



\*\*MCP (Model Context Protocol)\*\*

A standard for connecting language models to tools and data sources. Developed by Anthropic, now widely adopted. Essentially a USB standard for agent tools — implement once, works everywhere. Covered in detail in \[Section 03](../03\_frameworks/).



\*\*Memory\*\*

How agents persist information. Four types: in-context (in the window), external (in a database), semantic (vector embeddings), episodic (logs of past runs). See \[Chapter 02](./02-anatomy-of-an-agent.md).



\*\*Multi-agent system\*\*

Multiple agents collaborating on a task, each specialised, coordinated by an orchestrator. Powerful. Also a great way to multiply your infrastructure costs and discover new distributed systems problems.



\## O



\*\*Orchestration\*\*

The code that manages the agent loop: passes tool results back, handles errors, decides when to stop, routes between agents. Can be a while loop. Can be a graph-based state machine with conditional routing. Section 03 covers the frameworks that do this for you.



\## R



\*\*RAG (Retrieval-Augmented Generation)\*\*

Giving agents access to knowledge that doesn't fit in the context window by storing it in a database and retrieving relevant chunks on demand. Not the same as an agent, but most agents that need domain knowledge use some form of RAG.



\*\*ReAct\*\*

Reasoning + Acting. The standard agent pattern: think about what to do → call a tool → observe the result → think again → repeat. See \[Chapter 03](./03-how-agents-think.md).



\## S



\*\*System prompt\*\*

Instructions given to the model before the user's input. Where you define the agent's role, tools, constraints, and context. The quality of your system prompt is directly correlated with the quality of your agent's outputs. This is not a metaphor.



\## T



\*\*Token\*\*

The unit of text a language model processes. Roughly ¾ of a word in English. Models are billed by token. Context windows are measured in tokens. Your infrastructure costs are measured in tokens.



\*\*Tool\*\*

A function the agent can call to interact with the world: search the web, run code, read files, call APIs. The model doesn't run the tool — it requests the call, your code runs it, the result goes back to the model.



\*\*Tool use / Function calling\*\*

The capability that allows a model to request execution of external functions. The thing that turns a language model into an agent.



---



\*\[← Back to Foundations](./README.md) · \[Back to main guide](../README.md)\*

