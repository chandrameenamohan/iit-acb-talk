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

# Your Speakers

**Chandra Mohan Meena**
Principal Engineer at Hakimo AI, B.Tech + M.Tech in CS from IIT Bombay. Builds production AI agents with Claude and Gemini. 12+ years at Amazon, Oracle, Walmart Labs. Has presented his work at USENIX OpML and ECML-PKDD.

**Nishant Shreshth**
Staff Engineer at Broadcom, B.Tech + M.Tech in EE from IIT Bombay. Builds AI agents at Broadcom. 15+ years at VMware, Coinbase, Hakimo, Amadeus Labs.

---

# Agenda

| Time (IST) | Session | Format |
|------------|---------|--------|
| 10:30 – 10:50 | What is an Agent? + Live Demo | Talk |
| 10:50 – 11:20 | Architecture Deep Dive | Talk |
| 11:20 – 11:30 | **Break** | ☕ |
| 11:30 – 11:55 | Mini Hands-On: Verify Setup + Run Starter | Code |
| 11:55 – 12:20 | Context Window, Models & Safety | Talk |
| 12:20 – 12:30 | Starter Code Walkthrough + Q&A | Talk |
| 12:30 – 1:30 | **Lunch** | 🍽️ |
| 1:30 – 3:30 | Hands-On Coding (4 milestones) | Workshop |

**Outcome:** You walk out with a working coding agent.

---

# Two Options: Choose Your SDK

| | **OpenAI SDK** (default) | **Anthropic SDK** |
|---|---|---|
| Files | `agent.py`, `solution.py` | `agent_anthropic.py`, `solution_anthropic.py` |
| Install | `pip install openai` | `pip install anthropic` |
| Works with | OpenAI, Gemini, Ollama, Anthropic | Anthropic only |
| Config | Env vars: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `MODEL` | `ANTHROPIC_API_KEY` |

**Recommendation:** Use the OpenAI SDK — one codebase, any provider.

---

# Provider Config (OpenAI SDK)

```bash
# OpenAI (default — nothing extra needed)
export OPENAI_API_KEY="sk-..."

# Google Gemini
export OPENAI_API_KEY="your-gemini-key"
export OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
export MODEL="gemini-2.0-flash"

# Ollama (local, free)
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="unused"
export MODEL="qwen2.5"

# Anthropic
export OPENAI_API_KEY="sk-ant-..."
export OPENAI_BASE_URL="https://api.anthropic.com/v1/"
export MODEL="claude-sonnet-4-20250514"
```

---

# What You Need

- ✅ Laptop with a code editor
- ✅ Python 3.10+
- ✅ An API key (OpenAI, Gemini, Anthropic, or Ollama running locally)
- ✅ Git installed

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
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

# Demo — Predict First

Before I run this, **you tell me:**

> "Create a file called hello.py that prints hello world"

What tools will the agent use? In what order?

🤔 Write your prediction down, then let's watch.

<!-- Facilitator: collect 2-3 predictions from audience, then run solution.py -->

---

# How Agents Fail

| Failure Mode | What Happens |
|---|---|
| Edit loops | Agent keeps retrying the same edit with wrong match string |
| Hallucinated paths | Reads/edits files that don't exist |
| Context overflow | Too many tool results fill up the context window |
| Bash hangs | `run_bash` blocks on interactive command (e.g. `python`) |
| Invalid tool args | Model sends wrong parameter names or types |

These aren't bugs in your code — they're **inherent to the pattern.**

---

# 1.2 — Architecture Deep Dive

```
 User Input
     │
     ▼
 ┌────────┐
 │  LLM   │◄── System Prompt + Tool Definitions
 │        │
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

# How Tool Use Works (OpenAI format)

You provide **tool definitions** — type, function name, description, parameters:

```python
{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"}
            },
            "required": ["path"]
        }
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

# Design Decisions

**Why these 5 tools?**
They cover the read-think-edit-verify loop. That's what coding is.

**Why string-replace, not whole-file rewrite?**
- Forces the model to read first (it needs the exact match string)
- Smaller changes = fewer tokens = cheaper + safer
- Easier to review what changed

**Why not LangChain / CrewAI / AutoGen?**
- 300 lines is easier to debug than a framework
- You understand every line
- Frameworks add abstractions you'll fight against

---

# Tool Results

After executing a tool, send the result back:

