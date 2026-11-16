#!/bin/bash
QUEUE_LEN=$(redis-cli llen hermes:queue 2>/dev/null || echo "0")
RETRY_LEN=$(redis-cli llen hermes:retry 2>/dev/null || echo "0")
DEAD_LEN=$(redis-cli llen hermes:dead 2>/dev/null || echo "0")
WORKER_COUNT=$(pgrep -f "services/worker/worker.sh" | wc -l)
echo "[$(date)] Queue length: $QUEUE_LEN | Retry: $RETRY_LEN | Dead: $DEAD_LEN | Active workers: $WORKER_COUNT"
