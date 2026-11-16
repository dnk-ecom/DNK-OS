# --- DNK-MRH-HEADER ---
# mrh_id: "references/cross_harness_presence_and_weak_loop_timeout_mitigation.md"
# purpose: "Cross-Harness Multi-Agent Presence Protocol, Weak-Loop Timeout Mitigation & Webhook Wake-Up Architecture."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🌐 Cross-Harness Multi-Agent Presence Protocol & Weak-Loop Mitigation

## 1. The Core Heterogeneous Harness Problem
When autonomous agents from different platforms (Cursor, Antigravity, Cline, Windsurf, Claude Code, Codex, Hermes) collaborate in a shared room or event bus, they operate under radically different runtime harnesses:

1. **Weak-Loop Client Harnesses (IDE Extensions & Desktop Apps)**:
   - *Clients*: Cursor, Antigravity, Cline, Windsurf, Claude Desktop, GitHub Copilot.
   - *Constraint*: Hard internal tool-call timeout at **45s – 60s**.
   - *Failure Mode*: If an MCP long-polling call (`room_listen`, `bus_poll`) exceeds 45s, the client harness forcibly aborts the connection with a `Tool Execution Timeout/Error`.
2. **Strong-Loop Client Harnesses (Dedicated CLI Runtimes)**:
   - *Clients*: Claude Code CLI, OpenAI Codex CLI, Gemini CLI, Hermes Agent.
   - *Capability*: Can hold long-polling tool execution up to **270s – 300s** without timing out.

---

## 2. The Tool-Call Dropout Trap (Presence Eviction)
Why do autonomous agents silently drop out of collaborative sessions?

```
[Server Long-Poll (60s)] 
       │
       ▼ (Client timeout hit at 45s)
[Harness Tool Error: Execution Timed Out]
       │
       ▼ (LLM reacts to error)
[LLM emits narrative apology: "The room timed out, I will wait..."]
       │
       ▼ (No follow-up tool call in turn response)
[Turn Finishes / Agent Process Halts] ──> AGENT HAS PERMANENTLY LEFT THE ROOM
```

- In all modern LLM harnesses, **a response with NO tool call ends the agent's turn**.
- An ended turn means the process is dormant; nothing restarts it unless an external event arrives.
- When an LLM explains why something timed out instead of immediately invoking the next listen tool, it evicts itself from the collaborative swarm.

---

## 3. The Stateless Harness Fingerprinting & Clamping Protocol

To prevent weak-loop dropouts, the server/harness coordinator must implement adaptive timeout clamping:

```typescript
// Stateless classification via User-Agent and MCP clientInfo
export function detectHarness(req: Request, clientInfo?: { name?: string }): HarnessProfile {
  const ua = req.headers.get("user-agent") || "";
  const client = (clientInfo?.name || "").toLowerCase();

  const isWeakLoop = /cursor|antigravity|cline|windsurf|claude-desktop|copilot/i.test(ua) ||
                     /cursor|antigravity|cline|windsurf|copilot/i.test(client);

  if (isWeakLoop) {
    return {
      type: "weak_loop",
      maxListenMs: 45_000,
      hint: "WEAK_LOOP_CLIENT: Timeout clamped to 45s. Do NOT increase timeoutMs. You MUST chain another room_listen call to remain present."
    };
  }

  return {
    type: "strong_loop",
    maxListenMs: 270_000,
    hint: null
  };
}
```

### Invariants:
1. **Never Emit Timeout Error**: When `maxListenMs` expires with no new events, return `exit_code: 0` with `status: "idle"` or `events: []`. Never return HTTP 408 / 504 or MCP tool errors.
2. **Inject Turn Discipline Hint (`NEXT_LISTEN`)**:
   Include a mandatory system prompt instruction in the return payload:
   > *"A reply with NO tool call ends your turn, which means you have permanently left the room. Do NOT write 'The room is quiet' to the user. End every turn by immediately calling the listen tool again."*

---

## 4. Webhook Wake-Up vs 24/7 Polling (Token-Diet Architecture)

For persistent daemon agents (such as Hermes or OpenClaw):
- **Problem**: Continuous 45s long-polling resends the entire conversation history on every turn, rapidly exhausting context windows and token budgets.
- **Solution (Webhook Wake-Up)**:
  1. Daemon registers an HTTP callback endpoint (`POST /api/v1/agent/webhook`) with a shared HMAC-SHA256 signing secret.
  2. Daemon immediately terminates its foreground poll loop and enters dormant state (0 tokens consumed).
  3. When a peer agent submits a message, task claim, or artifact tag (`[DECISION]`, `[TODO]`, `[RESULT]`), the server dispatches a signed webhook.
  4. The gateway wakes the agent, passes the single incoming event, and the agent executes one focused atomic turn.

---

## 5. Structured Collaboration Tags
To maintain clear cross-agent synchronization without natural-language ambiguity, agents communicating across harnesses must use deterministic markers:
- `[DECISION] <statement>`: Finalized architectural or implementation agreement.
- `[TODO] <assignment>`: Machine-parseable task assignment.
- `[STATUS] <progress>`: Milestone transition marker.
- `[RESULT] <evidence>`: Verified machine output, git diff, or test stdout.
