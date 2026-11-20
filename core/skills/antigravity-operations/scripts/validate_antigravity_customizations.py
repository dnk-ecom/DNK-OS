#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/antigravity_operations/scripts/validate_antigravity_customizations.py"
# purpose: "Autonomous validation script for Google Antigravity rules, skills, MCP configs, and hooks."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-23"
# author: "Antigravity & Gerych Prime"
# --- END DNK-MRH-HEADER ---

"""
validate_antigravity_customizations.py — Validates Google Antigravity workspaces and global configs.

Checks:
1. Rules: YAML frontmatter (trigger, description, globs), 24 KB size ceiling.
2. Skills: YAML frontmatter (name, description), 750 lines core-size ratchet, references integrity.
3. MCP Servers: mcp_config.json syntax, transport presence (command vs serverUrl), stdio PATH hygiene.
4. Hooks: hooks.json schema, valid event hooks (PreToolUse, PostToolUse, PreInvocation, PostInvocation, Stop).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

MAX_RULE_BYTES = 24_000
MAX_SKILL_LINES = 750
MAX_DESC_CHARS = 1024
NAME_RE = re.compile(r"^[a-z0-9]+([-_][a-z0-9]+)*$")
REF_PATH_RE = re.compile(r"`(references/[a-zA-Z0-9_\-\./]+)`")
VALID_TRIGGERS = {"always_on", "model_decision", "glob", "manual"}
VALID_HOOK_EVENTS = {"PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"}


def extract_frontmatter(content: str) -> Tuple[dict, str, str]:
    lines = content.splitlines(keepends=True)
    idx = 0
    if lines and lines[0].strip().startswith(("# --- DNK-MRH-HEADER ---", "<!-- --- DNK-MRH-HEADER ---", "<!--")):
        while idx < len(lines):
            line_str = lines[idx].strip()
            idx += 1
            if line_str in ("# --- END DNK-MRH-HEADER ---", "--- END DNK-MRH-HEADER --- -->", "-->"):
                break
        while idx < len(lines) and not lines[idx].strip():
            idx += 1

    remaining_lines = lines[idx:]
    if not remaining_lines or remaining_lines[0].strip() != "---":
        return {}, "".join(remaining_lines), "Missing starting '---' delimiter"

    end_idx = -1
    for i in range(1, len(remaining_lines)):
        if remaining_lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return {}, "".join(remaining_lines), "Unclosed YAML frontmatter"

    fm_text = "".join(remaining_lines[1:end_idx])
    body_text = "".join(remaining_lines[end_idx + 1:])
    try:
        data = yaml.safe_load(fm_text)
        return data if isinstance(data, dict) else {}, body_text, ""
    except Exception as e:
        return {}, body_text, f"YAML parse error: {e}"


def validate_rule_file(path: Path) -> List[str]:
    errors = []
    file_bytes = path.stat().st_size
    if file_bytes > MAX_RULE_BYTES:
        errors.append(f"Rule file size {file_bytes} bytes exceeds 24 KB ({MAX_RULE_BYTES} bytes) ceiling")

    content = path.read_text(encoding="utf-8", errors="replace")
    fm, _, err = extract_frontmatter(content)
    if err:
        errors.append(f"Frontmatter error: {err}")
        return errors

    trigger = fm.get("trigger")
    if not trigger:
        errors.append("Rule missing required 'trigger' key (always_on | model_decision | glob | manual)")
    elif trigger not in VALID_TRIGGERS:
        errors.append(f"Invalid trigger '{trigger}'. Supported: {', '.join(sorted(VALID_TRIGGERS))}")

    if trigger == "model_decision" and not fm.get("description"):
        errors.append("trigger: model_decision requires non-empty 'description' field")

    if trigger == "glob" and not (fm.get("globs") or fm.get("glob")):
        errors.append("trigger: glob requires 'globs' or 'glob' field with comma-separated patterns")

    return errors


def validate_skill_file(path: Path) -> List[str]:
    errors = []
    content = path.read_text(encoding="utf-8", errors="replace")
    total_lines = len(content.splitlines())
    if total_lines > MAX_SKILL_LINES:
        errors.append(f"Skill length {total_lines} lines exceeds ratchet ceiling of {MAX_SKILL_LINES} lines")

    fm, body, err = extract_frontmatter(content)
    if err:
        errors.append(f"Frontmatter error: {err}")
        return errors

    name = fm.get("name")
    if not name or not isinstance(name, str):
        errors.append("Skill missing required 'name' string")
    elif not NAME_RE.match(name):
        errors.append(f"Skill name '{name}' must be lowercase alphanumeric with hyphens or underscores")

    desc = fm.get("description")
    if not desc or not isinstance(desc, str):
        errors.append("Skill missing required 'description' string")
    elif len(desc) > MAX_DESC_CHARS:
        errors.append(f"Skill description length {len(desc)} exceeds {MAX_DESC_CHARS} characters limit")

    skill_dir = path.parent
    for match in REF_PATH_RE.finditer(body):
        ref_rel = match.group(1)
        ref_path = skill_dir / ref_rel
        if not ref_path.exists():
            errors.append(f"Referenced file `{ref_rel}` does not exist at {ref_path}")

    return errors


def validate_mcp_config(path: Path) -> List[str]:
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"Invalid JSON in {path}: {e}"]

    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        return ["mcp_config.json must contain a top-level 'mcpServers' object"]

    for name, s_cfg in servers.items():
        if not isinstance(s_cfg, dict):
            errors.append(f"Server '{name}' configuration must be an object")
            continue
        has_cmd = "command" in s_cfg
        has_url = "serverUrl" in s_cfg
        if not (has_cmd or has_url):
            errors.append(f"Server '{name}' requires either 'command' (stdio) or 'serverUrl' (remote)")
        if has_cmd and "env" in s_cfg:
            env = s_cfg.get("env", {})
            if isinstance(env, dict) and "PATH" not in env:
                errors.append(f"Warning: Server '{name}' specifies custom 'env' without explicit 'PATH'")

    return errors


def validate_hooks_config(path: Path) -> List[str]:
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"Invalid JSON in {path}: {e}"]

    if not isinstance(data, dict):
        return ["hooks.json must be a JSON object"]

    for hook_name, hook_spec in data.items():
        if not isinstance(hook_spec, dict):
            errors.append(f"Hook '{hook_name}' must be an object")
            continue
        for key in hook_spec.keys():
            if key in ("enabled",):
                continue
            if key not in VALID_HOOK_EVENTS:
                errors.append(f"Hook '{hook_name}' contains unrecognized event '{key}'. Supported: {', '.join(sorted(VALID_HOOK_EVENTS))}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate Antigravity customization files.")
    parser.add_argument("target_path", nargs="?", default=".", help="Path to workspace root or skill directory")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    root = Path(args.target_path).resolve()
    results = {"target": str(root), "valid": True, "errors": {}, "checked_files": 0}

    # If pointing directly to a skill folder or SKILL.md
    if root.is_file() and root.name == "SKILL.md":
        errs = validate_skill_file(root)
        results["checked_files"] += 1
        if errs:
            results["errors"][str(root)] = errs
            results["valid"] = False
    elif root.is_dir() and (root / "SKILL.md").exists():
        errs = validate_skill_file(root / "SKILL.md")
        results["checked_files"] += 1
        if errs:
            results["errors"][str(root / "SKILL.md")] = errs
            results["valid"] = False
    else:
        # Search workspace or directory recursively
        for p in root.rglob("*.md"):
            if ".agents/rules" in str(p) or "config/rules" in str(p):
                errs = validate_rule_file(p)
                results["checked_files"] += 1
                if errs:
                    results["errors"][str(p)] = errs
                    results["valid"] = False
            elif p.name == "SKILL.md":
                errs = validate_skill_file(p)
                results["checked_files"] += 1
                if errs:
                    results["errors"][str(p)] = errs
                    results["valid"] = False

        for p in root.rglob("mcp_config.json"):
            errs = validate_mcp_config(p)
            results["checked_files"] += 1
            if errs:
                results["errors"][str(p)] = errs
                results["valid"] = False

        for p in root.rglob("hooks.json"):
            errs = validate_hooks_config(p)
            results["checked_files"] += 1
            if errs:
                results["errors"][str(p)] = errs
                results["valid"] = False

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("========================================================")
        print("🛡️  Google Antigravity Customization Validator")
        print("========================================================")
        print(f"Target: {root}")
        print(f"Total checked files: {results['checked_files']}")
        if results["valid"]:
            print("✅ All Antigravity rules, skills, MCP, and hooks are VALID.")
        else:
            print("❌ Validation Failures Detected:")
            for f, errs in results["errors"].items():
                print(f"\n📄 {f}:")
                for e in errs:
                    print(f"   - {e}")
        print("========================================================")

    sys.exit(0 if results["valid"] else 1)


if __name__ == "__main__":
    main()