```python
{
    "role": "tool",
    "tool_call_id": tool_call.id,  # must match the request
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

GPT-4o / Claude Sonnet / Gemini Flash are all good choices.

---

# Cost Awareness

| | Input | Output |
|---|-------|--------|
| GPT-4o | $2.50/M tokens | $10/M tokens |
| Claude Sonnet | $3/M tokens | $15/M tokens |
| Gemini Flash | $0.075/M tokens | $0.30/M tokens |
| Ollama (local) | Free | Free |

A typical agent session: ~10-50K tokens = **$0.01 - $0.50**

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
  # ↑ Prevents hallucinated edits — model sees real content
- Explain what you're doing.
  # ↑ Makes the agent's reasoning visible to the user
- Be cautious with bash commands.
  # ↑ No safety net — shell commands run for real
"""
```

Each rule exists because agents **will** do the wrong thing without it.

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

# How Agents Fail — Live

Let's **make** the agent fail.

- Ask it to edit a file it hasn't read
- Give it an ambiguous edit string that matches multiple times
- Ask it to run an interactive command like `python` (no args)

Watch what happens. This is what debugging agents looks like.

<!-- Facilitator: pick 1-2 of these and demo live. Show the tool calls and error messages. -->

---

# ☕ Break (10 min)

---

# Mini Hands-On: Verify Setup

1. Clone the repo: `git clone <repo-url>`
2. Run `pip install openai` (or `pip install anthropic`)
3. Set your API key: `export OPENAI_API_KEY="sk-..."`
4. Run `python solution.py` — try asking it to read a file
5. Working? Great — you'll build this from scratch after lunch.

<!-- Facilitator: walk around, help with setup issues -->

---

# 1.6 — Starter Code Walkthrough

Let's look at `agent.py` together.

**Structure:**
1. Tool definitions (JSON schemas — OpenAI format)
2. Tool implementations (Python functions)
3. Tool dispatcher (`execute_tool`)
4. Agent loop (outer loop + inner tool loop)

---

# What You'll Build

```
agent.py              ← starter code with TODOs (OpenAI SDK)
solution.py           ← complete reference (OpenAI SDK)
milestone1_done.py    ← checkpoint after milestone 1
milestone2_done.py    ← checkpoint after milestone 2
milestone3_done.py    ← checkpoint after milestone 3
agent_anthropic.py    ← starter code (Anthropic SDK)
solution_anthropic.py ← complete reference (Anthropic SDK)
requirements.txt      ← openai + anthropic
```

4 milestones, each builds on the last. **Checkpoint files** let you catch up if you fall behind.

---

<!-- _class: lead -->

# Part 2: Hands-On

---

# Milestone 1 (0–40 min)

### Get the loop running with `read_file`

> **Checkpoint files available:** If you fall behind, copy `milestone1_done.py` → `agent.py` to catch up.

1. Fill in the API call in the agent loop
2. Handle `message.tool_calls` — execute tools, feed results back
3. Handle no tool calls — print the response
4. Test: ask the agent to read a file

---

# The API Call

```python
response = client.chat.completions.create(
    model=MODEL,
    max_tokens=MAX_TOKENS,
    tools=TOOLS,
    messages=messages,
)
```

---

# Processing the Response

```python
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
    if message.content:
        print(f"\nAgent: {message.content}")
    break
```

---

# ⏱️ Check-in — 2:00 PM

How's everyone doing? Raise a hand if you need help.

<!-- Facilitator: walk around, unblock anyone stuck -->

---

# Milestone 2 (40–80 min)

### Add `list_files` and `edit_file`

> **Falling behind?** Copy `milestone2_done.py` → `agent.py`

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

# ⏱️ Check-in — 2:40 PM

Almost there! After this milestone you have a fully working agent.

<!-- Facilitator: walk around, help stragglers catch up with milestone2_done.py -->

---

# Milestone 3 (80–110 min)

### Add `run_bash` with safety checks

> **Falling behind?** Copy `milestone3_done.py` → `agent.py`

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

# Milestone 4 — Stretch/Polish

### Give your agent a real task

> "Create an HTML file with a working calculator — buttons for 0-9, +, -, ×, ÷, =, and a display."

Watch it create the file, then open it in your browser.

### Other stretch goals
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

# What To Do This Week

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

---

# Resources

- **Guide:** ampcode.com/how-to-build-an-agent
- **Deep dive:** ghuntley.com/agent
- **API docs:** platform.openai.com/docs / docs.anthropic.com
- **Console:** console.anthropic.com
- **Course:** kaggle.com/learn-guide/5-day-agents (Google's 5-day AI Agents intensive — covers memory, evaluation, multi-agent patterns)

---

<!-- _class: lead -->

# Thank You!

### Now go build something.
