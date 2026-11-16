# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_knowledge_staleness.py"
# purpose: "Unit tests for Knowledge Staleness Guard and Adversarial Review Gate in DNK_OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

import pytest
from pathlib import Path
from core.sentinel.knowledge_staleness_guard import KnowledgeStalenessGuard
from core.sentinel.adversarial_review_gate import AdversarialReviewGate, CritiqueVerdict


def test_staleness_guard_file_detection(tmp_path):
    guard = KnowledgeStalenessGuard(workspace_root=tmp_path)
    
    # Create valid file
    valid_file = tmp_path / "core" / "valid_module.py"
    valid_file.parent.mkdir(parents=True, exist_ok=True)
    valid_file.write_text("# valid code")
    
    # Create a doc with 1 valid ref and 1 stale ref
    doc = tmp_path / "docs" / "test_doc.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(
        "See `core/valid_module.py` for implementation.\n"
        "Also see `core/ghost_file.py` which does not exist.\n"
    )
    
    stale_items = guard.audit_file(doc)
    assert len(stale_items) == 1
    assert stale_items[0].referenced_path == "core/ghost_file.py"
    assert stale_items[0].reason == "file_not_found"


def test_adversarial_review_gate_approval():
    gate = AdversarialReviewGate()
    res = gate.evaluate_proposal(
        subject="Living Knowledge Lifecycle & SCONES FTS5 Integration",
        what_this_is="Autonomous eviction of stale documentation and FTS5 BM25 retrieval for agent memories.",
        problem="Static notes rot in 60-90 days, causing attention entropy in LLMs.",
        fix="Enforce AST file-existence guards and SCONES FTS5 belief revision.",
        if_we_skip_it="Agents make mistakes using deprecated APIs and phantom files.",
    )
    assert res.verdict == CritiqueVerdict.APPROVED
    assert res.to_dict()["passed"] is True
    assert len(res.vectors) == 5


def test_adversarial_review_gate_rejection_on_critical_risk():
    gate = AdversarialReviewGate()
    res = gate.evaluate_proposal(
        subject="Unsafe bypass",
        what_this_is="Disable authentication on all routes",
        problem="Too many auth errors",
        fix="Remove auth middleware",
        if_we_skip_it="Developers annoyed",
        vector_assessments=[
            {}, {}, {}, {"risk": "CRITICAL", "observation": "Complete security breach"}, {}
        ]
    )
    assert res.verdict == CritiqueVerdict.REJECTED
    assert res.to_dict()["passed"] is False
