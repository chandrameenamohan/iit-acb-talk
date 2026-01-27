---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: 'Helvetica Neue', Arial, sans-serif;
  }
  h1 {
    color: #1a1a2e;
  }
  h2 {
    color: #16213e;
  }
  code {
    background: #f0f0f0;
    border-radius: 4px;
  }
  pre {
    background: #1a1a2e;
    color: #e0e0e0;
  }
  section.lead h1 {
    font-size: 2.5em;
  }
  section.lead {
    text-align: center;
  }
---

<!-- _class: lead -->

# Building an AI Coding Agent

### ~300 Lines of Python. That's It.

---

# Agenda

| Part | Topic | Duration |
|------|-------|----------|
| **1** | Theory & Guidelines | 2 hours |
| **2** | Hands-On Build | 2 hours |

**Outcome:** You walk out with a working coding agent.

---

# What You Need

- ✅ Laptop with a code editor
- ✅ Python 3.10+
- ✅ Anthropic API key (`console.anthropic.com`)
- ✅ $5-10 credit on your account
- ✅ Git installed

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

<!-- _class: lead -->

# Part 1: Theory

---

# 1.1 — What is an Agent?

An LLM + a loop + tools.

That's it.

---

# Not Magic — Just a Loop

```
while True:
    user_input = input()
    response = call_llm(user_input)

    while response.wants_to_use_tool:
        result = execute_tool(response.tool_call)
        response = call_llm(result)

    print(response.text)
```

---

# Demo

Let's see a working agent edit code in real time.

<!-- Facilitator: run solution.py and ask it to do a small task -->

---

# 1.2 — Architecture Deep Dive

```
 User Input
     │
     ▼
 ┌────────┐
 │  LLM   │◄── System Prompt + Tool Definitions
 │(Claude) │
 └───┬────┘
     │
     ▼
 Tool Call? ──Yes──► Execute Tool ──► Feed Result Back ──► Loop
     │
     No
     │
     ▼
 Print Response
```

---

# The Conversation Loop

1. User sends a message
2. Model responds — either **text** or a **tool call**
3. If tool call: execute it, send result back to model → go to 2
4. If text: print it → go to 1

The model decides when and which tools to call. You just execute.

---

# How Tool Use Works

You provide **tool definitions** — name, description, input schema:

```python
{
    "name": "read_file",
    "description": "Read the contents of a file",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path"}
        },
        "required": ["path"]
    }
}
```

The model is **trained** to emit tool calls in the right format.

---

# The 5 Core Tools

| Tool | What it Does |
|------|-------------|
| `read_file` | Read file contents |
| `list_files` | List directory entries |
| `edit_file` | String replacement in a file |
| `run_bash` | Execute shell commands |
| `search_files` | Regex search across files |

This is enough to build a useful coding agent.

---

# Tool Results

After executing a tool, send the result back:

```python
{
    "type": "tool_result",
    "tool_use_id": block.id,  # must match the request
    "content": "file contents here..."
}
```

The model reads this and decides what to do next.

---

# 1.3 — Context Window & Model Selection

---

# Context Window = Memory

Everything in the conversation must fit in the context window:

- System prompt
- All previous messages
- All tool calls and results
- The next response

**Less is more** — don't dump entire codebases into context.

---

# Choosing a Model

What matters for an agent:

- **Tool calling ability** — the model must reliably emit tool calls
- **Instruction following** — it must respect your system prompt
- **Reasoning** — it needs to break down problems

Claude Sonnet is a good balance of capability and cost.

---

# Cost Awareness

| | Input | Output |
|---|-------|--------|
| Sonnet | $3/M tokens | $15/M tokens |

A typical agent session: ~10-50K tokens = **$0.03 - $0.50**

$5-10 of credit is plenty for this workshop.

---

# 1.4 — System Prompts & Guardrails

---

# Crafting a System Prompt

```python
SYSTEM_PROMPT = """You are a helpful coding assistant.
You have access to tools that let you read, list,
edit, and search files, and run bash commands.

Important rules:
- Always read a file before editing it.
- Explain what you're doing.
- Be cautious with bash commands."""
```

Keep it concise. The model follows instructions well.

---

# Safety: Bash Execution

Block dangerous commands:

```python
dangerous = ["rm -rf /", "rm -rf ~", "mkfs", "> /dev/sd"]
for pattern in dangerous:
    if pattern in command:
        return "Error: refusing to run destructive command."
```

Also: set a **timeout** so commands don't hang forever.

---

# Ask vs. Act

Good agent design principle:

