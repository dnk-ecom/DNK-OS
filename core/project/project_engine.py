# --- DNK-MRH-HEADER ---
# mrh_id: "core/project/project_engine.py"
# purpose: "Vibe-Coder Core Project Control Plane (ProjectDNA lifecycle, 3-track scaffolding, and ThoughtDAG canvas binding)."
# canonical_source: true
# alters_files: ["docs/projects/*", "docs/canvas/projects/*"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, ConfigDict, Field

# Ensure repo root is on sys.path
_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from core.domain.vibe_core_contracts import (
    AccountSpec,
    ActionSurfaceMode,
    DesignSystemTokens,
    DualSurfaceActionSpec,
    ICPProfile,
    NodeLifecycleState,
    ProjectDNA,
    TrackKind,
    TrackSpec,
)

logger = logging.getLogger("dnk.core.project_engine")


class ProjectSummary(BaseModel):
    """High-level summary of an active business project in DNK Core."""
    model_config = ConfigDict(extra="ignore")

    project_id: str
    project_name: str
    domain_type: str
    account_id: str
    project_dir: str
    manifest_path: str
    brand_dna_path: str
    main_canvas_path: str
    tracks_count: int
    tracks: List[Dict[str, Any]] = Field(default_factory=list)


class ProjectStats(BaseModel):
    """Execution telemetry and node distribution for a business project."""
    model_config = ConfigDict(extra="ignore")

    project_id: str
    project_name: str
    domain_type: str
    total_nodes: int
    total_edges: int
    nodes_by_state: Dict[str, int]
    crystallized_count: int
    pending_count: int
    active_tracks: List[str]


