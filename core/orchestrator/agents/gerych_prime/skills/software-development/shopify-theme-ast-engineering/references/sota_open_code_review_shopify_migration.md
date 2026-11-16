# 🛡️ SOTA Open-Code-Review Pipeline for Shopify OS 2.0 Theme Migration

This reference outlines the integration of the assimilated **Alibaba Open-Code-Review (OCR)** engine (`core/orchestrator/`) into the Shopify OS 2.0 / Horizon Tinker theme migration pipeline, guaranteeing zero regressions, no 404 customizer redirects, and zero syntax crashes.

---

## 🏗️ The 4 Core Assimilated Components in Action

```
[Legacy Monolith / Diff] ──> [OCRDelegationEngine]
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
   [Chunk 1: Routing]      [Chunk 2: Blocks]       [Chunk 3: Config]
   templates/*.json        blocks/*.liquid         config/*.json
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    ▼
                      [CodeReviewRuleSniffer]
                      (SHOPIFY-001 ... SHOPIFY-005)
                                    ▼
                      [relocate_comment Algorithm]
                                    ▼
                      [AuditStateMachine Gates]
                      (0 BLOCKING Defects Required)
                                    ▼
                   [100% Green Verified Theme ZIP]
```

---

## 1. Automated Rule Sniffing (`CodeReviewRuleSniffer`)

During migration from Vintage / Sections 1.0 to OS 2.0 / Horizon Tinker, five fatal invariants must be enforced:

| Rule ID | Language | Severity | Failure Condition & Impact |
|---|---|---|---|
| `SHOPIFY-001` | `liquid` | `BLOCKING` | **Deprecated `{% include %}` Tag**: Leaks variables across parent scopes. Must use `{% render 'snippet', var: val %}` with explicit parameters. |
| `SHOPIFY-002` | `liquid` | `BLOCKING` | **Missing / Malformed `{% schema %}` JSON**: If section or block schema is invalid JSON (including illegal trailing commas before `}` or `]`), Shopify Theme Customizer crashes with a fatal error. |
| `SHOPIFY-003` | `shopify_json` | `BLOCKING` | **Undeclared Block Type in Section Schema**: If a JSON template (`templates/*.json`) references a block `"type"` under a section that is NOT declared in that section's schema `blocks: [...]`, Shopify fails rendering and redirects to 404 fallback ("This page doesn't have any sections"). |
| `SHOPIFY-004` | `liquid` | `WARNING` | **Monolithic Template Migration**: Monolithic `templates/*.liquid` files must be converted into section-referenced `templates/*.json`. |
| `SHOPIFY-005` | `liquid` | `BLOCKING` | **Missing Theme Layout Content Hooks**: `layout/theme.liquid` must contain `{{ content_for_header }}` and `{{ content_for_layout }}`. |
| `SHOPIFY-006` | `liquid` | `BLOCKING` | **Illegal Trailing Commas in `{% schema %}` Blocks**: Trailing commas before `}` or `]` violate strict RFC JSON and break Shopify Theme Customizer schema parser. Must sanitize via regex `re.sub(r',(\\s*[}\\]])', r'\\1', schema)` and verify with `json.loads()`. |

---

## 2. Token Chunking & Parallel Delegation (`OCRDelegationEngine`)

A full theme diff comprises 50–200 files and 20k–50k lines of code. Monolithic LLM context windows suffer cognitive rot and hallucinate when analyzing the diff all at once.

`OCRDelegationEngine` splits the diff into 4 semantic domain chunks:
1. **Templates & Routing Chunk (`templates/*.json`)**:
   - Validates existence of `404.json` and customer account flows (`customers/*.json`).
   - Ensures all `sections` and `order` keys are consistent and valid.
2. **Product Monolith & Blocks Chunk (`sections/`, `blocks/`)**:
   - Inspects `main-product.liquid` decomposition into modular `blocks/tinker-dnk-*.liquid`.
   - Confirms `{{ block.shopify_attributes }}` presence on all block containers.
3. **Theme Settings & Security Chunk (`config/*.json`)**:
   - Merges conversion settings, currency, and store protection into `settings_schema.json`.
   - Verifies `current` object integrity in `settings_data.json`.
4. **Snippets & Visual Assets Chunk (`snippets/`, `assets/`)**:
   - Checks variable scope in `snippets/*.liquid`.
   - Ensures CSS/JS bundle integrity without namespace collisions.

---

## 3. Algorithmic Comment Relocation (`relocate_comment`)

When refactoring a 24,000-line monolithic `main-product.liquid` into atomic blocks, line numbers shift dramatically (>1,000 lines).
Standard diff linters point to stale or incorrect line numbers.
`relocate_comment` uses fuzzy Levenshtein distance and contextual line matching:
- Analyzes surrounding 3 lines before and after.
- Re-anchors code review annotations and automated patches to the exact new location.

---

## 4. Fail-Closed Quality Gates (`AuditStateMachine`)

The `AuditStateMachine` enforces strict transition gates:
```
PENDING ──> IN_REVIEW ──> (Any BLOCKING defects?)
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
              YES                             NO
               │                              │
         BLOCKED_DEFECTS                  PASSED_GATE
   (Export to ZIP physically halted)  (Theme ZIP certified)
```

No theme ZIP is built or deployed if a `BLOCKING` defect exists. This completely prevents shipping themes that produce 404 errors or editor lockouts in Shopify admin.
