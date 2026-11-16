# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/deep_skill_harvester_and_execution_bridge_patterns.md"
# purpose: "Patterns for Deep Skill Reference Harvesting, Dynamic Domain Schemas, Swarm Worker Activation, and SCONES URL Hygiene."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-14"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# ⚡ Deep Skill Reference Harvester & Swarm Execution Bridge Patterns

## 🚨 Background & Anti-Patterns Identified

1. **The "Hollow Skill Gap"**:
   - Assimilation created skill directories with high-level summaries in `SKILL.md`, but left `references/` and `scripts/` empty.
   - Domain agents (`dnk_shopify`, `gerych_builder`) had no access to actual prompt formulas, checklists, or heuristic rules.
2. **Surface API Dossier & Hardcoded Schemas**:
   - Relying on generic GitHub metadata and hardcoded models (`SessionRecord`/`ActionLog`) instead of discovering repo-specific skills and generating domain-aware Pydantic schemas.
3. **Identifier Sanitization Failures**:
   - Transforming repo names containing hyphens (`agent-skills`) into Python class names via naive string replacement yielded `class Agent-SkillsConfig`, causing runtime `SyntaxError`.
4. **Passive Storage vs Active Execution**:
   - Storing TaskDNA DAGs only as text in Obsidian/markdown notes without generating runnable machine-readable rule files for Swarm workers.
5. **Path Validator URL False Positives**:
   - Regular expressions for local filesystem paths (e.g. Windows drive letters `[A-Za-z]:[/\\]`) accidentally matched `s:/` inside `https://` URLs, falsely rejecting valid repository web links.
6. **Isolated Staging vs Live Runtime Desync**:
   - Generating skills only into `core/skills/` left Gerych Prime's active Hermes skills index unaware of newly assimilated capabilities until manually copied.
7. **Brittle Swarm Info Extraction**:
   - Unsafe direct dictionary access `swarm_info["key"]` without fallback defaults caused `KeyError` when upstream agents or mocks emitted partial payloads.

---

## 🛠️ Canonical Solutions & Architectural Rules

### 1. Universal Deep Skill & Reference Harvester
- When assimilating repositories, the engine must not restrict scanning to `/contents/skills`.
- It dynamically probes multiple high-signal directories via GitHub API / MCP:
  - `/contents/skills`
  - `/contents/references`
  - `/contents/docs`
  - `/contents/architecture`
  - `/contents/examples`
- In addition, it directly ingests root architecture documents (`ARCHITECTURE.md`, `SPEC.md`, `DESIGN.md`) when present.
- Downloaded Markdown specifications are persisted directly to the skill's local `references/` directory.
- Domain agents inspect specific references via `skill_view(name, file_path='references/<file>.md')`.

### 2. Live Hermes Agent Skill Mirroring
Newly synthesized skills must be immediately usable by Gerych Prime and the swarm without daemon restarts:
- When `generate_hermes_skill` writes to `core/skills/<safe_name>/SKILL.md`, it simultaneously mirrors the skill directory (including `SKILL.md` and all harvested `references/`) to:
  `core/orchestrator/agents/gerych_prime/skills/<safe_name>/`
- This ensures the active Hermes Agent runtime dynamically indexes the new skill in real time.

### 3. Python Identifier Sanitization Rule
Never use simple `.replace('_', ' ').title().replace(' ', '')` when creating class names from repository or package slugs. Always sanitize non-alphanumeric characters first:
```python
import re

def to_valid_class_name(slug: str, suffix: str = "Config") -> str:
    clean = re.sub(r'[^a-zA-Z0-9]+', ' ', slug).strip().title().replace(' ', '')
    return f"{clean}{suffix}"
```

### 4. Active Swarm Worker Activation Bridge (`activate_assimilation_slice`)
Every assimilation must be actionable. The engine bridges harvested knowledge into worker-specific configuration files:
- **`dnk_shopify`**: Emits `services/dnk_shopify/assimilated_conversion_rules.json` with concrete UI/conversion directives (Hero CTA, Risk Inversion, Anti-Slop UI).
  - Runtime Consumer: `DNKShopifyOrchestrator.load_assimilated_conversion_rules()` dynamically loads these rules and extends `self.drift_rules` during theme drift detection.
- **`gerych_auditor`**: Emits `core/security/assimilated_audit_rules.json` with strict pre-commit test and security gates (Authorization Scope, Secret Exfiltration, Injection Guard).
  - Runtime Consumer: `AdversarialReviewEngine.load_assimilated_rules()` dynamically parses active audit rules and applies them during code and component reviews.
- **Tool Integration**: Invoked automatically inside `dnk_assimilate_tool` (`dnk_assimilate_repo`) Step 8 and returned directly in the tool's JSON output under the `"activation"` key.
- **Targeted Test Suite**: Full end-to-end verification covered by `tests/core/test_dna_assimilation_activation.py` (8/8 tests green: URL hygiene, identifier sanitization, rule emission, reference population, dynamic consumer loading, and active Hermes skill mirroring).

### 5. Safe Payload Defaults for Autonomous Swarm Info
When rendering templates or generating skills from multi-agent outputs, always use `.get()` with sensible fallbacks:
```python
worker = swarm_info.get("target_worker", "gerych_builder")
action = swarm_info.get("recommended_action", "Direct SOTA component synthesis and pattern adoption.")
component = swarm_info.get("target_component", "core/services/")
```

### 6. SCONES Expectation Validator URL Hygiene
When validating records for forbidden user directory paths:
1. Strip URLs (`re.sub(r'https?://\S+', '', value)`) before evaluating path regexes:
   ```python
   clean_val = re.sub(r'https?://\S+', '', raw_value)
   ```
2. Ensure drive-letter regexes require non-alphanumeric boundaries: `(?<![A-Za-z0-9])[A-Za-z]:[/\\](?![/\\])`.
