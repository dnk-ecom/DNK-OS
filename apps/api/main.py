# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/main.py"
# purpose: "FastAPI Application Entry Point for DNK OS: Microkernel v2.5.0, Action Bus, and Health Telemetry."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.5.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routers.kernel_router import router as kernel_router, get_kernel
from apps.api.routers.swarm_live_ws import router as swarm_live_router
from apps.api.routers.taskboard_canvas_router import router as taskboard_canvas_router
from apps.api.routers.actions_router import router as actions_router
from apps.api.routers.client_cockpit_router import router as client_cockpit_router
from apps.api.routers.node_tasks_router import router as node_tasks_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dnk.api")

app = FastAPI(
    title="DNK OS Microkernel API",
    version="2.5.0",
    description="Sovereign AI Core API: Thought-to-Plan, Spatial Canvas, Fan-In Aggregation, Quarantine Sentinel, and SCONES FTS5 Memory.",
)

# CORS Middleware for React Flow Web Shell & Browser Extensions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Microkernel v2.5.0 Routers
app.include_router(kernel_router)
app.include_router(swarm_live_router)
app.include_router(taskboard_canvas_router)
app.include_router(actions_router)
app.include_router(client_cockpit_router)
app.include_router(node_tasks_router)


@app.get("/health", tags=["Telemetry"])
@app.get("/api/v1/health", tags=["Telemetry"])
def health_check():
    """Liveness probe for DNK OS runtime."""
    return {"status": "ok", "service": "dnk-os-api", "version": "2.5.0"}


@app.get("/api/v1/status", tags=["Telemetry"])
def status_overview():
    """System overview and active subsystems status."""
    kernel = get_kernel()
    if hasattr(kernel, "get_system_status"):
        return kernel.get_system_status()
    elif hasattr(kernel, "get_status"):
        return kernel.get_status()
    return {"status": "ok", "kernel": "active"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
