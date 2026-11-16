# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/references/agent_native_shopify_os_and_dimensional_pricing_patterns.md"
# purpose: "Clean-room SOTA patterns from kontakt755/teppich-paradies-shopify-ai: 0.01-unit dimensional pricing, GraphQL MCP mutation firewall, deploy-window cross-session lock, and 4-file bulk metafield protocol."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-19"
# author: "Gerych (Hermes Prime)"
# --- END DNK-MRH-HEADER ---

# 🧬 Agent-Native Shopify OS: Dimensional Pricing, MCP GraphQL Firewall & Deploy-Window Locks

Clean-room synthesis of production patterns from `kontakt755/teppich-paradies-shopify-ai` (Track 2 — Clean-Room Architecture Synthesis).

---

## 1. Centimeter-Exact Dimensional Pricing in Standard Integer Shopify Carts (`0.01 m²` Unit Pattern)

### Problem
Standard Shopify `/cart/add.js` only accepts integer `quantity` values (`variant.price * quantity`) without Shopify Plus Cart Transform functions or paid third-party price-calculator apps. For custom-cut or dimensional goods (carpets, fabrics, cables, timber, custom prints), rounding fractional area (`6.66 m²` -> `7 m²`) overcharges the customer.

### Solution Pattern (`custom.preis_pro_001_qm`)
1. **Product Metafield Toggle**: Set `product.metafields.custom.preis_pro_001_qm = true`.
2. **Variant Unit Price Scaling**: Store the variant price in Shopify Admin as the price per `0.01 m²` (i.e., `1/100th` of the square-meter price).
   - In Liquid, recover the display price per `1 m²` via `{% assign qm_preis_cents = current_variant.price | times: 100 %}` when `preis_pro_001 == true`.
3. **Exact Integer Quantity Mapping**:
   - When roll widths are multiples of `100 cm` (`200`, `300`, `400`, `500 cm`), any integer centimeter length `L_cm` yields an exact integer number of `0.01 m²` units:
     $$\text{units}_{0.01\text{m}^2} = \text{round}\left(\frac{\text{width}_{\text{cm}} \times \text{length}_{\text{cm}}}{100}\right)$$
   - Example: `200 cm` width $\times$ `333 cm` length $= 6.66\text{ m}^2 = 666$ integer units of `0.01 m²`.
4. **Line-Item Properties & Checkout Hygiene**:
   - Attach customer-visible dimensional properties (`properties[Breite]`, `properties[Länge]`, `properties[Fläche]`, `properties[Zuschnitt]`) to the `/cart/add.js` payload so the cart drawer, checkout, and packing slips show human-readable dimensions alongside the unit quantity.
5. **Cross-Variant Cheaper Roll Recommendation**:
   - In the calculator JS, iterate over all width variants (`data-variant-prices` JSON map) and compare the custom-cut total (`Raummaß` + cut surcharge) against the next wider full roll (`Meterware`). If the wider roll is cheaper, surface an inline banner recommending the cheaper option.

---

## 2. PreToolUse GraphQL Mutation Lexer Firewall (`shopify-mcp-guard`)

### Problem
When AI agents have access to an authenticated Shopify Admin MCP tool (`mcp__*__graphql_mutation`), shell-level command guards cannot inspect GraphQL payloads. A single hallucinated mutation can delete a live/fallback theme or purge products.

### Solution Pattern
Implement a lightweight, zero-dependency GraphQL tokenizer/parser inside the PreToolUse hook that inspects the `query` and `variables` arguments of any `graphql_mutation` call:
1. **Unconditionally Blocked Root Mutations**:
   - `themeDelete` (never allow an agent to delete themes via MCP).
2. **Fallback Theme Write Protection**:
   - Read `fallback.themeId` from the canonical `live-theme.json` SSOT.
   - If the mutation is `themeUpdate`, `themePublish`, `themeFilesUpsert`, or `themeFilesDelete` and the query or variables reference the fallback theme ID, **block immediately**.
