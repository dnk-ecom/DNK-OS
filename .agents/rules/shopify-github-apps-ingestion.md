---
title: "Shopify GitHub App Ingestion Protocol"
description: "Mandatory Protocol for Ingestion, Audit, Sanitization, and Dev Store Readiness of Shopify Apps from GitHub."
mrh_id: ".agents/rules/shopify-github-apps-ingestion.md"
status: Active
version: "1.0.0"
updated: 2026-11-18
globs: "**/*"
alwaysApply: true
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: ".agents/rules/shopify-github-apps-ingestion.md"
> purpose: "Mandatory Protocol for Ingestion, Audit, Sanitization, and Dev Store Readiness of Shopify Apps from GitHub."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📦 Standard Protocol: Shopify GitHub App Ingestion & Dev Store Readiness

Whenever the user requests to download, clone, or intake a Shopify App from `github.com` (or any external git repository), all agents MUST strictly execute the following deterministic protocol:

## 1. Canonical Destination Directory (Zero-Pollution Invariant)
- **Target Root**: STRICTLY clone or extract into:
  `../DNKEcom/GitHub_Shopify_Apps/<app-folder>/`
- **Quarantine Invariant**: NEVER download, clone, or extract third-party apps directly into `DNK_HUB` root or subfolders. The app intake directory is external to `DNK_HUB` to preserve monorepo hygiene, prevent language server/indexer latency, and eliminate package/dependency cross-contamination.

## 2. Ingestion & Shallow Clone
- Perform a shallow clone to minimize disk and network overhead:
  `git clone --depth 1 <github_url> ../DNKEcom/GitHub_Shopify_Apps/<app-folder>`

## 3. Strict Package Manager & Dependency Hygiene
- **Strict pnpm Usage**: All dependencies must be installed via `pnpm install` in compliance with DNK OS zero-bloat tooling invariants. Bare `npm install` and `yarn` are prohibited.
- **Lockfile Hygiene**: If `pnpm-lock.yaml` is present or migrated, remove redundant `package-lock.json` or `yarn.lock` to avoid tooling confusion.
- **Database Initialization**: If using Prisma/SQLite, run migrations (`pnpm run setup` or `pnpm exec prisma migrate deploy`) to ensure local SQLite (`dev.sqlite`) is initialized and ready.

## 4. Foreign Credentials & Organization Decoupling Gate
- **Client ID Quarantine**: Open-source apps from GitHub frequently contain the original author's remote `client_id` in `shopify.app.toml`. Leaving this intact causes HTTP 403 Forbidden ("You are not a member of the requested organization") when running CLI commands.
- **Action**: Comment out or decouple the remote `client_id` in `shopify.app.toml`, preserving the author's ID in a comment for reference.
- **Environment Template**: Create or verify `.env.example` and a local `.env` defining required scopes, port, and database URL.

## 5. Verification & Zero-Error Compilation Gate
Before declaring an app ready for testing, the agent must physically execute and verify:
1. **App Build**: Run `pnpm run build` (SSR bundle / frontend assets must compile with exit code 0).
2. **Shopify Functions Build**: If the app contains Shopify Functions (`extensions/*/`), verify that GraphQL types generate and WebAssembly builds successfully via Javy/Rust.
3. **Unit Tests**: Run `pnpm test` (vitest/jest). Update outdated boilerplate fixtures to match real app logic so tests pass cleanly without hanging in watch mode (`vitest run`).
4. **Linter & Typecheck**: Run `pnpm run lint` and `pnpm run typecheck`. Fix trivial unused variables or ES module issues to guarantee clean developer experience.
5. **Theme App Extensions**: Run `shopify theme check` on any Theme App Extensions (`extensions/*/blocks`, `snippets`).

## 6. App Audit Report (`AUDIT_<app-folder>.md`)
Generate a structured audit markdown report saved directly in:
`../DNKEcom/GitHub_Shopify_Apps/AUDIT_<app-folder>.md`
The report MUST cover:
- **App Profile**: Repository, author, license, framework (Remix/React Router, Vite, Next.js), database/ORM, Shopify App CLI version.
- **Architecture & Extension Inventory**: Detailed breakdown of admin routes, webhooks, Theme App Extensions, Shopify Functions, Admin Blocks.
- **Security & Privacy Audit**: Permissions/access scopes requested, external network calls, telemetry, data storage practices.
- **Verification Matrix**: Machine execution proof of `pnpm install`, `prisma setup`, `build`, `test`, `lint`, and `theme check`.
- **Step-by-Step Dev Store Deployment & Testing Guide**: Exact interactive CLI commands (`shopify app dev`, `shopify app config link`), Partner App linking steps, theme embed activation, and end-to-end testing workflow on development store (`m-craft-top.myshopify.com`).
