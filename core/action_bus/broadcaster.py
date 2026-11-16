# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/broadcaster.py"
# purpose: "High-performance fan-out event broadcaster for SSE/WebSockets with non-blocking backpressure."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "Gerych Prime & dnk_dev_fullstack"
# --- END DNK-MRH-HEADER ---

import asyncio
from collections import deque
import logging
from typing import Deque, Dict, List, Optional, Set
import uuid

from core.action_bus.models import BusEvent, BusEventType, StreamEnvelope

logger = logging.getLogger("mvr_core.broadcaster")


class ClientSubscription:
    """Encapsulates a connected client's event stream buffer and filters."""

    def __init__(
        self,
        sub_id: str,
        queue: asyncio.Queue,
        filter_types: Optional[Set[BusEventType]] = None,
        task_id: Optional[str] = None,
        agent: Optional[str] = None,
    ):
        self.sub_id = sub_id
        self.queue = queue
        self.filter_types = filter_types
        self.task_id = task_id
        self.agent = agent
        self.dropped_events_count = 0

    def matches(self, envelope: StreamEnvelope) -> bool:
        if self.filter_types and envelope.event_type not in self.filter_types:
            return False
        if self.task_id and envelope.task_id != self.task_id:
            return False
        if self.agent and envelope.agent != self.agent:
            return False
        return True


class EventBroadcaster:
    """Non-blocking in-memory event broadcaster for SSE and WebSocket clients.
    
    Guarantees zero-blocking on slow or stalled clients by using a bounded queue
    with drop-oldest overflow policy and maintaining a ring buffer of recent events
    for instant UI initialisation.
    """

    def __init__(self, max_queue_size: int = 200, recent_history_size: int = 100):
        self._subscriptions: Dict[str, ClientSubscription] = {}
        self._max_queue_size = max_queue_size
        self._recent_events: Deque[StreamEnvelope] = deque(maxlen=recent_history_size)
        self._lock = asyncio.Lock()

    @property
    def active_subscribers_count(self) -> int:
        return len(self._subscriptions)

    async def subscribe(
        self,
        filter_types: Optional[List[BusEventType]] = None,
        task_id: Optional[str] = None,
        agent: Optional[str] = None,
    ) -> ClientSubscription:
        """Subscribes a client and returns its bounded subscription object."""
        sub_id = f"sub_{uuid.uuid4().hex[:8]}"
        q: asyncio.Queue = asyncio.Queue(maxsize=self._max_queue_size)
        types_set = set(filter_types) if filter_types else None

        sub = ClientSubscription(
            sub_id=sub_id,
            queue=q,
            filter_types=types_set,
            task_id=task_id,
            agent=agent,
        )

        async with self._lock:
            self._subscriptions[sub_id] = sub
        logger.info(f"Client subscribed: {sub_id} (active: {len(self._subscriptions)})")
        return sub

    async def unsubscribe(self, sub_id: str) -> None:
        """Removes a client subscription."""
        async with self._lock:
            if sub_id in self._subscriptions:
                del self._subscriptions[sub_id]
                logger.info(f"Client unsubscribed: {sub_id} (active: {len(self._subscriptions)})")

    def broadcast(
        self,
        event: BusEvent,
        agent: Optional[str] = None,
        artifact_uri: Optional[str] = None,
    ) -> StreamEnvelope:
        """Broadcasts an event envelope to all matching active clients without blocking."""
        envelope = StreamEnvelope(
            event_id=event.event_id,
            event_type=event.event_type,
            task_id=event.task_id,
            timestamp=event.timestamp,
            agent=agent or event.payload.get("target_agent") or event.payload.get("handled_by"),
            payload=event.payload,
            artifact_uri=artifact_uri or event.payload.get("artifact_uri"),
        )

        self._recent_events.append(envelope)

        for sub in list(self._subscriptions.values()):
            if sub.matches(envelope):
                try:
                    sub.queue.put_nowait(envelope)
                except asyncio.QueueFull:
                    # Drop oldest item to make room for newest (non-blocking drop policy)
                    try:
                        _ = sub.queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    try:
                        sub.queue.put_nowait(envelope)
                    except asyncio.QueueFull:
                        pass
                    sub.dropped_events_count += 1
                    logger.warning(
                        f"Subscription {sub.sub_id} queue overflowed. Total dropped: {sub.dropped_events_count}"
                    )

        return envelope

    def get_recent_envelopes(
        self,
        limit: int = 50,
        filter_type: Optional[BusEventType] = None,
    ) -> List[StreamEnvelope]:
        """Returns recent broadcasted events from the ring buffer."""
        items = list(self._recent_events)
        if filter_type:
            items = [item for item in items if item.event_type == filter_type]
        return items[-limit:]

    def get_events_since(
        self,
        last_event_id: str,
        limit: int = 100,
        filter_type: Optional[BusEventType] = None,
        task_id: Optional[str] = None,
    ) -> List[StreamEnvelope]:
        """Returns events broadcasted strictly after last_event_id for resilient reconnection.
        
        If last_event_id is not in buffer (e.g. client was disconnected too long),
        returns up to limit most recent events to resynchronise client state.
        """
        all_items = list(self._recent_events)
        target_idx = -1
        for idx, item in enumerate(all_items):
            if item.event_id == last_event_id:
                target_idx = idx
                break

        if target_idx != -1:
            candidates = all_items[target_idx + 1:]
        else:
            candidates = all_items

        if filter_type:
            candidates = [c for c in candidates if c.event_type == filter_type]
        if task_id:
            candidates = [c for c in candidates if c.task_id == task_id]

        return candidates[:limit]

