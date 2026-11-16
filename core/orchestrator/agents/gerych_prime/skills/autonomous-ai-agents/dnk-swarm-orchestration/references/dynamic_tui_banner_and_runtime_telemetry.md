# Dynamic TUI Banner & Runtime Telemetry Protocol

## Problem & Anti-Pattern
Previously, the TUI welcome banner (`core/hermes_agent/hermes_cli/banner.py`) contained hardcoded static values:
- Hardcoded model provider: `'Google Vertex AI'` even when running under Anthropic, OpenRouter, Groq, or Ollama.
- Hardcoded skills count: `573` with mock category `canvas_ui_ux (413)` instead of the true skill catalog.
- Hardcoded agent roster: fixed 10 agents rather than dynamic discovery of the 14 specialized agents in `core/orchestrator/agents/`.
- Hardcoded or static MCP server counts disconnected from live server health.

## Core Solution Architecture
To maintain SSOT (Single Source of Truth) and prevent telemetry drift:

1. **Model Provider Mapping**:
   Dynamically resolve the provider from `args.provider` or active config, mapping engine keys to user-friendly titles:
   - `vertex` -> `Google Vertex AI`
   - `google` / `gemini` -> `Google AI Studio`
   - `anthropic` -> `Anthropic`
   - `openrouter` -> `OpenRouter`
   - `groq` -> `Groq`
   - `ollama` -> `Ollama (Local)`

2. **Live MCP Status Discovery**:
   Call `tools.mcp_tool.get_mcp_status()` and `tools.mcp_tool._get_mcp_servers()` to check both configured and connected MCP servers.
   Label as `(N активних)` when connected servers > 0, otherwise `(N налаштовано)`.

3. **Autonomous Agent Roster Discovery**:
   Dynamically inspect `core/orchestrator/agents/` for directory entries. Map agent directory names to friendly descriptions with fallback to capitalized name.

4. **Dynamic Skills Matrix**:
   Import `get_available_skills()` and `_find_all_skills()` from `tools.skills_tool`.
   Calculate the true total skill count across real categories (`devops`, `software-development`, `note-taking`, etc.) and sample real categories for display.

5. **Tool Scope Accuracy**:
   Sample only tools actually active and passed to the session, avoiding hardcoded assumptions.

6. **Rich TUI Border Hygiene**:
   Avoid composite VS16 emojis (`\ufe0f`) like `🛠️` which desync character width between Rich and terminal emulators. Use canonical single-codepoint emojis (e.g. `🔧` U+1F527). Verify rendering via `ensure_dnk_tui_integrity.py`.
