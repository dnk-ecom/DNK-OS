# --- DNK-MRH-HEADER ---
# mrh_id: "references/video_retention_auditor_and_fastapi_testclient_protocol.md"
# purpose: "Video Retention Auditor Invariants & FastAPI TestClient Lifespan Scoping Protocol"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# Video Retention Auditor & FastAPI TestClient Lifespan Protocol

## 1. FastAPI TestClient Scope Invariant (Middleware Astack Trap)

### Problem
When writing isolated integration tests for FastAPI service routers, passing an `APIRouter` instance directly into Starlette's `TestClient` fails:
```python
# FAILS:
from fastapi.testclient import TestClient
from services.dnk_video_retention_auditor.src.router import router

client = TestClient(router)
# Result: AssertionError: fastapi_middleware_astack not found in request scope
```

### Root Cause
Starlette/FastAPI's ASGI request scope relies on lifespan context and middleware stacks (`fastapi_middleware_astack`, exception handlers, routing state) that are exclusively initialized on the `FastAPI` application root, not on an unmounted `APIRouter`.

### Mandatory Solution
Always wrap routers in an explicit test application instance:
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from services.dnk_video_retention_auditor.src.router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)
```

---

## 2. Video Retention Auditor Engine Architecture (TASK-DNK-RETENTION-20260913-001)

### Domain Thresholds & Invariants
1. **Zero-Latency Speech Compliance**:
   - Speech start latency threshold: `speech_start_latency <= 0.20s`.
   - If audio speech starts > 0.20s from frame 0, apply dynamic penalty: `(latency - 0.20) * 20.0`.
2. **Opening Pattern Interrupt (First 1.8s)**:
   - Must detect at least one scene cut, 1.2x punch-in zoom, or dynamic on-screen motion within the first 1.8s.
   - Missing interrupt triggers recommendation and deducts 20 points from the hook strength score.
3. **Curiosity Gap Linguistic Triggers**:
   - Evaluates linguistic gap triggers across English, Ukrainian, and Russian:
     - EN: `"secret"`, `"why"`, `"stop doing"`, `"how to"`, `"mistake"`
     - UK: `"чому"`, `"як"`, `"секрет"`, `"зупиніться"`, `"помилка"`
     - RU: `"почему"`, `"как"`, `"секрет"`, `"ошибка"`, `"хватит"`
4. **Hardware & Conversion Evaluator**:
   - **Action-to-Face Ratio**: Ideal target ≥ 0.70 (product/code in action vs talking head).
   - **Mechanism of Action**: Flag indicating whether internal mechanics or architecture are demonstrated visually.
   - **Commercial CTA Friction**:
     - Early CTA (< 30% video progress): High friction (75/100).
     - Mid CTA (30% - 60% progress): Medium friction (45/100).
     - Late CTA (> 60% progress after delivering value): Low friction (20/100).
5. **Composite Retention Score Synthesis**:
   $$\text{Retention} = 0.35 \times \text{Hook} + 0.30 \times \text{Pacing} + 0.20 \times \text{Acoustic} + 0.15 \times \text{Hardware}$$
6. **Micro-Clip Discovery**:
   - Segments with pace density $\ge 18\text{ cuts/min}$ are flagged as high-retention candidates for short-form repurposing.
