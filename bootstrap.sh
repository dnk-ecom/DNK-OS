#!/usr/bin/env bash
# --- DNK-MRH-HEADER ---
# mrh_id: "bootstrap.sh"
# purpose: "Sovereign Autonomous Self-Deployment Script for DNK OS (DEC-070, DEC-071)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧬 Initializing DNK OS Sovereign Self-Deployment..."

# 1. Environment Template Setup
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    echo "📋 Copying .env.example -> .env"
    cp .env.example .env
  else
    echo "⚠️ Warning: .env.example not found. Creating empty .env"
    touch .env
  fi
fi

# 2. Stateful Directory Setup & UID Permissions Guard
mkdir -p data logs
if [[ "$OSTYPE" == "linux"* ]]; then
  echo "🐧 Linux host detected. Enforcing UID 1000 permissions for container mounts..."
  CURRENT_UID=$(id -u)
  if [ "$CURRENT_UID" -eq 0 ]; then
    chown -R 1000:1000 data logs
  fi
fi

# 3. Mode Selection: Docker or Local
if [ "$1" == "--local" ]; then
  echo "💻 Starting DNK OS in Local Cockpit mode..."
  if command -v python3 &>/dev/null; then
    python3 scripts/dnk_os_cli.py status
    python3 scripts/dnk_os_cli.py verify
  else
    echo "❌ Python 3 is required for local mode."
    exit 1
  fi
elif command -v docker &>/dev/null && docker compose version &>/dev/null; then
  echo "🐳 Docker Compose detected. Building and deploying container..."
  docker compose up -d --build
  echo "✅ DNK OS Kernel deployed in Docker. Checking status:"
  docker compose ps
else
  echo "💻 Docker not found. Running local cockpit status..."
  python3 scripts/dnk_os_cli.py status
fi

echo "🚀 DNK OS Initialization Complete."
