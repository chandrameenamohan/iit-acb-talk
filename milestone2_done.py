"""
AI Coding Agent — Milestone 2 Complete
Loop + read_file + list_files + edit_file working.

Provider compatibility (set env vars before running):
  OpenAI (default):  OPENAI_API_KEY=sk-...
  Gemini:            OPENAI_API_KEY=... OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/ MODEL=gemini-2.0-flash
  Ollama:            OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=unused MODEL=qwen2.5
  Anthropic:         OPENAI_API_KEY=sk-ant-... OPENAI_BASE_URL=https://api.anthropic.com/v1/ MODEL=claude-sonnet-4-20250514
"""

import json
import os
from openai import OpenAI

# --- Configuration ---
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("MODEL", "gpt-4o")
MAX_TOKENS = 4096

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SYSTEM_PROMPT = """You are a helpful coding assistant. You have access to tools that let you
read, list, and edit files. Use these tools to help the user with their coding tasks.

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
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at the given path. If no path is provided, lists the current directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to list (defaults to current directory)",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit a file by replacing an exact string match. The old_string must appear exactly once in the file. Read the file first to get the exact content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to edit",
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The exact string to find and replace",
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The string to replace it with",
                    },
                },
                "required": ["path", "old_string", "new_string"],
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


def list_files(path: str = ".") -> str:
    """List files and directories at the given path."""
    try:
        entries = os.listdir(path)
        entries.sort()
        result = []
        for entry in entries:
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                result.append(f"[DIR]  {entry}")
            else:
                result.append(f"[FILE] {entry}")
        return "\n".join(result) if result else "(empty directory)"
    except Exception as e:
        return f"Error listing files: {e}"


def edit_file(path: str, old_string: str, new_string: str) -> str:
    """Replace old_string with new_string in the file at path."""
    try:
        content = read_file(path)
        if content.startswith("Error"):
            return content

        count = content.count(old_string)
        if count == 0:
            return "Error: old_string not found in file."
        if count > 1:
            return f"Error: old_string appears {count} times. Provide a more unique string."

        new_content = content.replace(old_string, new_string, 1)
        with open(path, "w") as f:
            f.write(new_content)
        return "File edited successfully."
    except Exception as e:
        return f"Error editing file: {e}"


def execute_tool(name: str, args: dict) -> str:
    """Dispatch a tool call to the right function."""
    if name == "read_file":
        return read_file(args["path"])
    elif name == "list_files":
        return list_files(args.get("path", "."))
    elif name == "edit_file":
        return edit_file(args["path"], args["old_string"], args["new_string"])
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
