---
name: gcp-account-rotation
description: Autonomous Google Cloud (GCP) account and project rotation, quota management, and Vertex AI Gemini 3.x verification for DNK OS agents.
---

# 🔄 GCP Account Rotation & Vertex AI Management

## Purpose
Enables any autonomous agent (Gerych, Herich Librarian, Antigravity, Subagents) to:
1. Inspect the active Google Cloud account, Project ID, region, and Gemini models.
2. Autonomously switch GCP accounts and projects when quota limits (HTTP 429), permission errors (HTTP 403), or billing limits occur.
3. Keep the Single Source of Truth (`.dnk_active_project.env`) synchronized across the entire swarm.

---

## 🛠️ Available Agent Capabilities

### Option 1: Native Python Tool (Preferred in Hermes)
- `gcp_status()`: Returns active account, project ID, region, and endpoint.
- `gcp_switch(account="email@gmail.com", project_id="project-id", region="global")`: Switches credentials and updates all configurations across the swarm.

### Option 2: CLI Command (via Terminal / Bash)
Run the canonical SSOT switcher script:
```bash
./scripts/switch_gcp_account.sh [EMAIL] [PROJECT_ID] [REGION]
```

Example:
```bash
./scripts/switch_gcp_account.sh cadkuzmen070826@gmail.com dnk-220826 global
```

---

## 📋 Standard Operational Procedures for Agents

### When to Trigger Rotation:
1. **HTTP 429 (Resource Exhausted / Quota Exceeded)**: Vertex AI rate limits hit.
2. **HTTP 403 (Permission Denied / Billing Disabled)**: Account free credits expired or billing issue.
3. **User Request**: User explicitly asks to change Google Cloud account or project.

### Step-by-Step Autonomous Recovery:
1. Identify the error type (429 Quota / 403 Billing).
2. Execute `gcp_status()` or check `scripts/switch_gcp_account.sh`.
3. If new credentials or project ID are provided by the user, execute:
   ```bash
   ./scripts/switch_gcp_account.sh <NEW_EMAIL> <NEW_PROJECT_ID> global
   ```
4. Verify that the response returns `✅ [SSOT Switcher] Успішно! Модель gemini-3.7-flash активна`.
5. Continue the interrupted task seamlessly with the new project credits.
