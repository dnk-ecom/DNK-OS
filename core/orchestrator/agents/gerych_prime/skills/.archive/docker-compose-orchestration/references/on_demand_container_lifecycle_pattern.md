# On-Demand Docker Compose Lifecycle Pattern (Zero-Idle RAM)

## Problem
In local developer environments and resource-constrained edge/cloud hosts, running full secondary application stacks (e.g., Postiz, Whisper servers, heavy headless browsers, local vector databases) continuously in the background consumes 250MB–2GB+ of RAM and background CPU cycles even when no active tasks require them.

## Solution: On-Demand Just-In-Time (JIT) Container Lifecycle
Instead of keeping peripheral service stacks perpetually running:
1. **Container State**: Kept in stopped state (`docker compose stop` or idle).
2. **Auto-Start on Execution**: The client/publisher service checks health before dispatch. If unreachable, it programmatically invokes `docker compose -f <compose_file> up -d` and polls the health endpoint until ready (e.g. 3–5 seconds).
3. **Execution & Release**:
   - The job/payload is dispatched to the service.
   - For batch jobs, containers can either remain active for a bounded timeout or be immediately stopped via `docker compose -f <compose_file> stop` to restore 0 MB RAM idle state.
4. **Single-Pane-of-Glass Embedded UI**:
   - Host frontend integrates an embedded webview/iframe or direct API endpoints to toggle container status and perform initial OAuth logins without requiring separate terminals.