3. **ID-Bearing Resource Deletions Blocked**:
   - Block `productDelete`, `productDeleteAsync`, `productVariantsBulkDelete`, `collectionDelete`, `pageDelete`, `articleDelete`, `blogDelete`, `menuDelete`, `metafieldDefinitionDelete`, `metaobjectDelete`, `metaobjectDefinitionDelete`, `discountCodeDelete`, `discountAutomaticDelete`, `fileDelete`, `customerDelete`, `orderDelete`, and `draftOrderDelete`.
   - Recommend safe reversible alternatives (`status: ARCHIVED` via `productUpdate`, or closing an issue/draft).

---

## 3. Theme-ID Drift Guard & Cross-Session Deploy Window Lock

### 3.1 Anti-Drift Theme SSOT (`live-theme.json` + `theme:guard`)
- **Failure Mode**: Agents read stale numeric Shopify Theme IDs written in prose inside `AGENTS.md` or `CLAUDE.md` and push changes to deleted or retired themes.
- **Invariant**: Numeric Theme IDs are strictly forbidden in Markdown documentation (enforced by a regex linter in `qa/run-live-theme-guard`). All tools and agents must resolve `live.themeId`, `preview.themeId`, `fallback.themeId`, and `arbeit.themeId` from a single JSON manifest (`live-theme.json`) containing a mandatory `verifiedAt` ISO date and a `retired` dictionary mapping old IDs to their deactivation reasons.

### 3.2 Cross-Session Deploy Window Lock (`.workflow/deploy-fenster.json`)
- **Failure Mode**: While Session A is validating `workflow:preview` before running `workflow:live`, Session B merges a PR into `main`, invalidating the preview state (`LIVE_SOURCE` / `PREVIEW_DRIFT` race condition).
- **Invariant**:
  1. Running `preview` creates `.workflow/deploy-fenster.json` with a 60-minute TTL and a SHA-256 fingerprint of the entire worktree (including untracked files up to 20MB).
  2. While `.workflow/deploy-fenster.json` exists and is unexpired, the Git/GitHub PreToolUse guard rejects `gh pr merge` and `git push origin main` across all other agent sessions.
  3. Running `live` verifies that the current worktree SHA-256 matches the preview fingerprint and removes `.workflow/deploy-fenster.json` in a `finally` block.

---

## 4. 4-File Bulk Metafield Write & Verification Protocol (`shopify-massendaten`)

When writing $>50$ product or variant metafields to Shopify:
1. **`plan.json`**: Every planned `(ownerId, namespace, key, type, value)` entry paired with its explicit data source (`quelle`) and confidence. Never guess metafield types—query `metafieldDefinitions` first (`url` vs `single_line_text_field` vs `list.metaobject_reference`).
2. **`rollback.json`**: Snapshot of prior values from `bulkOperationRunQuery` before mutating (`metafieldsDelete` for previously null fields, `metafieldsSet` with old value for existing fields).
3. **`batches/xNNN.gql` + `write-log.json`**: Batch into ~30KB GraphQL files (8 aliased `metafieldsSet` calls per file, max 25 metafields per call). After execution, run a fresh `bulkOperationRunQuery` export and diff every `(ownerId, namespace, key)` against `plan.json`. Empty `userErrors` alone is not proof of persistence.
4. **`offen.json` (Dead-End Negative Cache)**: Record every SKU/product that could NOT be enriched, the exact reason why, and the required next step. This prevents subsequent agent sessions from burning tokens re-investigating the same missing supplier data.

---

## 5. Token Prefix Validation in Dual-Mode GraphQL Proxies
- Shopify App-Automation tokens (`atkn_...`) work only for webhooks/CI triggers and fail against the GraphQL Admin API with `Invalid API key or access token`.
- Admin API access tokens start with `shpat_...`.
- Always validate token prefixes at client initialization and fail fast with an explicit diagnostic message if an `atkn_` token is supplied where `shpat_` is required.
