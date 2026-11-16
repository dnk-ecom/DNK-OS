# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/tests/test_local_storefront.py"
# purpose: "Unit tests for LocalStorefrontManager and lsf CLI in DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import subprocess
import sys
from pathlib import Path
import pytest

from services.dnk_shopify.runtime.local_storefront import LocalStorefrontManager


@pytest.fixture
def theme_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "DNK_Sovereign_Apex"


def test_local_storefront_manager_init():
    lsf = LocalStorefrontManager(default_port=9292)
    assert lsf.port == 9292
    assert lsf.base_url == "http://127.0.0.1:9292"


def test_local_storefront_check(theme_dir: Path):
    lsf = LocalStorefrontManager()
    res = lsf.run_check(theme_dir)
    assert res["success"] is True
    assert res["returncode"] == 0
    assert "0 problem(s)" in res["stderr"]


def test_local_storefront_profile(theme_dir: Path):
    lsf = LocalStorefrontManager()
    res = lsf.run_profile(theme_dir, path="/")
    assert res["success"] is True
    assert "template" in res["output"]


def test_cli_lsf_check(theme_dir: Path):
    cli_path = Path(__file__).resolve().parent.parent / "cli.py"
    cmd = [sys.executable, str(cli_path), "lsf-check", "--theme", str(theme_dir), "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert '"success": true' in proc.stdout
