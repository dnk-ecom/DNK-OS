# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/skills_assimilated/references/wizard_generator.md"
# purpose: "Reference guide for generating interactive human-in-the-loop bash wizards."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-11"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🧙 Interactive Bash Wizard Generator

Assimilated from `mattpocock/skills/engineering/wizard`.

## 1. When to Use
Use a **Wizard** when an operation cannot be automated by the agent directly:
- Generating OAuth tokens or browser-based MFA logins.
- Provisioning external cloud accounts (Shopify Partner, Stripe, Vercel, Supabase).
- Walkthroughs of third-party dashboards requiring credit card / human identity confirmation.
- Safe cutover or database migration where a human must confirm every critical step.

## 2. Wizard Script Invariants
A generated wizard script must:
1. Use `#!/usr/bin/env bash` with `set -euo pipefail`.
2. Open target URLs automatically (`open "$URL"` on macOS, `xdg-open` on Linux).
3. Display clear, numbered human instructions with colorful terminal styling.
4. Prompt for user input (`read -r -p "Enter token: " TOKEN`).
5. Validate the input immediately (non-empty check, regex match, ping API).
6. Store credentials safely into the local workspace vault (`dnk_vault_set_secret` or `.env.local`), never printing raw secrets to standard output.