- **Read-only tools** → just do it
- **Writes / edits** → do it, but explain before and after
- **Destructive actions** → consider asking for confirmation

(Stretch goal: add confirmation prompts!)

---

# ☕ Break (10 min)

---

# 1.6 — Starter Code Walkthrough

Let's look at `agent.py` together.

**Structure:**
1. Tool definitions (JSON schemas)
2. Tool implementations (Python functions)
3. Tool dispatcher (`execute_tool`)
4. Agent loop (outer loop + inner tool loop)

---

# What You'll Build

```
agent.py          ← starter code with TODOs
solution.py       ← complete reference (no peeking!)
requirements.txt  ← just "anthropic"
```

4 milestones, each builds on the last.

---

<!-- _class: lead -->

# Part 2: Hands-On

---

# Milestone 1 (0-30 min)

### Get the loop running with `read_file`

1. Fill in the API call in the agent loop
2. Handle `stop_reason == "tool_use"` — execute tools, feed results back
3. Handle `stop_reason == "end_turn"` — print the response
4. Test: ask the agent to read a file

---

# The API Call

```python
response = client.messages.create(
    model=MODEL,
    max_tokens=MAX_TOKENS,
    system=SYSTEM_PROMPT,
    tools=TOOLS,
    messages=messages,
)
```

---

# Processing the Response

```python
messages.append({"role": "assistant", "content": response.content})

if response.stop_reason == "tool_use":
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })
    messages.append({"role": "user", "content": tool_results})
else:
    for block in response.content:
        if hasattr(block, "text"):
            print(f"\nAgent: {block.text}")
    break
```

---

# Milestone 2 (30-60 min)

### Add `list_files` and `edit_file`

1. Add tool definitions to `TOOLS` list
2. Implement the functions
3. Wire them into `execute_tool`
4. Test: ask the agent to list files, then edit one

---

# `list_files` Implementation

```python
def list_files(path="."):
    entries = sorted(os.listdir(path))
    result = []
    for entry in entries:
        full = os.path.join(path, entry)
        prefix = "[DIR] " if os.path.isdir(full) else "[FILE]"
        result.append(f"{prefix} {entry}")
    return "\n".join(result) or "(empty)"
```

---

# `edit_file` Implementation

```python
def edit_file(path, old_string, new_string):
    content = read_file(path)
    count = content.count(old_string)
    if count == 0:
        return "Error: old_string not found."
    if count > 1:
        return f"Error: {count} matches. Be more specific."
    new_content = content.replace(old_string, new_string, 1)
    with open(path, "w") as f:
        f.write(new_content)
    return "File edited successfully."
```

Key: require **exact, unique** string match.

---

# Milestone 3 (60-90 min)

### Add `run_bash` with safety checks

1. Add tool definition
2. Implement with safety checks + timeout
3. Test: ask the agent to run tests or install a package

---

# `run_bash` Implementation

```python
def run_bash(command):
    dangerous = ["rm -rf /", "rm -rf ~", "mkfs"]
    for p in dangerous:
        if p in command:
            return "Refusing to run destructive command."

    result = subprocess.run(
        command, shell=True,
        capture_output=True, text=True, timeout=30,
    )
    output = result.stdout
    if result.stderr:
        output += f"\nSTDERR: {result.stderr}"
    return output or "(no output)"
```

---

# Milestone 4 (90-120 min)

### Polish & Test

- Try a real task: "Add a function to sort a list and write a test for it"
- Watch the agent read, think, edit, and run tests

### Stretch Goals
- Add `search_files` (regex grep across files)
- Add confirmation prompts before edits
- Persist conversation history to a file

---

# What You Built

```
┌──────────────────────────┐
│    ~300 lines of Python   │
│                          │
│  • Conversation loop     │
│  • 5 tools               │
│  • Safety guardrails     │
│  • Multi-turn context    │
│                          │
│  That's a coding agent.  │
└──────────────────────────┘
```

---

# Key Takeaways

1. **An agent is just a loop** — LLM + tools + iteration
2. **Tool definitions are the API** — the model is trained to use them
3. **Less is more** — 5 well-defined tools go a long way
4. **Safety matters** — validate inputs, block destructive actions
5. **The model decides** — you provide tools, it chooses when to use them

---

# Resources

- **Guide:** ampcode.com/how-to-build-an-agent
- **Deep dive:** ghuntley.com/agent
- **API docs:** docs.anthropic.com
- **Console:** console.anthropic.com

---

<!-- _class: lead -->

# Thank You!

### Now go build something.
