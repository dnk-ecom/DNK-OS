# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_os/core/agent.py"
# purpose: "DNKAgent with full Multi-Agent Core (Supervisor + Worker + Checkpointer + HITL Approval Gate) and Health/Metrics API"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.2.0"
# updated_at: "2026-08-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""
DNKAgent Core Integration.

Provides unified interface orchestrating:
- DNKSupervisor (LangGraph state graphs)
- DNKWorker (Multi-adapter task executor)
- DNKCheckpointer (Persistence)
- DNKApprovalGate (Human-in-the-Loop approval workflows)
- HealthChecker (System health monitoring)
- MetricsCollector (Performance and utilization metrics)
"""

import time
from typing import Any, Callable, Dict, List, Optional
from dnk_os.core.checkpointer import DNKCheckpointer, create_checkpointer
from dnk_os.core.supervisor import DNKSupervisor
from dnk_os.core.worker import DNKWorker
from dnk_os.core.approval_gate import DNKApprovalGate, ApprovalStatus
from dnk_os.core.health import HealthChecker
from dnk_os.core.metrics import MetricsCollector
from dnk_os.core.streaming import StreamingService
from dnk_os.core.session import SessionManager
from dnk_os.utils.logging import setup_logging


class DNKAgent:
    """
    DNK OS Agent with full Multi-Agent Core + HITL.
    
    Orchestrates:
    - DNKSupervisor for task delegation and routing
    - DNKWorker (Герич) for multi-adapter execution
    - DNKCheckpointer for state persistence
    - DNKApprovalGate for human-in-the-loop validation of sensitive actions
    """
    
    def __init__(
        self,
        name: str = "DNKAgent",
        checkpointer_backend: str = "memory",
        checkpointer: Optional[DNKCheckpointer] = None,
        supervisor: Optional[DNKSupervisor] = None,
        worker: Optional[DNKWorker] = None,
        approval_gate: Optional[DNKApprovalGate] = None,
        **kwargs: Any
    ):
        """Initialize DNKAgent with core components."""
        self.name = name
        self.checkpointer = checkpointer or create_checkpointer(backend=checkpointer_backend)
        self.supervisor = supervisor or DNKSupervisor(
            name="Antigravity",
            checkpointer=self.checkpointer,
            **kwargs
        )
        self.worker = worker or DNKWorker(name="Герич", **kwargs)
        self.approval_gate = approval_gate or DNKApprovalGate(
            checkpointer=self.checkpointer,
            **kwargs
        )
        self._setup_orchestration()

    def _setup_orchestration(self) -> None:
        """Register worker and setup supervisor graph."""
        self.supervisor.register_worker(
            worker_name=self.worker.name,
            worker_config={
                "name": self.worker.name,
                "role": "Primary Worker",
            },
            capabilities=self.worker.get_capabilities()
        )
        self.supervisor.create_state_graph()
        self.supervisor.compile()

    def execute_task(self, task: str, thread_id: str = "default_thread", **kwargs: Any) -> Dict[str, Any]:
        """Delegate task through supervisor orchestration."""
        return self.supervisor.delegate_task(task=task, thread_id=thread_id, **kwargs)

    def execute_worker_direct(self, task: str, task_type: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Execute task directly using worker without supervisor graph."""
        return self.worker.execute_task(task=task, task_type=task_type, **kwargs)

    def execute_sensitive_action(
        self,
        action: str,
        action_function: Callable[..., Any],
        context: Dict[str, Any],
        thread_id: str = "default_thread",
        auto_approve_actions: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute sensitive action with approval gate.
        
        Args:
            action: Action name (e.g. "delete_agent", "deploy")
            action_function: Callable to execute once approved
            context: Context dictionary
            thread_id: Thread ID
            auto_approve_actions: List of auto-approved actions
            **kwargs: Extra parameters
            
        Returns:
            Result dict with status, output, and approval_status
        """
        return self.approval_gate.execute_with_approval(
            action=action,
            action_function=action_function,
            context=context,
            thread_id=thread_id,
            auto_approve_actions=auto_approve_actions,
            **kwargs
        )

    def get_state(self, thread_id: str = "default_thread") -> Optional[Dict[str, Any]]:
        """Retrieve state from persistence checkpointer."""
        return self.checkpointer.get(thread_id=thread_id)


# Global monitoring & logging singletons
health_checker = HealthChecker()
metrics = MetricsCollector()
streaming_service = StreamingService()
session_manager = SessionManager()
logger = setup_logging(level="INFO")

# FastAPI Application instance for HTTP / Docker serving
try:
    from fastapi import FastAPI, HTTPException, Request

    app = FastAPI(title="DNK OS Multi-Agent Core API", version="2.2.0")

    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable[..., Any]):
        """Log all requests with structured metrics."""
        start_time = time.time()
        
        response = await call_next(request)
        
        latency_ms = (time.time() - start_time) * 1000
        metrics.record_request(latency_ms=latency_ms)
        
        if response.status_code >= 400:
            metrics.record_error()
        
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {latency_ms:.2f}ms")
        
        return response

    @app.get("/health")
    def health_check() -> Dict[str, Any]:
        """Health check endpoint for container and monitoring probes."""
        return health_checker.get_full_health()

    @app.get("/metrics")
    def get_metrics_endpoint() -> Dict[str, Any]:
        """Metrics endpoint."""
        return metrics.get_metrics()

    @app.get("/stream/task/{task_id}")
    async def stream_task(task_id: str, worker: str = "Герич"):
        """
        Stream task execution in real-time.
        
        Args:
            task_id: Task identifier
            worker: Worker name
            
        Returns:
            SSE stream
        """
        async def generate():
            async for event in streaming_service.stream_task_execution(
                task_id=task_id,
                worker_name=worker,
                task_description=f"Executing task {task_id}"
            ):
                yield event
        
        return streaming_service.create_sse_response(generate())

    @app.post("/execute/stream")
    async def execute_task_streaming(request: Request):
        """
        Execute task with streaming output.
        
        Args:
            request: Request with task description
            
        Returns:
            SSE stream with task output
        """
        data = await request.json()
        task = data.get("task", "Default task")
        
        async def generate():
            async for event in streaming_service.stream_worker_output(
                worker_name="Герич",
                output=f"Executing task: {task}\nResult: Task completed successfully!",
                stream_mode="tokens"
            ):
                yield event
        
        return streaming_service.create_sse_response(generate())

    @app.get("/stream/example")
    async def stream_example():
        """
        Example streaming endpoint.
        
        Returns:
            SSE stream with example text
        """
        async def generate():
            text = "This is an example of token-level streaming in DNK OS Multi-Agent Core."
            async for event in streaming_service.stream_tokens(text, tokens_per_second=30):
                yield event
        
        return streaming_service.create_sse_response(generate())

    @app.post("/session/create")
    async def create_session(request: Request):
        """Create new session."""
        user_id = request.query_params.get("user_id")
        metadata = None
        try:
            body = await request.json()
            if isinstance(body, dict):
                user_id = body.get("user_id", user_id)
                metadata = body.get("metadata", None)
        except Exception:
            pass
        session_id = session_manager.create_session(user_id=user_id, metadata=metadata)
        return {"session_id": session_id, "status": "created"}

    @app.get("/session/stats")
    async def get_session_stats():
        """Get session statistics."""
        return session_manager.get_session_stats()

    @app.post("/session/cleanup")
    async def cleanup_sessions():
        """Cleanup expired sessions."""
        cleaned = session_manager.cleanup_expired_sessions()
        return {"cleaned_sessions": cleaned}

    @app.get("/sessions")
    async def list_sessions(user_id: Optional[str] = None, limit: int = 100):
        """List sessions."""
        sessions = session_manager.list_sessions(user_id=user_id, limit=limit)
        return {"sessions": sessions, "count": len(sessions)}

    @app.get("/session/{session_id}")
    async def get_session(session_id: str):
        """Get session data."""
        session_data = session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_data

    @app.post("/session/{session_id}/update")
    async def update_session(session_id: str, request: Request):
        """Update session data."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        updates = body.get("updates", body) if isinstance(body, dict) else {}
        success = session_manager.update_session(session_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_manager.get_session(session_id)

    @app.delete("/session/{session_id}")
    async def delete_session(session_id: str):
        """Delete session."""
        success = session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "deleted", "session_id": session_id}

    @app.get("/")
    def root() -> Dict[str, str]:
        """Root API status."""
        return {"name": "DNK OS Multi-Agent Core", "version": "2.2.0", "status": "running"}

except ImportError:
    app = None
