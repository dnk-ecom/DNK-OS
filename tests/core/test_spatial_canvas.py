# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_spatial_canvas.py"
# purpose: "Senior Developer Test Suite verifying Spatial Canvas per-node session isolation, context surgery, and JSON Canvas 1.0 sync."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-15"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

import json
import shutil
import tempfile
from pathlib import Path
import pytest

from core.canvas.session_router import SpatialCanvasSessionRouter


@pytest.fixture
def temp_canvas_env(tmp_path: Path):
    """Create an isolated test environment with SQLite DB and a test .canvas file."""
    db_path = tmp_path / "test_sessions.db"
    canvas_path = tmp_path / "test_pipeline.canvas"

    canvas_data = {
        "nodes": [
            {
                "id": "node_1",
                "type": "text",
                "text": "### 1. Inception\n**Agent**: `researcher_prime`\nGoal: Collect market benchmarks.",
                "x": 0,
                "y": 0,
                "width": 300,
                "height": 200,
                "color": "5",
            },
            {
                "id": "node_2",
                "type": "text",
                "text": "### 2. Strategy\n**Agent**: `strategist_prime`\nGoal: Build CRO funnel.",
                "x": 400,
                "y": 0,
                "width": 300,
                "height": 200,
                "color": "2",
            },
        ],
        "edges": [
            {
                "id": "edge_1_to_2",
                "fromNode": "node_1",
                "fromSide": "right",
                "toNode": "node_2",
                "toSide": "left",
                "label": "Benchmark Matrix",
            }
        ],
    }
    canvas_path.write_text(json.dumps(canvas_data, indent=2), encoding="utf-8")

    router = SpatialCanvasSessionRouter(db_path=db_path)
    return router, canvas_path, db_path


def test_deterministic_session_id_mapping(temp_canvas_env):
    router, _, _ = temp_canvas_env
    session_id = router.format_session_id("shopify_vibe_pipeline.canvas", "node_competitors")
    assert session_id == "node:shopify_vibe_pipeline:node_competitors"


def test_per_node_conversational_isolation(temp_canvas_env):
    router, canvas_path, _ = temp_canvas_env
    canvas_id = canvas_path.stem

    # Node 1 session & message
    s1 = router.get_or_create_session(canvas_id, "node_1", "researcher_prime")
    router.post_message(s1.id, "user", "Research top 5 competitors in beauty niche.")
    router.post_message(s1.id, "assistant", "Done. Found 5 DTC brands. Average AOV is $75.")

    # Node 2 session & message
    s2 = router.get_or_create_session(canvas_id, "node_2", "strategist_prime")
    router.post_message(s2.id, "user", "Design PDP upsell funnel.")

    # Verify complete isolation
    msgs1 = router.get_messages(s1.id)
    msgs2 = router.get_messages(s2.id)

    assert len(msgs1) == 2
    assert len(msgs2) == 1
    assert "AOV is $75" in msgs1[1].content
    assert "upsell funnel" in msgs2[0].content
    # Node 2 must have ZERO visibility of Node 1's conversational banter
    assert not any("AOV is $75" in m.content for m in msgs2)


