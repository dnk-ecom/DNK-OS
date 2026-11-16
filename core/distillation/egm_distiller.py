# --- DNK-MRH-HEADER ---
# mrh_id: "core/distillation/egm_distiller.py"
# purpose: "Elephant-Goldfish & Harness2 Knowledge Distillation Engine for DNK OS and DNK-Ecom_OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-28"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

"""
Elephant-Goldfish & Harness² Knowledge Distillation Engine (DEC-046).

Assimilates architecture from:
1. Google Elephant-Goldfish Model (EGM): Elephant (Deep-context synthesis) + Goldfish (Zero-context adversarial audit).
2. Google Research Harness² (arXiv:2610.14224): Propose-Probe-Compose recursion & experience reflection.
3. EntireIO AST Graph & Diff Index: Code-locus verified memory and anchor stability.

Distills noisy architectural documentation, ADRs, and SOTA digests into:
- Tier A (Agent): STE-Agentic concise rules (Simplified Technical English, <= 25 words per step, imperative action verbs).
- Tier B (Human): Clean Fumadocs/MDX pages with strict MRH headers & boundary rationale.
- Tier C (Durable Facts): Deterministic SQLite FTS5 facts anchored to AST symbols/files.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from core.memory.scones_anchor_verifier import AnchorRef, SconesAnchorVerifier
from core.memory.scones_bm25_index import DurableFact, SconesBM25Index

logger = logging.getLogger("dnk.core.distillation.egm")

# Words strictly banned by Anti-Sycophancy Invariant
BANNED_FLUFF_TOKENS = {
    "чудово",
    "чудовий",
    "чудова",
    "геніально",
    "геніальний",
    "ідеально",
    "ідеальний",
    "ідеальне",
    "прекрасно",
    "неймовірно",
    "дивовижно",
    "perfect",
    "amazing",
    "revolutionary",
    "game-changer",
    "flawless",
    "masterpiece",
    "magnificent",
}

VALID_STE_VERBS = {
    "RUN",
    "CHECK",
    "VERIFY",
    "ABORT",
    "ENSURE",
    "DISPATCH",
    "PATCH",
    "TEST",
    "LOAD",
    "READ",
    "WRITE",
    "SCAN",
    "INDEX",
    "VALIDATE",
    "DEPLOY",
    "HALT",
    "EMIT",
    "DELEGATE",
    "MUST",
    "PREFER",
    "RESTRICT",
    "FORBID",
}


@dataclass
class DistillationCandidate:
    """Raw candidate produced by the Elephant synthesizer."""
    candidate_id: str
    title: str
    category: str
    source_path: str
    raw_content: str
    human_tier: str = ""
    agent_tier: str = ""
    durable_facts: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistillationResult:
    """Outcome of Goldfish adversarial audit and Harness² composition."""
    candidate_id: str
    accepted: bool
    scores: Dict[str, float]
    critique: List[str]
    distilled_human_tier: Optional[str] = None
    distilled_agent_tier: Optional[str] = None
    verified_facts: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ElephantHarvester:
    """
    Elephant Synthesizer: Scans deep project context and digests raw knowledge into candidate structures.
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    def parse_frontmatter(self, text: str) -> Tuple[Dict[str, str], str]:
        """Extract frontmatter and body from markdown text."""
        metadata: Dict[str, str] = {}
        body = text

        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm_text = parts[1]
                body = parts[2].strip()
                for line in fm_text.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip('"\'')

        return metadata, body

    def harvest_file_all(self, file_path: Path) -> List[DistillationCandidate]:
        """Read a file and draft dual-tier candidates (handles single docs or registry tables)."""
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
        dec_candidates = self._extract_decision_table_candidates(file_path, raw_text)
        if dec_candidates:
            return dec_candidates
        return [self.harvest_file(file_path)]

    def _extract_decision_table_candidates(self, file_path: Path, raw_text: str) -> List[DistillationCandidate]:
        candidates: List[DistillationCandidate] = []
        rel_path = file_path.relative_to(self.workspace_root) if file_path.is_absolute() else file_path

        pattern = re.compile(r'\|\s*\*\*?(DEC-\d+)\*\*?\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|', re.IGNORECASE)
        for match in pattern.finditer(raw_text):
            dec_id = match.group(1).upper()
            topic = match.group(2).strip()
            standard = match.group(3).strip()
            status = match.group(4).strip()

            clean_standard = standard.replace("**", "").replace("`", "")

            human_mdx = f"""---
title: "{dec_id}: {topic}"
description: "{clean_standard[:150]}"
status: "{status}"
category: "01_architecture_decisions"
---

# {dec_id}: {topic}

## Architectural Standard
{standard}

## Status
{status}
"""
            agent_ste = f"""---
id: "{dec_id}"
type: "decision_rule"
status: "{status}"
---

# {dec_id} Action Rules

1. ENSURE system adheres to standard: {clean_standard[:200]}.
2. REJECT conflicting implementations that violate {dec_id}.
3. VERIFY compliance with {dec_id} before closing task.
"""
            facts = [
                {
                    "id": dec_id.lower(),
                    "topic": f"{dec_id.lower()}: {topic.lower()}",
                    "statement": clean_standard,
                    "category": "01_architecture_decisions",
                    "file_anchor": str(rel_path),
                    "symbol_anchor": dec_id,
                }
            ]
            candidates.append(
                DistillationCandidate(
                    candidate_id=dec_id.lower(),
                    title=f"{dec_id}: {topic}",
                    category="01_architecture_decisions",
                    source_path=str(rel_path),
                    raw_content=match.group(0),
                    human_tier=human_mdx,
                    agent_tier=agent_ste,
                    durable_facts=facts,
                    tags=["dec", "architecture", dec_id.lower()],
                    metadata={"status": status, "id": dec_id},
                )
            )
        return candidates

    def harvest_file(self, file_path: Path) -> DistillationCandidate:
        """Read a file and draft dual-tier candidate."""
        rel_path = file_path.relative_to(self.workspace_root) if file_path.is_absolute() else file_path
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")

        meta, body = self.parse_frontmatter(raw_text)

        # Candidate ID from filename or frontmatter
        stem = file_path.stem.lower().replace(" ", "-")
        cid = meta.get("id") or meta.get("mrh_id") or stem
        title = meta.get("title") or stem.replace("-", " ").title()

        # Categorize
        category = "architecture"
        if "inv-" in stem or "invariant" in stem:
            category = "invariants"
        elif "runbook" in stem or "guide" in stem:
            category = "runbooks"
        elif "sota" in str(file_path).lower():
            category = "sota"

        # Synthesize Human-Tier candidate
        human_mdx = self._synthesize_human_mdx(title, category, meta, body)

        # Synthesize Agent-Tier candidate (STE-Agentic)
        agent_ste = self._synthesize_agent_ste(title, body)

        # Extract Candidate Durable Facts
        facts = self._extract_candidate_facts(cid, title, category, str(rel_path), body)

        return DistillationCandidate(
            candidate_id=cid,
            title=title,
            category=category,
            source_path=str(rel_path),
            raw_content=raw_text,
            human_tier=human_mdx,
            agent_tier=agent_ste,
            durable_facts=facts,
            metadata=meta,
        )

    def _synthesize_human_mdx(self, title: str, category: str, meta: Dict[str, str], body: str) -> str:
        """Create clean Fumadocs MDX document."""
        desc = meta.get("description") or meta.get("purpose") or f"Specification and rationale for {title}."
        status = meta.get("status") or "LOCKED"

        # Filter out noisy comments or legacy header markers
        cleaned_body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()

        mdx = [
            "---",
            f'title: "{title}"',
            f'description: "{desc}"',
            f'category: "{category}"',
            "---",
            "",
            f"# {title}",
            "",
            "## Status",
            f"**{status}**",
            "",
            "## Specification & Rationale",
            cleaned_body[:3000] if len(cleaned_body) > 3000 else cleaned_body,
            "",
            "## Boundary Conditions & Invariants",
            "- Strict adherence required across all DNK OS agents.",
            "- Verification enforced via SCONES determinism and automated test suites.",
        ]
        return "\n".join(mdx)

    def _synthesize_agent_ste(self, title: str, body: str) -> str:
        """Synthesize Simplified Technical English (STE) action steps."""
        lines = body.splitlines()
        rules: List[str] = []

        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            # Look for imperative or rule-like lines
            clean = re.sub(r"^[-*0-9.]+\s*", "", line_str).strip()
            words = clean.split()
            if not words:
                continue

            first_word = words[0].upper().rstrip(":,")
            if first_word in VALID_STE_VERBS:
                rule = " ".join(words[:25])  # Limit to 25 words per STE rule
                rules.append(rule)
            elif any(kw in clean.lower() for kw in ["must", "invariant", "rule", "forbidden", "prohibited"]):
                rule = f"ENSURE {clean}"
                rules.append(" ".join(rule.split()[:25]))

            if len(rules) >= 7:
                break

        if not rules:
            rules = [
                f"VERIFY state matches requirements for {title}.",
                "CHECK boundary conditions before applying changes.",
                "RUN deterministic test suite to confirm zero regressions.",
            ]

        out = [
            "---",
            f'title: "{title} (STE-Agentic)"',
            'description: "Deterministic STE Execution Invariant"',
            "---",
            "",
            f"# {title}",
            "",
            "## Action Rules (STE-Agentic)",
        ]
        for idx, r in enumerate(rules, start=1):
            out.append(f"{idx}. {r}")

        return "\n".join(out)

    def _extract_candidate_facts(self, cid: str, title: str, category: str, rel_path: str, body: str) -> List[Dict[str, Any]]:
        """Extract candidate durable facts from code anchors in text."""
        facts: List[Dict[str, Any]] = []

        # Find backtick code references e.g. `path/to/file.py:Symbol` or `core/memory/scones_store.py`
        code_refs = re.findall(r"`([a-zA-Z0-9_\-\./]+(?::[a-zA-Z0-9_]+)?)`", body)
        for ref in set(code_refs):
            if "/" in ref and not ref.startswith("http"):
                file_anchor = ref
                symbol_anchor = None
                if ":" in ref:
                    file_anchor, symbol_anchor = ref.split(":", 1)

                facts.append({
                    "id": f"{cid}_{abs(hash(ref)) % 100000}",
                    "topic": title,
                    "statement": f"{title} anchors to {ref}",
                    "category": category,
                    "file_anchor": file_anchor,
                    "symbol_anchor": symbol_anchor,
                })

        # Also add default fact for the module itself
        facts.append({
            "id": f"{cid}_core",
            "topic": title,
            "statement": f"{title} standard specification defined in {rel_path}",
            "category": category,
            "file_anchor": rel_path,
            "symbol_anchor": None,
        })
        return facts


