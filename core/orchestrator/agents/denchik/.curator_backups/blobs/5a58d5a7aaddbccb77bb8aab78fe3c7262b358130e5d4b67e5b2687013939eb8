# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/references/dual_track_store_engine_and_harness_convergence.md"
# purpose: "Reference architecture and specification for Dual-Track Shopify Store Engine with Harness Convergence."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-30"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🏗️ Dual-Track Shopify Store Engine Architecture

## 1. Executive Summary
The Dual-Track Store Engine (`services/dnk_shopify/studio/engine/dual_track_store_engine.py`) unifies reference page adaptation and from-scratch conversion rate optimization (CRO) into a single deterministic delivery pipeline. Regardless of creation vector, both tracks converge into an invariant-guaranteed `HarnessContract` validated by a zero-tolerance gate (`GateVerdict`).

```
                      [DualTrackStoreRequest]
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       Track 1: clone_and_restyle     Track 2: generative_cro
       - DOM & CSS capture            - High-converting CRO sections
       - Brand token restyling        - Structured PDP architecture
       - Script triage (Dynamics)     - Invariant enforcement
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                     [Single Convergence Point]
                      HarnessContract (SHA-256)
                                 │
                                 ▼
                     [Ralph Convergence Gate]
                      evaluate_gate() -> GateVerdict
                      (visual_pass == True, open_deltas == 0)
```

---

## 2. Track Breakdown

### Track 1: Clone & Restyle (`_run_clone_and_restyle`)
- **Use Case**: Replicating a high-performing competitor/donor landing page while rebranding it to client design tokens.
- **Capture Stage**:
  1. Captures DOM tree and section boundaries from donor HTML.
  2. Extracts existing color palettes and font styles.
  3. Deconstructs sections into Shopify OS 2.0 sections (`sections/*.liquid`, `templates/index.json`).
- **Restyling Stage**:
  1. Overwrites extracted styles with client `DesignTokens` (primary, secondary, accent, background, font headings, font body).
  2. Compiles `config/settings_data.json` with client design system tokens.
- **Dynamics Triage (`DynamicsContract`)**:
  - Classifies every interactive or dynamic script on the donor page:
    - `REBUILD`: Recreate natively via Liquid + Alpine.js / Tailwind.
    - `DEFER`: External vendor widget to load via Theme App Extension / App Block.
    - `DROP`: Redundant third-party analytics or tracker scripts.

### Track 2: Generative CRO (`_run_generative_cro`)
- **Use Case**: Generating an optimized e-commerce landing / product store from scratch based on product USP and proven conversion architecture.
- **Structural Sections**:
  1. **Announcement Bar**: Urgency & shipping threshold incentives.
  2. **Hero Header**: High-clarity H1, primary CTA button, benefit bullet points.
  3. **Social Proof & Trust Badges**: Verified customer reviews, press mentions, guarantee seal.
  4. **Product Showcase (PDP)**: Main image gallery, price anchors, sticky ATC trigger, variant selector.
  5. **Comparison Matrix**: Us vs Them tabular proof.
  6. **Interactive FAQ**: Accordion addressing primary objection vectors.
  7. **Sticky ATC Banner**: Mobile-first persistent purchase button.
- **Design Injection**: Directly binds `DesignTokens` into theme presets and section settings.

---

## 3. Harness Convergence Contracts

Located in `services/dnk_shopify/schemas/harness_contracts.py`:

```python
class HarnessContract(BaseModel):
    store_id: str
    target_theme: str
    sections: List[SectionContract]
    dynamics: DynamicsContract
    contract_sha256: str

class SectionContract(BaseModel):
    section_id: str
    section_type: str
    must_match: List[CheckRule]
    status: str = "pending"

class DynamicsItem(BaseModel):
    id: str
    selector: str
    purpose: str
    classification: DynamicsClassification  # REBUILD | DEFER | DROP
    status: str = "identified"

class GateVerdict(BaseModel):
    is_ready: bool
    visual_pass: bool
    open_deltas: int
    deltas: List[GateDelta]
    evaluated_at: str
    target_theme: str
```

---

## 4. Gate Verification Protocol (`evaluate_gate`)
Release readiness is deterministically enforced:
1. `contract_sha256` integrity check against rendered template outputs.
2. Section presence and rule satisfaction: every `CheckRule` in `must_match` is evaluated.
3. Strict pass criteria:
   ```python
   is_ready = visual_pass and (len(open_deltas) == 0)
   ```
4. Emits `visual-deltas.md` detailing any visual regressions or missing elements.

---

## 5. Execution Interfaces & Tooling

### 5.1 Standalone CLI Runner (`harness_runner.py`)
Run headless store generation and export the complete Harness Evidence Pack (`contract.json`, `dynamics.json`, `visual-deltas.md`, `gate.json`):
```bash
python services/dnk_shopify/tools/harness_runner.py \
  --mode generative_cro \
  --name "Brand Store" \
  --niche "tech_apparel" \
  --output-dir "artifacts/harness_pack"
```

### 5.2 FastMCP Server Tools (`services/dnk_shopify/server.py`)
Swarm agents and visual orchestrators can invoke:
- `dual_track_synthesize_store(mode, store_name, niche, donor_html, brand_tokens_json)`
- `evaluate_harness_gate(contract_json, rendered_files_json)`

### 5.3 REST API Endpoints (`apps/api/routers/shopify.py`)
- `POST /api/v1/shopify/dual-track/synthesize`: JSON payload generating zip bundle & contract manifest.
- `POST /api/v1/shopify/dual-track/gate`: Validates rendering against contract with 0-delta enforcement.

---

## 6. Verification & Testing
- Unit tests: `tests/shopify/test_dual_track_store_engine.py`
  - `test_generative_cro_track`: verifies CRO section synthesis, settings generation, and contract creation.
  - `test_clone_and_restyle_track`: verifies DOM parsing, token substitution, and dynamics inventory.
  - `test_harness_convergence_evaluation_pass_and_fail`: verifies gate pass with 0 deltas and rejection on missing sections.
  - `test_fastmcp_tools_dual_track`: tests MCP registration and payload execution.
  - `test_harness_runner_cli`: verifies subprocess execution of the CLI runner and evidence pack export.
