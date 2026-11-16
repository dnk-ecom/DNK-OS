# --- DNK-MRH-HEADER ---
# mrh_id: "core_skills_curator_py"
# purpose: "Autonomous Skill Curator & Observation Ingestion Engine (Assimilated from rebelytics/one-skill-to-rule-them-all)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-21"
# author: "DNK Swarm (dnk_dev_fullstack & Gerych Prime)"
# --- END DNK-MRH-HEADER ---

"""
skills_curator.py — Autonomous Skill Curation, Continuous Observation, and Invariant Ratchet.

Assimilated patterns:
1. Session-start / Background Observation ingestion without context bloat.
2. 4-Vector Generalisability Test (filters out one-off noise from general rules).
3. Second Violation Invariant enforcement (forces structural barriers for repeated faults).
4. Sibling Family propagation (cross-pollinates fixes across related skills).
5. Clean Markdown Digest generation for Obsidian Vault (./docs/notes/).
"""

import argparse
import datetime
import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# Known Skill Families for Sibling Propagation
SKILL_FAMILIES = {
    "ecommerce": [
        "dnk-shopify",
        "shopify-theme-ast-engineering",
    ],
    "media_video": [
        "dnk-video-ai-creator",
        "video-retention-engineering",
        "word-anchored-shorts",
    ],
    "swarm_orchestration": [
        "dnk-swarm-orchestration",
        "beads-task-forest-integration",
        "hermes-agent",
    ],
    "engineering_quality": [
        "architecture-invariants-and-blast-radius",
        "systematic-debugging",
        "test-driven-development",
        "requesting-code-review",
    ],
    "memory_knowledge": [
        "obsidian",
        "obsidian-vault-hygiene",
        "review-gated-ingest",
        "sota-repository-assimilation",
    ],
}


@dataclass
class SkillObservation:
    id: str
    skill_name: str
    trigger_context: str
    user_correction: str
    failure_mode: str
    violation_count: int = 1
    generality_score: float = 0.0
    structural_barrier_required: bool = False
    sibling_skills_checked: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    status: str = "pending"  # pending, staged, promoted, dismissed


