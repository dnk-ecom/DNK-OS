# Shopify MCP Server Architecture, OAuth 2026 & Blast-Radius Guardrails

<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/software-development/sota-repository-assimilation/references/shopify_mcp_architecture_and_blast_radius_guardrails.md"
purpose: "Architectural audit, OAuth 2026 Client Credentials patterns, context-budget constraints, supply-chain trojan fork defenses, and mutation firewalls for Shopify MCP servers."
status: "Active"
version: "1.1.0"
updated_at: "2026-10-29"
author: "Gerych Prime & DNK-e.com Maksym"
--- END DNK-MRH-HEADER -->

## 1. Shopify OAuth 2026 Client Credentials Invariant

As of January 1, 2026, Shopify Dev Dashboard apps mandate OAuth 2.0 Client Credentials for new applications:
- **Token Lifecycle**: Static `shpat_` tokens are legacy. New apps use `client_id` + `client_secret` to request short-lived access tokens (`expires_in ≈ 86,400s / 24h`) via `POST /admin/oauth/access_token` with `grant_type=client_credentials`.
- **Hot-Swappable Transparent Refresh**: MCP servers must decouple credential storage from the underlying GraphQL client. Implement a scheduled refresh timer with a 5-minute pre-expiry margin (`REFRESH_MARGIN_MS = 5 * 60 * 1000`) and hot-swap the `X-Shopify-Access-Token` request header in memory to maintain unbroken agent sessions.
- **Unref Timer Hygiene**: Refresh timers in Node.js runtime must call `timer.unref()` to allow clean process termination during agent teardown.

## 2. Blast-Radius & Context-Bloat Pitfalls in Monolithic MCPs

When evaluating or integrating third-party e-commerce MCP servers (e.g. `GeLi2001/shopify-mcp`):

1. **Context-Window Bloat (40+ Standing Schemas)**:
   - Exposing 30–50 discrete CRUD tools via Stdio injects 9,000–12,000 tokens of Zod schemas into the system prompt on *every single turn*.
   - **Resolution**: Violates the JIT-Tooling law (baseline standing overhead ≤ 6,000 tokens). Replace monolithic tool registries with FastMCP Code Mode or domain-scoped subagents.

2. **Unbounded Destructive Mutations (Zero Blast Radius Guardrails)**:
   - Exposing raw destructive mutations (`deleteProduct`, `orderCancel`, `createRefund`, `deleteProductVariants`, `deleteCustomer`) directly to an autonomous LLM creates an unacceptable operational risk.
   - **Resolution**: Implement Human-in-the-Loop (HITL) approval gates, two-phase dry-run diff previews, and role-based tool partitioning (`shopify-read` vs `shopify-admin-hitl`).

3. **GraphQL Leaky-Bucket Rate Limiting**:
   - Lightweight GraphQL clients (`graphql-request`) lack automatic cost calculation. Under sequential agent iteration, Shopify Admin API responds with `THROTTLED`.
   - **Resolution**: Integrate exponential backoff retry algorithms monitoring `extensions.cost.throttleStatus` (`maximumAvailable`, `currentlyAvailable`, `restoreRate`) or use `@shopify/admin-api-client`.

4. **Package Registry Drift**:
   - Verify whether published package versions (e.g. on npm) match the latest GitHub master branch commits before running with `npx`. Verify enum definitions (e.g. `MetafieldOwnerType` uppercase vs concatenated casing).

## 3. Supply-Chain Trojan Forks & Credential Exfiltration Defense

Community forks of popular MCP servers frequently masquerade as "production-ready v2" upgrades with added caching or features (e.g. `Cesarjoquin/shopify-mcp`), but serve as credential-harvesting Trojans:

### Proven Attack Vector (Dissected from `Cesarjoquin/shopify-mcp`):
1. **Fork Camouflage**: The attacker forks a verified repo (`GeLi2001/shopify-mcp`), inflates the version (`2.0.0`), adds realistic architectural diagrams, and claims to implement "Redis Token Caching" or "Connection Management".
2. **Dependency Typosquatting / Swapping**:
   - Instead of standard `ioredis`, the attacker injects an obscure package (`ioredis-xyz` ➔ `oscar-redis`).
   - When npm security takes down the package (`oscar-redis@0.0.1-security security holding package`), the attacker immediately substitutes another typosquat (`oracle-redis` published under a throwaway email).
3. **Targeted Exfiltration**: The "token cache" class (`RedisTokenCache`) intercepts raw OAuth access tokens and credentials during server bootstrap and serializes them into the rogue library.

### Mandatory Verification Checklist for Third-Party MCP Forks:
- **Diff Against Upstream**: Always check the root commit diff against the original author. If commits are squashed or feature additions touch dependencies, inspect every new package.
- **Dependency Provenance Check**: Run `npm view <dependency> maintainers dist-tags` or `pnpm info <dependency>`. If a dependency has 0 downloads, recent throwaway maintainers, or references a "security holding package", it is hostile.
- **Credential Path Audit**: Trace all imports in files handling `accessToken`, `clientId`, `clientSecret`, or `apiKey`. No token or credential should ever be passed to an unvetted third-party storage or telemetry client.

## 4. Sovereign DNK OS Direct-Connection Pattern

Rather than running foreign MCP servers as standing background daemons:
- **Direct GraphQL Execution**: Execute authenticated GraphQL calls directly via native `services/dnk_shopify` or Python sandbox (`urllib`/`httpx`).
- **Zero Overhead & Zero Attack Surface**: Direct API calls eliminate foreign npm dependencies, third-party supply-chain risks, and context-window pollution.
- **Port Auth Core Only**: If using OAuth 2026 Client Credentials, isolate and audit only the pure token-refresh logic (`ShopifyAuth`), never external wrapper packages.
