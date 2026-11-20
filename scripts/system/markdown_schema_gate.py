#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/markdown_schema_gate.py"
# purpose: "Deterministic Epistemic & Markdown Schema Gate for R&D, SOTA Audits, ADRs, and Contracts."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-16"
# author: "DNK-e.com Maksym & Antigravity Mentor"
# --- END DNK-MRH-HEADER ---

"""
Markdown Schema & Epistemic Armor Gate for DNK OS.

Enforces deterministic quality gates for non-code artifacts:
1. SOTA Audits & Research: Mandatory Dissent (3 Flaws), Boundary Conditions, Skeptic Alternative, Checklist.
2. ADRs: Context & Problem, Architectural Decision, Consequences & Trade-offs.
3. Contracts: Bounded Context, Invariants / Quality Gates.
4. Task Specs: Negative Scope (Anti-Scope), Whitelist Manifest, Tool Budget.
5. General Markdown: Valid MRH, min length (>= 80 words), zero placeholders (TODO, TBD, lorem ipsum),
   zero banned sycophantic praise tokens, zero absolute paths (/Users/...).
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dnk_md_triple_optics import audit_triple_optics  # noqa: E402

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

EXCLUDE_PARTS: Set[str] = {
    ".venv", "node_modules", ".git", ".next", "dist", "build",
    "__pycache__", ".pytest_cache", "coverage", "vendor", "cache",
    "sessions", "artifacts", ".data", ".od", ".worktrees", "skills", "templates", "archive", "self_heal", "my_task", "decisions", "distillations"
}

# Forbidden sycophantic flattery tokens
BANNED_PRAISE_PATTERNS = [
    (re.compile(r"(?i)\b(?:чудово|геніально|це ідеальне рішення|ви абсолютно маєте рацію|бездоганна ідея)[!.]?"), "SYCOPHANTIC_FLATTERY_TOKEN"),
    (re.compile(r"(?i)\b(?:brilliant idea|this is perfect|you are absolutely right|flawless approach)[!.]?"), "SYCOPHANTIC_FLATTERY_TOKEN"),
]

# Forbidden ungrounded placeholders
PLACEHOLDER_PATTERNS = [
    (re.compile(r"\b(?:TODO|TBD|FIXME)\s*:\s*\[?(?:insert|replace|fill|add)\b", re.IGNORECASE), "UNRESOLVED_PLACEHOLDER"),
    (re.compile(r"\b\[(?:INSERT|REPLACE|ADD)\s+[^\]]+\]", re.IGNORECASE), "UNRESOLVED_PLACEHOLDER"),
    (re.compile(r"\blorem\s+ipsum\b", re.IGNORECASE), "LOREM_IPSUM_PLACEHOLDER"),
]

ABSOLUTE_PATH_PATTERN = re.compile(r"/Users/[a-zA-Z0-9_\.]+/")


@dataclass
class MarkdownViolation:
    file_path: str
    line_number: int
    archetype: str
    violation_type: str
    description: str
    evidence: str


class MarkdownSchemaAuditor:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or _ROOT

    def detect_archetype(self, rel_path: str, content: str) -> str:
        lower_path = rel_path.lower()
        file_name = Path(rel_path).name.lower()
        first_header = content[:3000].lower()

        # Index and README files are always general documents, never specialized archetypes
        if file_name in ("00. index.md", "index.md", "readme.md") or file_name.endswith("_index.md"):
            return "GENERAL_DOC"

        # Explicit archetype declared in MRH header or YAML frontmatter
        mrh_match = re.search(r"archetype:\s*[\"']?([a-zA-Z_]+)[\"']?", first_header)
        if mrh_match:
            declared = mrh_match.group(1).upper()
            if declared in {
                "DEV_SPEC", "API_CONTRACT", "USER_GUIDE", "SOP_RUNBOOK",
                "AGENT_DIRECTIVE", "SKILL_SPEC", "ADR", "SOTA_AUDIT",
                "CONTRACT", "TASK_SPEC", "GENERAL_DOC"
            }:
                return declared

        if ("task-" in lower_path or file_name.startswith("task_")) and ("docs/tasks/" in lower_path or "tasks/" in lower_path):
            return "TASK_SPEC"
        if ("/adr/" in lower_path or file_name.startswith("adr-") or file_name.startswith("adr_") or "adr:" in first_header):
            return "ADR"
        if ("/contracts/" in lower_path or file_name.startswith("contract-") or file_name.startswith("contract_") or "contract:" in first_header):
            return "CONTRACT"
        if (
            "sota_audit" in file_name
            or "sota_assimilation" in file_name
            or "sota audit" in first_header
            or "sota assimilation" in first_header
            or ("/sota/" in lower_path and file_name != "00. index.md")
        ):
            return "SOTA_AUDIT"
        if "dev_spec" in file_name or "dev_spec" in first_header or "dev_spec:" in first_header:
            return "DEV_SPEC"
        if "api_contract" in file_name or "api_contract" in first_header or "api_contract:" in first_header:
            return "API_CONTRACT"
        if "user_guide" in file_name or "user_guide" in first_header or "user_guide:" in first_header or "керівництво користувача" in first_header:
            return "USER_GUIDE"
        if "sop_runbook" in file_name or "sop_runbook" in first_header or "runbook" in file_name:
            return "SOP_RUNBOOK"
        if "agent_directive" in file_name or "agent_directive" in first_header:
            return "AGENT_DIRECTIVE"
        if "skill_spec" in file_name or "skill_spec" in first_header:
            return "SKILL_SPEC"

        return "GENERAL_DOC"

    def audit_content(self, rel_path: str, content: str) -> List[MarkdownViolation]:
        violations: List[MarkdownViolation] = []
        lines = content.splitlines()
        words = content.split()
        archetype = self.detect_archetype(rel_path, content)

        # 1. Minimum Density (Reject empty stubs < 40 words, excluding short index files)
        file_name = Path(rel_path).name.lower()
        is_index = file_name in ("00. index.md", "index.md", "readme.md") or file_name.endswith("_index.md")
        if len(words) < 40 and not is_index:
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype=archetype,
                violation_type="SHALLOW_CONTENT",
                description=f"Document has only {len(words)} words (minimum 40 required to prevent empty stub compliance).",
                evidence=""
            ))

        # 2. MRH Header Check (Standard DNK-MRH-HEADER or Obsidian YAML frontmatter with status)
        has_dnk_mrh = "--- DNK-MRH-HEADER ---" in content or "<!-- --- DNK-MRH-HEADER ---" in content
        has_yaml_frontmatter = (
            content.startswith("---\n")
            and "\nstatus:" in content[:500]
            and "\n---" in content[4:800]
        )
        if not (has_dnk_mrh or has_yaml_frontmatter):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype=archetype,
                violation_type="MISSING_MRH_HEADER",
                description="Missing mandatory Machine-Readable Header (DNK-MRH-HEADER) or YAML frontmatter with status.",
                evidence=lines[0] if lines else ""
            ))
        elif has_dnk_mrh:
            # Verify required fields for standard DNK-MRH-HEADER
            for req_field in ("mrh_id:", "purpose:", "status:"):
                if req_field not in content:
                    violations.append(MarkdownViolation(
                        file_path=rel_path,
                        line_number=1,
                        archetype=archetype,
                        violation_type="INCOMPLETE_MRH_HEADER",
                        description=f"MRH header is missing required key '{req_field}'.",
                        evidence=""
                    ))

        # 3. Path Hygiene Check (/Users/...)
        for i, line in enumerate(lines, 1):
            if ABSOLUTE_PATH_PATTERN.search(line):
                violations.append(MarkdownViolation(
                    file_path=rel_path,
                    line_number=i,
                    archetype=archetype,
                    violation_type="ABSOLUTE_PATH_LEAK",
                    description="Detected forbidden absolute path (/Users/...). Must use relative paths.",
                    evidence=line.strip()
                ))

        # 3b. Triple-Optics Contract (frontmatter keys + single MRH callout + callout proximity)
        triple = audit_triple_optics(rel_path, content)
        for reason in triple.reasons():
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=triple.callout_line or 1,
                archetype=archetype,
                violation_type="TRIPLE_OPTICS_VIOLATION",
                description=reason,
                evidence=lines[0] if lines else ""
            ))

        # 4. Sycophantic Flattery & Hollow Praise
        for pat, v_type in BANNED_PRAISE_PATTERNS:
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                # Ignore lines that are defining negative rules or quoting banned tokens
                if any(w in line_lower for w in ("banned", "forbidden", "prohibited", "zero flattery", "anti-sycophancy", "rule:", "rules")):
                    continue
                if pat.search(line):
                    violations.append(MarkdownViolation(
                        file_path=rel_path,
                        line_number=i,
                        archetype=archetype,
                        violation_type=v_type,
                        description="Forbidden sycophantic flattery / hollow praise token detected (AGENTS.md Section 6 violation).",
                        evidence=line.strip()
                    ))

        # 5. Placeholders Check
        for pat, v_type in PLACEHOLDER_PATTERNS:
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                # Ignore lines defining negative rules that explicitly forbid placeholders
                if any(w in line_lower for w in ("заборон", "forbidden", "prohibited", "banned", "rule:", "rules", "не дозволя")):
                    continue
                if pat.search(line):
                    violations.append(MarkdownViolation(
                        file_path=rel_path,
                        line_number=i,
                        archetype=archetype,
                        violation_type=v_type,
                        description="Unresolved placeholder detected. Document must be fully formulated before sealing.",
                        evidence=line.strip()
                    ))

        # 6. Archetype-Specific Epistemic Invariants
        if archetype == "SOTA_AUDIT":
            self._audit_sota_sections(rel_path, content, violations)
        elif archetype == "ADR":
            self._audit_adr_sections(rel_path, content, violations)
        elif archetype == "CONTRACT":
            self._audit_contract_sections(rel_path, content, violations)
        elif archetype == "TASK_SPEC":
            self._audit_task_spec_sections(rel_path, content, violations)
        elif archetype == "DEV_SPEC":
            self._audit_dev_spec_sections(rel_path, content, violations)
        elif archetype == "API_CONTRACT":
            self._audit_api_contract_sections(rel_path, content, violations)
        elif archetype == "USER_GUIDE":
            self._audit_user_guide_sections(rel_path, content, violations)
        elif archetype == "SOP_RUNBOOK":
            self._audit_sop_runbook_sections(rel_path, content, violations)
        elif archetype == "AGENT_DIRECTIVE":
            self._audit_agent_directive_sections(rel_path, content, violations)
        elif archetype == "SKILL_SPEC":
            self._audit_skill_spec_sections(rel_path, content, violations)

        return violations

    def _get_body(self, content: str) -> str:
        """Strips the MRH header to inspect only the markdown body content."""
        if "--- END DNK-MRH-HEADER ---" in content:
            return content.split("--- END DNK-MRH-HEADER ---", 1)[1]
        if "--- END DNK-MRH-HEADER -->" in content:
            return content.split("--- END DNK-MRH-HEADER -->", 1)[1]
        return content

    def _audit_sota_sections(self, rel_path: str, content: str, violations: List[MarkdownViolation]):
        """SOTA Audits must enforce the Mandatory Dissent & Epistemic Armor (Rule of 3 Flaws)."""
        body_lower = self._get_body(content).lower()

        # 1. Summary / Analysis
        if not re.search(r"##\s+.*(?:суть|аналіз|дослідження|overview|summary|порівняльний)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="SOTA_AUDIT",
                violation_type="MISSING_SOTA_SUMMARY",
                description="SOTA Audit missing Research Summary / Comparative Analysis section heading (## ...).",
                evidence=""
            ))

        # 2. Mandatory Dissent (3 Flaws / Hidden Risks)
        if not re.search(r"##\s+.*(?:дисципліна скептика|приховані ризики|3 ризики|3 flaws|hidden risks|dissent)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="SOTA_AUDIT",
                violation_type="MISSING_MANDATORY_DISSENT",
                description="SOTA Audit missing Mandatory Dissent / 3 Hidden Risks section heading (## ...).",
                evidence=""
            ))

        # 3. Boundary Conditions
        if not re.search(r"##\s+.*(?:граничні умови|boundary conditions)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="SOTA_AUDIT",
                violation_type="MISSING_BOUNDARY_CONDITIONS",
                description="SOTA Audit missing Boundary Conditions section heading (## ...).",
                evidence=""
            ))

        # 4. Skeptic Alternative
        if not re.search(r"##\s+.*(?:скептична альтернатива|skeptic alternative|minimalist solution|канонічна архітектура)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="SOTA_AUDIT",
                violation_type="MISSING_SKEPTIC_ALTERNATIVE",
                description="SOTA Audit missing Skeptic Alternative / Minimalist Solution section heading (## ...).",
                evidence=""
            ))

        # 5. Implementation Plan with Checklist
        has_plan = re.search(r"##\s+.*(?:покроковий план|implementation plan|roadmap|план впровадження)", body_lower)
        has_checklist = "- [ ]" in content or "- [x]" in content or "* [ ]" in content or "* [x]" in content
        if not (has_plan and has_checklist):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="SOTA_AUDIT",
                violation_type="MISSING_ACTIONABLE_PLAN",
                description="SOTA Audit missing actionable Implementation Plan section (## ...) with checklist items (- [ ] / - [x]).",
                evidence=""
            ))

    def _audit_adr_sections(self, rel_path: str, content: str, violations: List[MarkdownViolation]):
        body_lower = self._get_body(content).lower()
        if not re.search(r"(?:контекст|проблематика|context|problem)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="ADR",
                violation_type="MISSING_ADR_CONTEXT",
                description="ADR missing Context & Problem Statement section.",
                evidence=""
            ))
        if not re.search(r"(?:архітектурне рішення|рішення|decision|solution)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="ADR",
                violation_type="MISSING_ADR_DECISION",
                description="ADR missing Architectural Decision section.",
                evidence=""
            ))
        if not re.search(r"(?:наслідки|компроміси|ризики|consequences|trade-offs)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="ADR",
                violation_type="MISSING_ADR_CONSEQUENCES",
                description="ADR missing Consequences / Trade-offs / Risks section.",
                evidence=""
            ))

    def _audit_contract_sections(self, rel_path: str, content: str, violations: List[MarkdownViolation]):
        body_lower = self._get_body(content).lower()
        if not re.search(r"(?:призначення|мета|purpose|scope|bounded context)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="CONTRACT",
                violation_type="MISSING_CONTRACT_PURPOSE",
                description="Contract missing Purpose & Bounded Context section.",
                evidence=""
            ))
        if not re.search(r"(?:інваріант|правил|гейт|інтерфейс|invariants|rules|gates|schema)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="CONTRACT",
                violation_type="MISSING_CONTRACT_INVARIANTS",
                description="Contract missing Invariants, Verification Gates, or Protocol Rules section.",
                evidence=""
            ))

    def _audit_task_spec_sections(self, rel_path: str, content: str, violations: List[MarkdownViolation]):
        body_lower = self._get_body(content).lower()
        if not re.search(r"(?:negative scope|anti-scope|заборон)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="TASK_SPEC",
                violation_type="MISSING_TASK_ANTISCOPE",
                description="Task Spec missing Negative Scope / Anti-Scope boundaries (mandatory ADR-006).",
                evidence=""
            ))
        if not re.search(r"(?:targeted file|manifest|whitelist|маніфест)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="TASK_SPEC",
                violation_type="MISSING_TASK_WHITELIST",
                description="Task Spec missing Targeted File Whitelist Manifest.",
                evidence=""
            ))

    def _audit_dev_spec_sections(self, rel_path: str, content: str, violations: List[MarkdownViolation]):
        body_lower = self._get_body(content).lower()
        if not re.search(r"##\s+.*(?:призначення|bounded context|purpose|scope|контекст)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="DEV_SPEC",
                violation_type="MISSING_DEV_SPEC_PURPOSE",
                description="DEV_SPEC missing Purpose & Bounded Context section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:архітектур|модел|data model|dto|схем|architecture|models)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="DEV_SPEC",
                violation_type="MISSING_DEV_SPEC_ARCHITECTURE",
                description="DEV_SPEC missing Architecture & Data Models section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:інваріант|граничн|invariants|boundary|limits)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="DEV_SPEC",
                violation_type="MISSING_DEV_SPEC_INVARIANTS",
                description="DEV_SPEC missing System Invariants or Boundary Conditions section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:верифікац|план|verification|quality gate|tests?)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="DEV_SPEC",
                violation_type="MISSING_DEV_SPEC_VERIFICATION",
                description="DEV_SPEC missing Deterministic Verification Plan section (## ...).",
                evidence=""
            ))

    def _audit_api_contract_sections(self, rel_path: str, content: str, violations: List[MarkdownViolation]):
        body_lower = self._get_body(content).lower()
        if not re.search(r"##\s+.*(?:призначення|bounded context|purpose|scope|контекст)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="API_CONTRACT",
                violation_type="MISSING_API_CONTRACT_PURPOSE",
                description="API_CONTRACT missing Purpose & Bounded Context section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:ендпоінт|специфікац|запит|відповід|endpoints?|dto|payload|schemas?)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="API_CONTRACT",
                violation_type="MISSING_API_CONTRACT_ENDPOINTS",
                description="API_CONTRACT missing Endpoints Specification or Payload section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:каталог помилок|коди помилок|помилк|error catalog|errors?|status codes?)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="API_CONTRACT",
                violation_type="MISSING_API_CONTRACT_ERRORS",
                description="API_CONTRACT missing Error Catalog or Status Codes section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:інваріант|ідемпотент|invariants|idempotency)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="API_CONTRACT",
                violation_type="MISSING_API_CONTRACT_INVARIANTS",
                description="API_CONTRACT missing Invariants or Idempotency Rules section (## ...).",
                evidence=""
            ))

    def _audit_user_guide_sections(self, rel_path: str, content: str, violations: List[MarkdownViolation]):
        body_lower = self._get_body(content).lower()
        if not re.search(r"##\s+.*(?:призначення|огляд|аудиторі|overview|target audience|мета|для кого)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="USER_GUIDE",
                violation_type="MISSING_USER_GUIDE_OVERVIEW",
                description="USER_GUIDE missing Overview & Target Audience section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:передумов|підготовк|prerequisites|перед тим)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="USER_GUIDE",
                violation_type="MISSING_USER_GUIDE_PREREQUISITES",
                description="USER_GUIDE missing Prerequisites section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:покроков|інструкці|крок|workflow|steps|налаштування)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="USER_GUIDE",
                violation_type="MISSING_USER_GUIDE_WORKFLOW",
                description="USER_GUIDE missing Step-by-Step Workflow section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:перевірк|результат|verification|expected results?|успішн)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="USER_GUIDE",
                violation_type="MISSING_USER_GUIDE_VERIFICATION",
                description="USER_GUIDE missing Result Verification section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:faq|troubleshooting|часті запитання|проблем|вирішення проблем)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="USER_GUIDE",
                violation_type="MISSING_USER_GUIDE_FAQ",
                description="USER_GUIDE missing FAQ or Troubleshooting section (## ...).",
                evidence=""
            ))

    def _audit_sop_runbook_sections(self, rel_path: str, content: str, violations: List[MarkdownViolation]):
        body_lower = self._get_body(content).lower()
        if not re.search(r"##\s+.*(?:мета|тригер|purpose|trigger|запуск)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="SOP_RUNBOOK",
                violation_type="MISSING_SOP_TRIGGER",
                description="SOP_RUNBOOK missing Purpose & Trigger section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:ролі|відповідальн|roles|responsibilities|виконавець)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="SOP_RUNBOOK",
                violation_type="MISSING_SOP_ROLES",
                description="SOP_RUNBOOK missing Roles & Responsibilities section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:чек-ліст|операційн|інструкці|дії|procedure|steps|checklist)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="SOP_RUNBOOK",
                violation_type="MISSING_SOP_STEPS",
                description="SOP_RUNBOOK missing Operational Steps / Checklist section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:відкат|аварійний|rollback|recovery)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="SOP_RUNBOOK",
                violation_type="MISSING_SOP_ROLLBACK",
                description="SOP_RUNBOOK missing Rollback Procedure section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:перевірк|фіксація|результат|verification|sign-off|log)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="SOP_RUNBOOK",
                violation_type="MISSING_SOP_VERIFICATION",
                description="SOP_RUNBOOK missing Verification & Sign-off section (## ...).",
                evidence=""
            ))

    def _audit_agent_directive_sections(self, rel_path: str, content: str, violations: List[MarkdownViolation]):
        body_lower = self._get_body(content).lower()
        if not re.search(r"##\s+.*(?:роль|персон|role|persona|bounded scope|місія)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="AGENT_DIRECTIVE",
                violation_type="MISSING_AGENT_ROLE",
                description="AGENT_DIRECTIVE missing Role & Persona section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:інструмент|whitelist|tool|дозволен|sanctioned)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="AGENT_DIRECTIVE",
                violation_type="MISSING_AGENT_TOOLS",
                description="AGENT_DIRECTIVE missing Sanctioned Tools Whitelist section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:negative scope|anti-scope|заборон)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="AGENT_DIRECTIVE",
                violation_type="MISSING_AGENT_ANTISCOPE",
                description="AGENT_DIRECTIVE missing Negative Scope (Anti-Scope) section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:протокол|алгоритм|dag|execution protocol|workflow|етап)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="AGENT_DIRECTIVE",
                violation_type="MISSING_AGENT_PROTOCOL",
                description="AGENT_DIRECTIVE missing Execution Protocol section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:критерії завершення|definition of done|dod|результат|успіх)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="AGENT_DIRECTIVE",
                violation_type="MISSING_AGENT_DOD",
                description="AGENT_DIRECTIVE missing Definition of Done (DoD) section (## ...).",
                evidence=""
            ))

    def _audit_skill_spec_sections(self, rel_path: str, content: str, violations: List[MarkdownViolation]):
        body_lower = self._get_body(content).lower()
        if not re.search(r"##\s+.*(?:призначення|тригер|overview|activation|тригери)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="SKILL_SPEC",
                violation_type="MISSING_SKILL_OVERVIEW",
                description="SKILL_SPEC missing Overview & Activation Triggers section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:інструмент|оточення|prerequisites|tools)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="SKILL_SPEC",
                violation_type="MISSING_SKILL_TOOLS",
                description="SKILL_SPEC missing Tools & Prerequisites section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:алгоритм|покроков|workflow|instructions|крок)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="SKILL_SPEC",
                violation_type="MISSING_SKILL_WORKFLOW",
                description="SKILL_SPEC missing Workflow & Instructions section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:рівні деталізації|додаткові матеріали|lod|references|scripts)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="SKILL_SPEC",
                violation_type="MISSING_SKILL_LOD",
                description="SKILL_SPEC missing Level-of-Detail (LOD) References section (## ...).",
                evidence=""
            ))
        if not re.search(r"##\s+.*(?:критерії успіху|критерії завершення|definition of done|dod)", body_lower):
            violations.append(MarkdownViolation(
                file_path=rel_path, line_number=1, archetype="SKILL_SPEC",
                violation_type="MISSING_SKILL_DOD",
                description="SKILL_SPEC missing Definition of Done section (## ...).",
                evidence=""
            ))

    def audit_file(self, path: Path) -> List[MarkdownViolation]:
        try:
            rel_path = str(path.relative_to(self.repo_root))
        except ValueError:
            rel_path = str(path)
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as err:
            return [MarkdownViolation(
                file_path=rel_path,
                line_number=1,
                archetype="UNKNOWN",
                violation_type="FILE_READ_ERROR",
                description=f"Cannot read markdown file: {err}",
                evidence=""
            )]
        return self.audit_content(rel_path, content)

    def get_affected_markdown_files(self) -> List[Path]:
        try:
            res = subprocess.run(
                ["git", "-c", "core.quotepath=false", "status", "--porcelain"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                check=True
            )
        except Exception:
            return []

        affected = []
        for line in res.stdout.splitlines():
            if len(line) < 4:
                continue
            status = line[:2]
            raw_path = line[3:].strip()
            if " -> " in raw_path:
                raw_path = raw_path.split(" -> ")[1].strip()
            if raw_path.startswith('"') and raw_path.endswith('"'):
                raw_path = raw_path[1:-1]

            # Only check staged files (in index) or modified tracked files in work tree
            is_staged = status[0] in ("M", "A", "R", "C")
            is_tracked_modified = status[1] == "M"

            if not (is_staged or is_tracked_modified):
                continue

            p = self.repo_root / raw_path
            if p.suffix != ".md" or not p.is_file():
                continue
            if any(part in p.parts for part in EXCLUDE_PARTS):
                continue

            affected.append(p)
        return affected

    def run(self, files: Optional[List[Path]] = None) -> Tuple[bool, List[MarkdownViolation]]:
        target_files = files if files is not None else self.get_affected_markdown_files()
        all_violations: List[MarkdownViolation] = []

        for f in target_files:
            if f.is_file() and f.suffix == ".md":
                violations = self.audit_file(f)
                all_violations.extend(violations)

        passed = len(all_violations) == 0
        return passed, all_violations


def main():
    parser = argparse.ArgumentParser(description="Markdown Schema & Epistemic Gate for DNK OS")
    parser.add_argument("--affected", action="store_true", help="Audit only affected/modified markdown files (default)")
    parser.add_argument("--all", action="store_true", help="Audit all markdown files in the workspace")
    parser.add_argument("files", nargs="*", help="Explicit markdown files to audit")
    args = parser.parse_args()

    target_root = _ROOT
    if args.files:
        files = [Path(f).resolve() for f in args.files]
        if files:
            # Detect root for the specified files
            first_file = files[0]
            for parent in first_file.parents:
                if (parent / ".git").exists() or parent == Path.cwd():
                    target_root = parent
                    break
    elif args.all:
        files = [p for p in _ROOT.glob("docs/**/*.md") if not any(part in p.parts for part in EXCLUDE_PARTS)]
    else:
        files = MarkdownSchemaAuditor(_ROOT).get_affected_markdown_files()

    gate = MarkdownSchemaAuditor(target_root)

    print(f"🛡️ [Markdown Schema Gate] Inspecting {len(files)} markdown document(s)...")
    passed, violations = gate.run(files)

    if not passed:
        print("\n❌ MARKDOWN SCHEMA GATE BREACH: Non-compliant or hollow documentation detected!\n")
        for v in violations:
            print(f"  🚨 [{v.archetype} -> {v.violation_type}] {v.file_path}:{v.line_number}")
            print(f"     Description: {v.description}")
            if v.evidence:
                print(f"     Evidence:    {v.evidence}")
            print()
        print("💡 REMEDY: Epistemic armor requires all sections (3 Flaws, Boundaries, Checklist) to be fully formulated.")
        sys.exit(1)

    print(f"✅ Markdown Schema Gate Passed: 0 schema violations across {len(files)} document(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
