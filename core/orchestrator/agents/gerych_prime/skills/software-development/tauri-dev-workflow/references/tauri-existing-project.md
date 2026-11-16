---
name: tauri-existing-project
description: Cloning and running existing Tauri v2 projects from source
license: Apache-2.0
---

# Cloning & Running Existing Tauri v2 Projects

## When to Use

- "clone tauri", "run tauri dev", "existing tauri project", "tauri from source", "tauri github repo"

## Prerequisites Check

```bash
# Verify Rust toolchain
rustc --version && cargo --version
# If missing: install via rustup (see below)

# Verify Tauri CLI
tauri --version
# If missing: cargo install tauri-cli --locked
```

## Step-by-Step Setup

```bash
# 1. Clone repository
git clone <repo-url> <target-dir>
cd <target-dir>

# 2. Install Rust toolchain (if missing)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# 3. Install Tauri CLI
cargo install tauri-cli --locked

# 4. Install Node dependencies
npm install
# or: pnpm install / bun install / yarn

# 5. Run development mode
npm run tauri dev
```

## Background Execution (Automation)

For long-running dev builds in automated contexts:

```bash
# Start in background
npm run tauri dev &
# or with background=true in terminal tool

# Poll for completion (Rust compilation takes 2-5 min first run)
# Look for: "Finished 'dev' profile in Xm Xs"
```

## Environment Notes

- Always source `$HOME/.cargo/env` in fresh shells
- First `tauri dev` compiles all Rust dependencies (slow)
- Subsequent runs are incremental (~seconds)
- App may be menu-bar only (no window) — check macOS top bar

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `rustc: command not found` | `source "$HOME/.cargo/env"` or restart shell |
| `tauri: command not found` | `cargo install tauri-cli --locked` |
| `npm run tauri dev` hangs | First build compiles Rust; wait 2-5 min |
| No window opens | Check menu bar (tray-only apps) |
| Node version mismatch | `nvm use` or match `.nvmrc`/`engines` |

## References

- https://v2.tauri.app/start/create-project/
- https://v2.tauri.app/start/prerequisites/