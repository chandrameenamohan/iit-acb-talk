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

## Debugging Your Agent

When things go wrong, check these in order:

1. **Read the tool calls** — print `block.name` and `block.input` for every tool call. Is the model sending what you expect?
2. **Check the tool result** — is your function returning an error string? The model sees that error and tries to recover.
3. **Look at message history** — print `len(messages)` to check if you're running out of context. If it's over 50 messages, something is looping.
4. **Test the tool in isolation** — call your function directly from a Python REPL with the same arguments.
5. **Simplify the prompt** — if the model keeps making bad tool calls, your system prompt or tool description may be confusing it.

## Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Edit loops | Agent retries same edit repeatedly | Check that `old_string` matching is exact; print the match count |
| Hallucinated paths | "Error: file not found" | Ensure system prompt says "list files before guessing paths" |
| Context overflow | API error about token limit | Truncate old messages or start a new conversation |
| Bash hangs | Agent stops responding | Add `timeout=30` to `subprocess.run`; block interactive commands |
| Invalid tool args | KeyError in `execute_tool` | Use `.get()` with defaults; validate before calling |

## What To Do This Week

**Tonight:**
- Push your agent to GitHub
- Try giving it a task in one of your own projects

**This week:**
- Add `search_files` if you didn't finish Milestone 4
- Add conversation history saving/loading
- Read ampcode.com/how-to-build-an-agent end to end

**This month:**
- Build a specialized agent (test runner, PR reviewer, doc generator)
- Try the Kaggle 5-Day AI Agents course
- Explore MCP (Model Context Protocol) for connecting agents to external tools

## Quick Reference

- API Docs: https://docs.anthropic.com
- Console: https://console.anthropic.com
- Guide: https://ampcode.com/how-to-build-an-agent
- Further Learning: https://www.kaggle.com/learn-guide/5-day-agents (5-Day AI Agents course by Google & Kaggle)

## Setup Checklist

- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] `pip install anthropic`
- [ ] API key set: `export ANTHROPIC_API_KEY="sk-ant-..."`
- [ ] Run `python agent.py` — should start without errors
