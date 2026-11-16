#!/usr/bin/env python3
"""
HTTP endpoint for Hermes worker queue service.
Provides /health (JSON) and /metrics (Prometheus format).
"""
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import os

QUEUE_NAME = "hermes:queue"
RETRY_QUEUE = "hermes:retry"
DEAD_QUEUE = "hermes:dead"
WORKER_PATTERN = "services/worker/worker.sh"

def run_redis_command(cmd):
    try:
        output = subprocess.check_output(["redis-cli"] + cmd, stderr=subprocess.DEVNULL)
        return output.strip().decode('utf-8')
    except Exception:
        return None

def get_queue_length():
    res = run_redis_command(["llen", QUEUE_NAME])
    return int(res) if res is not None else -1

def get_retry_length():
    res = run_redis_command(["llen", RETRY_QUEUE])
    return int(res) if res is not None else 0

def get_dead_length():
    res = run_redis_command(["llen", DEAD_QUEUE])
    return int(res) if res is not None else 0

def get_worker_count():
    try:
        output = subprocess.check_output(["pgrep", "-f", WORKER_PATTERN], stderr=subprocess.DEVNULL)
        lines = output.strip().split(b'\n')
        lines = [l for l in lines if l]
        return len(lines)
    except Exception:
        return 0

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            queue_len = get_queue_length()
            retry_len = get_retry_length()
            dead_len = get_dead_length()
            worker_count = get_worker_count()
            response = {
                "queue_length": queue_len,
                "retry_length": retry_len,
                "dead_length": dead_len,
                "worker_count": worker_count,
                "timestamp": int(time.time())
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/metrics":
            queue_len = get_queue_length()
            retry_len = get_retry_length()
            dead_len = get_dead_length()
            worker_count = get_worker_count()
            # We don't have processed/failed counters without modifying worker to report them.
            # For now, we just expose gauges.
            metrics = []
            metrics.append(f"hermes_queue_length {queue_len}")
            metrics.append(f"hermes_retry_length {retry_len}")
            metrics.append(f"hermes_dead_length {dead_len}")
            metrics.append(f"hermes_worker_count {worker_count}")
            # Add a timestamp
            metrics.append(f"hermes_scrape_timestamp {int(time.time())}")
            output = "\n".join(metrics) + "\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(output.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress log messages
        pass

if __name__ == "__main__":
    port = 8000
    server = HTTPServer(("", port), Handler)
    print(f"Starting health-check server on port {port}")
    server.serve_forever()
