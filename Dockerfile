# --- DNK-MRH-HEADER ---
# mrh_id: "Dockerfile"
# purpose: "Production Multi-Stage Dockerfile for DNK OS Sovereign Kernel (DEC-070, DEC-071)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

# ==========================================
# Stage 1: Build Dependencies via uv
# ==========================================
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

# Install uv for fast, deterministic dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml ./
RUN uv venv /opt/venv && \
    uv pip install --no-cache -r pyproject.toml

# ==========================================
# Stage 2: Production Non-Root Runtime
# ==========================================
FROM python:3.12-slim-bookworm AS runner

# Install essential agent system tools (DEC-071)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ripgrep \
    dumb-init \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Enforce Non-Root UID 1000 (Linux Permission Parity)
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} dnk && \
    useradd -u ${UID} -g dnk -m -s /bin/bash dnk

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copy application source code
COPY --chown=dnk:dnk . /app

# Ensure writable data and logs directories
RUN mkdir -p /app/data /app/logs && chown -R dnk:dnk /app/data /app/logs

USER dnk

EXPOSE 8000 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3", "-m", "core.kernel"]
