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
│   │         │                           │
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

## Two SDK Options

The workshop code uses the **OpenAI SDK** by default. The OpenAI SDK works with many providers via `BASE_URL`:

| Provider | `OPENAI_API_KEY` | `OPENAI_BASE_URL` | `MODEL` |
|----------|------------------|--------------------|---------|
| **OpenAI** (default) | `sk-...` | *(not needed)* | `gpt-4o` |
| **Gemini** | your Gemini key | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-2.0-flash` |
| **Ollama** (local) | `unused` | `http://localhost:11434/v1` | `qwen2.5` |
| **Anthropic** | `sk-ant-...` | `https://api.anthropic.com/v1/` | `claude-sonnet-4-20250514` |

If you prefer the **Anthropic SDK** directly, use the `_anthropic` variants:
- `agent_anthropic.py` — starter code
- `solution_anthropic.py` — complete solution

## The 5 Core Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `read_file` | Read file contents | `path` |
| `list_files` | List directory contents | `path` (optional) |
| `edit_file` | Replace text in a file | `path`, `old_string`, `new_string` |
| `run_bash` | Execute shell commands | `command` |
| `search_files` | Regex search in files | `pattern`, `path` (optional) |

## Tool Definition Format (OpenAI format)

```python
{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
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
}
```

## The Agent Loop (Pseudocode)

```python
from openai import OpenAI
import json, os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)

messages = [{"role": "system", "content": SYSTEM_PROMPT}]
while True:
    user_input = input("> ")
    messages.append({"role": "user", "content": user_input})

    while True:  # tool loop
        response = client.chat.completions.create(
            model=os.getenv("MODEL", "gpt-4o"),
            tools=TOOLS,
            messages=messages,
            max_tokens=4096,
        )

        message = response.choices[0].message
        messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = execute_tool(tool_call.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            print(message.content)
            break
```

## Key Concepts

**Context Window:** The model's "memory" — all messages + tool results must fit. Keep it lean.

**tool_calls:** After each API call, check `message.tool_calls`:
- If it has tool calls → execute them, send results back, loop
- If `None` → model is done, print `message.content`

**Tool Results:** After executing a tool, send the result back as a message with `role: "tool"` and the matching `tool_call_id`.

## Debugging Your Agent

When things go wrong, check these in order:

1. **Read the tool calls** — print `tool_call.function.name` and the parsed arguments. Is the model sending what you expect?
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

- API Docs: https://platform.openai.com/docs
- Anthropic Docs: https://docs.anthropic.com
- Guide: https://ampcode.com/how-to-build-an-agent
- Further Learning: https://www.kaggle.com/learn-guide/5-day-agents (5-Day AI Agents course by Google & Kaggle)

## Setup Checklist

- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] `pip install openai` (or `pip install anthropic` for Anthropic SDK variant)
- [ ] API key set: `export OPENAI_API_KEY="sk-..."` (or your provider's key)
- [ ] Run `python agent.py` — should start without errors