class GoldfishAuditor:
    """
    Goldfish Critic: Evaluates candidate with zero conversation memory across 4 orthogonal lenses.
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.anchor_verifier = SconesAnchorVerifier(workspace_root)

    def audit(self, candidate: DistillationCandidate) -> Tuple[bool, Dict[str, float], List[str], List[Dict[str, Any]]]:
        """Perform adversarial zero-context audit."""
        critiques: List[str] = []

        # Lens 1: Anti-Sycophancy & Tone
        sycophancy_score, syc_critique = self._audit_anti_sycophancy(candidate)
        critiques.extend(syc_critique)

        # Lens 2: STE Compliance
        ste_score, ste_critique = self._audit_ste_compliance(candidate)
        critiques.extend(ste_critique)

        # Lens 3: Anchor Integrity (AST/File verification)
        anchor_score, anchor_critique, verified_facts = self._audit_anchors(candidate)
        critiques.extend(anchor_critique)

        # Lens 4: Size and Conciseness Budget (DEC-033)
        size_score, size_critique = self._audit_size_budget(candidate)
        critiques.extend(size_critique)

        # Calculate overall weighted score
        overall = (
            0.30 * anchor_score +
            0.30 * ste_score +
            0.20 * sycophancy_score +
            0.20 * size_score
        )

        scores = {
            "anti_sycophancy": round(sycophancy_score, 2),
            "ste_compliance": round(ste_score, 2),
            "anchor_integrity": round(anchor_score, 2),
            "size_budget": round(size_score, 2),
            "overall": round(overall, 2),
        }

        # Threshold: pass if overall >= 0.70 and anchor_score >= 0.50
        accepted = overall >= 0.70 and anchor_score >= 0.50
        return accepted, scores, critiques, verified_facts

    def _audit_anti_sycophancy(self, candidate: DistillationCandidate) -> Tuple[float, List[str]]:
        """Check for forbidden flattery words and subjective bloat."""
        critiques: List[str] = []
        text_lower = (candidate.human_tier + " " + candidate.agent_tier).lower()
        found_tokens = [w for w in BANNED_FLUFF_TOKENS if re.search(r"\b" + re.escape(w) + r"\b", text_lower)]

        if found_tokens:
            critiques.append(f"Anti-Sycophancy Violation: Banned tokens detected: {found_tokens}")
            penalty = min(1.0, len(found_tokens) * 0.3)
            return max(0.0, 1.0 - penalty), critiques

        return 1.0, critiques

    def _audit_ste_compliance(self, candidate: DistillationCandidate) -> Tuple[float, List[str]]:
        """Verify action rules follow STE standards (imperative action verb, <= 25 words)."""
        critiques: List[str] = []
        lines = candidate.agent_tier.splitlines()
        action_rules = [l for l in lines if re.match(r"^\d+\.\s+", l.strip())]

        if not action_rules:
            critiques.append("STE Violation: No numbered action rules found in agent tier.")
            return 0.3, critiques

        valid_count = 0
        for rule_line in action_rules:
            clean = re.sub(r"^\d+\.\s+", "", rule_line.strip())
            words = clean.split()
            first_word = words[0].upper().rstrip(":,") if words else ""

            is_valid_verb = first_word in VALID_STE_VERBS
            is_length_ok = len(words) <= 25

            if is_valid_verb and is_length_ok:
                valid_count += 1
            else:
                if not is_valid_verb:
                    critiques.append(f"STE Verb Violation: Rule does not start with valid verb: '{clean}'")
                if not is_length_ok:
                    critiques.append(f"STE Length Violation: Rule exceeds 25 words ({len(words)} words): '{clean}'")

        score = valid_count / len(action_rules) if action_rules else 0.0
        return score, critiques

    def _audit_anchors(self, candidate: DistillationCandidate) -> Tuple[float, List[str], List[Dict[str, Any]]]:
        """Verify code anchors against the workspace filesystem and AST."""
        critiques: List[str] = []
        verified: List[Dict[str, Any]] = []

        if not candidate.durable_facts:
            return 1.0, critiques, []

        valid_count = 0
        for fact in candidate.durable_facts:
            file_anchor = fact.get("file_anchor")
            symbol_anchor = fact.get("symbol_anchor")

            if not file_anchor:
                valid_count += 1
                verified.append(fact)
                continue

            # Verify file exists
            fpath = self.workspace_root / file_anchor
            if fpath.exists():
                # Verify symbol if present
                if symbol_anchor:
                    anchor_ref = AnchorRef(
                        file_path=file_anchor,
                        symbol=symbol_anchor,
                    )
                    v_res = self.anchor_verifier.verify_anchor(anchor_ref)
                    if v_res.status == "verified":
                        valid_count += 1
                        verified.append(fact)
                    else:
                        critiques.append(f"Anchor Warning: Symbol '{symbol_anchor}' not found in {file_anchor}")
                else:
                    valid_count += 1
                    verified.append(fact)
            else:
                critiques.append(f"Anchor Error: Referenced file anchor does not exist: {file_anchor}")

        score = valid_count / len(candidate.durable_facts) if candidate.durable_facts else 1.0
        return score, critiques, verified

    def _audit_size_budget(self, candidate: DistillationCandidate) -> Tuple[float, List[str]]:
        """Verify character budget complies with lean repository constraints."""
        critiques: List[str] = []
        human_len = len(candidate.human_tier)
        agent_len = len(candidate.agent_tier)

        score = 1.0
        if human_len > 8000:
            critiques.append(f"Size Budget Warning: Human tier document is large ({human_len} chars > 8000)")
            score -= 0.3
        if agent_len > 2500:
            critiques.append(f"Size Budget Warning: Agent tier document is large ({agent_len} chars > 2500)")
            score -= 0.3

        return max(0.2, score), critiques


class HarnessComposer:
    """
    Harness² Composer: Recursive Propose-Probe-Compose refinery.
    """

    def __init__(self, auditor: GoldfishAuditor):
        self.auditor = auditor

    def compose(self, candidate: DistillationCandidate) -> DistillationResult:
        """Probe candidate and compose refined output based on Goldfish critique."""
        accepted, scores, critiques, verified_facts = self.auditor.audit(candidate)

        distilled_human = candidate.human_tier
        distilled_agent = candidate.agent_tier

        # If rejected due to sycophancy, sanitize
        if scores.get("anti_sycophancy", 1.0) < 0.8:
            for bad_word in BANNED_FLUFF_TOKENS:
                pattern = re.compile(r"\b" + re.escape(bad_word) + r"\b", re.IGNORECASE)
                distilled_human = pattern.sub("", distilled_human)
                distilled_agent = pattern.sub("", distilled_agent)

        # Ensure agent tier action rules are strictly formatted
        if scores.get("ste_compliance", 1.0) < 0.8:
            distilled_agent = self._reformat_ste(distilled_agent)

        # Second audit pass (Probe after adjustment)
        sanitized_cand = DistillationCandidate(
            candidate_id=candidate.candidate_id,
            title=candidate.title,
            category=candidate.category,
            source_path=candidate.source_path,
            raw_content=candidate.raw_content,
            human_tier=distilled_human,
            agent_tier=distilled_agent,
            durable_facts=verified_facts,
            metadata=candidate.metadata,
        )
        accepted_final, scores_final, critiques_final, final_facts = self.auditor.audit(sanitized_cand)

        return DistillationResult(
            candidate_id=candidate.candidate_id,
            accepted=accepted_final,
            scores=scores_final,
            critique=critiques_final,
            distilled_human_tier=distilled_human if accepted_final else None,
            distilled_agent_tier=distilled_agent if accepted_final else None,
            verified_facts=final_facts,
            metadata={
                "source": candidate.source_path,
                "original_scores": scores,
            },
        )

    def _reformat_ste(self, agent_text: str) -> str:
        """Normalize agent rules to valid STE imperative form."""
        lines = agent_text.splitlines()
        reformatted: List[str] = []
        rule_idx = 1

        for line in lines:
            if re.match(r"^\d+\.\s+", line.strip()):
                clean = re.sub(r"^\d+\.\s+", "", line.strip())
                words = clean.split()
                if not words:
                    continue
                first = words[0].upper().rstrip(":,")
                if first not in VALID_STE_VERBS:
                    clean = f"RUN {clean}"
                    words = clean.split()
                truncated = " ".join(words[:24])
                reformatted.append(f"{rule_idx}. {truncated}")
                rule_idx += 1
            else:
                reformatted.append(line)

        return "\n".join(reformatted)


class EGMDistiller:
    """
    Main Orchestrator for the Elephant-Goldfish & Harness² Distillation Engine.
    """

    def __init__(self, workspace_root: Optional[Union[str, Path]] = None):
        self.workspace_root = Path(workspace_root or ".").resolve()
        self.harvester = ElephantHarvester(self.workspace_root)
        self.auditor = GoldfishAuditor(self.workspace_root)
        self.composer = HarnessComposer(self.auditor)

    def distill_file(self, file_path: Union[str, Path]) -> DistillationResult:
        """Distill a single architectural document or SOTA note."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.workspace_root / path

        candidates = self.harvester.harvest_file_all(path)
        if not candidates:
            raise ValueError(f"No candidates found in {path}")
        return self.composer.compose(candidates[0])

    def distill_file_all(self, file_path: Union[str, Path]) -> List[DistillationResult]:
        """Distill all candidates from a file (handles single files and registries)."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.workspace_root / path

        candidates = self.harvester.harvest_file_all(path)
        return [self.composer.compose(cand) for cand in candidates]

    def distill_directory(
        self,
        source_dir: Union[str, Path],
        file_glob: str = "*.md",
    ) -> List[DistillationResult]:
        """Distill all markdown documents matching glob in a directory."""
        dir_path = Path(source_dir)
        if not dir_path.is_absolute():
            dir_path = self.workspace_root / dir_path

        results: List[DistillationResult] = []
        for fpath in sorted(dir_path.glob(file_glob)):
            if fpath.is_file() and not fpath.name.startswith("."):
                try:
                    file_results = self.distill_file_all(fpath)
                    results.extend(file_results)
                except Exception as e:
                    logger.warning("Failed to distill %s: %s", fpath, e)

        return results

    def export_to_target_repo(
        self,
        target_root: Union[str, Path],
        results: List[DistillationResult],
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Export distilled results to target repository (e.g. ../DNK-Ecom_OS).
        Creates:
        - target_root/content/human/<category>/<id>.md
        - target_root/content/agent/<category>/<id>.md
        - Populates SCONES BM25 Index in target_root/core/memory/scones.db
        """
        target = Path(target_root).resolve()
        human_dir = target / "content" / "human"
        agent_dir = target / "content" / "agent"

        exported_human = 0
        exported_agent = 0
        exported_facts = 0

        target_bm25_db = target / "core" / "memory" / "scones.db"
        bm25_index: Optional[SconesBM25Index] = None
        if not dry_run and target.exists():
            target_bm25_db.parent.mkdir(parents=True, exist_ok=True)
            bm25_index = SconesBM25Index(db_path=target_bm25_db)

        for res in results:
            if not res.accepted:
                continue

            cid = res.candidate_id
            cat = res.metadata.get("category", "01_architecture_decisions")

            # 1. Export Human Tier
            if res.distilled_human_tier:
                h_out_dir = human_dir / cat
                h_file = h_out_dir / f"{cid}.md"
                if not dry_run:
                    h_out_dir.mkdir(parents=True, exist_ok=True)
                    h_file.write_text(res.distilled_human_tier, encoding="utf-8")
                exported_human += 1

            # 2. Export Agent Tier
            if res.distilled_agent_tier:
                a_out_dir = agent_dir / cat
                a_file = a_out_dir / f"{cid}.md"
                if not dry_run:
                    a_out_dir.mkdir(parents=True, exist_ok=True)
                    a_file.write_text(res.distilled_agent_tier, encoding="utf-8")
                exported_agent += 1

            # 3. Export Facts to SCONES BM25 DB
            if res.verified_facts:
                if bm25_index:
                    for f in res.verified_facts:
                        fact = DurableFact(
                            id=f["id"],
                            topic=f["topic"],
                            statement=f["statement"],
                            category=f.get("category", "architecture"),
                            file_anchor=f.get("file_anchor"),
                            symbol_anchor=f.get("symbol_anchor"),
                        )
                        bm25_index.upsert_fact(fact)
                exported_facts += len(res.verified_facts)

        return {
            "target_root": str(target),
            "dry_run": dry_run,
            "exported_human_files": exported_human,
            "exported_agent_files": exported_agent,
            "exported_durable_facts": exported_facts,
            "total_accepted": sum(1 for r in results if r.accepted),
            "total_candidates": len(results),
        }
