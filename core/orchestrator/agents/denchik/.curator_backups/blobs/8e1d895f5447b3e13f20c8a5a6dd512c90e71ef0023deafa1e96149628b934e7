# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/mcp_stdio_never_die_and_team_send_budget_protocol.md"
# purpose: "MCP Stdio Runtime Never-Die Invariant, Team Send Budget Loop Breaker, and macOS Artifact Audit Protocol."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🛡️ MCP Stdio Never-Die Runtime & Team Send Budget Protocol

This protocol codifies critical resilience invariants extracted from real-world multi-agent desktop harnesses (such as `AgentsRoom` and SOTA MCP runtimes).

---

## 1. The MCP Stdio "Never-Die" Process Invariant

### 💥 The Problem
When an LLM agent CLI (Claude Code, Hermes, OpenCode, Cursor) spawns an MCP server as a child process over stdio:
- Any uncaught promise rejection (`unhandledRejection`), stream parse error (`JSON.parse` failure in `readline`), or write error (`EPIPE` when the CLI stream encounters backpressure) will crash the Node/Python process.
- **The CLI's reaction is brutal**: when the MCP process dies or exits non-zero, the client agent CLI permanently drops the toolset from the LLM session. The agent loses its tools, fails subsequent steps, and aborts the task.

### 🛡️ The Implementation Rule
Every stdio MCP server must wrap its entrypoint with a crash-proof runtime:
1. **Global Rejection & Exception Catchers**:
   ```javascript
   process.on("unhandledRejection", (reason) => {
     // Log exclusively to stderr — NEVER corrupt stdout (JSON-RPC channel)
     process.stderr.write(`[MCP Runtime Warning] Unhandled rejection: ${reason}\n`);
   });

   process.on("uncaughtException", (err) => {
     process.stderr.write(`[MCP Runtime Warning] Uncaught exception: ${err?.stack || err}\n`);
   });
   ```
2. **Stdout Stream Guard (`EPIPE` Defense)**:
   ```javascript
   process.stdout.on("error", (err) => {
     if (err.code === "EPIPE") {
       // Parent process closed the pipe or disconnected; ignore and exit cleanly
       process.exit(0);
     }
   });
   ```
3. **Strict Separation of Diagnostic Channels**:
   - `stdout`: Reserved 100% for valid JSON-RPC 2.0 lines (`\n` separated).
   - `stderr`: Dedicated to debug logs, tracing, and stack dumps. Never emit `console.log()` to stdout.

---

## 2. Multi-Agent Team Send Budget (Anti-Loop Circuit Breaker)

### 💥 The Problem
In multi-agent architectures (e.g. Builder ↔ Auditor, Researcher ↔ Creator), agents frequently fall into polite conversational ping-pong loops:
- "Thank you for the update." -> "You're welcome! Let me know if you need anything else." -> "Understood, standing by."
- Or cascading retry handoffs where neither agent makes tangible progress, draining token budgets and hitting tool limits.

### 🛡️ The Implementation Rule (`teamSendBudget`)
1. **Sliding Window Cap**:
   - Maintain a rolling window (e.g. 10 minutes) tracking messages between agent role pairs `(sender_role, recipient_role)`.
   - Hard cap: Maximum 12 messages per pair per window; global swarm fanout cap of 30.
2. **Actionable Directive vs Machine Error Code**:
   - **DO NOT** return an HTTP 429 or machine exception code. LLMs interpret error codes as transient network failures and immediately trigger retry logic.
   - **DO** return a plain-language operational directive:
     ```
     [TEAM_SEND_BUDGET_EXCEEDED]
     You have reached the communication limit with this agent for this cycle.
     DO NOT send another note or handoff.
     Synthesize your current state, output your final findings, and wait for human steering.
     ```

---

## 3. macOS DMG & Binary Artifact Inspection Protocol

When auditing compiled macOS artifacts (`.dmg`, `.app`, `.pkg`):

1. **Non-Interactive Headless Mount**:
   ```bash
   hdiutil attach "<dmg_path>" -nobrowse -readonly
   # Output gives mount point, e.g. /Volumes/<VolumeName>
   ```
   *Always use `-nobrowse` to prevent opening Finder UI windows.*

2. **Entitlements & Code Signing Verification**:
   ```bash
   codesign -dvvv --entitlements :- "/Volumes/<VolumeName>/<App>.app"
   ```
   **Security Flags to Scrutinize**:
   - `com.apple.security.app-sandbox: false` — Process runs outside OS sandbox with full user permissions.
   - `com.apple.security.cs.disable-library-validation: true` — Allows loading arbitrary dynamic libraries.
   - `com.apple.security.cs.allow-dyld-environment-variables: true` — Subject to DYLD injection attacks.
   - `com.apple.security.automation.apple-events: true` — Can control other desktop apps via AppleScript/JXA.

3. **Electron Resource Inspection**:
   - Inspect `Contents/Resources/` for loose `.cjs`/`.py` scripts and adapters.
   - Unpack `app.asar` via `npx @electron/asar extract` or inspect listing via `npx @electron/asar list`.

4. **Mandatory Cleanup Invariant**:
   Immediately after inspection, unmount the volume to avoid system mount leaks:
   ```bash
   hdiutil detach "/Volumes/<VolumeName>"
   ```
