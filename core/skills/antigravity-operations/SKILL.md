---
name: antigravity-operations
description: >-
  Comprehensive operational guide and reference runbook for Google Antigravity ecosystem
  (Antigravity IDE, Antigravity 2.0 desktop, Antigravity CLI 'agy', and Python SDK).
  Use when creating or debugging rules, skills, MCP servers (stdio and SSE/HTTP),
  lifecycle hooks (PreToolUse, PostToolUse, PreInvocation, PostInvocation, Stop), plugins,
  and workspace customizations.
---

<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/skills/antigravity_operations/SKILL.md"
purpose: "Google Antigravity Operations Runbook: Rules, Skills, MCP, Hooks, CLI, and Python SDK."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-10-23"
author: "Antigravity & Gerych Prime"
--- END DNK-MRH-HEADER --- -->

# 🚀 Google Antigravity Operations & Customization Runbook

This skill is the canonical production runbook for extending, configuring, and operating Google Antigravity across its development surfaces: the standalone **Antigravity IDE**, the desktop app **Antigravity 2.0**, the terminal CLI **`agy`**, and the **Python SDK**.

---

## 🧭 1. Customization Matrix & Decision Tree

Choose the right customization primitive based on operational scope and lifecycle requirements:

```text
Goal                                  Primitive     Primary Config File           Activation Trigger
---------------------------------------------------------------------------------------------------------
Enforce coding styles & safety rules  Rules         .agents/rules/*.md, AGENTS.md always_on | model_decision | glob | manual
Teach multi-step procedures & tools   Skills        .agents/skills/<name>/SKILL.md Progressive disclosure / Slash command
Connect external tools & databases    MCP Servers   .agents/mcp_config.json       Stdio subprocess or Streamable HTTP/SSE
Deterministic pre/post safety gates   Hooks         .agents/hooks.json            PreToolUse | PostToolUse | Stop
Package & distribute team toolkit     Plugins       .agents/plugins/<name>/       Bundled manifest (plugin.json)
```

For comprehensive deep-dives, consult the modular references:

- Rules hierarchy & trigger mechanics: `references/rules_and_workflows.md`
- Skill architecture & progressive disclosure: `references/skills_and_progressive_disclosure.md`
- MCP server transports & authentication: `references/mcp_and_tool_integration.md`
- Deterministic lifecycle hooks: `references/lifecycle_hooks_spec.md`
- Python SDK & CLI reference: `references/python_sdk_and_cli_reference.md`

---

## 🏛️ 2. Loading Priority & Precedence Hierarchy

When multiple customizations are discovered, Antigravity resolves naming collisions using strict precedence (highest to lowest):

1. **Workspace Project**: Hierarchical discovery traversing up from the current working directory to repository root (`.agents/`).
2. **Explicit Declared Configs**: Customizations listed in `.agents/rules.json`, `skills.json`, or `plugins.json`.
3. **Global Discovery**: Local machine configurations in `~/.gemini/config/`.
4. **Built-in Customizations**: Default platform skills bundled with Antigravity.
5. **Global Declared Configs**: Listed in global user JSON configurations.

---

## 📋 3. Rules & Workflows Standard

Rules are markdown documents enforcing invariants, boundaries, and project guidelines.

### Frontmatter Triggers

Rules inside `.agents/rules/*.md` support YAML frontmatter:

```yaml
---
trigger: model_decision       # Required: always_on | model_decision | glob | manual
description: "..."            # Required for model_decision; recommended for all rules
globs: "*.py, tests/**/*.py"  # Required for glob (quoted patterns)
---
```

### Invariants

- **`model_decision`**: Only path + `description` are loaded upfront into the prompt index. The full body is read on-demand (zero context bloat).
- **`always_on`**: Loaded into every turn unconditionally. Keep concise!
- **`glob`**: Loaded only when active files match `globs`.
- **`manual`**: Loaded only when explicitly `@mentioned` in chat.
- **Includes**: Use `@[label](path)` to inline files directly; use `@filename` to rewrite to canonical absolute workspace paths.
- **Size Ceilings**: Maximum 24 KB per rule file. Aggregate rules share a 20,000-token budget; oversized rules are automatically demoted to pointers.

