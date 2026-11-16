# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/bus.py"
# purpose: "Async Agent Action Bus with SQLite WAL persistence, non-blocking subscriber notifications, and DI."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-12"
# author: "Gerych Prime & dnk_dev_fullstack"
# --- END DNK-MRH-HEADER ---

import asyncio
import datetime
import logging
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from core.action_bus.artifact_store import ArtifactStore
from core.action_bus.broadcaster import EventBroadcaster
from core.action_bus.hitl_bridge import HitlApprovalBridge
from core.action_bus.models import (
    ActionExecutionResponse,
    ActionTask,
    ActionTaskStatus,
    BusEvent,
    BusEventType,
    SwarmBatchResponse,
    SwarmPipelineResponse,
    SwarmRouteResult,
)
from core.action_bus.persistence import ActionBusPersistence
from core.action_bus.swarm_router import SwarmExecutionEngine, SwarmTaskRouter
from core.plugins.models import SandboxStatus
from core.plugins.policy import PluginPolicyError
from core.plugins.sandbox_runner import PluginSandboxRunner
from core.sandbox.docker_runner import DockerExecutionResult, DockerSandboxRunner

logger = logging.getLogger("dnk.action_bus")


class AgentActionBus:
    """
    Central Asynchronous Action Bus (AAB) for Agent Swarms and MVR Plugins.
    Provides execution sandboxing, persistence via SQLite WAL, and multi-tenant isolation.
    """

    def __init__(
        self,
        sandbox_runner: Optional[PluginSandboxRunner] = None,
        persistence: Optional[ActionBusPersistence] = None,
        tenant_id: str = "tenant-default",
        workspace_id: str = "ws-alpha-001",
        swarm_router: Optional[SwarmTaskRouter] = None,
        broadcaster: Optional[EventBroadcaster] = None,
        artifact_store: Optional[ArtifactStore] = None,
        hitl_bridge: Optional[HitlApprovalBridge] = None,
        docker_sandbox_runner: Optional[DockerSandboxRunner] = None,
    ):
        self._sandbox_runner = sandbox_runner or PluginSandboxRunner()
        self._docker_sandbox_runner = docker_sandbox_runner or DockerSandboxRunner()
        self._persistence = persistence
        self.tenant_id = tenant_id
        self.workspace_id = workspace_id
        self._swarm_router = swarm_router or SwarmTaskRouter()
        self._broadcaster = broadcaster or EventBroadcaster()
        self._artifact_store = artifact_store or ArtifactStore(persistence=self._persistence)
        if self._artifact_store.persistence is None and self._persistence is not None:
            self._artifact_store.persistence = self._persistence
            self._artifact_store.load_from_persistence()
        self._swarm_engine = SwarmExecutionEngine(self, self._swarm_router, self._artifact_store)
        self._hitl_bridge = hitl_bridge or HitlApprovalBridge(bus=self)

        self._tasks: Dict[str, ActionTask] = {}
        self._results: Dict[str, ActionExecutionResponse] = {}
        self._events: List[BusEvent] = []
        self._subscribers: List[Callable[[BusEvent], Any]] = []
        self._loop_locks: Dict[asyncio.AbstractEventLoop, asyncio.Lock] = {}
        self._running = True

    @property
    def hitl_bridge(self) -> HitlApprovalBridge:
        return self._hitl_bridge

    @property
    def docker_sandbox_runner(self) -> DockerSandboxRunner:
        return self._docker_sandbox_runner

    @docker_sandbox_runner.setter
    def docker_sandbox_runner(self, runner: DockerSandboxRunner) -> None:
        self._docker_sandbox_runner = runner

    async def execute_sandbox(
        self,
        code: str,
        language: str = "python",
        timeout: float = 10.0,
        task_id: Optional[str] = None,
    ) -> DockerExecutionResult:
        """
        Executes code securely inside DockerSandboxRunner (or emulated fallback)
        and publishes SANDBOX_EXECUTION_COMPLETED event to the bus with telemetry.
        """
        eff_task_id = task_id or f"sandbox_{uuid.uuid4().hex[:10]}"
        result = await self._docker_sandbox_runner.run_code(
            code=code,
            language=language,
            timeout=timeout,
        )
        duration_ms = round(result.duration_seconds * 1000.0, 2)
        ram_bytes = getattr(result, "ram_bytes", 0)

        payload = {
            "ram_bytes": ram_bytes,
            "duration_ms": duration_ms,
            "exit_code": result.exit_code,
            "status": result.status,
            "timed_out": result.timed_out,
            "oom_killed": result.oom_killed,
            "mode": result.mode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

        await self._publish(
            event_type=BusEventType.SANDBOX_EXECUTION_COMPLETED,
            task_id=eff_task_id,
            payload=payload,
        )
        return result

    @property
    def broadcaster(self) -> EventBroadcaster:
        return self._broadcaster

    @property
    def artifact_store(self) -> ArtifactStore:
        return self._artifact_store

    @artifact_store.setter
    def artifact_store(self, store: ArtifactStore) -> None:
        self._artifact_store = store
        if self._artifact_store.persistence is None and self._persistence is not None:
            self._artifact_store.persistence = self._persistence
            self._artifact_store.load_from_persistence()
        if hasattr(self, "_swarm_engine"):
            self._swarm_engine.artifact_store = store

    @property
    def router(self) -> SwarmTaskRouter:
        return self._swarm_router

    @property
    def swarm_engine(self) -> SwarmExecutionEngine:
        return self._swarm_engine

    async def dispatch_swarm_parallel(
        self,
        tasks: List[ActionTask],
        timeout_seconds: float = 30.0,
        fail_fast: bool = False,
    ) -> SwarmBatchResponse:
        """Executes a batch of ActionTasks concurrently across specialized swarm agents."""
        return await self._swarm_engine.execute_parallel(
            tasks=tasks, timeout_seconds=timeout_seconds, fail_fast=fail_fast
        )

    async def dispatch_swarm_pipeline(
        self,
        stages: List[ActionTask],
        stop_on_failure: bool = True,
    ) -> SwarmPipelineResponse:
        """Executes a sequence of ActionTasks in phased order."""
        return await self._swarm_engine.execute_pipeline(
            stages=stages, stop_on_failure=stop_on_failure
        )

    async def delegate_task(
        self,
        from_agent: str,
        to_agent: str,
        task: ActionTask,
    ) -> ActionExecutionResponse:
        """Explicit Agent-to-Agent (A2A) task delegation."""
        return await self._swarm_engine.delegate_task(
            from_agent=from_agent, to_agent=to_agent, task=task
        )

    @property
    def _lock(self) -> asyncio.Lock:
        """Loop-aware lock to prevent cross-event-loop deadlocks in async test suites."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.Lock()
        if loop not in self._loop_locks:
            self._loop_locks[loop] = asyncio.Lock()
        return self._loop_locks[loop]

    def subscribe(self, callback: Callable[[BusEvent], Any]) -> None:
        """Register an event listener callback."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[BusEvent], Any]) -> None:
        """Unregister an event listener callback."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    @staticmethod
    def _handle_subscriber_task_result(task: asyncio.Task) -> None:
        try:
            exc = task.exception()
            if exc:
                logger.warning(f"Event subscriber task failed with exception: {exc}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.warning(f"Failed to inspect subscriber task result: {e}")

    async def _publish(
        self, event_type: BusEventType, task_id: str, payload: Dict[str, Any]
    ) -> BusEvent:
        event = BusEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            task_id=task_id,
            payload=payload,
        )
        return await self.publish_event(event)

    async def publish(
        self, event_type: BusEventType, task_id: str, payload: Dict[str, Any]
    ) -> BusEvent:
        """Convenience method to publish an event by type, task_id, and payload."""
        return await self._publish(event_type=event_type, task_id=task_id, payload=payload)

    async def publish_event(self, event: BusEvent) -> BusEvent:
        """Publishes a pre-constructed BusEvent across persistence, subscribers, and broadcaster."""
        self._events.append(event)

        # Persistent storage for audit event
        if self._persistence:
            try:
                await self._persistence.append_event(event)
            except Exception as e:
                logger.error(f"Failed to persist event {event.event_id}: {e}")

        # Non-blocking async fan-out to subscribers
        if self._subscribers:
            for sub in list(self._subscribers):
                try:
                    res = sub(event)
                    if asyncio.iscoroutine(res):
                        task_fut = asyncio.create_task(res)
                        task_fut.add_done_callback(self._handle_subscriber_task_result)
                except Exception as err:
                    logger.warning(f"Error in event subscriber: {err}")

        # Real-time stream broadcast for SSE & WebSockets
        try:
            self._broadcaster.broadcast(event)
        except Exception as e:
            logger.warning(f"Error broadcasting event {event.event_id}: {e}")

        return event

    async def dispatch_task(self, task: ActionTask) -> ActionExecutionResponse:
        """
        Dispatches an action task through the bus, enforcing security policies,
        dynamic agent routing, isolated sandbox execution, and persistent logging.
        """
        # Auto-route if target_agent is missing
        if not task.target_agent:
            route_res = self._swarm_router.route_task(task)
            task.target_agent = route_res.matched_agent
            task.routing_metadata = route_res.model_dump()
            await self._publish(
                BusEventType.TASK_ROUTED,
                task.task_id,
                {"target_agent": task.target_agent, "routing": route_res.model_dump()},
            )

        if task.delegated_by:
            await self._publish(
                BusEventType.TASK_DELEGATED,
                task.task_id,
                {"delegated_by": task.delegated_by, "target_agent": task.target_agent},
            )

        async with self._lock:
            self._tasks[task.task_id] = task
            if self._persistence:
                try:
                    await self._persistence.save_task(task)
                except Exception as e:
                    logger.error(f"Failed to persist task {task.task_id}: {e}")

        await self._publish(
            BusEventType.TASK_SUBMITTED,
            task.task_id,
            {
                "action_type": task.action_type,
                "tenant_id": task.tenant_id,
                "target_agent": task.target_agent,
            },
        )

        await self._publish(
            BusEventType.TASK_QUEUED,
            task.task_id,
            {"queue": "default_fifo"},
        )

        await self._publish(
            BusEventType.TASK_STARTED,
            task.task_id,
            {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()},
        )

        # Execution Phase
        start_time = datetime.datetime.now(datetime.timezone.utc)
        response: ActionExecutionResponse

        try:
            if task.plugin_card_path:
                card_p = Path(task.plugin_card_path)
                if not card_p.is_file():
                    err_resp = ActionExecutionResponse(
                        task_id=task.task_id,
                        status=ActionTaskStatus.REJECTED,
                        exit_code=1,
                        error_message=f"Plugin card file not found: {task.plugin_card_path}",
                        execution_time_ms=0.1,
                    )
                    async with self._lock:
                        self._results[task.task_id] = err_resp
                    await self._publish(
                        BusEventType.TASK_REJECTED,
                        task.task_id,
                        {"error": err_resp.error_message},
                    )
                    return err_resp

                res = await asyncio.to_thread(
                    self._sandbox_runner.run,
                    card_path=card_p,
                    payload=task.payload,
                )
                end_time = datetime.datetime.now(datetime.timezone.utc)
                duration_ms = (end_time - start_time).total_seconds() * 1000.0

                if res.status == SandboxStatus.COMPLETED:
                    final_status = ActionTaskStatus.COMPLETED
                    exit_code = 0
                elif res.status == SandboxStatus.BLOCKED:
                    final_status = ActionTaskStatus.REJECTED
                    exit_code = 1
                else:
                    final_status = ActionTaskStatus.FAILED
                    exit_code = 1

                response = ActionExecutionResponse(
                    task_id=task.task_id,
                    status=final_status,
                    exit_code=exit_code,
                    stdout=f"Plugin {res.plugin_id} executed with status: {res.status.value}",
                    output=res.output,
                    error_message=res.reason if final_status != ActionTaskStatus.COMPLETED else None,
                    execution_time_ms=duration_ms,
                    completed_at=end_time.isoformat(),
                )
            else:
                # Generic in-bus execution mock/fallback
                end_time = datetime.datetime.now(datetime.timezone.utc)
                duration_ms = (end_time - start_time).total_seconds() * 1000.0
                response = ActionExecutionResponse(
                    task_id=task.task_id,
                    status=ActionTaskStatus.COMPLETED,
                    exit_code=0,
                    stdout=f"Generic action '{task.action_type}' processed successfully by agent '{task.target_agent or 'system'}'.",
                    stderr="",
                    output={
                        "received_payload": task.payload,
                        "handled_by": task.target_agent,
                        "routing": task.routing_metadata,
                    },
                    error_message=None,
                    execution_time_ms=max(duration_ms, 0.1),
                    completed_at=end_time.isoformat(),
                )

        except PluginPolicyError as pe:
            end_time = datetime.datetime.now(datetime.timezone.utc)
            duration_ms = (end_time - start_time).total_seconds() * 1000.0
            response = ActionExecutionResponse(
                task_id=task.task_id,
                status=ActionTaskStatus.REJECTED,
                exit_code=1,
                error_message=f"Plugin policy error: {str(pe)}",
                execution_time_ms=duration_ms,
                completed_at=end_time.isoformat(),
            )
        except Exception as exc:
            end_time = datetime.datetime.now(datetime.timezone.utc)
            duration_ms = (end_time - start_time).total_seconds() * 1000.0
            logger.error("Error executing task %s: %s", task.task_id, str(exc), exc_info=True)
            response = ActionExecutionResponse(
                task_id=task.task_id,
                status=ActionTaskStatus.FAILED,
                exit_code=1,
                stdout="",
                stderr=str(exc),
                output={},
                error_message=str(exc),
                execution_time_ms=duration_ms,
                completed_at=end_time.isoformat(),
            )

        async with self._lock:
            self._results[task.task_id] = response
            if self._persistence:
                try:
                    await self._persistence.save_execution_response(response)
                except Exception as e:
                    logger.error(f"Failed to persist response for {task.task_id}: {e}")

        # Post-execution event publishing
        if response.status == ActionTaskStatus.COMPLETED:
            await self._publish(
                BusEventType.TASK_COMPLETED,
                task.task_id,
                {"execution_time_ms": response.execution_time_ms},
            )
        elif response.status == ActionTaskStatus.REJECTED:
            await self._publish(
                BusEventType.TASK_REJECTED,
                task.task_id,
                {"error": response.error_message},
            )
        else:
            await self._publish(
                BusEventType.TASK_FAILED,
                task.task_id,
                {"error": response.error_message, "exit_code": response.exit_code},
            )

        return response

    async def get_task_status(self, task_id: str) -> Optional[ActionExecutionResponse]:
        """Query execution response for a task_id from memory or persistent storage."""
        if task_id in self._results:
            return self._results[task_id]
        if self._persistence:
            return await self._persistence.get_execution_response(task_id)
        return None

    async def get_task(self, task_id: str) -> Optional[ActionTask]:
        """Query task definition by task_id from memory or persistent storage."""
        if task_id in self._tasks:
            return self._tasks[task_id]
        if self._persistence:
            return await self._persistence.get_task(task_id)
        return None

    def get_events(self, task_id: Optional[str] = None) -> List[BusEvent]:
        """Synchronous in-memory event retrieval for backward compatibility."""
        if task_id:
            return [e for e in self._events if e.task_id == task_id]
        return list(self._events)

    async def get_persistent_events(
        self, task_id: Optional[str] = None, limit: int = 100
    ) -> List[BusEvent]:
        """Retrieve events with fallback to SQLite WAL persistence."""
        if self._persistence:
            return await self._persistence.get_events(task_id=task_id, limit=limit)
        return self.get_events(task_id=task_id)[:limit]

    def clear(self) -> None:
        """Reset internal memory buffers (for testing)."""
        self._tasks.clear()
        self._results.clear()
        self._events.clear()
        self._subscribers.clear()
        self._loop_locks.clear()

    async def close(self) -> None:
        """Gracefully close bus and flush persistence."""
        self._running = False
        if self._persistence:
            await self._persistence.close()


# Factory and Dependency Injection Support
def create_action_bus(
    tenant_id: str = "tenant-default",
    workspace_id: str = "ws-alpha-001",
    db_path: Optional[Union[str, Path]] = None,
    sandbox_runner: Optional[PluginSandboxRunner] = None,
    persistence: Optional[ActionBusPersistence] = None,
    swarm_router: Optional[SwarmTaskRouter] = None,
    broadcaster: Optional[EventBroadcaster] = None,
    artifact_store: Optional[ArtifactStore] = None,
    hitl_bridge: Optional[HitlApprovalBridge] = None,
    docker_sandbox_runner: Optional[DockerSandboxRunner] = None,
) -> AgentActionBus:
    """
    Factory function to create an isolated AgentActionBus instance.
    Ideal for FastAPI Dependency Injection and multi-tenant isolation.
    """
    if persistence is None and db_path:
        persistence = ActionBusPersistence(db_path=db_path)

    return AgentActionBus(
        sandbox_runner=sandbox_runner,
        persistence=persistence,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        swarm_router=swarm_router,
        broadcaster=broadcaster,
        artifact_store=artifact_store,
        hitl_bridge=hitl_bridge,
        docker_sandbox_runner=docker_sandbox_runner,
    )


# Default Singleton Instance for backward compatibility
_default_action_bus: Optional[AgentActionBus] = None


def get_default_action_bus(
    db_path: Optional[Union[str, Path]] = None,
    fresh: bool = False,
) -> AgentActionBus:
    """
    Returns the default singleton AgentActionBus.
    Can be refreshed with fresh=True for testing.
    """
    global _default_action_bus
    if _default_action_bus is None or fresh:
        _default_action_bus = create_action_bus(
            tenant_id="tenant-default",
            workspace_id="ws-alpha-001",
            db_path=db_path,
        )
    return _default_action_bus
