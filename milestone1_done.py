"""
AI Coding Agent — Milestone 1 Complete
Loop + read_file working.
"""

import anthropic

# --- Configuration ---
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096

SYSTEM_PROMPT = """You are a helpful coding assistant. You have access to tools that let you
read files. Use these tools to help the user with their coding tasks.

Important rules:
- Always read a file before editing it.
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
]


# --- Tool Implementations ---


def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def execute_tool(name: str, input: dict) -> str:
    """Dispatch a tool call to the right function."""
    if name == "read_file":
        return read_file(input["path"])
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
