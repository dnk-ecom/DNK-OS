# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_repo_progressive_index.py"
# purpose: "Unit tests for Two-Level Progressive Disclosure Index (LOD Navigation Standard) of 1,663 repositories."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
import pytest
from core.registry.repo_catalog import (
    get_repo_progressive_index,
    PROGRESSIVE_SOVEREIGN_DOMAINS,
)


def test_repo_progressive_index_level_0():
    """Verify Level 0 Root LOD returns concise overview of all 3 pillars <= 1,000 tokens."""
    res = get_repo_progressive_index()
    assert res["level"] == "L0_Root_Overview"
    assert res["total_catalog_repos"] == 1663
    
    pillars = res["sovereign_pillars"]
    assert "shopify" in pillars
    assert "media" in pillars
    assert "core" in pillars
    
    assert pillars["shopify"]["repo_count"] == 145
    assert pillars["media"]["repo_count"] == 209
    assert pillars["core"]["repo_count"] == 1309
    
    # Verify strict prompt diet: serialized JSON <= 3,000 chars (~750 tokens)
    serialized = json.dumps(res, ensure_ascii=False)
    assert len(serialized) <= 3000, f"L0 index too heavy: {len(serialized)} chars"


@pytest.mark.parametrize("domain_key", ["shopify", "media", "core"])
def test_repo_progressive_index_level_1_domains(domain_key: str):
    """Verify Level 1 Domain Slice returns targeted Tier 1 blueprints <= 1,500 tokens."""
    res = get_repo_progressive_index(domain=domain_key)
    assert res["level"] == f"L1_Domain_Slice_{domain_key}"
    assert res["domain"] == domain_key
    assert res["total_repositories"] > 0
    assert len(res["golden_core_blueprints"]) > 0
    
    # Verify all returned blueprints are Tier 1
    for blueprint in res["golden_core_blueprints"]:
        assert "Tier 1" in blueprint["tier"]
        assert blueprint["name"]
        assert len(blueprint["what_it_gives"]) <= 120
        
    # Verify strict prompt diet: serialized JSON <= 6,000 chars (~1,500 tokens)
    serialized = json.dumps(res, ensure_ascii=False)
    assert len(serialized) <= 6000, f"L1 slice too heavy: {len(serialized)} chars"


def test_repo_progressive_index_aliases_and_errors():
    """Verify domain aliases resolve properly and invalid domains return actionable error."""
    # Aliases
    assert get_repo_progressive_index("ecom")["domain"] == "shopify"
    assert get_repo_progressive_index("video")["domain"] == "media"
    assert get_repo_progressive_index("swarm")["domain"] == "core"
    
    # Error handling
    err_res = get_repo_progressive_index("quantum_blockchain")
    assert "error" in err_res
    assert "valid_domains" in err_res
    assert set(err_res["valid_domains"]) == {"shopify", "media", "core"}
