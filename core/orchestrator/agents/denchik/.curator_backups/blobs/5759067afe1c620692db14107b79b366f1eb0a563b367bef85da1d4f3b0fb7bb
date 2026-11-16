# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/saap_v1_synthetic_customers_and_funnel_sse_protocol.md"
# purpose: "SAAP v1.0 Synthetic Customer & Funnel Swarm Simulation Architecture, SSE Streaming Protocol & Integration Contracts."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# SAAP v1.0 Synthetic Customer & Funnel Swarm Simulation Protocol

## 1. Context & Architecture (Clean-Room Synthesis)
This protocol formalizes the production-grade integration of **SAAP v1.0 (Synthetic Audience & Persona Generation Engine)** into the DNK OS ecosystem, bridging `packages/swarm_simulation` domain algorithms with `services/dnk_synthetic_customers` and FastAPI `/api/v1/simulation`.

It synthesizes:
1. **Evidence-Grounded Focus Group** principles from `rodaddy/ai-marketing-panel` (MIT):
   - Rich psychological customer dossiers (1,200–1,800 words).
   - Mandatory Dissent / "Hard-No" Seat (cynic / wrong-fit archetypes) to break LLM sycophancy bias.
   - Isolated evaluation waves to eliminate groupthink.
2. **High-Throughput Swarm Simulation** principles from `666ghj/MiroFish` (AGPL-3.0 Clean-Room):
   - Fast Monte Carlo funnel simulations (100–1000 agents in <1s).
   - Price elasticity & trust threshold calculations.
   - Dynamic step drop-off analytics.

---

## 2. Service Directory Anatomy & Manifest Contract
Microservice standard per `DNK-STD-0075`:
```
services/dnk_synthetic_customers/
├── service_manifest.yaml     # ServiceCard v1alpha1 (name, version, endpoints, protocols)
├── __init__.py               # Service export & version
├── src/
│   ├── __init__.py
│   ├── schemas.py            # Pydantic models (GenerateCohortRequest, RunFunnelRequest, etc.)
│   ├── service.py            # SyntheticCustomerService (engine adapter, cache, SSE generator)
│   └── router.py             # APIRouter(prefix="/api/v1/simulation")
├── docs/
│   └── SPECIFICATION.md      # Full architecture specification & formulas
└── tests/
    └── test_service.py       # Unit tests (health, cohort, funnel, streaming)
```

FastAPI Gateway Mount Adapter:
- File: `apps/api/routers/synthetic_customers.py`
- Auto-discovered by `apps/api/main.py` scanner:
  ```python
  from services.dnk_synthetic_customers.src.router import router as synthetic_customers_router
  ```

---

## 3. Server-Sent Events (SSE) Streaming Protocol for Visual Canvas HUD
For real-time Visual Canvas and TaskDNA HUD animations, the service exposes `/api/v1/simulation/funnel/stream`:

- Content-Type: `text/event-stream`
- Cache-Control: `no-cache`
- Connection: `keep-alive`

### Event Sequence:
1. `event: simulation_start`
   - Payload: `{"simulation_id": "sim_...", "total_agents": N, "steps": [...]}`
2. `event: step_progress` (emitted per funnel stage)
   - Payload: `{"simulation_id": "...", "step_id": "step_landing", "step_name": "Landing Page View", "reached": 50, "passed": 42, "drop_off": 8, "conversion_rate": 0.84}`
3. `event: simulation_complete`
   - Payload: `{"simulation_id": "...", "overall_conversion_rate": 0.35, "recommendations": [...]}`

---

## 4. Key Implementation Invariants & Pitfalls

### 4.1. Step ID Invariant in Default Shopify Funnels
- `packages/swarm_simulation/funnel_simulator.py` generates canonical step IDs:
  `["step_landing", "step_pdp", "step_cart", "step_checkout"]`.
- Tests and UI HUD adapters must NOT hardcode arbitrary step identifiers (e.g. `landing_page` or `checkout`), but query `/api/v1/simulation/funnel/default-steps` or inspect `create_default_shopify_funnel()`.

### 4.2. Pydantic ⇄ Domain Dataclass Conversion Layer
- Domain models in `packages/swarm_simulation/models.py` use Python standard dataclasses (`CustomerPersona`, `CohortReport`, `FunnelSimulationResult`).
- FastAPI schemas in `src/schemas.py` use Pydantic `BaseModel`.
- The service adapter MUST explicitly map dictionary outputs (`asdict(obj)`) into Pydantic models or validate nested structures to prevent `AttributeError: 'dict' object has no attribute 'x'` during serialization.

### 4.3. Anti-Sycophancy "Hard-No" Seat Validation
- When `include_dissent_seats=True`, at least one persona in the generated cohort MUST have the archetype `The Skeptic` or `The Cynic` with:
  - `trust_barrier >= 0.85`
  - `price_sensitivity >= 0.9`
  - `objection_profile` targeting verification, fine print, and refund difficulty.
- In funnel simulations, this agent acts as an epistemic stress-test on conversion metrics.
