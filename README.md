# Build Your Own AI Coding Agent

Workshop: Building an AI Coding Agent in ~300 lines of Python.

## Setup

1. **Python 3.10+** required
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```
4. Run the solution (facilitator reference):
   ```bash
   python solution.py
   ```
5. Or work through the exercise:
   ```bash
   python agent.py
   ```

## Workshop Structure

- `agent.py` — Starter code with TODOs for you to fill in
- `solution.py` — Complete working solution (no peeking!)
- `handout.md` — Printable reference sheet

## What You'll Build

A coding agent that can:
- Read and list files in a project directory
- Edit files using string replacement
- Run bash commands (with safety checks)
- Search file contents with regex
- Have a multi-turn conversation

## Getting an API Key

1. Go to https://console.anthropic.com
2. Sign up / log in
3. Go to API Keys and create one
4. Add $5-10 of credit (sufficient for the workshop)
