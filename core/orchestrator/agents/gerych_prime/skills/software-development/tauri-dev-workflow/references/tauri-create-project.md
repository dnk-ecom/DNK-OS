---
name: tauri-create-project
description: Creating new Tauri v2 projects with create-tauri-app
license: Apache-2.0
---

# Creating New Tauri v2 Projects

## When to Use

- "create tauri app", "new tauri project", "bootstrap tauri", "create-tauri-app"

## Installation Methods

### npm
```bash
npm create tauri-app@latest
```

### pnpm
```bash
pnpm create tauri-app@latest
```

### bun
```bash
bun create tauri-app@latest
```

### cargo (Rust-first)
```bash
cargo install create-tauri-app && cargo create-tauri-app
```

## Interactive Prompts

The CLI will prompt for:
1. Project name
2. Package manager (npm, pnpm, yarn, bun)
3. Frontend template (React, Vue, Svelte, Vanilla, Solid, etc.)
4. TypeScript / JavaScript
5. Router (if applicable)
6. CSS framework (Tailwind, plain CSS, etc.)

## Post-Creation Steps

```bash
cd <project-name>
npm install
npm run tauri dev
```

## References

- https://v2.tauri.app/start/create-project/
- https://v2.tauri.app/start/prerequisites/