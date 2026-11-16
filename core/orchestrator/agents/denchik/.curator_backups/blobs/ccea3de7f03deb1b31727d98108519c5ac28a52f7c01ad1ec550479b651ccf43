# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/agent_native_shopify_os_and_dimensional_cart_guards.md"
# purpose: "Condensed SOTA architecture patterns from kontakt755/teppich-paradies-shopify-ai: 0.01-unit dimensional pricing, Liquid cart anti-tampering, GraphQL MCP mutation firewall, deploy-window locking, and zero-app room visualizer."
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-19"
# author: "Gerych (Hermes Prime)"
# --- END DNK-MRH-HEADER ---

# Agent-Native Shopify OS 2.0, Dimensional Cart Guards & MCP Mutation Firewalls

Assimilated from `kontakt755/teppich-paradies-shopify-ai` (Track 2 — Clean-Room Architecture Synthesis; local clone in `../SHOPIFY/DNKShopify/DNKEcom/DNKEcom Theme Dev/Git_Repos_Shopify/_GitHub_Shopify_Themes/teppich-paradies-shopify-ai`).

---

## 1. Zero-App Dimensional Pricing (`0.01 m²` Unit Metafield + Anti-Tampering Cart Guard)

### 1.1 The `custom.preis_pro_001_qm` Integer-Cart Workaround
- **Problem**: Standard Shopify carts (without Shopify Plus Cart Transform functions or paid price-calculator apps) only accept integer quantities (`line_price = variant.price * quantity`), forcing fractional dimensions (e.g., `6.66 m²`) to round up and overcharge buyers.
- **Solution**: Set variant price to represent `0.01 m²` (or `0.01` linear meters) and mark the product with `custom.preis_pro_001_qm = true`. Any centimeter dimension (`width_cm * length_cm / 100`) converts to an exact integer unit count (`quantity`) in `/cart/add.js` while storing human-readable dimensions in line-item properties (`_laenge_cm`, `_breite_cm`, `_flaeche_m2`, `_form`).
- **Smart Width Optimization**: Compare the customer's exact cut (`Raummaß` / `Wunschmaß`) against full-roll widths (`Meterware`: 200/300/400/500 cm) across live variant prices and automatically suggest the wider roll when its lower per-m² rate makes the total order cheaper.

### 1.2 Server-Side Liquid & Email Anti-Tampering Guard (`tp-cart-gruppe.liquid`)
- **Attack Vector**: A buyer can inspect `/cart/change.js` in DevTools and lower `quantity` from `600` (`6.00 m²`) to `75` (`0.75 m²`) while leaving `properties["Maße"] = "200 x 300 cm"`, paying a fraction of the price for a large custom cut.
- **Defense Invariant**:
  1. Never trust the display property `_flaeche_m2` during verification — always recompute required integer units directly from raw dimensional properties (`_laenge_cm`, `_breite_cm`, `_form`) inside pure Liquid (`snippets/tp-cart-gruppe.liquid` and order confirmation email `bestellmail-masspruefung`).
  2. Support all geometric shapes deterministically:
     - Rectangle / Square: `ceil(width_cm * length_cm / 100)`
     - Circle: `ceil(3.14159 * r * r / 100)`
     - Oval: Ramanujan perimeter & area approximation for edging (`Kettelservice`) and surface units.
  3. If `item.quantity < expected_units`, physically disable the Checkout submit button in the cart template and render a red tamper alert banner in the merchant/customer order confirmation email.

### 1.3 Physical Roll Inventory Sync via Hidden Bundle Parent (`rollenbestand.md`)
- When the same physical warehouse roll is sold both as standard roll cuts (`Meterware`) and custom room dimensions (`Raummaß`), maintain a single hidden master product (`Rollenbestand`) tracking available centimeters and bind storefront variants via `productBundleComponent` so every custom cut deducts exact linear centimeters from the shared roll.

---

## 2. Deterministic Agent Governance & Shopify MCP Firewalls

