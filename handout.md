# Building an AI Coding Agent — Reference Handout

## Architecture

```
┌─────────────────────────────────────────┐
│              AGENT LOOP                 │
│                                         │
│   User Input                            │
│       │                                 │
│       ▼                                 │
│   ┌─────────┐                           │
│   │  LLM    │◄─── System Prompt         │
│   │ (Claude)│                           │
│   └────┬────┘                           │
│        │                                │
│        ▼                                │
│   ┌─────────┐    ┌──────────────────┐   │
│   │ Tool    │───►│ Execute Tool     │   │
│   │ Call?   │    │ (read, edit,     │   │
│   └────┬────┘    │  list, bash,     │   │
│        │ No      │  search)         │   │
│        ▼         └────────┬─────────┘   │
│   Print Response          │             │
│                           ▼             │
│                    Feed result back     │
│                    to LLM ─────►loop    │
└─────────────────────────────────────────┘
```

## The 5 Core Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `read_file` | Read file contents | `path` |
| `list_files` | List directory contents | `path` (optional) |
| `edit_file` | Replace text in a file | `path`, `old_string`, `new_string` |
| `run_bash` | Execute shell commands | `command` |
| `search_files` | Regex search in files | `pattern`, `path` (optional) |

## Tool Definition Format (for Anthropic API)

```python
{
    "name": "read_file",
    "description": "Read the contents of a file",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read"
            }
        },
        "required": ["path"]
    }
}
```

## The Agent Loop (Pseudocode)

```python
messages = []
while True:
    user_input = input("> ")
    messages.append({"role": "user", "content": user_input})

    while True:  # tool loop
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            max_tokens=4096,
        )

        # Collect assistant response
        messages.append({"role": "assistant", "content": response.content})

        # If model wants to use tools, execute them
        if response.stop_reason == "tool_use":
            tool_results = execute_tools(response.content)
            messages.append({"role": "user", "content": tool_results})
        else:
            # Model is done — print text and break
            print_response(response.content)
            break
```

## Key Concepts

**Context Window:** The model's "memory" — all messages + tool results must fit. Keep it lean.

**stop_reason:** After each API call, check `response.stop_reason`:
- `"end_turn"` → model is done, print the text
- `"tool_use"` → model wants to call a tool, execute it and loop

**Tool Results:** After executing a tool, send the result back as a user message with `type: "tool_result"`.

## Quick Reference

- API Docs: https://docs.anthropic.com
- Console: https://console.anthropic.com
- Guide: https://ampcode.com/how-to-build-an-agent

## Setup Checklist

- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] `pip install anthropic`
- [ ] API key set: `export ANTHROPIC_API_KEY="sk-ant-..."`
- [ ] Run `python agent.py` — should start without errors
