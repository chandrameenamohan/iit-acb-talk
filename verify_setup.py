#!/usr/bin/env python3
"""
Workshop Setup Verification Script

Run this BEFORE the workshop to confirm your setup is working.

Usage:
  1. Install the SDK:     pip install openai
  2. Set your API key:    export OPENAI_API_KEY="sk-..."
  3. Run this script:     python verify_setup.py

For other providers, set these environment variables:

  OpenAI (default):
    export OPENAI_API_KEY="sk-..."

  Google Gemini:
    export OPENAI_API_KEY="your-gemini-api-key"
    export OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
    export MODEL="gemini-2.0-flash"

  Ollama (local, free):
    export OPENAI_BASE_URL="http://localhost:11434/v1"
    export OPENAI_API_KEY="unused"
    export MODEL="qwen2.5"

  Anthropic:
    export OPENAI_API_KEY="sk-ant-..."
    export OPENAI_BASE_URL="https://api.anthropic.com/v1/"
    export MODEL="claude-sonnet-4-20250514"
"""

import os
import sys

def main():
    print("=" * 50)
    print("  Workshop Setup Verification")
    print("=" * 50)
    print()

    # Step 1: Check Python version
    print("[1/4] Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"      ✓ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"      ✗ Python {version.major}.{version.minor}.{version.micro}")
        print("        Please install Python 3.10 or higher")
        return False
    print()

    # Step 2: Check OpenAI SDK installed
    print("[2/4] Checking OpenAI SDK...")
    try:
        from openai import OpenAI
        import openai
        print(f"      ✓ openai {openai.__version__} installed")
    except ImportError:
        print("      ✗ OpenAI SDK not installed")
        print("        Run: pip install openai")
        return False
    print()

    # Step 3: Check API key
    print("[3/4] Checking API key...")
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("MODEL", "gpt-4o")

    if not api_key:
        print("      ✗ OPENAI_API_KEY not set")
        print("        Run: export OPENAI_API_KEY=\"your-key-here\"")
        return False

    # Determine provider from base_url
    if "anthropic" in base_url:
        provider = "Anthropic"
    elif "generativelanguage.googleapis" in base_url:
        provider = "Google Gemini"
    elif "localhost:11434" in base_url:
        provider = "Ollama (local)"
    else:
        provider = "OpenAI"

    print(f"      ✓ API key found")
    print(f"      ✓ Provider: {provider}")
    print(f"      ✓ Model: {model}")
    print()

    # Step 4: Test API call
    print("[4/4] Testing API connection...")
    print("      (Making a small test request...)")
    print()

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'Setup verified!' and nothing else."}
            ],
        )
        reply = response.choices[0].message.content.strip()
        print(f"      ✓ API responded: \"{reply}\"")
    except Exception as e:
        print(f"      ✗ API error: {e}")
        print()
        print("  Troubleshooting:")
        print("  - Check that your API key is valid")
        print("  - Check that you have credits/quota available")
        print("  - For Ollama, ensure the server is running: ollama serve")
        return False

    print()
    print("=" * 50)
    print("  ✓ All checks passed! You're ready for the workshop.")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
