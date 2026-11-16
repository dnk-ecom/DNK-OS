#!/bin/bash
# Hermes Worker with retry and dead letter queue
# Expects job as JSON string: {"payload": "...", "retry": 0}
WORKER_ID="${1:-worker}"
MAX_RETRY=3
QUEUE_NAME="hermes:queue"
RETRY_QUEUE="hermes:retry"
DEAD_LETTER_QUEUE="hermes:dead"

echo "[$(date)] $WORKER_ID started, listening to $QUEUE_NAME"
while true; do
  # Blocking pop from main queue
  job=$(redis-cli blpop "$QUEUE_NAME" 0 2>/dev/null)
  if [ -n "$job" ]; then
    # job format: "queue_name\\nactual_job_data"
    value=$(echo "$job" | cut -d' ' -f2-)
    echo "[$(date)] $WORKER_ID received job: $value"
    # Parse JSON to get retry count (if any)
    # We'll use a simple approach: if the value contains "retry", we extract it, else assume 0
    # This is a very basic JSON parsing for demo purposes.
    retry_count=0
    if echo "$value" | grep -q '"retry"'; then
      # Extract the number after "retry": 
      retry_count=$(echo "$value" | grep -o '"retry": *[0-9]*' | grep -o '[0-9]*')
    fi
    # Simulate work - replace with actual task processing
    # For demonstration, we'll fail randomly
    if [ $((RANDOM % 10)) -lt 3 ]; then  # 30% chance of failure
      echo "[$(date)] $WORKER_ID job failed: $value"
      if [ "$retry_count" -lt "$MAX_RETRY" ]; then
        new_retry=$((retry_count + 1))
        # Create new JSON with incremented retry
        new_job=$(echo "$value" | sed "s/\"retry\": $retry_count/\"retry\": $new_retry/")
        # If no retry field, add it
        if ! echo "$value" | grep -q '"retry"'; then
          new_job=$(echo "$value" | sed 's/}$/,"retry": 1}/')
        fi
        # Push to retry queue (or back to main queue? We'll use a separate retry queue for now)
        redis-cli lpush "$RETRY_QUEUE" "$new_job"
        echo "[$(date)] $WORKER_ID job requeued to $RETRY_QUEUE with retry $new_retry"
      else
        # Send to dead letter queue
        redis-cli lpush "$DEAD_LETTER_QUEUE" "$value"
        echo "[$(date)] $WORKER_ID job moved to dead letter queue after $MAX_RETRY retries"
      fi
    else
      echo "[$(date)] $WORKER_ID processing job: $value"
      sleep 2  # Simulate work
      echo "[$(date)] $WORKER_ID completed job: $value"
    fi
  fi
done
