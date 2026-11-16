<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/shopify_ai_assistant_lean_fact_check_and_eval_patterns.md"
purpose: "Reference patterns for Shopify AI Shopping Assistants, Lean Fact-Checking Engines, Deterministic Resolvers, and Mock Storefront E2E Testing."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.1.0"
updated_at: "2026-10-27"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER --- -->

# 🛍️ Shopify AI Assistant: Lean Fact-Check, Deterministic Resolvers & Eval Patterns

Based on the SOTA reverse-engineering of `hajirshariati/seos-assistant` (HajirAI / SEoS Assistant, 1,405 commits, ~70.8k LOC across 304 files, 32 passing offline eval suites).

---

## 1. "Claude Decides, Code Checks Facts" Engine Architecture

### The Anti-Hallucination Pipeline (`app/lib/lean/verify.js`)
Instead of complex pre-classifiers or raw text post-processing, the engine implements a tight 3-step loop:
1. **Tool Invocation**: Claude calls tools (`search`, `product_details`, `store_info`, `orders`, `recommenders`).
2. **Deterministic Fact-Check Gate (`verifyLeanAnswer`)**:
   - **Style Family Match (`unverified_product`)**: Ensures every product style name mentioned by the LLM was returned by a tool or shown earlier in the conversation history.
   - **Price Verification (`unverified_price`)**: Regex `/\$\s?(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)/g` extracts all quoted prices and verifies against the allowed price set of seen catalog products.
   - **Missing Cards Gate (`missing_cards`)**: If products are recommended in text, `show_products` tool call must be present to guarantee UI card rendering.
   - **Discount/Coupon Gate (`unverified_offer`)**: Verifies that any mentioned discount percentage (`XX% off`) or coupon code actually exists in active merchant campaigns.
3. **Auto-Rewrite Loop**: If verification fails, the exact discrepancy list is fed back to Claude for a bounded rewrite attempt before streaming to the shopper.

---

## 2. Deterministic Decision Tree Resolver (`decision-tree-resolver.server.js`)

For complex diagnostic or clinical recommendations (e.g. arch types, overpronation, plantar fasciitis):
- **LLM Boundary**: The LLM is **STRICTLY FORBIDDEN** from guessing the final SKU. The LLM only acts as an empathetic interviewer gathering attributes (`gender`, `useCase`, `arch`, `condition`).
- **Deterministic Resolver**:
  1. Applies defaults for unanswered non-critical attributes.
  2. Hard-filters candidate catalog on load-bearing attributes (`gender`, `useCase`).
  3. Strict policy enforcement (e.g., Kids gender cannot be substituted by Adult Unisex).
  4. Condition scoring (`heel_spurs`, `mortons_neuroma`, `metSupport=true`).
  5. Lexicographical tie-breaking by `masterSku` — guarantees 100% deterministic, reproducible outputs across identical inputs.

---

## 3. Spending Limits, Peak Mode & CS Cheat Codes

- **Store & IP Dual Rate Limiting**: `checkIpShopRate` prevents scraping; `checkStoreChatRate` enforces store-wide limits.
- **Daily Message Cap (`ChatUsage.server.js`)**: Merchants configure hard daily quotas to cap LLM token spend.
- **Peak Mode (`peak-mode.js`)**: Dynamic limits elevated during Black Friday / Cyber Monday sales.
- **CS Team Cheat Codes**: An exact merchant-configured pass-phrase typed in chat immediately dumps active store campaigns from the database, bypassing the LLM completely for deterministic CS staff utility.
- **Anthropic Prompt Caching**: Uses `cache_control: { type: "ephemeral" }` on system prompts and tools, dramatically reducing token costs and turn latency.

---

## 4. Evaluation & Offline E2E Testing Infrastructure

### Offline Evals (`scripts/run-evals.mjs`)
- **32 Test Suites Without API Keys**: Tests rate-limiters, history sanitization, orthotic decision trees, price extraction, token thresholds, and regression transcripts.
- **Prisma ESM Import Prerequisite**: `pnpm prisma generate` must be run prior to running `node scripts/run-evals.mjs` to populate the generated client.

### Post-Hoc Hallucination Audit (`scripts/audit-hallucinations.mjs`)
- Queries real chat logs in PostgreSQL across date ranges and evaluates transcripts against catalog snapshots to detect any live unverified products or fabricated discount promises.

### Mock Storefront E2E Harness (`mock-store.mjs`)
- Mocks Shopify App Proxy endpoints (`/apps/hajirai/*`), Cart API, and customer account sessions for headless Playwright E2E verification without live Shopify dev stores.

---

## 5. Licensing & Assimilation Invariant (Track 2)

- **Unspecified / Missing License Invariant**: When a public repository lacks a `LICENSE` file and `package.json` license field, default international copyright ("All Rights Reserved") applies.
- **Permitted**: Architectural extraction, AST patterns, eval harness methodologies, reverse-engineered schema patterns.
- **Prohibited**: Direct physical code copying or un-reengineered distribution.
