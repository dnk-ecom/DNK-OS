# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_hermes_ext/overlay/tools/dnk_adversarial_review_tool.py"
# purpose: "Native Hermes tool executing 2-Agent Adversarial Review (Red-Team Auditor vs Blue-Team Builder)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-27"
# --- END DNK-MRH-HEADER ---

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DNKAdversarialReviewTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DNKOS_MVP_PATH = HUB_ROOT
if str(DNKOS_MVP_PATH) not in sys.path:
    sys.path.insert(0, str(DNKOS_MVP_PATH))

# Ensure namespace/package path includes core if core is already imported
if "core" in sys.modules and hasattr(sys.modules["core"], "__path__"):
    mvp_core_path = str(DNKOS_MVP_PATH / "core")
    if mvp_core_path not in sys.modules["core"].__path__:
        sys.modules["core"].__path__.insert(0, mvp_core_path)

try:
    from core.security.adversarial_review import AdversarialReviewEngine
except ImportError:
    try:
        import importlib.util
        adv_path = DNKOS_MVP_PATH / "core" / "security" / "adversarial_review.py"
        if adv_path.exists():
            spec = importlib.util.spec_from_file_location("adversarial_review", str(adv_path))
            if spec and spec.loader:
                adv_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(adv_module)
                AdversarialReviewEngine = getattr(adv_module, "AdversarialReviewEngine", None)
            else:
                AdversarialReviewEngine = None
        else:
            AdversarialReviewEngine = None
    except Exception as e:
        logger.error(f"Failed to load AdversarialReviewEngine: {e}")
        AdversarialReviewEngine = None

try:
    from core.action_bus.runtime_events import RuntimeEvent, RuntimeEventBus
except Exception:
    RuntimeEvent = None
    RuntimeEventBus = None


def dnk_run_adversarial_review(
    target_path: Optional[str] = None,
    workspace_id: str = "ws-alpha-001",
    task_id: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """
    Executes a 2-agent competitive Adversarial Code Review:
    - Red Team (Auditor): Attacks code for hardcoded paths, secret leaks, missing MRH headers, and concurrency bugs.
    - Blue Team (Builder): Cross-examines and refutes false positives.
    
    Args:
        target_path: Relative path to file or directory to audit (defaults to 'core/').
        workspace_id: Target workspace identifier.

    Returns:
        JSON string containing the total attack findings, defended false positives, and confirmed real issues.
    """
    if AdversarialReviewEngine is None:
        return json.dumps({"status": "error", "message": "AdversarialReviewEngine unavailable"})

    try:
        engine = AdversarialReviewEngine(root_dir=str(DNKOS_MVP_PATH))
        root_target = DNKOS_MVP_PATH / (target_path or "core")
        
        target_files = []
        if root_target.is_file():
            target_files = [root_target]
        elif root_target.is_dir():
            target_files = list(root_target.glob("**/*.py"))[:20]

        total_findings = 0
        total_refuted = 0
        confirmed_issues = []

        for file_p in target_files:
            rel_p = str(file_p.relative_to(DNKOS_MVP_PATH))
            findings = engine.attack_file(rel_p)
            total_findings += len(findings)

            for finding in findings:
                verdict = engine.defend_finding(finding)
                if verdict.status == "refuted":
                    total_refuted += 1
                else:
                    confirmed_issues.append({
                        "id": finding.finding_id,
                        "file": finding.file_path,
                        "category": finding.category,
                        "severity": finding.severity,
                        "description": finding.description
                    })

        # Emit live event to Visual Cabinet
        if RuntimeEvent and RuntimeEventBus:
            try:
                bus = RuntimeEventBus.get_instance()
                bus.publish(RuntimeEvent(
                    tenant_id="tenant-alpha-001",
                    workspace_id=workspace_id,
                    canvas_id="canvas-main-001",
                    graph_id="graph-swarm-001",
                    thread_id="thread-adversarial-review",
                    execution_id="exec-adv-review",
                    node_id="gerych_auditor",
                    event_type="security.reviewed",
                    sequence_number=1,
                    payload={
                        "target": target_path or "core",
                        "total_attack_findings": total_findings,
                        "refuted_false_positives": total_refuted,
                        "confirmed_issues": len(confirmed_issues)
                    }
                ))
            except Exception:
                pass

        return json.dumps({
            "status": "success",
            "target": target_path or "core",
            "workspace_id": workspace_id,
            "total_attack_findings": total_findings,
            "refuted_false_positives": total_refuted,
            "confirmed_issues_count": len(confirmed_issues),
            "confirmed_issues": confirmed_issues[:5],
            "passed": len(confirmed_issues) == 0
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_adversarial_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "dnk_run_adversarial_review",
            "description": "Executes a competitive 2-Agent Adversarial Review (Red-Team Auditor vs Blue-Team Builder) to detect and filter security/quality bugs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_path": {"type": "string", "description": "File or folder path to audit (default: 'core')."},
                    "workspace_id": {"type": "string", "description": "Target workspace (default: ws-alpha-001)."}
                }
            }
        }
    }


try:
    from tools import registry
    registry.register(
        name="dnk_run_adversarial_review",
        toolset="security",
        schema=get_adversarial_schema(),
        handler=dnk_run_adversarial_review,
    )
except Exception:
    pass
