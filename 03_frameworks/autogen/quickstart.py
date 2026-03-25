"""
AutoGen Quickstart — A two-agent coding assistant

What this builds:
  An Assistant that writes code + a UserProxy that executes it.
  They converse until the task is done or a limit is hit.

Install:
  pip install pyautogen

Run:
  python quickstart.py
"""

from autogen import ConversableAgent, UserProxyAgent

# ── LLM configuration ─────────────────────────────────────────────────────────
# AutoGen uses a config_list pattern for LLM settings.
# You can use any OpenAI-compatible API, including Anthropic via proxy.

llm_config = {
    "config_list": [
        {
            "model": "gpt-4o",           # Swap for claude-sonnet-4-5 if using Anthropic
            "api_key": "your-api-key",   # Or use env: os.environ["OPENAI_API_KEY"]
        }
    ],
    "timeout": 60,
    "temperature": 0,
}


# ── 1. The Assistant agent ────────────────────────────────────────────────────
# Writes code and explains its reasoning.
# When it's done, it says TERMINATE.

assistant = ConversableAgent(
    name="coding_assistant",
    system_message=(
        "You are an expert Python developer. "
        "When asked to write code, provide clean, well-commented solutions. "
        "After the code has been successfully executed, say TERMINATE."
    ),
    llm_config=llm_config,
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
)


# ── 2. The UserProxy agent ────────────────────────────────────────────────────
# Executes code that the assistant writes.
# human_input_mode="NEVER" means fully automated — no human in the loop.

user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "agent_output",    # Code runs in this directory
        "use_docker": False,           # Set True in production for safety
    },
    max_consecutive_auto_reply=5,     # Stops infinite loops
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
)


# ── 3. Start the conversation ─────────────────────────────────────────────────

if __name__ == "__main__":
    print("AutoGen — Code Writing + Execution Agent")
    print("=" * 40)

    user_proxy.initiate_chat(
        assistant,
        message=(
            "Write a Python function that finds all prime numbers up to N "
            "using the Sieve of Eratosthenes. Then test it with N=50."
        ),
    )


# ── What's happening ──────────────────────────────────────────────────────────
#
# Conversation flow:
#
#   user_proxy → "Write a prime sieve and test it with N=50"
#       ↓
#   assistant → "Here's the code: [writes sieve function + test]"
#       ↓
#   user_proxy → [executes the code] → "Output: [2, 3, 5, 7, 11, ...]"
#       ↓
#   assistant → "The function works correctly. TERMINATE"
#       ↓
#   Conversation ends (TERMINATE detected)
#
# The UserProxy automatically extracts code blocks from the assistant's
# messages and executes them. Results are fed back as the next message.
#
# Try changing the task to something iterative — e.g. "write code to
# scrape a website, run it, fix any errors, run again" — to see how
# the conversation naturally handles failure and retry.
#
# For multi-agent conversations, see:
#   from autogen import GroupChat, GroupChatManager
