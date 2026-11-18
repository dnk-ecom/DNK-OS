# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_sota_assimilation_pipeline.py"
# purpose: "Unit tests for Autonomous SOTA Open-Source Assimilation Pipeline."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import os
from pathlib import Path
from services.dnk_git_research.src.sota_pipeline import SOTAPipelineRunner


def test_parse_repo_identifier():
    runner = SOTAPipelineRunner()
    res1 = runner.parse_repo_identifier("https://github.com/deepseek-ai/dsh-superagent-prototype")
    assert res1["owner"] == "deepseek-ai"
    assert res1["name"] == "dsh-superagent-prototype"
    assert res1["slug"] == "dsh_superagent_prototype"

    res2 = runner.parse_repo_identifier("NousResearch/hermes-agent")
    assert res2["owner"] == "NousResearch"
    assert res2["slug"] == "hermes_agent"


def test_evaluate_egm_rubric():
    runner = SOTAPipelineRunner()
    meta = {"owner": "test", "name": "benchmark", "full_name": "test/benchmark", "slug": "benchmark"}
    score = runner.evaluate_egm_rubric(meta, "services/dnk_shopify")
    assert score.passed is True
    assert score.composite_score >= 4.0
    assert len(score.dissent_3_flaws) == 3


def test_pipeline_generates_valid_spec_and_task(tmp_path):
    runner = SOTAPipelineRunner(repo_root=tmp_path)
    out = runner.run("https://github.com/sample-ai/agentic-gem", target_module="core")
    assert out.success is True
    assert out.repo_slug == "agentic_gem"

    spec_abs = tmp_path / out.spec_path
    task_abs = tmp_path / out.task_path

    assert spec_abs.exists()
    assert task_abs.exists()

    spec_txt = spec_abs.read_text(encoding="utf-8")
    assert "DNK-MRH-HEADER" in spec_txt
    assert "SOTA_AUDIT" in spec_txt
    assert "## 2. Обов'язкова Дискусія та 3 Приховані Ризики" in spec_txt

    task_txt = task_abs.read_text(encoding="utf-8")
    assert "DNK-MRH-HEADER" in task_txt
    assert "TASK_SPEC" in task_txt
    assert "Negative Scope" in task_txt
    assert "Permitted Files Whitelist" in task_txt
