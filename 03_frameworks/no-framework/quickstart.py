"""
No-Framework Quickstart — A raw agent loop from scratch

What this builds:
  A complete ReAct agent using only the Anthropic SDK.
  No LangGraph, no CrewAI, no AutoGen. Just Python and an LLM.

Install:
  pip install anthropic

Run:
  python quickstart.py
  
Why read this:
  This is what every framework is doing under the hood.
  Understanding this makes you better at using frameworks.
"""

import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-5"


# ── 1. Define tools (plain Python functions) ────────────────────────────────

def search_web(query: str) -> str:
    """Simulated web search. Replace with real API (Tavily, Serper, etc.)"""
    return f"[Search result for '{query}']: AI agents use LLM reasoning + tools to complete tasks autonomously."

def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def get_current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── 2. Tool registry ────────────────────────────────────────────────────────
# A dict mapping tool names to functions.
# This is your "tool dispatcher" — what frameworks do for you automatically.

TOOLS = {
    "search_web": search_web,
    "calculate": calculate,
    "get_current_time": get_current_time,
}

# Tool definitions in the format the API expects
TOOL_DEFINITIONS = [
    {
        "name": "search_web",
        "description": "Search the web for information about a topic",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "The search query"}},
            "required": ["query"],
        },
    },
    {
        "name": "calculate",
        "description": "Evaluate a mathematical expression",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "Math expression to evaluate"}},
            "required": ["expression"],
        },
    },
    {
        "name": "get_current_time",
        "description": "Get the current date and time",
        "input_schema": {"type": "object", "properties": {}},
    },
]


# ── 3. The agent loop ────────────────────────────────────────────────────────
# This is the core of every AI agent, laid bare.

def run_agent(user_message: str, max_iterations: int = 10) -> str:
    """
    Run an agent loop until the LLM produces a final answer.
    
    Steps:
      1. Add user message to history
      2. Call LLM
      3. If LLM calls tools → execute them → add results → go to 2
      4. If LLM gives final text response → return it
    """
    messages = [{"role": "user", "content": user_message}]
    
    for iteration in range(max_iterations):
        print(f"  [Iteration {iteration + 1}] Calling LLM...")
        
        # Call the LLM
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )
        
        # If the LLM is done (no tool calls), return its response
        if response.stop_reason == "end_turn":
            final_text = next(
                (block.text for block in response.content if hasattr(block, "text")),
                ""
            )
            return final_text
        
        # The LLM wants to call tools
        if response.stop_reason == "tool_use":
            # Add the assistant's response (with tool call requests) to history
            messages.append({"role": "assistant", "content": response.content})
            
            # Execute each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    
                    print(f"  [Tool] {tool_name}({json.dumps(tool_input)})")
                    
                    # Dispatch to the right function
                    if tool_name in TOOLS:
                        func = TOOLS[tool_name]
                        result = func(**tool_input)
                    else:
                        result = f"Error: Unknown tool '{tool_name}'"
                    
                    print(f"  [Result] {result}")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            
            # Add tool results to history and loop back to LLM
            messages.append({"role": "user", "content": tool_results})
    
    return "Max iterations reached without a final answer."


# ── 4. Run it ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Raw Agent Loop — No Framework")
    print("=" * 40)
    
    question = "What is 1337 * 42? Also, what time is it right now?"
    print(f"Question: {question}\n")
    
    answer = run_agent(question)
    
    print("\n" + "=" * 40)
    print(f"Final answer:\n{answer}")


# ── Annotated flow ──────────────────────────────────────────────────────────
#
# messages = [{"role": "user", "content": "What is 1337 * 42?"}]
#
# Iteration 1:
#   LLM decides to call calculate("1337 * 42") and get_current_time()
#   stop_reason = "tool_use"
#   → execute both tools
#   → append results to messages
#
# Iteration 2:
#   LLM sees the tool results, synthesises final answer
#   stop_reason = "end_turn"
#   → return the text
#
# That's the entire agent pattern. Every framework wraps this in 
# more abstraction, more features, and more magic.
# Now you know what's behind the curtain.
