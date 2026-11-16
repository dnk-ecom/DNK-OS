---
name: tauri-dev-workflow
description: "Use when creating, cloning, or running Tauri v2 apps."
version: "1.0.0"
category: "software-development"
---

# Tauri v2 Development Workflow

Class-level skill covering the full Tauri v2 development lifecycle.

## Trigger Phrases

- "create tauri app", "new tauri project", "bootstrap tauri"
- "clone tauri", "run tauri dev", "existing tauri project", "tauri from source"
- "tauri dev mode", "tauri debug", "tauri build", "tauri release"
- "tauri menu bar", "tauri tray app", "tauri sidecar"

## Sub-Skills / References

This skill indexes the following reference files (in `references/`):

- `references/tauri-create-project.md` — Creating new Tauri v2 projects with create-tauri-app
- `references/tauri-existing-project.md` — Cloning and running existing Tauri v2 projects from source
- `references/tauri-dev-mode.md` — Daily development workflow, dev server vs static assets, dual-side debugging
- `references/tauri-menu-bar-apps.md` — Special considerations for menu-bar/tray-only Tauri apps
- `references/tauri-release-build.md` — Production builds, signing, notarization, distribution

## Quick Reference: Common Commands

### New Project
```bash
# npm
npm create tauri-app@latest

# pnpm
pnpm create tauri-app@latest

# bun
bun create tauri-app@latest

# cargo
cargo install create-tauri-app && cargo create-tauri-app
```

### Existing Project Setup
```bash
git clone <repo-url> <target-dir>
cd <target-dir>

# Install Rust (if missing)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# Install Tauri CLI
cargo install tauri-cli --locked

# Install Node deps
npm install

# Run dev mode
npm run tauri dev
```

### Release Build
```bash
npm run tauri build
# Output: src-tauri/target/release/bundle/
```

## Common Pitfalls

1. **Missing Rust toolchain** — Always verify `rustc --version` first
2. **Missing tauri-cli** — Required for `tauri dev`/`tauri build` commands
3. **First dev build is slow** — 2-5 minutes for Rust compilation; subsequent runs are incremental
4. **Menu-bar only apps** — No window opens; check macOS menu bar (top-right) for icon
5. **Background execution** — Use background=true + polling for `npm run tauri dev` in automation
6. **Node version** — Match project's `.nvmrc` or `package.json` engines field

## Verification Checklist (Dev Launch)

- [ ] `rustc --version` && `cargo --version` ✓
- [ ] `tauri --version` ✓
- [ ] `npm install` completes without errors ✓
- [ ] `npm run tauri dev` compiles successfully (`Finished 'dev' profile`)
- [ ] App appears: window opens OR menu-bar icon visible ✓
- [ ] DevTools accessible (Cmd+Option+I for webview) ✓

## Architecture Notes

- Tauri v2 uses Rust for backend, any frontend framework (React, Vue, Svelte, vanilla)
- `tauri.conf.json` / `tauri.conf.json5` is the single source of truth for app config
- Frontend dev server (Vite) + Rust binary run simultaneously in dev mode
- IPC: `invoke` (Rust → Frontend) and `listen`/`emit` (event-based)
- Sidecars: External binaries bundled with app (`tauri.conf.json > bundle > externalBin`)