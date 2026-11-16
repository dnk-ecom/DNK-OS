# Omarchy & Herdr: Agentic Linux & Background Agent Supervisor Patterns

## Overview
Omarchy (`omacom/omarchy`, DHH/Omacom) is an opinionated Arch/Hyprland distribution built for the agentic era. Alongside it, `herdr` (`omacom/herdr`) provides a dedicated Rust-based background supervisor and socket API for autonomous coding agents.

## Core Architectural Invariants

### 1. `herdr` Agent Supervisor Architecture
- **State vs Runtime Separation**: `AppState` and `PaneState` are pure data structures testable without PTYs or async event loops. `PaneRuntime` isolates OS-level process management.
- **Pure Render Loop**: Geometry and layout mutations are computed first (`compute_view()`); rendering draws pure `&AppState` without state side effects.
- **Background Daemon Persistence**: The supervisor lives across lid closes, network drops, and terminal disconnects. Agents keep running unattended.
- **Status & Blocker Detection**: Explicit inspection of agent output buffers to classify panes as `working`, `blocked`, or `idle` without parsing volatile scrollback.
- **Agent Socket API**: Exposes an IPC socket allowing agents to spawn sibling panes, prompt peer agents, and await resolution of blocking states.

### 2. OS-Level Crash-to-Agent Pipeline
- System crashes handled via `systemd-coredump` / `coredumpctl`.
- Triggers a desktop notification bound to an agentic skill (`diagnose-crash`), auto-feeding backtraces and binary symbols to the agent for instant self-healing.

### 3. Agent Toolchain Lazy Launchers
- Integrated with `mise` runtime manager.
- Lazy stubs in `~/.local/bin/` for Hermes, Claude Code, OpenAI Codex, Antigravity (`agy`), OpenCode, etc.
- Unified theme synchronization across editor, terminal, desktop chrome, and agent interfaces via `aether`.
