# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_shopify_squad.py"
# purpose: "Unit tests for Shopify Dev Squad agents and turnkey pipeline runner"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

from pathlib import Path
import yaml
import pytest
from core.orchestrator.shopify_squad_runner import ShopifySquadRunner, ShopifyStoreBrief

ROOT_DIR = Path(__file__).resolve().parents[2]


def test_shopify_squad_agents_manifests_exist():
    """Verify all 5 specialized Shopify agents exist with required SOUL.md, agent_card.yaml, config.yaml."""
    agents_dir = ROOT_DIR / "core" / "orchestrator" / "agents"
    expected_agents = [
        "shopify_brand_architect",
        "shopify_cro_engineer",
        "shopify_theme_craftsman",
        "shopify_performance_lead",
        "shopify_store_auditor",
    ]

    for agent_name in expected_agents:
        agent_path = agents_dir / agent_name
        assert agent_path.is_dir(), f"Missing agent directory: {agent_name}"
        assert (agent_path / "SOUL.md").exists(), f"Missing SOUL.md for {agent_name}"
        assert (agent_path / "agent_card.yaml").exists(), f"Missing agent_card.yaml for {agent_name}"
        assert (agent_path / "config.yaml").exists(), f"Missing config.yaml for {agent_name}"

        # Verify agent_card.yaml is valid YAML and has agent_id
        with open(agent_path / "agent_card.yaml", "r", encoding="utf-8") as f:
            card = yaml.safe_load(f)
            assert card["agent_id"] == agent_name


def test_shopify_squad_runner_pipeline():
    """Verify turnkey 5-stage pipeline executes and returns valid result."""
    brief = ShopifyStoreBrief(
        brand_name="Test Brand",
        target_audience="Test Audience",
        niche="Test Niche",
        core_pains=["Slow sleep"],
        key_products=["Pillow"]
    )
    runner = ShopifySquadRunner(repo_root=ROOT_DIR)
    res = runner.execute_turnkey_pipeline(brief)
    assert res.overall_status == "SUCCESS"
    assert len(res.stages) == 5
    assert res.stages[0].agent_id == "shopify_brand_architect"
    assert res.stages[4].agent_id == "shopify_store_auditor"
