# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_os/core/streaming.py"
# purpose: "Token-level and task execution SSE streaming service for DNK OS Multi-Agent Core"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""
Streaming Service for DNK OS Multi-Agent Core.

Supports:
- Server-Sent Events (SSE)
- Token-level streaming
- Task progress streaming
- Worker output streaming (tokens, words, lines)
"""

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, Optional
from fastapi.responses import StreamingResponse


class StreamingService:
    """
    Streaming service for DNK OS Multi-Agent Core.
    
    Supports:
    - Server-Sent Events (SSE)
    - Token-level streaming
    - Progress updates
    - Completion events
    """
    
    def __init__(self) -> None:
        """Initialize streaming service."""
        pass

    async def stream_tokens(
        self,
        text: str,
        tokens_per_second: int = 50,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """
        Stream text token-by-token (simulated).
        
        Args:
            text: Text to stream
            tokens_per_second: Streaming speed
            
        Yields:
            JSON SSE messages
        """
        words = text.split()
        delay = 1.0 / tokens_per_second if tokens_per_second > 0 else 0.0
        
        for i, word in enumerate(words):
            event = {
                "type": "token",
                "data": {
                    "token": word,
                    "index": i,
                    "total": len(words)
                }
            }
            yield f"data: {json.dumps(event)}\n\n"
            if delay > 0:
                await asyncio.sleep(delay)
        
        # Completion event
        event = {
            "type": "completion",
            "data": {
                "total_tokens": len(words),
                "status": "complete"
            }
        }
        yield f"data: {json.dumps(event)}\n\n"

    async def stream_task_execution(
        self,
        task_id: str,
        worker_name: str,
        task_description: str,
        sleep_interval: float = 0.01,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """
        Stream task execution progress.
        
        Args:
            task_id: Task identifier
            worker_name: Worker name
            task_description: Task description
            sleep_interval: Delay between progress steps in seconds
            
        Yields:
            JSON SSE messages with progress updates
        """
        # Start event
        event = {
            "type": "start",
            "data": {
                "task_id": task_id,
                "worker": worker_name,
                "description": task_description,
                "status": "started"
            }
        }
        yield f"data: {json.dumps(event)}\n\n"
        
        # Simulate execution progress
        for progress in range(0, 101, 10):
            if sleep_interval > 0:
                await asyncio.sleep(sleep_interval)
            event = {
                "type": "progress",
                "data": {
                    "task_id": task_id,
                    "progress_percent": progress,
                    "status": "running"
                }
            }
            yield f"data: {json.dumps(event)}\n\n"
        
        # Completion event
        event = {
            "type": "completion",
            "data": {
                "task_id": task_id,
                "progress_percent": 100,
                "status": "completed",
                "result": {
                    "output": "Task completed successfully"
                }
            }
        }
        yield f"data: {json.dumps(event)}\n\n"

    async def stream_worker_output(
        self,
        worker_name: str,
        output: str,
        stream_mode: str = "tokens",
        sleep_interval: float = 0.01,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """
        Stream worker output.
        
        Args:
            worker_name: Worker name
            output: Worker output text
            stream_mode: Streaming mode ("tokens", "words", "lines")
            sleep_interval: Delay between items in seconds
            
        Yields:
            JSON SSE messages
        """
        if stream_mode == "tokens":
            tokens_per_sec = int(1.0 / sleep_interval) if sleep_interval > 0 else 1000
            async for chunk in self.stream_tokens(output, tokens_per_second=tokens_per_sec):
                yield chunk
            return
        elif stream_mode == "words":
            words = output.split()
            for i, word in enumerate(words):
                event = {
                    "type": "word",
                    "data": {
                        "word": word,
                        "index": i,
                        "total": len(words)
                    }
                }
                yield f"data: {json.dumps(event)}\n\n"
                if sleep_interval > 0:
                    await asyncio.sleep(sleep_interval)
        elif stream_mode == "lines":
            lines = output.split("\n")
            for i, line in enumerate(lines):
                event = {
                    "type": "line",
                    "data": {
                        "line": line,
                        "index": i,
                        "total": len(lines)
                    }
                }
                yield f"data: {json.dumps(event)}\n\n"
                if sleep_interval > 0:
                    await asyncio.sleep(sleep_interval)
        
        # Completion
        event = {
            "type": "completion",
            "data": {
                "worker": worker_name,
                "status": "complete"
            }
        }
        yield f"data: {json.dumps(event)}\n\n"

    def create_sse_response(
        self,
        generator: AsyncGenerator[str, None],
        media_type: str = "text/event-stream",
        **kwargs: Any
    ) -> StreamingResponse:
        """
        Create FastAPI StreamingResponse for SSE.
        
        Args:
            generator: Async generator for SSE events
            media_type: Response media type
            
        Returns:
            StreamingResponse
        """
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
        return StreamingResponse(
            generator,
            media_type=media_type,
            headers=headers
        )
