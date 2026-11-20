<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/antigravity_operations/references/lifecycle_hooks_spec.md"
# purpose: "Comprehensive specification for Google Antigravity Lifecycle Hooks (hooks.json)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-23"
# author: "Antigravity & Gerych Prime"
# --- END DNK-MRH-HEADER ---
-->

# Google Antigravity Lifecycle Hooks Specification (`hooks.json`)

Lifecycle hooks allow executing external shell commands, security policies, and linter scripts at deterministic checkpoints during the Agent's execution loop.

---

## 1. File Location & Structure

Hooks are configured in a single `hooks.json` file:

- **Workspace Project**: `<workspace-root>/.agents/hooks.json`
- **Global Configuration**: `~/.gemini/config/hooks.json`
- **Plugin Scoped**: `plugins/<plugin_name>/hooks.json`

```json
{
  "safety-guard": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/system/hermes_pre_tool_hook.py",
            "timeout": 10
          }
        ]
      }
    ]
  },
  "linter-gate": {
    "PostToolUse": [
      {
        "matcher": "replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/system/auto_post_tool_lint.sh",
            "timeout": 15
          }
        ]
      }
    ]
  },
  "session-sentinel": {
    "Stop": [
      {
        "type": "command",
        "command": "./scripts/system/session_sentinel.py --on-stop"
      }
    ]
  }
}
```

---

## 2. Supported Lifecycle Events

| Event | When It Triggers | Matcher Target | Schema Structure |
| :--- | :--- | :--- | :--- |
| `PreToolUse` | Before a tool step executes | Tool name (e.g., `run_command`, `write_to_file`) | Grouped (`matcher` + `hooks` array) |
| `PostToolUse` | Immediately after a tool completes | Tool name (e.g., `replace_file_content`) | Grouped (`matcher` + `hooks` array) |
| `PreInvocation` | Before the LLM model inference call | N/A (fires for every turn) | Flat (list of handler objects) |
| `PostInvocation` | After LLM finishes generating tool calls | N/A (fires after turn) | Flat (list of handler objects) |
| `Stop` | When the agent execution loop terminates | N/A (cleanup trigger) | Flat (list of handler objects) |

---

## 3. Execution Semantics & Exit Codes

1. **Deterministic Blocking (Exit Code 0 vs Non-Zero)**:
   - **`exit code 0`**: Hook passed successfully. The agent proceeds with tool execution or generation.
   - **`non-zero exit code`**: Hook failed. For `PreToolUse`, the tool execution is intercepted and blocked, and stderr is returned to the agent as an error message.
2. **Timeout Enforcement**:
   - Each hook specifies an optional `timeout` in seconds (default: 30s).
   - If exceeded, the hook process is terminated, and a timeout error is raised.
3. **Merging Order**:
   - Hooks from multiple configurations (workspace, plugin, global) for the same event run sequentially.