class ProjectEngine:
    """
    Sovereign Project Control Plane for DNK Core.
    
    Coordinates the 4-layer hierarchy:
    L1 Account (Vibe-Coder profile)
      └── L2 Business Projects (ProjectDNA: Brand, ICP, Design Tokens)
            └── Tracks (Functional Workstreams: Foundry, Sales, Benchmarks)
                  └── L3 ThoughtDAG Nodes (Chat-to-DAG isolated tasks)
    """

    def __init__(
        self,
        projects_dir: Optional[Path] = None,
        canvas_dir: Optional[Path] = None,
        account_path: Optional[Path] = None,
    ):
        _root = Path(__file__).resolve().parent.parent.parent
        self.projects_dir = projects_dir or (_root / "docs/projects" if (_root / "docs/projects").exists() else Path("docs/projects"))
        self.canvas_dir = canvas_dir or (_root / "docs/canvas/projects" if (_root / "docs/canvas/projects").exists() else Path("docs/canvas/projects"))
        self.account_path = account_path or (_root / "core/config/vibe_coder_account.json" if (_root / "core/config/vibe_coder_account.json").exists() else Path("core/config/vibe_coder_account.json"))

    def load_account(self) -> AccountSpec:
        """Loads and validates the L1 Vibe-Coder Account specification."""
        if not self.account_path.exists():
            raise FileNotFoundError(f"Account spec not found at: {self.account_path}")
        with open(self.account_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AccountSpec.model_validate(data)

    def list_projects(self) -> List[ProjectSummary]:
        """Scans docs/projects and returns all registered business projects."""
        projects: List[ProjectSummary] = []
        if not self.projects_dir.exists():
            return projects

        for item in sorted(self.projects_dir.iterdir()):
            if not item.is_dir():
                continue

            dna_file = item / "brand_dna.json"
            manifest_file = item / "project.manifest.yaml"
            canvas_file = self.canvas_dir / item.name / "main.canvas"

            if not dna_file.exists():
                continue

            try:
                with open(dna_file, "r", encoding="utf-8") as f:
                    dna_data = json.load(f)
                dna = ProjectDNA.model_validate(dna_data)

                tracks_summary = [
                    {
                        "track_id": t.track_id,
                        "kind": t.kind.value if hasattr(t.kind, "value") else str(t.kind),
                        "title": t.title,
                        "assigned_workhorse": t.assigned_workhorse,
                        "repo_root_rel": t.repo_root_rel,
                    }
                    for t in dna.tracks
                ]

                projects.append(
                    ProjectSummary(
                        project_id=dna.project_id,
                        project_name=dna.project_name,
                        domain_type=dna.domain_type,
                        account_id=dna.account_id,
                        project_dir=f"./{item}",
                        manifest_path=f"./{manifest_file}" if manifest_file.exists() else "",
                        brand_dna_path=f"./{dna_file}",
                        main_canvas_path=f"./{canvas_file}" if canvas_file.exists() else "",
                        tracks_count=len(dna.tracks),
                        tracks=tracks_summary,
                    )
                )
            except Exception as e:
                logger.warning("Failed parsing project in %s: %s", item, e)

        return projects

    def get_project(self, project_id: str) -> ProjectDNA:
        """Retrieves and validates ProjectDNA by ID (e.g. 'proj-shopify-dnk-ecom')."""
        # 1. Search by direct slug directory
        slug = project_id.replace("proj-", "").replace("-", "_")
        candidate_dna = self.projects_dir / slug / "brand_dna.json"
        if candidate_dna.exists():
            with open(candidate_dna, "r", encoding="utf-8") as f:
                return ProjectDNA.model_validate(json.load(f))

        # 2. Linear scan of all project directories
        for item in self.projects_dir.iterdir():
            if item.is_dir():
                dna_file = item / "brand_dna.json"
                if dna_file.exists():
                    try:
                        with open(dna_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if data.get("project_id") == project_id:
                            return ProjectDNA.model_validate(data)
                    except Exception:
                        pass

        raise KeyError(f"Project not found with ID: '{project_id}'")

    def get_project_manifest(self, project_id: str) -> Dict[str, Any]:
        """Loads the raw YAML manifest for a project."""
        slug = project_id.replace("proj-", "").replace("-", "_")
        manifest_file = self.projects_dir / slug / "project.manifest.yaml"
        if not manifest_file.exists():
            # Search by scan
            for item in self.projects_dir.iterdir():
                if item.is_dir() and (item / "project.manifest.yaml").exists():
                    try:
                        with open(item / "project.manifest.yaml", "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f)
                        if data.get("project_id") == project_id:
                            return data
                    except Exception:
                        pass
            raise FileNotFoundError(f"Project manifest not found for: '{project_id}'")

        with open(manifest_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def create_project(
        self,
        slug: str,
        name: str,
        domain_type: str = "shopify_theme",
        icp_name: Optional[str] = None,
        value_proposition: Optional[str] = None,
        repo_root_rel: Optional[str] = None,
    ) -> ProjectSummary:
        """
        Scaffolds a new Sovereign Business Project with:
        1. docs/projects/<slug>/brand_dna.json (L2 ProjectDNA with 3 standard tracks)
        2. docs/projects/<slug>/project.manifest.yaml
        3. docs/canvas/projects/<slug>/main.canvas (Open JSON Canvas with Root + 3 Track Nodes + DAG edges)
        """
        clean_slug = slug.strip().lower().replace("-", "_")
        project_id = f"proj-{slug.strip().lower().replace('_', '-')}"
        account = self.load_account()

        proj_dir = self.projects_dir / clean_slug
        proj_canvas_dir = self.canvas_dir / clean_slug
        proj_dir.mkdir(parents=True, exist_ok=True)
        proj_canvas_dir.mkdir(parents=True, exist_ok=True)

        target_repo_root = repo_root_rel or f"./services/{clean_slug}"

        # 1. Construct Tracks
        track_1 = TrackSpec(
            track_id="track-theme-core" if domain_type == "shopify_theme" else "track-product-core",
            project_id=project_id,
            kind=TrackKind.CORE_RND,
            title="Track 1: R&D & Core Product Foundry",
            mission=f"Build and maintain sovereign core engine for {name}.",
            assigned_workhorse="dnk_shopify" if domain_type == "shopify_theme" else "core",
            repo_root_rel=target_repo_root,
            root_canvas_path=f"./docs/canvas/projects/{clean_slug}/track_core.canvas",
            default_actions=[
                DualSurfaceActionSpec(
                    action_id="core.verify_integrity",
                    label_uk="Перевірити цілісність ядра",
                    description_en="Verify 7-gate integrity or core tests",
                    surface_mode=ActionSurfaceMode.DUAL,
                    mcp_brick="dnk_shopify" if domain_type == "shopify_theme" else "core",
                    mcp_tool_name="shopify_verify_7gates" if domain_type == "shopify_theme" else "run_tests",
                    input_json_schema={},
                    ui_widget="button",
                    ui_tone="primary",
                    requires_human_confirmation=False,
                    idempotent=True,
                    allowed_states=[NodeLifecycleState.DECOMPOSED, NodeLifecycleState.AWAITING_APPROVAL],
                )
            ],
            deterministic_gates=["echo 'Gate Passed'"],
        )

        track_2 = TrackSpec(
            track_id="track-marketing-sales",
            project_id=project_id,
            kind=TrackKind.MARKETING_SALES,
            title="Track 2: Marketing, Sales & Conversion Funnels",
            mission=f"Craft high-converting landing pages, PDP copy, and sales enablement for {name}.",
            assigned_workhorse="dnk_distribution",
            repo_root_rel=target_repo_root,
            root_canvas_path=f"./docs/canvas/projects/{clean_slug}/track_marketing_sales.canvas",
            default_actions=[],
            deterministic_gates=[],
        )

        track_3 = TrackSpec(
            track_id="track-donor-audit",
            project_id=project_id,
            kind=TrackKind.DONOR_AUDIT,
            title="Track 3: SOTA Competitor Audit & Reverse-Engineering",
            mission="Deconstruct leading market solutions and extract high-value patterns.",
            assigned_workhorse="dnk_shopify" if domain_type == "shopify_theme" else "core",
            repo_root_rel="./docs/notes/sota_audits",
            root_canvas_path=f"./docs/canvas/projects/{clean_slug}/track_donor_audit.canvas",
            default_actions=[],
            deterministic_gates=[],
        )

        # 2. Construct ProjectDNA
        project_dna = ProjectDNA(
            project_id=project_id,
            account_id=account.account_id,
            project_name=name,
            domain_type=domain_type,  # type: ignore[arg-type]
            design_system=DesignSystemTokens(
                primary_colors={
                    "bg": "#0B0F17",
                    "surface": "#161B26",
                    "text": "#F3F4F6",
                    "accent": "#10B981",
                    "border": "#2D3748",
                },
                typography={
                    "heading": "Inter, sans-serif",
                    "body": "Inter, sans-serif",
                    "mono": "JetBrains Mono, monospace",
                },
                spacing_unit_px=4,
                border_radius_px=8,
                component_rules=["Zero external dependencies", "Semantic clean code"],
            ),
            icp=ICPProfile(
                segment_name=icp_name or f"High-tier {name} Clients",
                pain_points=[
                    "Bloated and slow legacy solutions",
                    "Rigid architectures lacking flexibility",
                ],
                value_proposition=value_proposition or f"Sovereign ultra-fast modular {name}",
                brand_voice_rules=[
                    "Direct response copy with crisp clarity",
                    "Assertive, technical precision, zero AI slop",
                    "Ukrainian for founder communications, English for code and store assets",
                ],
                forbidden_cliches=[
                    "Revolutionary",
                    "Game-changer",
                    "Seamless experience",
                    "Next-level",
                    "Magic in one click",
                ],
            ),
            business_rules=["100% test clean", "Zero external app bloat"],
            technical_constraints=["Apple Silicon local APFS testing", "FastMCP microkernel integration"],
            tracks=[track_1, track_2, track_3],
            system_inside_system_mode=True,
            dna_version="1.0.0",
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        # Write brand_dna.json
        dna_path = proj_dir / "brand_dna.json"
        with open(dna_path, "w", encoding="utf-8") as f:
            json.dump(project_dna.model_dump(), f, indent=2, ensure_ascii=False)

        # 3. Construct Manifest YAML
        manifest_path = proj_dir / "project.manifest.yaml"
        manifest_content = f"""# --- DNK-MRH-HEADER ---
# mrh_id: "docs/projects/{clean_slug}/project.manifest.yaml"
# purpose: "Canonical Project Manifest for Business Project '{name}'."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

project_id: "{project_id}"
account_id: "{account.account_id}"
project_name: "{name}"
domain_type: "{domain_type}"
dna_version: "1.0.0"
brand_dna_file: "./docs/projects/{clean_slug}/brand_dna.json"
main_canvas: "./docs/canvas/projects/{clean_slug}/main.canvas"

workstreams:
  track_1_core_rnd:
    track_id: "{track_1.track_id}"
    kind: "core_rnd"
    title: "{track_1.title}"
    assigned_workhorse: "{track_1.assigned_workhorse}"
    repo_root: "{track_1.repo_root_rel}"
    canvas: "./docs/canvas/projects/{clean_slug}/track_core.canvas"
    definition_of_done: "100% tests and gates pass"

  track_2_marketing_sales:
    track_id: "{track_2.track_id}"
    kind: "marketing_sales"
    title: "{track_2.title}"
    assigned_workhorse: "{track_2.assigned_workhorse}"
    repo_root: "{track_2.repo_root_rel}"
    canvas: "./docs/canvas/projects/{clean_slug}/track_marketing_sales.canvas"
    definition_of_done: "Conversion copywriting and funnels validated"

  track_3_donor_audit:
    track_id: "{track_3.track_id}"
    kind: "donor_audit"
    title: "{track_3.title}"
    assigned_workhorse: "{track_3.assigned_workhorse}"
    repo_root: "{track_3.repo_root_rel}"
    canvas: "./docs/canvas/projects/{clean_slug}/track_donor_audit.canvas"
    definition_of_done: "Reverse engineering audits complete"
"""
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest_content)

        # 4. Construct Open JSON Canvas 1.0 (main.canvas)
        canvas_path = proj_canvas_dir / "main.canvas"
        canvas_data = {
            "nodes": [
                {
                    "id": "node_project_root",
                    "type": "text",
                    "text": f"### 🚀 Project: {name} (L2 Project DNA)\n\n**Account**: `{account.account_id}`\n**Project ID**: `{project_id}`\n**Domain**: `{domain_type}`\n**Manifest**: `docs/projects/{clean_slug}/project.manifest.yaml`\n**Brand DNA**: `docs/projects/{clean_slug}/brand_dna.json`\n\n**Mission**:\n{project_dna.icp.value_proposition}",
                    "x": 600,
                    "y": 50,
                    "width": 420,
                    "height": 260,
                    "color": "5",
                },
                {
                    "id": "node_track_1_core_rnd",
                    "type": "text",
                    "text": f"### 🛠️ Track 1: Core Foundry\n\n**Track ID**: `{track_1.track_id}`\n**Workhorse**: `{track_1.assigned_workhorse}`\n**Repo Root**: `{track_1.repo_root_rel}`\n**Mission**: {track_1.mission}\n\n**Agent**: `denchik`\n**Gate**: `verify`",
                    "x": 100,
                    "y": 400,
                    "width": 380,
                    "height": 220,
                    "color": "2",
                },
                {
                    "id": "node_track_2_marketing_sales",
                    "type": "text",
                    "text": f"### 📈 Track 2: Marketing & Sales\n\n**Track ID**: `{track_2.track_id}`\n**Workhorse**: `{track_2.assigned_workhorse}`\n**Mission**: {track_2.mission}\n\n**Agent**: `strategist`\n**Gate**: `copy_review`",
                    "x": 620,
                    "y": 400,
                    "width": 380,
                    "height": 220,
                    "color": "3",
                },
                {
                    "id": "node_track_3_donor_audit",
                    "type": "text",
                    "text": f"### 🔍 Track 3: Competitor Audit\n\n**Track ID**: `{track_3.track_id}`\n**Workhorse**: `{track_3.assigned_workhorse}`\n**Mission**: {track_3.mission}\n\n**Agent**: `gerych`\n**Gate**: `verify_donor_audit`",
                    "x": 1140,
                    "y": 400,
                    "width": 380,
                    "height": 220,
                    "color": "6",
                },
            ],
            "edges": [
                {
                    "id": "edge_root_to_t1",
                    "fromNode": "node_project_root",
                    "fromSide": "bottom",
                    "toNode": "node_track_1_core_rnd",
                    "toSide": "top",
                    "label": "Workstream 1",
                },
                {
                    "id": "edge_root_to_t2",
                    "fromNode": "node_project_root",
                    "fromSide": "bottom",
                    "toNode": "node_track_2_marketing_sales",
                    "toSide": "top",
                    "label": "Workstream 2",
                },
                {
                    "id": "edge_root_to_t3",
                    "fromNode": "node_project_root",
                    "fromSide": "bottom",
                    "toNode": "node_track_3_donor_audit",
                    "toSide": "top",
                    "label": "Workstream 3",
                },
            ],
        }
        with open(canvas_path, "w", encoding="utf-8") as f:
            json.dump(canvas_data, f, indent=2, ensure_ascii=False)

        rel_proj_dir = f"./{proj_dir}" if not proj_dir.is_absolute() else str(proj_dir)
        rel_manifest_path = f"./{manifest_path}" if not manifest_path.is_absolute() else str(manifest_path)
        rel_dna_path = f"./{dna_path}" if not dna_path.is_absolute() else str(dna_path)
        rel_canvas_path = f"./{canvas_path}" if not canvas_path.is_absolute() else str(canvas_path)

        return ProjectSummary(
            project_id=project_id,
            project_name=name,
            domain_type=domain_type,
            account_id=account.account_id,
            project_dir=rel_proj_dir,
            manifest_path=rel_manifest_path,
            brand_dna_path=rel_dna_path,
            main_canvas_path=rel_canvas_path,
            tracks_count=len(project_dna.tracks),
            tracks=[
                {
                    "track_id": t.track_id,
                    "kind": t.kind.value,
                    "title": t.title,
                    "assigned_workhorse": t.assigned_workhorse,
                    "repo_root_rel": t.repo_root_rel,
                }
                for t in project_dna.tracks
            ],
        )

    def get_project_stats(self, project_id: str) -> ProjectStats:
        """Computes live execution telemetry for the project's ThoughtDAG canvas."""
        dna = self.get_project(project_id)
        canvas_path: Optional[Path] = None

        # 1. Try finding canvas from manifest first
        try:
            manifest = self.get_project_manifest(project_id)
            if manifest and "main_canvas" in manifest:
                p = Path(manifest["main_canvas"].lstrip("./"))
                if p.exists():
                    canvas_path = p
        except Exception:
            pass

        # 2. Check candidate directories
        if canvas_path is None:
            slug = project_id.replace("proj-", "").replace("-", "_")
            candidates = [
                self.canvas_dir / slug / "main.canvas",
                self.canvas_dir / slug.replace("shopify_", "") / "main.canvas",
                self.canvas_dir / "dnk_ecom" / "main.canvas",
            ]
            for c in candidates:
                if c.exists():
                    canvas_path = c
                    break

        if canvas_path is None or not canvas_path.exists():
            return ProjectStats(
                project_id=project_id,
                project_name=dna.project_name,
                domain_type=dna.domain_type,
                total_nodes=0,
                total_edges=0,
                nodes_by_state={},
                crystallized_count=0,
                pending_count=0,
                active_tracks=[t.track_id for t in dna.tracks],
            )

        with open(canvas_path, "r", encoding="utf-8") as f:
            canvas_data = json.load(f)

        nodes = canvas_data.get("nodes", [])
        edges = canvas_data.get("edges", [])

        state_counts: Dict[str, int] = {}
        crystallized = 0

        for n in nodes:
            text = n.get("text", "")
            if "CRYSTALLIZED" in text or n.get("color") == "4":
                state = "crystallized"
                crystallized += 1
            elif "RUNNING" in text:
                state = "running"
            elif "AWAITING" in text:
                state = "awaiting_approval"
            elif "node_track_" in n.get("id", "") or "node_project_root" in n.get("id", ""):
                state = "track_structural"
            else:
                state = "pending"
            state_counts[state] = state_counts.get(state, 0) + 1

        return ProjectStats(
            project_id=project_id,
            project_name=dna.project_name,
            domain_type=dna.domain_type,
            total_nodes=len(nodes),
            total_edges=len(edges),
            nodes_by_state=state_counts,
            crystallized_count=crystallized,
            pending_count=len(nodes) - crystallized - state_counts.get("track_structural", 0),
            active_tracks=[t.track_id for t in dna.tracks],
        )

    def format_ascii_dashboard(self) -> str:
        """Renders an ASCII Kanban and project portfolio overview for terminal or chat."""
        projects = self.list_projects()
        account = self.load_account()

        lines = [
            "╔══════════════════════════════════════════════════════════════════════════════╗",
            f"║ 👑 DNK OS VIBE-CODER CONTROL PLANE: {account.owner_name} ({account.account_id})",
            "╠══════════════════════════════════════════════════════════════════════════════╣",
        ]

        if not projects:
            lines.append("║ Жодного зареєстрованого бізнес-проєкту. Створіть перший: just new-project  ║")
        else:
            for p in projects:
                stats = self.get_project_stats(p.project_id)
                lines.append(f"║ 🚀 Проєкт: {p.project_name} [`{p.project_id}`]")
                lines.append(f"║    ├─ Домен: `{p.domain_type}` | Треків: {p.tracks_count} | Нод у Canvas: {stats.total_nodes}")
                lines.append(f"║    ├─ Стан: 📌 Завершено: {stats.crystallized_count} | ⏳ У роботі/черзі: {stats.pending_count}")
                lines.append(f"║    └─ Canvas: `{p.main_canvas_path}`")
                for t in p.tracks:
                    lines.append(f"║       • {t['title']} (Workhorse: `{t['assigned_workhorse']}`)")
                lines.append("╟──────────────────────────────────────────────────────────────────────────────╢")

        lines.append("╚══════════════════════════════════════════════════════════════════════════════╝")
        return "\n".join(lines)


# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="DNK OS Vibe-Coder Project Control Plane")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # list
    subparsers.add_parser("list", help="List all registered business projects")

    # get
    get_p = subparsers.add_parser("get", help="Get ProjectDNA JSON")
    get_p.add_argument("project_id", help="e.g. proj-shopify-dnk-ecom")

    # stats
    stats_p = subparsers.add_parser("stats", help="Get project execution telemetry")
    stats_p.add_argument("project_id", help="e.g. proj-shopify-dnk-ecom")

    # new
    new_p = subparsers.add_parser("new", help="Scaffold a new project")
    new_p.add_argument("slug", help="URL-friendly slug (e.g. fashion_brand)")
    new_p.add_argument("name", help="Display name (e.g. 'Fashion Brand Luxury')")
    new_p.add_argument("--domain", default="shopify_theme", choices=["shopify_theme", "saas_app", "agency_pipeline", "media_product"])
    new_p.add_argument("--icp", default=None, help="Target ICP segment name")
    new_p.add_argument("--value-prop", default=None, help="Value proposition")
    new_p.add_argument("--repo-root", default=None, help="Relative path to working directory")

    args = parser.parse_args()
    engine = ProjectEngine()

    if args.subcommand == "list":
        print(engine.format_ascii_dashboard())

    elif args.subcommand == "get":
        dna = engine.get_project(args.project_id)
        print(json.dumps(dna.model_dump(), indent=2, ensure_ascii=False))

    elif args.subcommand == "stats":
        stats = engine.get_project_stats(args.project_id)
        print(json.dumps(stats.model_dump(), indent=2, ensure_ascii=False))

    elif args.subcommand == "new":
        summary = engine.create_project(
            slug=args.slug,
            name=args.name,
            domain_type=args.domain,
            icp_name=args.icp,
            value_proposition=args.value_prop,
            repo_root_rel=args.repo_root,
        )
        print(f"✅ Проєкт успішно створено: {summary.project_name} (`{summary.project_id}`)")
        print(f"  • Brand DNA: {summary.brand_dna_path}")
        print(f"  • Manifest:  {summary.manifest_path}")
        print(f"  • Canvas:    {summary.main_canvas_path}")


if __name__ == "__main__":
    main()