class SkillsCurator:
    def __init__(self, hub_root: Optional[Path] = None, storage_dir: Optional[Path] = None):
        if hub_root is None:
            self.hub_root = Path(__file__).resolve().parent.parent
        else:
            self.hub_root = Path(hub_root)

        if storage_dir is None:
            self.storage_dir = self.hub_root / "core" / "orchestrator" / "agents" / "gerych_prime" / "skill-observations"
        else:
            self.storage_dir = Path(storage_dir)

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.obs_file = self.storage_dir / "observations_ledger.json"
        self._load_ledger()

    def _load_ledger(self):
        if self.obs_file.exists():
            try:
                data = json.loads(self.obs_file.read_text(encoding="utf-8"))
                self.observations = [SkillObservation(**item) for item in data]
            except Exception:
                self.observations = []
        else:
            self.observations = []

    def _save_ledger(self):
        data = [asdict(obs) for obs in self.observations]
        self.obs_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def record_observation(
        self,
        skill_name: str,
        trigger_context: str,
        user_correction: str,
        failure_mode: str,
        violation_count: int = 1,
    ) -> SkillObservation:
        """Records a new observation and runs evaluation gates."""
        obs_id = f"obs-{len(self.observations) + 1:04d}-{re.sub(r'[^a-z0-9]+', '-', skill_name.lower())[:30]}"
        
        # Check existing observations for this skill/failure mode to increment violation count
        for prev in self.observations:
            if prev.skill_name == skill_name and prev.failure_mode == failure_mode:
                violation_count = max(violation_count, prev.violation_count + 1)
                break

        obs = SkillObservation(
            id=obs_id,
            skill_name=skill_name,
            trigger_context=trigger_context,
            user_correction=user_correction,
            failure_mode=failure_mode,
            violation_count=violation_count,
        )

        # 1. 4-Vector Generalisability Test
        obs.generality_score = self.evaluate_generality(obs)

        # 2. Second Violation Invariant
        if obs.violation_count >= 2:
            obs.structural_barrier_required = True

        # 3. Sibling Propagation Analysis
        obs.sibling_skills_checked = self.find_sibling_skills(skill_name)

        self.observations.append(obs)
        self._save_ledger()
        return obs

    def evaluate_generality(self, obs: SkillObservation) -> float:
        """
        4-Vector Generalisability Test:
        - v1: Multi-project applicability (not tied to specific ephemeral customer/variable names)
        - v2: Rule/Workflow vs one-off artifact (describes invariant or procedure)
        - v3: Frequency / severity (repeated violation or explicit user steering)
        - v4: Actionable structural solution identified
        """
        score = 0.0

        # V1: Check absence of ultra-specific ephemeral tokens (UUIDs, raw temp paths)
        if not re.search(r"(/tmp|var/folders|[0-9a-f]{8}-[0-9a-f]{4})", obs.trigger_context + obs.user_correction):
            score += 0.25

        # V2: Identifies rule/invariant keywords
        rule_keywords = ["must", "invariant", "never", "always", "schema", "timeout", "path", "header", "order"]
        combined = (obs.user_correction + " " + obs.failure_mode).lower()
        if any(kw in combined for kw in rule_keywords):
            score += 0.25

        # V3: Explicit user correction or repeated violation
        if obs.violation_count >= 2 or len(obs.user_correction.strip()) > 10:
            score += 0.25

        # V4: Failure mode is structured and categorizable
        if len(obs.failure_mode) > 5 and not obs.failure_mode.startswith("unknown"):
            score += 0.25

        return round(score, 2)

    def find_sibling_skills(self, skill_name: str) -> List[str]:
        """Identifies related skills within the same family."""
        clean_name = skill_name.lower().replace("_", "-")
        siblings: Set[str] = set()
        for family, members in SKILL_FAMILIES.items():
            if any(clean_name in m or m in clean_name for m in members):
                for m in members:
                    if m != clean_name and m != skill_name:
                        siblings.add(m)
        return sorted(list(siblings))

    def generate_digest_markdown(self, title: str = "Skill Curator & Continuous Improvement Digest") -> str:
        """Generates an Obsidian-compliant Markdown digest with MRH header."""
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        total = len(self.observations)
        pending = [o for o in self.observations if o.status == "pending"]
        structural_req = [o for o in self.observations if o.structural_barrier_required]

        md = f"""# --- DNK-MRH-HEADER ---
# mrh_id: "docs_notes_skill_curator_digest_md"
# purpose: "{title}"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')}"
# author: "SkillsCurator (DNK OS Swarm)"
# --- END DNK-MRH-HEADER ---

# 🧬 {title}
*Last Synced: {now_str} | Total Observations: {total} | Pending: {len(pending)} | Structural Barriers Required: {len(structural_req)}*

## 📊 Summary Pulse
- **High-Generality Opportunities (Score ≥ 0.75)**: {len([o for o in self.observations if o.generality_score >= 0.75])}
- **Second Violation Invariant Triggers (2+ Occurrences)**: {len(structural_req)}
- **Sibling Propagation Audits**: {sum(len(o.sibling_skills_checked) for o in self.observations)}

---

## 🚨 Second Violation Invariants (Deterministic Barrier Required)
> *Rule: If an agent violates a rule twice, DO NOT reword prompts. Build a hook, AST check, or linter.*

"""
        if not structural_req:
            md += "_No recurring violations requiring structural barriers detected._\n\n"
        else:
            for obs in structural_req:
                md += f"""### ⚠️ `{obs.skill_name}`: {obs.failure_mode}
- **Observation ID**: `{obs.id}`
- **Violations Count**: {obs.violation_count}
- **User Correction**: {obs.user_correction}
- **Mandated Structural Action**: Implement pre-tool hook check in `scripts/system/hermes_pre_tool_hook.py` or unit test in `tests/`.
- **Siblings to Protect**: {', '.join(f'`{s}`' for s in obs.sibling_skills_checked) if obs.sibling_skills_checked else 'None'}

"""

        md += """---

## 🔍 Pending Observations Queue (Evaluated via Generalisability Test)

"""
        if not pending:
            md += "_Queue is clear. No pending observations._\n"
        else:
            for obs in pending:
                badge = "🟢 General" if obs.generality_score >= 0.75 else ("🟡 Specific" if obs.generality_score >= 0.5 else "⚪ One-Off")
                md += f"""#### [{badge} {obs.generality_score}] `{obs.skill_name}` — `{obs.id}`
- **Failure Mode**: {obs.failure_mode}
- **Context**: {obs.trigger_context}
- **Correction**: {obs.user_correction}
- **Siblings Checked**: {', '.join(obs.sibling_skills_checked) if obs.sibling_skills_checked else 'None'}
- **Action**: {'Stage into SKILL.md' if obs.generality_score >= 0.75 else 'Archive as specific incident'}

"""

        return md

    def export_digest_to_notes(self, filename: str = "Skill Curator Digest.md") -> Path:
        """Writes the digest to Obsidian vault directory ./docs/notes/."""
        notes_dir = self.hub_root / "docs" / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        target = notes_dir / filename
        content = self.generate_digest_markdown()
        target.write_text(content, encoding="utf-8")
        return target


def main() -> int:
    parser = argparse.ArgumentParser(description="DNK OS Autonomous Skill Curator")
    parser.add_argument("--record", action="store_true", help="Record a test observation")
    parser.add_argument("--skill", default="dnk-shopify", help="Target skill name")
    parser.add_argument("--correction", default="Must use relative paths only", help="User correction")
    parser.add_argument("--failure", default="used absolute path", help="Failure mode")
    parser.add_argument("--context", default="File export step", help="Trigger context")
    parser.add_argument("--export-digest", action="store_true", help="Export digest to ./docs/notes/")
    parser.add_argument("--summary", action="store_true", help="Print summary of observations")
    args = parser.parse_args()

    curator = SkillsCurator()

    if args.record:
        obs = curator.record_observation(
            skill_name=args.skill,
            trigger_context=args.context,
            user_correction=args.correction,
            failure_mode=args.failure,
        )
        print(f"✅ Recorded observation: {obs.id} (Generality: {obs.generality_score}, Barrier: {obs.structural_barrier_required})")
        print(f"   Siblings checked: {obs.sibling_skills_checked}")

    if args.export_digest:
        dest = curator.export_digest_to_notes()
        print(f"📝 Digest exported to: {dest}")

    if args.summary or (not args.record and not args.export_digest):
        print(f"📊 Total observations: {len(curator.observations)}")
        req = [o for o in curator.observations if o.structural_barrier_required]
        print(f"🚨 Structural barriers required: {len(req)}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