### 2.1 Zero-Dependency GraphQL Mutation Firewall (`shopify-mcp-guard.mjs`)
- **Problem**: Granting agents `mcp__*__graphql_mutation` bypasses Bash command guards.
- **Solution**: Implement a lightweight GraphQL document tokenizer/lexer inside the PreToolUse hook that inspects every `mutation` operation before execution:
  - Hard-block `themeDelete` and any mutation targeting the emergency fallback `themeId` stored in `domains/shopify/live-theme.json`.
  - Hard-block destructive ID-bearing deletions (`productDelete`, `productVariantsBulkDelete`, `collectionDelete`, `menuDelete`, `discountCodeDelete`, `fileDelete`) while permitting safe catalog updates (`productVariantsBulkUpdate`, `metafieldsSet`, status archival).

### 2.2 Anti-Drift Theme SSOT (`live-theme.json` + `run-live-theme-guard.mjs`)
- Never hardcode numeric Shopify Theme IDs inside `AGENTS.md`, `CLAUDE.md`, or skill files (agents trust stale prose and push to deleted themes).
- Store the active live and fallback theme IDs in a single machine-verified JSON file (`live-theme.json` with `verifiedAt` timestamp) and run a regex guard across all markdown/instruction files to reject hardcoded 12-digit theme IDs.

### 2.3 Cross-Session Deploy Window Lock (`deploy-fenster.mjs`)
- Running `workflow:preview` writes `.workflow/deploy-fenster.json` (60-minute TTL) with a SHA-256 fingerprint of the entire git worktree (including untracked files).
- While a deploy window is open, the `git-gh-guard` hook blocks `gh pr merge` and `git push origin main` across all other concurrent agent sessions until `workflow:live` verifies the worktree hash and closes the window.

### 2.4 4-File Bulk Metafield Mutation Protocol (`shopify-massendaten`)
- Every bulk Shopify catalog write must generate 4 artifacts before mutating live data:
  1. `plan.json` — planned values paired with concrete provenance/evidence.
  2. `rollback.json` — pre-mutation snapshot for 1-command restoration.
  3. `batches/xNNN.gql` — chunked GraphQL mutations (~30 KB, 8 aliased `metafieldsSet` calls per batch).
  4. `offen.json` — negative cache of unresolvable items so subsequent agent sessions never waste tokens re-investigating known dead ends.

---

## 3. Zero-App Client-Side Interactive Storefront Components

### 3.1 5KB HTML5 Canvas / WebGL Room Visualizer (`tp-boden-raumansicht.js`)
- Perspective floor texture projection inside a 5 KB zero-dependency Vanilla JS module (`blocks/tp-boden-raumansicht.liquid` + `assets/tp-boden-raumansicht.js`).
- Supports preset room scenes or local customer photo uploads processed 100% in browser memory (`FileReader` / `URL.createObjectURL`) with zero server upload (strictly GDPR-compliant), honoring physical pattern repeat (`rapport_breite_cm`) and 90° tile/roll rotation.

### 3.2 Server-Rendered JSON Product Finder Index (`tp-boden-finder-daten.liquid`)
- Instead of paid Quiz SaaS apps or heavy Storefront GraphQL queries, render a dedicated data section (`tp-boden-finder-daten.liquid`) that serializes collection products and technical metafields (`nutzungsklasse`, `fussbodenheizung`, `wasserfest`, `flormaterial`) into a compact JSON payload consumed by a 5-step client-side filter and room-budget calculator.

---

## 4. Node.js ESM Path Pitfall in Directories with Spaces
- When running Node.js (`v20–v24`) test suites or build scripts inside directory trees containing spaces (e.g., `DNKEcom Theme Dev`), NEVER resolve local paths via `new URL('../templates', import.meta.url).pathname` — URL percent-encoding leaves `%20` in the string and causes `fs.readdirSync` / `fs.readFileSync` to throw `ENOENT`. Always wrap `import.meta.url` with `fileURLToPath(new URL(..., import.meta.url))` from `node:url`.
