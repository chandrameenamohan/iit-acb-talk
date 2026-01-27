"""
AI Coding Agent — Complete Solution

A working coding agent in ~300 lines of Python.
This is the facilitator reference / complete solution.
"""

import os
import re
import subprocess
import anthropic

# --- Configuration ---
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096

SYSTEM_PROMPT = """You are a helpful coding assistant. You have access to tools that let you
read, list, edit, and search files, and run bash commands. Use these tools to help the user
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
    {
        "name": "search_files",
        "description": "Search for a regex pattern across files in a directory. Returns matching lines with file paths and line numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The regex pattern to search for",
                },
                "path": {
                    "type": "string",
                    "description": "The directory to search in (defaults to current directory)",
                },
            },
            "required": ["pattern"],
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
    # Safety: block obviously destructive commands
    dangerous_patterns = ["rm -rf /", "rm -rf ~", "mkfs", "> /dev/sd", "dd if="]
    for pattern in dangerous_patterns:
        if pattern in command:
            return f"Error: refusing to run potentially destructive command."

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


def search_files(pattern: str, path: str = ".") -> str:
    """Search for a regex pattern in files under path."""
    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"Invalid regex pattern: {e}"

    matches = []
    for root, dirs, files in os.walk(path):
        # Skip hidden directories and common non-code directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv")]
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if regex.search(line):
                            matches.append(f"{filepath}:{i}: {line.rstrip()}")
                            if len(matches) >= 50:
                                matches.append("(truncated at 50 matches)")
                                return "\n".join(matches)
            except (OSError, UnicodeDecodeError):
                continue

    return "\n".join(matches) if matches else "No matches found."


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
    elif name == "search_files":
        return search_files(input["pattern"], input.get("path", "."))
    else:
        return f"Unknown tool: {name}"


# --- Agent Loop ---


def agent_loop():
    """Main conversation loop."""
    client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var
    messages = []

    print("AI Coding Agent (type 'quit' to exit)")
    print("=" * 40)

    while True:
        # Get user input
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

        # Add user message to conversation
        messages.append({"role": "user", "content": user_input})

        # Inner loop: keep going while the model wants to use tools
        while True:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":
                # Process all tool calls in the response
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

                # Feed tool results back to the model
                messages.append({"role": "user", "content": tool_results})
            else:
                # Model is done — print text blocks
                for block in response.content:
                    if hasattr(block, "text"):
                        print(f"\nAgent: {block.text}")
                break


if __name__ == "__main__":
    agent_loop()
