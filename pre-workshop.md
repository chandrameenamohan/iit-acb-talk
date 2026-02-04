# Pre-Workshop Reading: AI Agents

Welcome! Please complete the setup steps and skim the reading material before the workshop. This will help you hit the ground running.

---

## 1. Setup Checklist (Do This First!)

### Get an API Key

You'll need an API key from **one** of these providers:

| Provider | Free Tier? | Get a Key |
|----------|------------|-----------|
| **OpenAI** | $5 credit for new accounts | [platform.openai.com](https://platform.openai.com) |
| **Google Gemini** | Free tier available | [aistudio.google.com](https://aistudio.google.com) |
| **Anthropic** | $5 credit for new accounts | [console.anthropic.com](https://console.anthropic.com) |
| **Ollama** (local) | Free, runs on your machine | [ollama.com](https://ollama.com) |

**Recommendation:** OpenAI or Gemini are easiest to set up. Ollama is free but requires local installation.

### Install Dependencies

```bash
# Check Python version (need 3.10+)
python3 --version

# Install the SDK
pip install openai

# Set your API key (add to ~/.bashrc or ~/.zshrc to persist)
export OPENAI_API_KEY="sk-..."
```

For other providers, see the [Provider Configuration](#provider-configuration) section below.

### Verify Your Setup

Download and run our verification script:

```bash
# Download the workshop repo
git clone https://github.com/YOUR-REPO-HERE/iitacb-agent.git
cd iitacb-agent

# Run verification
python verify_setup.py
```

You should see:
```
==================================================
  Workshop Setup Verification
==================================================

[1/4] Checking Python version...
      ✓ Python 3.12.0

[2/4] Checking OpenAI SDK...
      ✓ openai 1.x.x installed

[3/4] Checking API key...
      ✓ API key found
      ✓ Provider: OpenAI
      ✓ Model: gpt-4o

[4/4] Testing API connection...
      ✓ API responded: "Setup verified!"

==================================================
  ✓ All checks passed! You're ready for the workshop.
==================================================
```

If you see errors, follow the troubleshooting steps in the output.

---

## 2. Pre-Reading (20-30 minutes)

### Required: The Anatomy of an AI Agent

Open `anatomy-of-an-agent.html` in your browser. This article explains the core concepts we'll implement:

- **The Loop** — The simplest conversation agent
- **Tools** — How models interact with the outside world
- **The Tool Loop** — The pattern that makes agents autonomous

### Optional: Deep Dives

If you want to go deeper before the workshop:

1. **How to Build an Agent** — [ampcode.com/how-to-build-an-agent](https://ampcode.com/how-to-build-an-agent)
   A detailed walkthrough of agent architecture from the perspective of building Claude Code.

2. **OpenAI Function Calling Guide** — [platform.openai.com/docs/guides/function-calling](https://platform.openai.com/docs/guides/function-calling)
   The official documentation for the tool format we'll use.

---

## 3. Provider Configuration

The workshop code uses the OpenAI SDK, which works with multiple providers by changing the base URL.

### OpenAI (default)
```bash
export OPENAI_API_KEY="sk-..."
# MODEL defaults to gpt-4o
```

### Google Gemini
```bash
export OPENAI_API_KEY="your-gemini-api-key"
export OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
export MODEL="gemini-2.0-flash"
```

### Anthropic
```bash
export OPENAI_API_KEY="sk-ant-..."
export OPENAI_BASE_URL="https://api.anthropic.com/v1/"
export MODEL="claude-sonnet-4-20250514"
```

### Ollama (local, free)
```bash
# First, install and start Ollama
ollama serve &
ollama pull qwen2.5

# Then set environment
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="unused"
export MODEL="qwen2.5"
```

---

## 4. What You'll Build

By the end of the workshop, you'll have a working AI coding agent that can:

- **Read files** — Examine source code and configuration
- **List directories** — Navigate project structure
- **Edit files** — Make targeted changes to code
- **Run commands** — Execute tests and shell operations

All in about **300 lines of Python**, with no frameworks or magic.

---

## 5. What to Bring

- ✅ Laptop with a code editor (VS Code, PyCharm, etc.)
- ✅ Working Python 3.10+ installation
- ✅ API key set up and verified
- ✅ Curiosity about how AI tools actually work

---

## Questions?

If you hit any setup issues, email us at [workshop@example.com] or arrive 15 minutes early and we'll help you troubleshoot.

See you at the workshop!
