---
title: "Readme"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/hermes_agent/services/worker/README.md"
> purpose: "Document: Readme"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# Hermes Worker Queue Service

This service implements a simple background worker pool that processes jobs from a Redis queue (`hermes:queue`).

## Components

- `worker.sh` – a bash script that blpops jobs from the Redis queue and simulates processing.
- `monitor.sh` – prints current queue length and number of active workers.
- Optional: `start_workers.sh` (example) to launch multiple workers.

## Prerequisites

- Docker (to run Redis) or a Redis server accessible at `localhost:6379`.
- Bash shell.

## Setup

1. Start Redis (if not already running):
   ```bash
   docker run -d --name hermes-redis -p 6379:6379 redis:alpine
   ```

2. Ensure the worker script is executable:
   ```bash
   chmod +x services/worker/worker.sh
   chmod +x services/worker/monitor.sh
   ```

## Starting Workers

Run one or more workers in the background using the Hermes `terminal` tool (or directly in a shell):

```bash
# Start a single worker with ID "worker-1"
./services/worker/worker.sh worker-1 &

# Or start multiple workers (example using a loop)
for i in {1..3}; do
  ./services/worker/worker.sh "worker-$i" &
done
```

When using the Hermes agent, prefer `terminal(background=true)` so the agent can track the process:

```bash
terminal(command="./services/worker/worker.sh worker-1", background=true)
```

## Monitoring

Check the queue length and active worker count:

```bash
./services/worker/monitor.sh
```

Example output:
```
[Thu Aug  6 23:43:22 EEST 2026] Queue length: 0 | Active workers:        6
```

For continuous monitoring, run a loop:

```bash
while true; do ./services/worker/monitor.sh; sleep 5; done
```

## Adding Jobs

Push jobs to the Redis queue:

```bash
redis-cli lpush hermes:queue "job_payload_1" "job_payload_2"
```

Workers will pick them up and process (currently just sleep 2 seconds and log).

## Stopping Workers

To stop all workers:

```bash
pkill -f "services/worker/worker.sh"
```

## Extending

Replace the simulated work (`sleep 2`) in `worker.sh` with actual task processing, e.g., calling Hermes tools, running scripts, or making API calls.

## Notes

- The worker uses `redis-cli blpop` with a timeout of 0 (blocking indefinitely).
- Logs are written to stdout; when started via `terminal(background=true)`, you can inspect output with `process(action='log', session_id='<id>')`.
- For production, consider adding log rotation, health checks, dynamic scaling, and proper error handling.


## Log Rotation

The worker script outputs to `services/worker/worker.log` when started with output redirection (e.g., `./worker.sh worker-1 >> worker.log 2>&1 &`).

To prevent the log file from growing indefinitely, you can use log rotation.

### Option 1: Using the provided rotation script

A simple log rotation script is available at `services/worker/rotate_log.sh`. It checks the log file size and rotates it if it exceeds 10 MB.

To run it periodically, add a cron job:

```bash
# Edit your crontab
crontab -e
# Add the following line to run the script every day at 2:30 AM (adjust HUB_ROOT to your local repository path)
30 2 * * * $HUB_ROOT/core/hermes_agent/services/worker/rotate_log.sh
```

### Option 2: Using logrotate

If you have `logrotate` installed (e.g., via Homebrew), you can use the provided configuration file.

Copy `services/worker/logrotate.conf` to `/etc/logrotate.d/hermes-worker` (or include it in your logrotate configuration).

Example configuration:

```
{{ contents of logrotate.conf }}
```

Make sure logrotate is run periodically (usually via a system cron job).

### Starting Workers with Log Output

When starting workers, redirect output to the log file:

```bash
# Start a worker and log to worker.log
./services/worker/worker.sh worker-1 >> services/worker/worker.log 2>&1 &
```

Or, using the Hermes agent's terminal tool:

```bash
terminal(command="./services/worker/worker.sh worker-1 >> services/worker/worker.log 2>&1", background=true)
```

