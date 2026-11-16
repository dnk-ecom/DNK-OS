---
name: tauri-dev-mode
description: Daily development workflow, dev server vs static assets, dual-side debugging
license: Apache-2.0
---

# Tauri v2 Dev Mode Workflow

## When to Use

- "tauri dev mode", "tauri debug", "tauri hot reload", "dual debugging"

## How Dev Mode Works

```
┌─────────────────────┐     ┌─────────────────────┐
│  Frontend Dev       │     │  Rust Backend       │
│  Server (Vite)      │     │  Binary (cargo)     │
│  Port: 1420/5173    │     │  IPC via invoke     │
└─────────┬───────────┘     └─────────┬───────────┘
          │                           │
          └───────────┬───────────────┘
                      ▼
            ┌─────────────────────┐
            │   WebView / Window  │
            │   (Tauri Runtime)   │
            └─────────────────────┘
```

## Starting Dev Mode

```bash
# Standard
npm run tauri dev

# With custom port
npm run tauri dev -- --port 3000

# Skip frontend build (if already running)
npm run tauri dev -- --no-dev-server
```

## Debugging

### Frontend (WebView)
- **macOS**: Cmd+Option+I (opens DevTools)
- **Windows/Linux**: Ctrl+Shift+I
- **Programmatic**: `tauri dev --devtools` or set `TAURI_DEBUG=1`

### Rust Backend
```bash
# VS Code launch.json
{
  "type": "lldb",
  "request": "attach",
  "name": "Debug Tauri Backend",
  "pid": "${command:pickProcess}"
}

# Or: cargo run --target x86_64-apple-darwin (with debug symbols)
```

### Console Logging
- Frontend: `console.log` → DevTools console
- Rust: `log::info!`, `eprintln!`, `tracing` → terminal where `tauri dev` runs

## Hot Reload Behavior

| Change Type | Behavior |
|-------------|----------|
| Frontend (React/Vue/Svelte) | Vite HMR → instant browser update |
| Rust (src-tauri/src/) | Cargo rebuild → binary restart (2-10s) |
| tauri.conf.json | Full restart required |
| Cargo.toml | Full rebuild + restart |

## Common Dev Commands

```bash
# Watch Rust changes only (no frontend)
cd src-tauri && cargo watch -x run

# Type-check without building
cd src-tauri && cargo check

# Run tests
cd src-tauri && cargo test

# Lint
cd src-tauri && cargo clippy
```

## Dev Mode Flags

```bash
tauri dev --help
# --devtools          Open DevTools on startup
# --no-dev-server     Skip Vite dev server (use built assets)
# --port <PORT>       Frontend dev server port
# --target <TRIPLE>   Cross-compile target
```

## References

- https://v2.tauri.app/develop/debugging/
- https://v2.tauri.app/develop/hot-reload/