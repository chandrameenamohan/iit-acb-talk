"""
AI Coding Agent — Milestone 3 Complete
Loop + read_file + list_files + edit_file + run_bash working.
"""

import os
import subprocess
import anthropic

# --- Configuration ---
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096

SYSTEM_PROMPT = """You are a helpful coding assistant. You have access to tools that let you
read, list, and edit files, and run bash commands. Use these tools to help the user
with their coding tasks.

Important rules:
- Always read a file before editing it.
- Use the tools available to you rather than guessing at file contents.
- Explain what you're doing before and after making changes.
- Be cautious with bash commands — never run destructive commands."""

# --- Tool Definitions ---

TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path. Returns the file content as a string.",
        "input_schema": {
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
    {
        "name": "list_files",
        "description": "List files and directories at the given path. If no path is provided, lists the current directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory path to list (defaults to current directory)",
                }
            },
        },
    },
    {
        "name": "edit_file",
        "description": "Edit a file by replacing an exact string match. The old_string must appear exactly once in the file. Read the file first to get the exact content.",
        "input_schema": {
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
    {
        "name": "run_bash",
        "description": "Run a bash command and return its stdout and stderr. Use this for running tests, installing packages, or other shell operations. Do not use for destructive commands like rm -rf.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute",
                }
            },
            "required": ["command"],
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


def run_bash(command: str) -> str:
    """Run a bash command with basic safety checks."""
    dangerous_patterns = ["rm -rf /", "rm -rf ~", "mkfs", "> /dev/sd", "dd if="]
    for pattern in dangerous_patterns:
        if pattern in command:
            return "Error: refusing to run potentially destructive command."

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("" if not output else "\n") + f"STDERR: {result.stderr}"
        if not output:
            output = "(no output)"
        return output
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 30 seconds."
    except Exception as e:
        return f"Error running command: {e}"


def execute_tool(name: str, input: dict) -> str:
    """Dispatch a tool call to the right function."""
    if name == "read_file":
        return read_file(input["path"])
    elif name == "list_files":
        return list_files(input.get("path", "."))
    elif name == "edit_file":
        return edit_file(input["path"], input["old_string"], input["new_string"])
    elif name == "run_bash":
        return run_bash(input["command"])
    else:
        return f"Unknown tool: {name}"


# --- Agent Loop ---


def agent_loop():
    """Main conversation loop."""
    client = anthropic.Anthropic()
    messages = []

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
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"  [tool] {block.name}({block.input})")
                        result = execute_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result,
                            }
                        )
                messages.append({"role": "user", "content": tool_results})
            else:
                for block in response.content:
                    if hasattr(block, "text"):
                        print(f"\nAgent: {block.text}")
                break


if __name__ == "__main__":
    agent_loop()
