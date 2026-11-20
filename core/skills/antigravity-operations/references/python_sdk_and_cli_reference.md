<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/antigravity_operations/references/python_sdk_and_cli_reference.md"
# purpose: "Comprehensive reference on Google Antigravity Python SDK and agy CLI commands."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-23"
# author: "Antigravity & Gerych Prime"
# --- END DNK-MRH-HEADER ---
-->

# Google Antigravity Python SDK & CLI Reference

This document provides code patterns and CLI workflows for orchestrating Antigravity agents programmatically and via terminal sessions.

---

## 1. Antigravity Python SDK

### Installation

```bash
pip install google-antigravity
```

### Complete Async Pipeline Example

```python
import asyncio
import sys
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

async def run_autonomous_agent(prompt: str):
    # Configure capabilities: default is read-only for safety.
    # CapabilitiesConfig() enables command execution and file modification.
    config = LocalAgentConfig(
        system_instructions=(
            "You are a Senior Systems Architect and Autonomous Builder. "
            "Follow Zero-Waste High-Velocity Protocols and verify all outputs."
        ),
        capabilities=CapabilitiesConfig(),
    )

    async with Agent(config) as agent:
        response = await agent.chat(prompt)

        # 1. Stream real-time thoughts / internal reasoning
        async for thought in response.thoughts:
            print(f"[REASONING] {thought}")

        # 2. Intercept and monitor strongly-typed ToolCalls
        async for call in response.tool_calls:
            print(f"[TOOL] Executing {call.name} with: {call.args}")

        # 3. Stream generated response tokens
        async for token in response:
            sys.stdout.write(token)
            sys.stdout.flush()
        print()

if __name__ == "__main__":
    asyncio.run(run_autonomous_agent("Audit codebase invariants and run test suite."))
```

---

## 2. Antigravity CLI (`agy`)

### Core Usage

- **Launch Interactive Session**: `agy`
- **One-Shot Headless Prompt**: `agy "Audit recent git diffs"`
- **List Installed Plugins & Skills**: `agy plugin list --json`
- **Help & Options**: `agy --help`

### Configuration (`~/.gemini/antigravity-cli/settings.json`)

The CLI reads local preferences from `settings.json`:

```json
{
  "theme": "dark",
  "auto_approve_readonly": true,
  "default_model": "gemini-3.8-flash",
  "default_reasoning_effort": "medium"
}
```