See `references/rules_and_workflows.md` for complete schema and inheritance rules.

---

## 🧠 4. Progressive Disclosure Skills Standard

Skills teach the agent specialized procedural runbooks and tool sequences without exhausting the baseline context window.

### Standard Layout

```text
skills/<skill_name>/
├── SKILL.md          # REQUIRED: Frontmatter + instructions (≤ 750 lines)
├── scripts/          # OPTIONAL: Executable helper scripts (run with --help first)
└── references/       # OPTIONAL: Modular Level-of-Detail (LOD) documentation
```

### Rules & Invariants

1. **Name**: Lowercase alphanumeric with hyphens (`^[a-z0-9]+([-_][a-z0-9]+)*$`).
2. **Description**: Concise third-person summary specifying what it does and when to activate it (≤ 1,024 characters).
3. **Core-Size Ratchet**: `SKILL.md` body line count MUST NOT exceed **750 lines**. Relegate exhaustive schemas, APIs, and catalogs into `references/`.
4. **Slash Command**: Folder `skills/<name>` is automatically converted into `/<name>` in Antigravity App & CLI.

See `references/skills_and_progressive_disclosure.md` for LOD retrieval patterns.

---

## 🔌 5. Model Context Protocol (MCP) Standard

MCP integrates external services (PostgreSQL, Notion, Chrome DevTools, Shopify, GitHub) into the agent's toolset via `.agents/mcp_config.json` or `~/.gemini/config/mcp_config.json`.

### Stdio Transport (Local Tools)

```json
{
  "mcpServers": {
    "sqlite-helper": {
      "command": "/opt/homebrew/bin/node",
      "args": ["/path/to/server.js"],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### Remote Transport (Streamable HTTP / SSE)

```json
{
  "mcpServers": {
    "remote-service": {
      "serverUrl": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

### Invariants & Gotchas

- Always specify explicit `PATH` inside `"env"` to prevent `env: node: No such file or directory`.
- Heavy MCPs (Notion MCP ~37k tokens, Chrome DevTools ~15k tokens) should be detached or set to `"disabled": true` during code refactoring.
- OAuth tokens are auto-persisted at `~/.gemini/antigravity/mcp_oauth_tokens.json`.

See `references/mcp_and_tool_integration.md` for OAuth2, ADC, and troubleshooting.

---

## 🪝 6. Lifecycle Hooks Standard (`hooks.json`)

Lifecycle hooks execute deterministic scripts before or after agent actions to enforce safety and formatting:

```json
{
  "safety-guard": {
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
  }
}
```

- **`PreToolUse`**: Exit code `0` permits tool execution; non-zero blocks execution and reports stderr.
- **`PostToolUse`**: Runs post-execution linter/formatters.
- **`Stop`**: Cleanup and audit persistence triggers.

See `references/lifecycle_hooks_spec.md` for hook payload formats.

---

## 🐍 7. Python SDK & CLI Workflows

### Python SDK (`google-antigravity`)

```python
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

async with Agent(LocalAgentConfig(capabilities=CapabilitiesConfig())) as agent:
    response = await agent.chat("Run test suite")
    async for token in response:
        print(token, end="", flush=True)
```

### Antigravity CLI (`agy`)

- Run `agy` for interactive sessions.
- Run `agy "prompt"` for headless one-shot executions.
- List active extensions: `agy plugin list --json`.

See `references/python_sdk_and_cli_reference.md` for streaming thoughts and tool monitoring.

---

## ✅ 8. Autonomous Validation & Quality Gates

Run the automated validator to verify all rules, skills, MCP servers, and hooks before committing:

```bash
# Validate this skill bundle
python3 core/skills/antigravity_operations/scripts/validate_antigravity_customizations.py core/skills/antigravity_operations

# Validate entire workspace
python3 core/skills/antigravity_operations/scripts/validate_antigravity_customizations.py .
```
