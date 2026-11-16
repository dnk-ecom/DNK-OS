# --- DNK-MRH-HEADER ---
# mrh_id: "core/kernel_cli.py"
# purpose: "Headless CLI command dispatcher for FastMCP Microkernel (DEC-110 Narrow Waist extraction)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import asyncio
import json
import logging
import os
from typing import Any, List

logger = logging.getLogger("dnk.core.kernel_cli")


async def run_cli_command(kernel: Any, args: List[str]) -> int:
    """
    Headless CLI handler for DNK OS Microkernel.
    Allows fast atomic execution by Smol-Workers or scripts without MCP schema overhead.
    """
    if not args or args[0] in ("-h", "--help", "help"):
        print("DNK OS Microkernel CLI:")
        print("  status                    - Show kernel health & status")
        print("  thought <dsl_text>        - Parse and validate ThoughtDSL")
        print("  action <type> [json]      - Dispatch an action to the Action Bus")
        print("  memory <topic> [limit]    - Query SCONES cognitive memory")
        print("  codemap <file_path>       - Generate AST symbol map of a file")
        print("  prune <file_or_text>      - Prune verbose logs")
        print("  clipboard <status|search|projects|screenshots> - Query ClipBoardLine database")
        print("  node <context|post|messages|crystallize> [args...] - Spatial Canvas node session control")
        return 0

    cmd = args[0]
    if cmd == "status":
        print(json.dumps(kernel.get_system_status(), indent=2, ensure_ascii=False))
        return 0
    elif cmd == "thought":
        dsl = args[1] if len(args) > 1 else ""
        res = kernel.parse_thoughts(dsl)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res.get("success") is True else 1
    elif cmd == "action":
        action_type = args[1] if len(args) > 1 else "ping"
        payload_str = args[2] if len(args) > 2 else "{}"
        try:
            payload = json.loads(payload_str)
        except Exception:
            payload = {"raw": payload_str}
        res = await kernel.dispatch_action(action_type, payload)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    elif cmd == "memory":
        topic = args[1] if len(args) > 1 else "general"
        limit = int(args[2]) if len(args) > 2 else 5
        res = await kernel.query_memory(topic, limit=limit)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    elif cmd == "codemap":
        from core.code_map import generate_code_map_from_file

        path = args[1] if len(args) > 1 else ""
        res = generate_code_map_from_file(path)
        print(res.to_compact_summary())
        return 0 if not res.error else 1
    elif cmd == "prune":
        from core.pruner import prune_terminal_output

        target = args[1] if len(args) > 1 else ""
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = target
        print(prune_terminal_output(content))
        return 0
    elif cmd == "atlas":
        from core.self_awareness import SelfAwarenessEngine
        atlas = SelfAwarenessEngine().build_live_atlas()
        print(json.dumps(atlas, indent=2, ensure_ascii=False))
        return 0
    elif cmd == "locate":
        from core.self_awareness import SelfAwarenessEngine
        query = args[1] if len(args) > 1 else ""
        res = SelfAwarenessEngine().recommend_edit_targets(query)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    elif cmd == "companion":
        from core.orchestrator.thought_companion import FirstThoughtCompanionAgent, ThoughtCompanionRequest
        raw_thought = args[1] if len(args) > 1 else ""
        agent = FirstThoughtCompanionAgent()
        res = agent.structure_thoughts(ThoughtCompanionRequest(raw_thought=raw_thought))
        print(json.dumps(res.model_dump(mode="json"), indent=2, ensure_ascii=False))
        return 0
    elif cmd == "learn":
        from core.self_awareness import SelfAwarenessEngine
        topic = args[1] if len(args) > 1 else "general"
        insight = args[2] if len(args) > 2 else ""
        module_path = args[3] if len(args) > 3 else "core/kernel.py"
        res = SelfAwarenessEngine().record_learning(topic=topic, insight=insight, module_path=module_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    elif cmd == "catalog":
        from core.registry.repo_catalog import search_sota_repositories
        query = args[1] if len(args) > 1 else ""
        res = search_sota_repositories(query)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    elif cmd == "decision":
        from core.orchestrator.decision_draft import evaluate_decision, append_to_adhd_registry
        dec_id = args[1] if len(args) > 1 else "DEC-000"
        title = args[2] if len(args) > 2 else ""
        solution = args[3] if len(args) > 3 else ""
        res = evaluate_decision(decision_id=dec_id, title=title, proposed_solution=solution, domain="core")
        append_to_adhd_registry(res)
        print(json.dumps(res.model_dump() if hasattr(res, 'model_dump') else str(res), indent=2, ensure_ascii=False))
        return 0
    elif cmd == "blast":
        from core.orchestrator.sota_skills_engine import BlastRadiusAnalyzer
        target_path = args[1] if len(args) > 1 else "core/kernel.py"
        res = BlastRadiusAnalyzer().analyze_blast_radius(target_path)
        print(json.dumps(res.model_dump(mode="json"), indent=2, ensure_ascii=False))
        return 0
    elif cmd == "review":
        from core.orchestrator.sota_skills_engine import run_two_axis_review
        target_path = args[1] if len(args) > 1 else "core/kernel.py"
        res = run_two_axis_review(target_path)
        print(json.dumps(res.model_dump(mode="json"), indent=2, ensure_ascii=False))
        return 0
    elif cmd == "clipboard":
        from core.adapters.dnk_clipboard_adapter import DNKClipboardAdapter
        sub = args[1] if len(args) > 1 else "status"
        adapter = DNKClipboardAdapter()
        if sub == "status":
            print(json.dumps(adapter.get_database_status(), indent=2, ensure_ascii=False))
        elif sub == "projects":
            res = {"collections": adapter.list_collections(), "tags": adapter.list_tags()}
            print(json.dumps(res, indent=2, ensure_ascii=False))
        elif sub == "screenshots":
            ocr_filter = args[2] if len(args) > 2 else ""
            res = adapter.get_recent_screenshots(limit=10, ocr_filter=ocr_filter or None)
            print(json.dumps(res, indent=2, ensure_ascii=False))
        elif sub == "search":
            query = args[2] if len(args) > 2 else ""
            res = adapter.search_items(query=query or None, limit=10)
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"Unknown clipboard command: {sub}. Use status, projects, screenshots, or search.")
        return 0
    elif cmd == "node":
        from pathlib import Path
        if len(args) < 2:
            print("Usage: node <context|post|messages|crystallize> [args...]")
            return 1
        sub = args[1]
        if sub == "context":
            if len(args) < 4:
                print("Usage: node context <canvas_path> <node_id>")
                return 1
            c_path = Path(args[2])
            n_id = args[3]
            ctx = kernel.session_router.compile_node_context(canvas_path=c_path, node_id=n_id)
            print(json.dumps(ctx.model_dump() if hasattr(ctx, "model_dump") else str(ctx), indent=2, ensure_ascii=False))
            return 0
        elif sub == "post":
            if len(args) < 6:
                print("Usage: node post <canvas_id> <node_id> <role> <message>")
                return 1
            c_id = args[2]
            n_id = args[3]
            role = args[4]
            message = args[5]
            res = kernel.post_node_message(canvas_id=c_id, node_id=n_id, role=role, content=message)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return 0
        elif sub in ("messages", "history"):
            if len(args) < 4:
                print("Usage: node messages <canvas_id> <node_id> [limit]")
                return 1
            c_id = args[2]
            n_id = args[3]
            limit = int(args[4]) if len(args) > 4 else 50
            msgs = kernel.get_node_messages(canvas_id=c_id, node_id=n_id, limit=limit)
            print(json.dumps(msgs, indent=2, ensure_ascii=False))
            return 0
        elif sub == "crystallize":
            if len(args) < 5:
                print("Usage: node crystallize <canvas_path> <node_id> <summary> [artifacts_json]")
                return 1
            c_path = Path(args[2])
            n_id = args[3]
            summary = args[4]
            artifacts = json.loads(args[5]) if len(args) > 5 else []
            res = kernel.session_router.crystallize_node(
                canvas_path=c_path, node_id=n_id, summary=summary, artifact_refs=artifacts
            )
            print(json.dumps(res.model_dump() if hasattr(res, "model_dump") else str(res), indent=2, ensure_ascii=False))
            return 0
        else:
            print(f"Unknown node command: {sub}. Use context, post, messages, or crystallize.")
            return 1
    else:
        print(f"Unknown CLI command: {cmd}")
        return 1
