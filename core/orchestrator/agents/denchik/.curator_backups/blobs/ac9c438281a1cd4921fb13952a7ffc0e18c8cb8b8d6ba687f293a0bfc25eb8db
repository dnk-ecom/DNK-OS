<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/github_open_source_plugin_intake_patterns.md"
# purpose: "Architecture patterns for minimal GitHub open-source plugin intake into DNK OS sandbox"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---
-->

# GitHub Open-Source Plugin Intake Patterns (PLUGIN-004)

## Core Objective & Philosophy
Enables safe, declarative importation of open-source plugins from GitHub into DNK OS with guaranteed zero-privilege execution quarantine. A plugin imported via this intake pipeline is strictly non-executable and uncertified until passing the sandbox evaluation suite.

```text
GitHub Repo (URL + Commit SHA + SPDX License)
                   │
                   ▼ (plugin_github_intake.py generate-template)
┌────────────────────────────────────────────────────────┐
│ Canonical Intake Card Template                         │
│ - schema_version: dnk-plugin/v1.0                      │
│ - lifecycle: sandbox (IMMUTABLE AT INTAKE)             │
│ - permissions: ALL NONE (default-deny)                 │
│ - contract_test_path: null (quarantine before eval)    │
│ - relative paths only                                  │
└────────────────────────────────────────────────────────┘
                   │
                   ▼ (plugin_github_intake.py validate)
┌────────────────────────────────────────────────────────┐
│ Validation Gate (Exit 0 / Non-Zero)                    │
│ - SPDX license validation                              │
│ - Relative path invariant                              │
│ - Default-deny permissions invariant                   │
│ - Sandbox lifecycle enforcement                        │
└────────────────────────────────────────────────────────┘
```

## Mandatory Intake Invariants
1. **Lifecycle Sandbox Quarantine**: The lifecycle MUST be `sandbox`. Any intake attempt specifying `certified` or `active` is rejected.
2. **Default-Deny Privileges**: All resource permissions are locked to `none`:
   - `filesystem: none`
   - `network: none`
   - `secrets: none`
   - `git: none`
   - `database: none`
   - `external_write: none`
3. **SPDX License Normalization**: License must match recognized open-source SPDX identifiers (`MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `GPL-2.0-only`, `GPL-3.0-only`, `LGPL-2.1-only`, `LGPL-3.0-only`, `MPL-2.0`, `Unlicense`, `CC0-1.0`).
4. **URL & Commit Pinning**:
   - `repository_url`: Must start with `https://`.
   - `commit_sha`: Must be a valid hex string (6 to 64 characters) to prevent unpinned mutable branch pulls.
5. **Pre-Evaluation vs Runtime Contract**:
   - At initial intake generation, `contract_test_path` is `null` because tests have not yet been developed for the imported code.
   - Intake validation verifies this card schema without invoking execution runners.
6. **Strict Relative Path Invariant**: No absolute paths (`/Users/...`, `C:\...`) or parent traversals (`..`) are permitted anywhere in the card.

## Canonical CLI Commands
```bash
# 1. Generate Sandbox Intake Card
python3 scripts/system/plugin_github_intake.py generate-template \
  --repo-url https://github.com/example/plugin-repo \
  --commit-sha abc1234 \
  --license MIT \
  --plugin-id github-plugin-001 \
  --plugin-name "Example GitHub Plugin" \
  --plugin-kind tool

# 2. Validate Sandbox Intake Card
python3 scripts/system/plugin_github_intake.py validate \
  templates/plugin/github/github_plugin_001_card.yaml
```
