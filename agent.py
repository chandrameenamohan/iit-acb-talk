"""
AI Coding Agent — Workshop Starter Code

Fill in the TODOs to build your own coding agent!

Milestones:
  1. Get the loop running with read_file (0-30 min)
  2. Add list_files and edit_file (30-60 min)
  3. Add bash execution with safety checks (60-90 min)
  4. Polish, test, stretch goals (90-120 min)
"""

import os
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
# These tell the model what tools are available and their parameters.

TOOLS = [
    # MILESTONE 1: Start with just this tool
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
    # MILESTONE 2: Add these two tools
    #
    # TODO: Add a "list_files" tool definition
    #   - name: "list_files"
    #   - description: List files and directories at the given path (defaults to ".")
    #   - input_schema: one optional property "path" (string)
    #
    # TODO: Add an "edit_file" tool definition
    #   - name: "edit_file"
    #   - description: Edit a file by replacing old_string with new_string
    #   - input_schema: three required properties:
    #       "path" (string), "old_string" (string), "new_string" (string)
    #
    # MILESTONE 3: Add bash tool
    #
    # TODO: Add a "run_bash" tool definition
    #   - name: "run_bash"
    #   - description: Run a bash command and return stdout/stderr
    #   - input_schema: one required property "command" (string)
    #
    # STRETCH: Add search tool
    #
    # TODO: Add a "search_files" tool definition
    #   - name: "search_files"
    #   - description: Search for a regex pattern in files
    #   - input_schema: required "pattern" (string), optional "path" (string)
]


# --- Tool Implementations ---

def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


# TODO (MILESTONE 2): Implement list_files
# def list_files(path: str = ".") -> str:
#     """List files and directories at the given path."""
#     ...


# TODO (MILESTONE 2): Implement edit_file
# def edit_file(path: str, old_string: str, new_string: str) -> str:
#     """Replace old_string with new_string in the file at path."""
#     ...


# TODO (MILESTONE 3): Implement run_bash
# def run_bash(command: str) -> str:
#     """Run a bash command. Add safety checks!"""
#     ...


# TODO (STRETCH): Implement search_files
# def search_files(pattern: str, path: str = ".") -> str:
#     """Search for a regex pattern in files under path."""
#     ...


def execute_tool(name: str, input: dict) -> str:
    """Dispatch a tool call to the right function."""
    if name == "read_file":
        return read_file(input["path"])

    # TODO (MILESTONE 2): Add cases for list_files and edit_file
    # elif name == "list_files":
    #     return list_files(input.get("path", "."))
    # elif name == "edit_file":
    #     return edit_file(input["path"], input["old_string"], input["new_string"])

    # TODO (MILESTONE 3): Add case for run_bash
    # elif name == "run_bash":
    #     return run_bash(input["command"])

    # TODO (STRETCH): Add case for search_files
    # elif name == "search_files":
    #     return search_files(input["pattern"], input.get("path", "."))

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

        # --- Inner loop: keep going while the model wants to use tools ---
        while True:
            # TODO: Call the Anthropic API
            #   Use client.messages.create() with:
            #     model=MODEL, max_tokens=MAX_TOKENS, system=SYSTEM_PROMPT,
            #     tools=TOOLS, messages=messages
            response = None  # Replace this line!

            # TODO: Append the assistant's response to messages
            #   messages.append({"role": "assistant", "content": response.content})

            # TODO: Check response.stop_reason
            #   If "tool_use":
            #     - Find tool_use blocks in response.content
            #     - Execute each tool using execute_tool()
            #     - Build tool_result messages and append to messages
            #     - Continue the loop
            #   If "end_turn" (or anything else):
            #     - Print text blocks from response.content
            #     - Break out of the inner loop

            break  # Remove this once you implement the logic above


if __name__ == "__main__":
    agent_loop()