def test_context_surgery_and_upstream_contract_injection(temp_canvas_env):
    router, canvas_path, _ = temp_canvas_env
    canvas_id = canvas_path.stem

    # 1. Compile Node 1 context before crystallization (root node)
    ctx_1 = router.compile_node_context(canvas_path, "node_1")
    assert ctx_1.node_id == "node_1"
    assert ctx_1.agent_role == "researcher_prime"
    assert len(ctx_1.upstream_contracts) == 0
    assert "No parent nodes" in ctx_1.system_prompt

    # 2. Node 1 finishes and crystallizes its output contract
    summary = "Audited 5 brands: Key bundles are 3-pack (-15%) and free shipping threshold at $60."
    artifacts = ["artifacts/competitors.json", "docs/notes/pricing.md"]
    router.crystallize_node(canvas_path, "node_1", summary, artifacts)

    # 3. Verify .canvas file was updated on disk
    canvas_json = json.loads(canvas_path.read_text(encoding="utf-8"))
    node_1_data = next(n for n in canvas_json["nodes"] if n["id"] == "node_1")
    assert "CRYSTALLIZED" in node_1_data["text"]
    assert "free shipping threshold at $60" in node_1_data["text"]
    assert node_1_data["color"] == "4"  # Green

    # 4. Now compile Node 2 context (downstream child node)
    ctx_2 = router.compile_node_context(canvas_path, "node_2")
    assert ctx_2.node_id == "node_2"
    assert ctx_2.agent_role == "strategist_prime"
    assert len(ctx_2.upstream_contracts) == 1
    assert ctx_2.upstream_contracts[0].node_id == "node_1"
    assert "free shipping threshold at $60" in ctx_2.upstream_contracts[0].summary
    assert "artifacts/competitors.json" in ctx_2.upstream_contracts[0].artifacts

    # 5. Check synthesized zero-waste system prompt
    assert "Parent [node_1]" in ctx_2.system_prompt
    assert "Key bundles are 3-pack" in ctx_2.system_prompt
    assert "`artifacts/competitors.json`" in ctx_2.system_prompt


