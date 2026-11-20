# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_design_system_distiller.py"
# purpose: "Unit tests for Design System Distiller and 5-Stage Swarm Runner (DEC-135)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
from pathlib import Path
import pytest
from core.design_system.distiller import DesignSystemDistiller
from core.orchestrator.design_system_runner import (
    DesignSystemSwarmRunner,
    DesignSystemBrief,
)


@pytest.fixture
def mock_donor_theme(tmp_path: Path) -> Path:
    """Creates a mock Shopify theme structure with settings_data.json and CSS."""
    theme_dir = tmp_path / "mock_theme"
    config_dir = theme_dir / "config"
    assets_dir = theme_dir / "assets"
    config_dir.mkdir(parents=True)
    assets_dir.mkdir(parents=True)

    # 1. settings_data.json
    settings = {
        "current": {
            "color_background": "#FAFAFA",
            "color_text": "#1E293B",
            "color_primary": "#0F766E",
            "color_surface": "#F1F5F9",
        }
    }
    with open(config_dir / "settings_data.json", "w", encoding="utf-8") as f:
        json.dump(settings, f)

    # 2. base.css
    css_content = """
    :root {
      --spacing-base: 8px;
      --font-size-base: 16px;
    }
    """
    with open(assets_dir / "base.css", "w", encoding="utf-8") as f:
        f.write(css_content)

    return theme_dir


def test_distiller_extracts_and_compiles(mock_donor_theme: Path, tmp_path: Path):
    out_dir = tmp_path / "distilled_output"
    res = DesignSystemDistiller.distill_and_compile(
        donor_path=mock_donor_theme,
        brand_name="Mock Donor Brand",
        output_dir=out_dir,
    )

    assert res["status"] == "SUCCESS"
    assert res["brand_name"] == "Mock Donor Brand"
    assert res["lint_report"]["valid"] is True
    assert (out_dir / "dnk-tokens.css").exists()
    assert (out_dir / "tailwind-theme.css").exists()
    assert (out_dir / "media-motion-tokens.json").exists()
    assert (out_dir / "DESIGN.md").exists()
    assert (out_dir / "brand_tokens_spec.json").exists()
    assert (out_dir / "astryx-tokens.css").exists()
    assert (out_dir / "figma_variables.json").exists()
    assert (out_dir / "social_creative_matrix.json").exists()
    assert (out_dir / "BRAND.md").exists()
    assert (out_dir / "SKILL.md").exists()
    assert (out_dir / "AUDIT_WHAT_WE_FIX_FIRST.md").exists()
    assert (out_dir / "blocks" / "dnk-offer.liquid").exists()

    # Check generated CSS contents
    css_text = (out_dir / "dnk-tokens.css").read_text(encoding="utf-8")
    assert "--color-surface-primary: #FAFAFA;" in css_text
    assert "--color-surface-primary-rgb: 250 250 250;" in css_text
    assert "--color-action-primary: #0F766E;" in css_text


def test_swarm_runner_5_stage_pipeline(mock_donor_theme: Path, tmp_path: Path):
    out_dir = tmp_path / "swarm_output"
    runner = DesignSystemSwarmRunner()
    brief = DesignSystemBrief(
        donor_path=str(mock_donor_theme),
        brand_name="Sovereign Test Brand",
        target_output_dir=str(out_dir),
    )

    pipeline_res = runner.execute_turnkey_distillation(brief)
    assert pipeline_res.overall_status == "SUCCESS"
    assert len(pipeline_res.stages) == 5
    assert pipeline_res.stages[0].agent_id == "dnk_git_research"
    assert pipeline_res.stages[1].agent_id == "dnk_brand_typostyle"
    assert pipeline_res.stages[2].agent_id == "gerych_prime"
    assert pipeline_res.stages[3].agent_id == "denchik"
    assert pipeline_res.stages[4].agent_id == "shopify_store_auditor"
    assert pipeline_res.wcag_pass_rate == 100.0


def test_kernel_mcp_distill_tool(mock_donor_theme: Path, tmp_path: Path):
    from core.kernel import FastMCPKernel, create_fastmcp_server

    db_path = str(tmp_path / "action_bus.db")
    artifacts_dir = str(tmp_path / "artifacts")
    k = FastMCPKernel(db_path=db_path, artifacts_dir=artifacts_dir, workspace_id="test_distill")
    server = create_fastmcp_server(k, name="test-distill-server")

    tool = server._tool_manager.get_tool("distill_brand_design_system")
    assert tool is not None

    raw = tool.fn(
        donor_path=str(mock_donor_theme),
        brand_name="MCP Distilled Brand",
        target_output_dir=str(tmp_path / "mcp_out"),
    )
    res = json.loads(raw)
    assert res["success"] is True
    assert res["result"]["overall_status"] == "SUCCESS"
    assert len(res["result"]["stages"]) == 5


def test_distiller_extracts_from_url_mocked(tmp_path: Path, monkeypatch):
    """Verifies that distill_and_compile works with live website URLs."""
    import io
    import urllib.request

    mock_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root {
            --color-background: 255,255,255;
            --color-foreground: 4,24,43;
            --color-accent: 24,47,79;
            --color-button: 24,47,79;
            --color-button-text: 255,255,255;
            --font-heading-family: "Figtree", sans-serif;
            --font-body-family: "Figtree", sans-serif;
            --corner-button: 8px;
          }
        </style>
      </head>
      <body><h1>Sugar Test</h1></body>
    </html>
    """

    class MockResponse:
        def __init__(self, data: bytes):
            self._data = data

        def read(self):
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def mock_urlopen(req, *args, **kwargs):
        return MockResponse(mock_html.encode("utf-8"))

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    out_dir = tmp_path / "url_distilled_output"
    res = DesignSystemDistiller.distill_and_compile(
        donor_path="https://sugarthe.me/",
        brand_name="Sugar Theme Live Test",
        output_dir=out_dir,
    )

    assert res["status"] == "SUCCESS"
    assert res["brand_name"] == "Sugar Theme Live Test"
    assert res["lint_report"]["valid"] is True
    assert res["lint_report"]["contrast_pass_rate"] == 100.0
    assert (out_dir / "dnk-tokens.css").exists()
    assert (out_dir / "figma_variables.json").exists()
    assert (out_dir / "social_creative_matrix.json").exists()
    assert (out_dir / "astryx-tokens.css").exists()

