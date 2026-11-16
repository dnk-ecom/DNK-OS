<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/protected_instruction_files_and_approval_gates.md"
purpose: "Specification for Protected Agent-Instruction Files, Human-in-the-Loop Approvals, Timeout, and Multi-Tier Notification Configuration in Hermes."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.2.0"
updated_at: "2026-09-12"
author: "DNK-e.com Maksym"
--- END DNK-MRH-HEADER -->

# 🛡️ Protected Instruction Files, Human Approval Gates & Notification Architecture

## 1. Security Architecture & Threat Model
In the Hermes and DNK OS multi-agent ecosystem, agent-instruction files (`SOUL.md`, system prompts, agent identity definitions, safety filters) are cryptographically or heuristically protected by the execution harness.
- **Why Protection Exists**: To prevent runaway or compromised agents from rewriting their own core alignment, memory access invariants (e.g. Zero-Direct-Memory-Write), or spend limits.
- **The Core Invariant**: **"Silence is not consent"**. If a human operator does not explicitly confirm a mutation prompt within the configured timeout window, the runtime aborts the operation and locks out unconfirmed writes.

---

## 2. Interactive Approval Lifecycle & Timeout Pitfall

```
[Agent emits write_file / patch on SOUL.md]
                  │
                  ▼
[Hermes Runtime Intercepts Protected File]
                  │
                  ▼
[Triggers Multi-Tier Alert: macOS Push + Sound + Terminal Bell]
                  │
                  ▼
[Displays Interactive Prompt: Confirm [y/n] in CLI]
    ├── User confirms within timeout ➔ ✅ Operation Succeeds
    └── Timeout expires (default 60s) ➔ ❌ BLOCKED: "Silence is not consent"
```

### The Timeout Trap
By default, `approvals.timeout` is set to **60 seconds**. In real-world developer workflows, operators frequently switch windows, read specifications, or consult documentation, causing the 60-second window to expire silently.

---

## 3. Recommended Operational Protocol

### A. Pre-Mutation Warning (Agent Responsibility)
Before mutating any `SOUL.md` or protected instruction file:
1. Announce the upcoming mutation explicitly in the chat response.
2. Alert the user that an interactive confirmation prompt (`[y/n]`) will appear in their terminal.
3. Only trigger the write tool once the user is attentive or has approved the intent.

### B. Anti-Bypass Invariant (Zero-Stealth-Backdoor)
If an approval times out or is rejected:
- **STRICTLY FORBIDDEN**: Attempting to bypass the block via `terminal` shell commands (`sed`, `echo ... > SOUL.md`, python file-write scripts, `execute_code`).
- **MANDATORY ACTION**: Acknowledge the timeout honestly, explain why it occurred, and re-attempt the canonical tool call only after the user indicates readiness.

### C. Tri-Tier Notification & Timeout Configuration

To ensure the operator is always alerted immediately and has ample time to review and confirm actions:

#### 1. Extend Approval Timeout (CLI Config)
Set the approval prompt window to 5 or 10 minutes so backgrounded tasks do not abort prematurely:
```bash
# Extend approval window to 5 minutes (recommended default)
hermes config set approvals.timeout 300

# Or 10 minutes for complex multi-file architectural reviews:
hermes config set approvals.timeout 600
```

#### 2. Native macOS System Push Notification + Sound Chime
For macOS workstations, trigger a native Notification Center banner with a distinct audio cue (`Glass` or `Ping`):
```bash
osascript -e 'display notification "Hermes очікує вашого підтвердження" with title "Hermes Agent Approval" sound name "Glass"'
```
- **Behavior**: Fires across all macOS Spaces and over any active application.
- **Sound**: Plays the crisp, non-intrusive system chime even when the terminal window is fully unfocused or hidden behind browser tabs.

#### 3. IDE / Terminal Bell Audio Signals

- **Antigravity IDE / VS Code Integrated Terminal (`TERM_PROGRAM=vscode`)**:
  - Config location: `~/Library/Application Support/Antigravity IDE/User/settings.json` (or `Code/User/settings.json`).
  - Add the following keys:
    ```json
    {
      "terminal.integrated.enableBell": true,
      "accessibility.signals.terminalBell": {
        "sound": "on"
      }
    }
    ```
  - **Effect**: When the terminal receives ASCII `\a`, the IDE plays an audio chime and displays a bell badge indicator on the terminal tab.

- **Standalone Terminal Emulators (Ghostty, iTerm2, Alacritty, Terminal.app)**:
  - **iTerm2**: `Preferences` ➔ `Profiles` ➔ `Terminal` ➔ Enable `Silence bell`, enable `Send notification when idle/bell`.
  - **Ghostty**: `bell-action = sound,notification` in config.
  - **Terminal.app**: `Settings` ➔ `Profiles` ➔ `Advanced` ➔ `Audible bell` + `Bounce icon in Dock`.

#### 4. Hermes Native Bell on Turn Completion
Enable the native Hermes ASCII bell emission in `~/.hermes/config.yaml`:
```bash
hermes config set display.bell_on_complete true
```
This ensures `\a` is piped to stdout at the completion of actions or interactive pauses.

#### 5. Interactive Prompt Modal Hook (`core/hermes_agent/cli.py`)
Because standard CLI approval and clarify prompts default to rendering without an audible bell, add explicit bell and macOS banner triggers inside `_approval_callback` and `_clarify_callback` right after `self._paint_now()`:
```python
# Ring terminal bell and trigger macOS notification on modal prompt
try:
    sys.stdout.write("\a")
    sys.stdout.flush()
    if sys.platform == "darwin":
        import subprocess
        clean_desc = (description or command or "Потрібне підтвердження дії").replace('"', "'")[:100]
        subprocess.Popen([
            "osascript", "-e",
            f'display notification "{clean_desc}" with title "Hermes Agent: Підтвердження" sound name "Glass"'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception:
    pass
```
