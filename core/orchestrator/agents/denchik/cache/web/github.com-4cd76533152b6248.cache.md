## Repository

- Public, MIT License
- Website: https://hermes-agent.nousresearch.com
- Stars: 257,096 · Watchers: 986 · Forks: 56,316
- Default branch: main · Releases: 44 · Tags: 221
- Created: 2025-07-22

[![Hermes Agent](/NousResearch/hermes-agent/raw/main/assets/banner.png)](/NousResearch/hermes-agent/blob/main/assets/banner.png)

# Hermes Agent ☤

[Hermes Agent](https://hermes-agent.nousresearch.com/) | [Hermes Desktop](https://hermes-agent.nousresearch.com/)

[![Documentation](https://camo.githubusercontent.com/76d7a880842f286c4d4e07baf2db1046197c6cfaa564365e912938445fc54a32/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f63732d6865726d65732d2d6167656e742e6e6f757372657365617263682e636f6d2d4646443730303f7374796c653d666f722d7468652d6261646765)](https://hermes-agent.nousresearch.com/docs/) [![Discord](https://camo.githubusercontent.com/8c0fca73564f21d7a6f235747eb4d739a2e4aaa348b8e074904127baeb944b9e/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446973636f72642d3538363546323f7374796c653d666f722d7468652d6261646765266c6f676f3d646973636f7264266c6f676f436f6c6f723d7768697465)](https://discord.gg/NousResearch) [![License: MIT](https://camo.githubusercontent.com/153acf9dff19deb8abfc598c53bac50a4ceae0f5c83a552711060d3d78d2c057/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d4d49542d677265656e3f7374796c653d666f722d7468652d6261646765)](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE) [![Built by Nous Research](https://camo.githubusercontent.com/6195af06150f2173f79d16fa3462ccac43c7dbf78f06f3c7997dc4090d79b9ad/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4275696c7425323062792d4e6f757325323052657365617263682d626c756576696f6c65743f7374796c653d666f722d7468652d6261646765)](https://nousresearch.com) [![中文](https://camo.githubusercontent.com/574634232e93a1f4f7399d7056282748bde9c89ff98c338cc9bec8101117832b/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c616e672de4b8ade696872d7265643f7374796c653d666f722d7468652d6261646765)](/NousResearch/hermes-agent/blob/main/README.zh-CN.md) [![اردو](https://camo.githubusercontent.com/157912df78b013a19a3d2daa5f43dc4e062052fc3cf8ef914835ec9fe65bc67e/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c616e672dd8a7d8b1d8afd9882d677265656e3f7374796c653d666f722d7468652d6261646765)](/NousResearch/hermes-agent/blob/main/README.ur-pk.md) [![Español](https://camo.githubusercontent.com/fd0847426473d023cc0540582c550991fd302ec4be0a6610cf7933980f46f120/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c616e672d45737061c3b16f6c2d6f72616e67653f7374796c653d666f722d7468652d6261646765)](/NousResearch/hermes-agent/blob/main/README.es.md)

**The self-improving AI agent built by [Nous Research](https://nousresearch.com).** It's the only agent with a built-in learning loop — it creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening model of who you are across sessions. Run it on a $5 VPS, a GPU cluster, or serverless infrastructure that costs nearly nothing when idle. It's not tied to your laptop — talk to it from Telegram while it works on a cloud VM.

Use any model you want — [Nous Portal](https://portal.nousresearch.com), OpenRouter, OpenAI, your own endpoint, and [many others](https://hermes-agent.nousresearch.com/docs/integrations/providers). Switch with `hermes model` — no code changes, no lock-in.

| **A real terminal interface** | Full TUI with multiline editing, slash-command autocomplete, conversation history, interrupt-and-redirect, and streaming tool output. |
|---|---|
| **Lives where you do** | Telegram, Discord, Slack, WhatsApp, Signal, and CLI — all from a single gateway process. Voice memo transcription, cross-platform conversation continuity. |
| **A closed learning loop** | Agent-curated memory with periodic nudges. Autonomous skill creation after complex tasks. Skills self-improve during use. FTS5 session search with LLM summarization for cross-session recall. [Honcho](https://github.com/plastic-labs/honcho) dialectic user modeling. Compatible with the [agentskills.io](https://agentskills.io) open standard. |
| **Scheduled automations** | Built-in cron scheduler with delivery to any platform. Daily reports, nightly backups, weekly audits — all in natural language, running unattended. |
| **Delegates and parallelizes** | Spawn isolated subagents for parallel workstreams. In Desktop, choose their provider, model, and limits under Settings → Model → Subagents, then Apply the complete route. Write Python scripts that call tools via RPC, collapsing multi-step pipelines into zero-context-cost turns. |
| **Runs anywhere, not just your laptop** | Six built-in terminal backends — local, Docker, SSH, Modal, Daytona, and Vercel Sandbox — plus plugin backends such as Singularity/Apptainer. Daytona and Modal offer serverless persistence — your agent's environment hibernates when idle and wakes on demand, costing nearly nothing between sessions. Run it on a $5 VPS or a GPU cluster. |
| **Research-ready** | Batch trajectory generation, trajectory compression for training the next generation of tool-calling models. |

---

## Quick Install

### Linux, macOS, WSL2

```
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### Windows (native, PowerShell)

> **Heads up:** Native Windows runs Hermes without WSL — CLI, gateway, TUI, and tools all work natively. If you'd rather use WSL2, the Linux/macOS one-liner above works there too. Found a bug? Please [file issues](https://github.com/NousResearch/hermes-agent/issues).

Run this in PowerShell:

```
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

The source installer delegates Python 3.14, Node.js, npm, ripgrep, FFmpeg, and Python dependencies to PM. If Git is absent, it stages the verified Git for Windows archive in Hermes' tool store. It does not replace your system Git. See [installation methods](https://hermes-agent.nousresearch.com/docs/getting-started/installation) for the separate MSIX/App Installer package and its update ownership.

> **Android / Termux:** A signed APT repository is available for aarch64 devices, with a `stable` channel (tagged releases) and a prerelease `canary` channel. The package includes Python, Node.js, and the TUI. Use the [Termux guide](https://hermes-agent.nousresearch.com/docs/getting-started/termux), not the desktop/server installer script.
>
> **Windows:** Native Windows is fully supported — the PowerShell one-liner above installs everything. If you'd rather use WSL2, the Linux command works there too. Native Windows install lives under `%LOCALAPPDATA%\hermes`; WSL2 installs under `~/.hermes` as on Linux.

After installation:

```
source ~/.bashrc    # reload shell (or: source ~/.zshrc)
hermes              # start chatting!
```

### Troubleshooting

#### Windows Defender or antivirus flags `uv.exe` as malware

If your antivirus (Bitdefender, Windows Defender, etc.) quarantines `uv.exe` from the Hermes `bin` folder (`%LOCALAPPDATA%\hermes\bin\uv.exe`), this is a **false positive**. The file is Astral's `uv` — the Rust Python package manager Hermes bundles to manage its Python environment. ML-based antivirus engines commonly flag unsigned Rust binaries that download and install packages.

**To verify your copy is authentic:**

```
# Install GitHub CLI if needed
winget install --id GitHub.cli

# Login to GitHub
gh auth login

# Run verification
$uv = "$env:LOCALAPPDATA\hermes\bin\uv.exe"
$ver = (& $uv --version).Split(' ')[1]
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$zip = "$env:TEMP\uv.zip"
Invoke-WebRequest "https://github.com/astral-sh/uv/releases/download/$ver/uv-x86_64-pc-windows-msvc.zip" -OutFile $zip -UseBasicParsing
gh attestation verify $zip --repo astral-sh/uv
Expand-Archive $zip "$env:TEMP\uv_x" -Force
(Get-FileHash "$env:TEMP\uv_x\uv.exe").Hash -eq (Get-FileHash $uv).Hash
```

If attestation says "Verification succeeded" and the last line prints `True`, you're good.

**To whitelist Hermes:**

- **Windows Defender:** Run PowerShell as Admin → `Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\hermes\bin"`
- **Bitdefender:** Add an exception in the Bitdefender console (Protection > Antivirus > Settings > Manage Exceptions)
- Whitelist the **folder**, not the file hash — Hermes updates `uv` and the hash changes every version
For more context, see the upstream Astral reports: [astral-sh/uv#13553](https://github.com/astral-sh/uv/issues/13553), [astral-sh/uv#15011](https://github.com/astral-sh/uv/issues/15011), [astral-sh/uv#10079](https://github.com/astral-sh/uv/issues/10079).

---

## Getting Started

```
hermes              # Interactive CLI — start a conversation
hermes model        # Choose your LLM provider and model
hermes tools        # Configure which tools are enabled
hermes config set   # Set individual config values
hermes config get   # Print individual config values
hermes gateway      # Start the messaging gateway (Telegram, Discord, etc.)
hermes setup        # Run the full setup wizard (configures everything at once)
hermes update       # Update to the latest version
hermes doctor       # Diagnose any issues
```

📖 **[Full documentation →](https://hermes-agent.nousresearch.com/docs/)**

---

## Skip the API-key collection — Nous Portal

Hermes works with whatever provider you want — that's not changing. But if you'd rather not collect five separate API keys for the model, web search, image generation, TTS, and a cloud browser, **[Nous Portal](https://portal.nousresearch.com)** covers all of them under one subscription:

- **300+ models** — pick any of them with `/model <name>`
- **Tool Gateway** — web search, image generation (FAL), text-to-speech (OpenAI), cloud browser (Browser Use), all routed through your sub. No extra accounts.
One command from a fresh install:

```
hermes setup --portal
```

That logs you in via OAuth, sets Nous as your provider, and turns on the Tool Gateway. Check what's wired up any time with `hermes portal info`. Full details on the [Tool Gateway docs page](https://hermes-agent.nousresearch.com/docs/user-guide/features/tool-gateway).

You can still bring your own keys per-tool whenever you want — the gateway is per-backend, not all-or-nothing.

---

## CLI vs Messaging Quick Reference

Hermes has two entry points: start the terminal UI with `hermes`, or run the gateway and talk to it from Telegram, Discord, Slack, WhatsApp, Signal, or Email. Once you're in a conversation, many slash commands are shared across both interfaces.

| Action | CLI | Messaging platforms |
|---|---|---|
| Start chatting | `hermes` | Run `hermes gateway setup` + `hermes gateway start`, then send the bot a message |
| Start fresh conversation | `/new` or `/reset` | `/new` or `/reset` |
| Change model | `/model [provider:model]` | `/model [provider:model]` |
| Set a personality | `/personality [name]` | `/personality [name]` |
| Retry or undo the last turn | `/retry`, `/undo` | `/retry`, `/undo` |
| Compress context / check usage | `/compress`, `/usage`, `/insights [--days N]` | `/compress`, `/usage`, `/insights [days]` |
| Browse skills | `/skills` or `/<skill-name>` | `/<skill-name>` |
| Interrupt current work | `Ctrl+C` or send a new message | `/stop` or send a new message |
| Platform-specific status | `/platforms` | `/status`, `/sethome` |
For the full command lists, see the [CLI guide](https://hermes-agent.nousresearch.com/docs/user-guide/cli) and the [Messaging Gateway guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Documentation

All documentation lives at **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Section | What's Covered |
|---|---|
| [Quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Install → setup → first conversation in 2 minutes |
| [CLI Usage](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Commands, keybindings, personalities, sessions |
| [Configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Config file, providers, models, all options |
| [Messaging Gateway](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Security](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Command approval, DM pairing, container isolation |
| [Tools & Toolsets](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ tools, toolset system, terminal backends |
| [Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Procedural memory, Skills Hub, creating skills |
| [Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Persistent memory, user profiles, best practices |
| [MCP Integration](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Connect any MCP server for extended capabilities |
| [Cron Scheduling](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Scheduled tasks with platform delivery |
| [Context Files](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Project context that shapes every conversation |
| [Architecture](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Project structure, agent loop, key classes |
| [Contributing](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Development setup, PR process, code style |
| [CLI Reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | All commands and flags |
| [Environment Variables](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Complete env var reference |

---

## Migrating from OpenClaw or another agent

If you're coming from OpenClaw, Claude Code, Codex CLI or Cursor, Hermes can import your settings, memories and skills (and, for OpenClaw, API keys when you ask for them).

**During setup:** `hermes setup` asks whether to import from another agent, pre-selects the ones it finds (`~/.openclaw`, `~/.claude`, `~/.codex`, `~/.cursor`), installs the official `agent-importers` plugin and runs the import with a preview first.

**Anytime after install:**

```
hermes plugins install agent-importers          # once per profile
hermes import-agent openclaw                    # interactive migration (full preset)
hermes import-agent openclaw --dry-run          # preview what would be migrated
hermes import-agent openclaw --migrate-secrets  # also bring allowlisted API keys
hermes import-agent claude-code                 # or codex / cursor
```

What gets imported from OpenClaw:

- **SOUL.md** — persona file
- **Memories** — MEMORY.md and USER.md entries
- **Skills** — user-created skills → `~/.hermes/skills/openclaw-imports/`
- **Command allowlist** — approval patterns
- **Messaging settings** — platform configs, allowed users, working directory
- **API keys** — allowlisted secrets (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs), only with `--migrate-secrets`
- **TTS assets** — workspace audio files
- **Workspace instructions** — AGENTS.md (with `--workspace-target`)
`hermes claw migrate` still works as the older spelling. See the [OpenClaw migration guide](https://hermes-agent.nousresearch.com/docs/guides/migrate-from-openclaw) and [Import from Other Agents](https://hermes-agent.nousresearch.com/docs/user-guide/import-from-other-agents).

---

## Contributing

We welcome contributions! See the [Contributing Guide](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) for development setup, code style, and PR process.

Start with the [PM developer workflow](/NousResearch/hermes-agent/blob/main/website/docs/reference/package-management.md#developer-workflow) for activation, daily use, dependency changes, and leaving the environment. [Development Setup](/NousResearch/hermes-agent/blob/main/CONTRIBUTING.md#development-setup) covers the separate test environment and verification commands.

---

## Community

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — Linux desktop-control MCP server for Hermes and other MCP hosts, with AT-SPI accessibility trees, Wayland/X11 input, screenshots, and compositor window targeting.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Community WeChat bridge: Run Hermes Agent and OpenClaw on the same WeChat account.

---

## License

MIT — see [LICENSE](/NousResearch/hermes-agent/blob/main/LICENSE).

Built by [Nous Research](https://nousresearch.com).

## Files

.github/, acp_adapter/, agent/, apps/, assets/, contributors/, cron/, docker/, evals/, gateway/, hermes_cli/, hermes_platform/, locales/, native/fts5_cjk/, nix/, optional-mcps/, optional-skills/, plugin-catalog/, plugins/, pm/, providers/, scripts/, skills/, tests-js/, tests/, tools/, tui_gateway/, ui-tui/, web/, website/, .coderabbit.yaml, .dockerignore, .env.example, .envrc, .gitattributes, .gitignore, .hadolint.yaml, .mailmap, .npmrc, .nvmrc, .prettierignore, .prettierrc, .python-version, AGENTS.md, CONTRIBUTING.es.md, CONTRIBUTING.md, Dockerfile, LICENSE, README.es.md, README.md, README.ur-pk.md, README.zh-CN.md, SECURITY.es.md, SECURITY.md, SOUL.md, activate, activate.fish, activate.ps1, batch_runner.py, cli-config.yaml.example and 96 more