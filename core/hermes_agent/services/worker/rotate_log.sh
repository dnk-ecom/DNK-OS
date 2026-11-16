#!/bin/bash
# Hermes Worker Log Rotation Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGFILE="${SCRIPT_DIR}/worker.log"
MAX_SIZE=$((10 * 1024 * 1024))  # 10 MB

if [ -f "$LOGFILE" ]; then
  size=$(stat -f%z "$LOGFILE")
  if [ "$size" -ge "$MAX_SIZE" ]; then
    timestamp=$(date +%Y%m%d%H%M%S)
    mv "$LOGFILE" "$LOGFILE.$timestamp"
    # Create new empty log file
    touch "$LOGFILE"
    echo "[$(date)] Rotated log file due to size > 10MB" >> "$LOGFILE"
  fi
fi
