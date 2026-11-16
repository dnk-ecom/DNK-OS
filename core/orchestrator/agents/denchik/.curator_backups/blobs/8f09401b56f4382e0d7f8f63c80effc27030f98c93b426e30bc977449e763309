# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/ai_marketing_panel_and_synthetic_focus_groups.md"
# purpose: "Assimilation patterns, Comparative Audit & Evidence-Grounded Synthetic Customer Panel Architecture from rodaddy/ai-marketing-panel & 666ghj/MiroFish."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Evidence-Grounded Synthetic Customer Panel & Swarm Simulation Architecture

## 1. Upstream Archetype Profiles & Dual-Track Licensing
| Dimension | `rodaddy/ai-marketing-panel` | `666ghj/MiroFish` |
|---|---|---|
| **Repository Slug** | `rodaddy/ai-marketing-panel` | `666ghj/MiroFish` |
| **Stars / Community** | ~1k+ ⭐ (Specialized Marketing Focus) | 72.4k+ ⭐ (Large-Scale Swarm Intelligence) |
| **SPDX License** | `MIT` ➔ **Track 1 Direct Assimilation** | `AGPL-3.0` ➔ **Track 2 Clean-Room Reverse Engineering** |
| **Runtime Architecture** | Isolated Wave Panels (5–15 slots) | Social Interaction Graph (CAMEL-OASIS, 100–1000+) |
| **Primary Artifact Tested** | Copywriting, Headlines, Pricing, Landing Pages | Market Events, Social Narratives, Public Sentiments |
| **Data Grounding** | Support Tickets, Sales Transcripts (Evidence) | PRDs, Web URLs, Seed Entity Graphs |
| **Execution Speed** | 10–30s per wave (LLM-heavy) | Multi-minute iterative rounds |

---

## 2. Core Architectural Invariants from `ai-marketing-panel` (MIT)

### 2.1. Evidence-Grounded Dossiers (1,200–1,800 words)
- Synthetic personas must never be shallow demography cards (e.g. "Mark, 35, Tech Guy").
- Every dossier is synthesized from concrete data artifacts:
  1. Real customer support inquiries & common complaints.
  2. Sales call transcripts & documented objections from lost deals.
  3. Trust requirements, budget constraints, and specific decision triggers.

### 2.2. The Mandatory Dissent / "Hard-No" Seat (Anti-Sycophancy)
- Default LLM agents suffer from **"yes-man" sycophancy bias** (rating mediocre copy 8/10).
- **Rule**: Every focus group panel MUST allocate at least 1–2 seats to explicit hard dissenters:
  - *The Cynic*: Assumes every marketing claim is inflated; demands third-party verification.
  - *The Wrong-Fit*: Has constraints that make purchasing objectively irrational.
- If a panel returns 100% agreement or conversion, the test is treated as compromised/invalid.

### 2.3. Strict Context Isolation Waves (Anti-Groupthink)
- Personas must evaluate marketing material in strictly isolated prompt/agent contexts.
- No agent may observe another agent's rating or reaction before submitting their own.
- Synthesis happens post-evaluation via an independent `SynthesizerAgent`, which preserves conflicting opinions rather than smoothing them into an average.

### 2.4. Closed-Loop Rewrite & Retest Cycle
- Personas output structured objections (`objection_type`, `hesitation_score`, `unmet_expectation`).
- Copywriter agent ingests the specific objections, rewrites the copy/headline/pricing anchor.
- The revised asset is immediately re-evaluated against the exact same cohort to measure conversion lift.

---

## 3. Synergy & DNK OS Clean-Room Synthesis (`packages/swarm_simulation`)

DNK OS unites the deep qualitative grounding of `ai-marketing-panel` with the high-scale statistical efficiency inspired by `MiroFish`:

```
┌─────────────────────────────────────────────────────────────────┐
│                      DNK OS Simulation Matrix                   │
├───────────────────────────────┬─────────────────────────────────┤
│    Statistical Layer (0.1s)   │    Qualitative Layer (10-30s)   │
│   (packages/swarm_simulation) │  (services/dnk_synthetic_cust)  │
├───────────────────────────────┼─────────────────────────────────┤
│ • 100–1000 stochastic agents  │ • 5–15 deep LLM dossiers        │
│ • Price elasticity modeling   │ • "Hard-No" dissenting seats    │
│ • Monte Carlo funnel drop-off │ • Unfiltered objection quotes   │
│ • Instant CI test pass rate   │ • Automated copy rewrite loop   │
└───────────────────────────────┴─────────────────────────────────┘
```

### 3.1. Integration with DNK OS Pipelines
1. **`dnk_one_click_product_launch`**:
   - Pre-flight simulation before deploying Shopify stores.
   - Simulates 100 stochastic buyers across Landing -> Product Page -> Cart Drawer -> Checkout.
   - Recommends Liquid schema tweaks (e.g., adding trust badges, adjusting compare-at price).
2. **`dnk_video_ai_creator` / Video Retention**:
   - Evaluates video hook transcripts against simulated attention-span personas.
   - Flags drops in first 3 seconds before Remotion rendering.
3. **SAAP v1.0 Service (`services/dnk_synthetic_customers/`)**:
   - Standardized FastAPI endpoint for cohort generation and funnel simulation.
   - Real-time SSE / WebSocket streaming into Visual Canvas HUD.

---

## 4. Production Implementation & Verification (SAAP v1.0)

### 4.1. Implemented Components
- **Microservice Core**: `services/dnk_synthetic_customers/` with `service_manifest.yaml` (DNK OS ServiceCard v1alpha1), `src/schemas.py`, `src/service.py`, `src/router.py`, and `docs/SPECIFICATION.md`.
- **API Gateway Mounting**: `apps/api/routers/synthetic_customers.py` exposing `/api/v1/simulation`.
- **Verified Endpoints**:
  - `GET /api/v1/simulation/health` -> Service health, engine identifier, active simulations count.
  - `POST /api/v1/simulation/cohort/generate` -> Generates personas with mandatory dissent seats.
  - `POST /api/v1/simulation/funnel/run` -> Runs full funnel Monte Carlo simulation with drop-offs and bottleneck identification.
  - `POST /api/v1/simulation/funnel/stream` -> Server-Sent Events (`text/event-stream`) streaming live funnel progression.
  - `GET /api/v1/simulation/funnel/default-steps` -> Inspects default Shopify funnel step IDs (`step_landing`, `step_pdp`, `step_cart`, `step_checkout`).

### 4.2. Verification & Test Suite
- `pytest services/dnk_synthetic_customers/tests/test_service.py tests/simulation/test_api_endpoints.py` -> 9/9 passed.
- Total domain suite: `pytest tests/simulation/` -> 20/20 passed.