def test_canonical_shopify_vibe_pipeline_canvas_validity():
    """Verify the production docs/canvas/shopify_vibe_pipeline.canvas file."""
    pipeline_path = Path("docs/canvas/shopify_vibe_pipeline.canvas")
    assert pipeline_path.exists(), "shopify_vibe_pipeline.canvas must exist"

    data = json.loads(pipeline_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    assert len(nodes) == 5, "Must have exactly 5 nodes for the Shopify pipeline"
    assert len(edges) == 4, "Must have 4 connecting edges forming the linear DAG"

    expected_node_ids = [
        "node_competitors",
        "node_cro_audit",
        "node_brand_dna",
        "node_liquid_blocks",
        "node_pdp_copywriting",
    ]
    for nid in expected_node_ids:
        assert any(n["id"] == nid for n in nodes), f"Node {nid} must exist in canvas"

    # Verify edge connectivity
    edge_pairs = [(e["fromNode"], e["toNode"]) for e in edges]
    assert ("node_competitors", "node_cro_audit") in edge_pairs
    assert ("node_cro_audit", "node_brand_dna") in edge_pairs
    assert ("node_brand_dna", "node_liquid_blocks") in edge_pairs
    assert ("node_liquid_blocks", "node_pdp_copywriting") in edge_pairs


def test_three_tier_dag_context_flow(tmp_path: Path):
    """Test A -> B -> C: Node C compiles crystallized outputs from its immediate parent B."""
    db_path = tmp_path / "deep_sessions.db"
    canvas_path = tmp_path / "chain.canvas"

    canvas_data = {
        "nodes": [
            {"id": "node_a", "type": "text", "text": "### A. Specs\n**Agent**: `spec_agent`\nSpec details.", "x": 0, "y": 0, "width": 200, "height": 150},
            {"id": "node_b", "type": "text", "text": "### B. Code\n**Agent**: `builder_agent`\nCode details.", "x": 300, "y": 0, "width": 200, "height": 150},
            {"id": "node_c", "type": "text", "text": "### C. Review\n**Agent**: `auditor_agent`\nReview details.", "x": 600, "y": 0, "width": 200, "height": 150},
        ],
        "edges": [
            {"id": "e1", "fromNode": "node_a", "toNode": "node_b"},
            {"id": "e2", "fromNode": "node_b", "toNode": "node_c"},
        ],
    }
    canvas_path.write_text(json.dumps(canvas_data, indent=2), encoding="utf-8")
    router = SpatialCanvasSessionRouter(db_path=db_path)

    # Crystallize A
    router.crystallize_node(canvas_path, "node_a", "Spec finalized: v1.0", ["specs/v1.yaml"])

    # Compile B: sees A
    ctx_b = router.compile_node_context(canvas_path, "node_b")
    assert len(ctx_b.upstream_contracts) == 1
    assert ctx_b.upstream_contracts[0].node_id == "node_a"
    assert "Spec finalized: v1.0" in ctx_b.upstream_contracts[0].summary

    # Crystallize B
    router.crystallize_node(canvas_path, "node_b", "Build complete: 0 errors", ["dist/app.wasm"])

    # Compile C: sees B (clean, isolated boundary)
    ctx_c = router.compile_node_context(canvas_path, "node_c")
    assert len(ctx_c.upstream_contracts) == 1
    assert ctx_c.upstream_contracts[0].node_id == "node_b"
    assert "Build complete: 0 errors" in ctx_c.upstream_contracts[0].summary
    assert "dist/app.wasm" in ctx_c.upstream_contracts[0].artifacts


def test_pilot_project_dna_auto_injection(tmp_path: Path):
    """Test L2 ProjectDNA auto-injection into compiled node prompt (Zero Context Re-typing)."""
    router = SpatialCanvasSessionRouter(db_path=tmp_path / "dna_test.db")
    canvas_path = Path("docs/canvas/projects/dnk_ecom/main.canvas")
    assert canvas_path.exists(), "Pilot canvas must exist"

    # Compile context for T1.1 (Dual-Ready Theme Blocks)
    ctx = router.compile_node_context(canvas_path, "node_t1_dual_ready_blocks")
    assert ctx.node_id == "node_t1_dual_ready_blocks"
    assert ctx.agent_role == "dnk_shopify"

    # Verify L2 ProjectDNA was auto-discovered and attached
    assert ctx.project_dna is not None
    assert ctx.project_dna["project_id"] == "proj-shopify-dnk-ecom"
    assert ctx.project_dna["domain_type"] == "shopify_theme"

    # Verify L2 DNA sections are auto-injected into the prompt string
    assert "## 🧬 L2 Project DNA: Shopify Theme DNK-Ecom" in ctx.system_prompt
    assert "High-converting Shopify 2.0 Merchants & DTC Brands" in ctx.system_prompt
    assert "DNK-Ecom-Zerno-v.0.1.0 built for Shopify Theme Store" in ctx.system_prompt
    assert "Shopify Theme Store submission standards" in ctx.system_prompt


def test_chat_to_dag_subtask_tree_spawner(temp_canvas_env):
    """Test Chat-to-DAG Tree Spawner creating child subtask nodes and directed edges."""
    router, canvas_path, _ = temp_canvas_env
    from core.domain.vibe_core_contracts import (
        SubtaskNodeSpec,
        AgentRole,
        NodeLifecycleState,
        VerificationCriteria,
        DualSurfaceActionSpec,
    )

    subtasks = [
        SubtaskNodeSpec(
            node_id="subtask_1",
            canvas_id="test_pipeline",
            project_id="proj-shopify-dnk-ecom",
            track_id="track-theme-core",
            parent_node_id="node_2",
            session_id="node:test_pipeline:subtask_1",
            title="Create Hero Theme Block",
            goal="Synthesize modular hero block with {% doc %} typing",
            assigned_agent=AgentRole.DOMAIN_SHOPIFY,
            verification=VerificationCriteria(command="shopify theme check blocks/hero.liquid"),
            actions=[
                DualSurfaceActionSpec(
                    action_id="shopify.run_theme_check",
                    label_uk="Запустити Theme Check",
                    description_en="Run theme check",
                    mcp_brick="brick_04_shopify_engine",
                    mcp_tool_name="run_theme_check",
                )
            ],
        ),
        SubtaskNodeSpec(
            node_id="subtask_2",
            canvas_id="test_pipeline",
            project_id="proj-shopify-dnk-ecom",
            track_id="track-theme-core",
            parent_node_id="node_2",
            session_id="node:test_pipeline:subtask_2",
            title="Audit Hero Block Accessibility",
            goal="Ensure zero contrast and keyboard navigation errors",
            assigned_agent=AgentRole.AUDITOR_GERYСH,
            verification=VerificationCriteria(command="pnpm test:a11y"),
        ),
    ]

    created = router.decompose_node_to_subtasks(canvas_path, "node_2", subtasks)
    assert created == ["subtask_1", "subtask_2"]

    # Verify canvas file was updated with new nodes and edges
    data = json.loads(canvas_path.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in data["nodes"]}
    edges = data["edges"]

    assert "subtask_1" in nodes
    assert "subtask_2" in nodes
    assert "Create Hero Theme Block" in nodes["subtask_1"]["text"]
    assert "shopify.run_theme_check" in nodes["subtask_1"]["text"]
    assert "Audit Hero Block Accessibility" in nodes["subtask_2"]["text"]

    # Verify parent node was updated to DECOMPOSED
    assert "DECOMPOSED" in nodes["node_2"]["text"]
    assert nodes["node_2"]["color"] == "3"

    # Verify edges were created from node_2 to subtasks
    edge_pairs = [(e["fromNode"], e["toNode"]) for e in edges]
    assert ("node_2", "subtask_1") in edge_pairs
    assert ("node_2", "subtask_2") in edge_pairs

    # Verify isolated SQLite WAL sessions exist for subtasks
    s1 = router.get_or_create_session(canvas_path.stem, "subtask_1")
    s2 = router.get_or_create_session(canvas_path.stem, "subtask_2")
    assert s1.agent_role == "dnk_shopify"
    assert s2.agent_role == "gerych"


def test_vibe_core_contracts_validation():
    """Verify Pydantic v2 schemas boundaries and invariants."""
    from core.domain.vibe_core_contracts import (
        ProjectDNA,
        DesignSystemTokens,
        ICPProfile,
        TrackSpec,
        TrackKind,
        SubtaskNodeSpec,
        AgentRole,
        VerificationCriteria,
    )

    # 1. Duplicate track_id validation
    with pytest.raises(ValueError, match="Duplicate track_id"):
        ProjectDNA(
            project_id="proj-invalid-dup",
            account_id="acct-test",
            project_name="Duplicate Track Test",
            domain_type="shopify_theme",
            design_system=DesignSystemTokens(),
            icp=ICPProfile(segment_name="DTC", pain_points=["Slow"], value_proposition="Fast"),
            tracks=[
                TrackSpec(
                    track_id="track-dup",
                    project_id="proj-invalid-dup",
                    kind=TrackKind.CORE_RND,
                    title="Track A",
                    mission="Mission A",
                    assigned_workhorse="dnk_shopify",
                    repo_root_rel="./services/a",
                    root_canvas_path="./canvas/a.canvas",
                ),
                TrackSpec(
                    track_id="track-dup",
                    project_id="proj-invalid-dup",
                    kind=TrackKind.MARKETING_SALES,
                    title="Track B",
                    mission="Mission B",
                    assigned_workhorse="dnk_distribution",
                    repo_root_rel="./services/b",
                    root_canvas_path="./canvas/b.canvas",
                ),
            ],
        )

    # 2. Subtask max tool calls boundary (<= 25 per MASE)
    with pytest.raises(Exception):
        SubtaskNodeSpec(
            node_id="subtask_invalid_budget",
            canvas_id="test",
            project_id="proj-test",
            track_id="track-1",
            session_id="node:test:subtask_invalid",
            title="Exceeds Budget",
            goal="Overload",
            assigned_agent=AgentRole.BUILDER_DENCHIK,
            max_tool_calls=50,  # Invalid: must be <= 25
            verification=VerificationCriteria(command="exit 0"),
        )


def test_pilot_dnk_ecom_main_canvas_topology():
    """Verify docs/canvas/projects/dnk_ecom/main.canvas topology and 3-track connectivity."""
    canvas_path = Path("docs/canvas/projects/dnk_ecom/main.canvas")
    assert canvas_path.exists(), "Pilot main.canvas must exist"

    data = json.loads(canvas_path.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in data.get("nodes", [])}
    edges = data.get("edges", [])

    assert len(nodes) == 7, "Must contain exactly 7 nodes (Root + 3 Tracks + 3 Subtasks)"
    assert len(edges) == 8, "Must contain 8 edges (3 root->tracks, 3 tracks->subtasks, 2 cross-wires)"

    # Verify 3 workstreams present
    assert "node_project_root" in nodes
    assert "node_track_1_core_rnd" in nodes
    assert "node_track_2_marketing_sales" in nodes
    assert "node_track_3_donor_audit" in nodes

    # Verify cross-wires
    edge_pairs = [(e["fromNode"], e["toNode"]) for e in edges]
    assert ("node_t3_sugar_theme_audit", "node_t1_dual_ready_blocks") in edge_pairs
    assert ("node_t1_dual_ready_blocks", "node_t2_pdp_copywriting") in edge_pairs


def test_grounding_guard_anti_hallucination():
    """Verify GroundingGuard deterministically flags ungrounded numbers and dates."""
    from core.sentinel.grounding_guard import GroundingGuard, GroundingValidationError

    source_text = "The audit analyzed 5 stores. The average conversion rate is 3.5% with a cart AOV of $75.00."

    # 1. Grounded arguments pass
    valid_args = {"stores_audited": 5, "conversion_rate": 3.5, "aov": 75.00}
    ungrounded = GroundingGuard.validate_grounding(valid_args, source_text)
    assert len(ungrounded) == 0

    # 2. Hallucinated numeric values fail
    hallucinated_args = {"stores_audited": 5, "fake_profit": 9999.99}
    ungrounded_fail = GroundingGuard.validate_grounding(hallucinated_args, source_text)
    assert len(ungrounded_fail) == 1
    assert "fake_profit=9999.99" in ungrounded_fail[0]

    with pytest.raises(GroundingValidationError, match="ungrounded numeric hallucination"):
        GroundingGuard.enforce(hallucinated_args, source_text, tool_name="cro_report")


def test_topological_sort_subdag_kahn():
    """Verify chain-preserving Kahn's topological sort on SubDAG with branching and merge."""
    nodes_map = {
        "n_root": {"id": "n_root"},
        "n_branch_a": {"id": "n_branch_a"},
        "n_branch_b": {"id": "n_branch_b"},
        "n_merge": {"id": "n_merge"},
    }
    # Diamond graph: root -> branch_a -> merge, root -> branch_b -> merge
    edges = [
        {"fromNode": "n_root", "toNode": "n_branch_a"},
        {"fromNode": "n_branch_a", "toNode": "n_merge"},
        {"fromNode": "n_root", "toNode": "n_branch_b"},
        {"fromNode": "n_branch_b", "toNode": "n_merge"},
    ]

    order = SpatialCanvasSessionRouter.topological_sort_subdag(nodes_map, edges, "n_merge")
    assert len(order) == 3
    assert order[0] == "n_root"
    assert set(order[1:3]) == {"n_branch_a", "n_branch_b"}


def test_compile_lod_dna_slice_projections():
    """Verify Role-Based LOD DNA Projection (ADR-092 / DEC-120)."""
    from core.canvas.session_router import compile_lod_dna_slice
    from core.domain.vibe_core_contracts import ProjectDNA, DesignSystemTokens, ICPProfile, TrackSpec, TrackKind

    dna = ProjectDNA(
        project_id="proj-lod-test",
        account_id="acct-dnk-maksym",
        project_name="LOD Test Project",
        domain_type="shopify_theme",
        design_system=DesignSystemTokens(
            spacing_unit_px=8,
            border_radius_px=12,
            primary_colors={"accent": "#10B981"},
            component_rules=["Strict atomic blocks"]
        ),
        icp=ICPProfile(
            segment_name="High-Growth DTC",
            pain_points=["Slow checkout", "High bounce"],
            value_proposition="Ultra-fast zero-app theme",
            brand_voice_rules=["Crisp clarity", "Technical precision"],
            forbidden_cliches=["Revolutionary", "Game-changer"]
        ),
        business_rules=["Zero jQuery", "100% theme-check clean"],
        technical_constraints=["Theme store guidelines", "FastMCP dual-mount"],
        tracks=[
            TrackSpec(
                track_id="track-1",
                project_id="proj-lod-test",
                kind=TrackKind.CORE_RND,
                title="Track 1",
                mission="Mission",
                assigned_workhorse="dnk_shopify",
                repo_root_rel="./theme",
                root_canvas_path="./canvas/test.canvas",
            )
        ]
    )

    # 1. Builder projection (Denchik): includes tokens & constraints, excludes cliches
    builder_slice = compile_lod_dna_slice(dna, "denchik")
    assert "LOD: Builder Projection" in builder_slice
    assert "Spacing=8px" in builder_slice
    assert "Theme store guidelines" in builder_slice
    assert "Game-changer" not in builder_slice
    assert "High-Growth DTC" not in builder_slice

    # 2. Copywriter projection (Strategist): includes ICP & cliches, excludes CSS tokens
    copy_slice = compile_lod_dna_slice(dna, "strategist")
    assert "LOD: Strategist & Copywriting Projection" in copy_slice
    assert "High-Growth DTC" in copy_slice
    assert "Game-changer" in copy_slice
    assert "Spacing=8px" not in copy_slice

    # 3. Auditor / Architecture projection (Gerych): includes constraints & business rules
    arch_slice = compile_lod_dna_slice(dna, "gerych")
    assert "LOD: Architecture & Auditor Projection" in arch_slice
    assert "Theme store guidelines" in arch_slice
    assert "Zero jQuery" in arch_slice


def test_context_surgery_token_budget_pruning(tmp_path: Path):
    """Verify that Context Surgery prunes massive upstream contracts to stay <= 1500 tokens."""
    db_path = tmp_path / "budget_test.db"
    canvas_path = tmp_path / "budget_pipeline.canvas"

    # Parent node has a massive 12,000 character output (~3000 tokens)
    massive_summary = "CRITICAL FACT: Key finding A. " + ("Data payload filler text " * 500)
    canvas_data = {
        "nodes": [
            {
                "id": "node_heavy_parent",
                "type": "text",
                "text": "### Parent Heavy\n**Agent**: `researcher`\nHeavy research.",
                "x": 0,
                "y": 0,
                "width": 300,
                "height": 200,
            },
            {
                "id": "node_child_receiver",
                "type": "text",
                "text": "### Child Receiver\n**Agent**: `denchik`\nImplement based on findings.",
                "x": 400,
                "y": 0,
                "width": 300,
                "height": 200,
            },
        ],
        "edges": [
            {
                "id": "edge_h_to_c",
                "fromNode": "node_heavy_parent",
                "toNode": "node_child_receiver",
            }
        ],
    }
    canvas_path.write_text(json.dumps(canvas_data, indent=2), encoding="utf-8")
    router = SpatialCanvasSessionRouter(db_path=db_path)

    # Crystallize parent with massive summary
    router.crystallize_node(canvas_path, "node_heavy_parent", massive_summary, ["artifacts/big.json"])

    # Compile child context with max_upstream_tokens = 1500
    ctx = router.compile_node_context(canvas_path, "node_child_receiver", max_upstream_tokens=1500)

    # Must be pruned/condensed to fit token budget (1500 tokens * 4 chars = 6000 chars limit)
    assert len(ctx.upstream_contracts) == 1
    contract = ctx.upstream_contracts[0]
    assert len(contract.summary) <= 6000
    assert "[condensed <= 1500 tok]" in contract.summary
    assert "Key finding A" in contract.summary

