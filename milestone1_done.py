"""
AI Coding Agent — Milestone 1 Complete
Loop + read_file working.

Provider compatibility (set env vars before running):
  OpenAI (default):  OPENAI_API_KEY=sk-...
  Gemini:            OPENAI_API_KEY=... OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/ MODEL=gemini-2.0-flash
  Ollama:            OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=unused MODEL=qwen2.5
  Anthropic:         OPENAI_API_KEY=sk-ant-... OPENAI_BASE_URL=https://api.anthropic.com/v1/ MODEL=claude-sonnet-4-20250514
"""

import json
from openai import OpenAI
import os

# --- Configuration ---
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("MODEL", "gpt-4o")
MAX_TOKENS = 4096

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SYSTEM_PROMPT = """You are a helpful coding assistant. You have access to tools that let you
read files. Use these tools to help the user with their coding tasks.

Important rules:
- Always read a file before editing it.
- Explain what you're doing before and after making changes.
- Be cautious with bash commands — never run destructive commands."""

# --- Tool Definitions ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file at the given path. Returns the file content as a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to read",
                    }
                },
                "required": ["path"],
            },
        },
    },
]


# --- Tool Implementations ---


def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def execute_tool(name: str, args: dict) -> str:
    """Dispatch a tool call to the right function."""
    if name == "read_file":
        return read_file(args["path"])
    else:
        return f"Unknown tool: {name}"


# --- Agent Loop ---


def agent_loop():
    """Main conversation loop."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("AI Coding Agent (type 'quit' to exit)")
    print("=" * 40)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        while True:
            response = client.chat.completions.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                tools=TOOLS,
                messages=messages,
            )

            message = response.choices[0].message
            messages.append(message)

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    print(f"  [tool] {tool_call.function.name}({args})")
                    result = execute_tool(tool_call.function.name, args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )
            else:
                if message.content:
                    print(f"\nAgent: {message.content}")
                break


if __name__ == "__main__":
    agent_loop()
