---
title: "Hermes Bot Mode vs Headless Swarm Execution Protocol"
category: "autonomous-ai-agents"
---

# Hermes Bot Mode vs Headless Swarm Execution Protocol

## Context & Core Difference
- **Hermes Bot Mode (`hermes bot run`)**:
  - Operates as dedicated persistent agent profiles (`profiles/<name>/`) communicating via chat channels (Telegram, Discord, or Hermes Group Chat).
  - Uses explicit `@mentions` and conversational round-trips.
  - Useful for human-in-the-loop review, low-bandwidth mobile commands, and strict tool isolation (e.g., Researcher without write tools, Librarian with vault access only).
  - **Trade-off**: High latency due to chat turn sequencing and conversational filler; potential infinite ping-pong loops if bots trigger each other without termination bounds.

- **Headless Swarm Execution (`dnk_swarm_parallel` / `delegate_task`)**:
  - Operates via direct in-process/background subprocess dispatch with structured input/output JSON schemas.
  - Zero conversational chatter; parallel execution in 1–2 seconds per worker.
  - Mandatory for high-velocity code generation, adversarial audits, and multi-domain engineering tasks.

## Invariant for DNK OS
1. Never replace headless swarm execution with interactive chat-based bot loops for automated engineering pipelines.
2. Reserve Bot Mode strictly for mobile founder interaction (Telegram/Discord gateway) with single-user whitelist (`allowed_users`) and manual approval gates for write/destructive actions.
