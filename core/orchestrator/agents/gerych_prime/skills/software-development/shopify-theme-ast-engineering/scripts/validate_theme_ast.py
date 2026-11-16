#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/scripts/validate_theme_ast.py"
# purpose: "Fast AST validator script for Liquid files, Theme Blocks v2, and Schema integrity."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-28"
# author: "DNK OS Gerych Prime"
# --- END DNK-MRH-HEADER ---

import sys
from pathlib import Path

# Delegate to canonical dnk_shopify AST validator
from services.dnk_shopify.tools.theme_ast_validator import run_precommit_check

if __name__ == "__main__":
    files = sys.argv[1:]
    if not files:
        print("Usage: python3 validate_theme_ast.py <file1.liquid> [file2.liquid ...]")
        sys.exit(0)
    success = run_precommit_check(files)
    sys.exit(0 if success else 1)
