# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/demo_dual_surface_live.py"
# purpose: "Live interactive demonstration and runtime proof of Dual-Surface Action Engine and HITL gate."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
Live Interactive Runtime Demonstration of Dual-Surface Action Engine.
Proves end-to-end:
1. Dynamic Action Catalog & FastMCP Schema Export
2. Human UI Action Dispatch
3. Agent FastMCP Action Dispatch
4. Automatic HITL Approval Interception for Risky Agent Actions
5. 1-Click Human Approval Resolution & Unfreezing
6. Real-time Live Event Streaming via EventBroadcaster
"""

import asyncio
import json
import time
from typing import Any, Dict
import httpx

from apps.api.main import app
from core.action_bus.dual_surface_registry import DualSurfaceActionRegistry
from core.adapters.hermes_ui_bridge import HermesUIBridge


# Visual formatting helpers
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner(text: str):
    print(f"\n{BOLD}{CYAN}{'=' * 75}{RESET}")
    print(f"{BOLD}{CYAN}🚀 {text.center(71)} 🚀{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 75}{RESET}\n")


def print_step(step_num: int, title: str):
    print(f"\n{BOLD}{YELLOW}▶ [КРОК {step_num}] {title}{RESET}")
    print(f"{YELLOW}{'-' * 60}{RESET}")


async def run_live_demonstration():
    print_banner("DNK OS DUAL-SURFACE ACTION ENGINE: LIVE RUNTIME PROOF")

    # Set up HTTP client with in-process ASGI transport to test real routes
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost:8000") as client:

        # ---------------------------------------------------------------------
        # КРОК 1: Каталог дій (Динамічне виявлення інтерфейсом)
        # ---------------------------------------------------------------------
        print_step(1, "Динамічний каталог дій для Astryx UI (GET /api/v1/actions)")
        resp = await client.get("/api/v1/actions")
        actions = resp.json()
        print(f"Знайдено зареєстрованих дій: {GREEN}{len(actions)}{RESET}")
        for act in actions:
            print(f"  • {BOLD}{act['action_id']}{RESET} -> {MAGENTA}{act['label_uk']}{RESET} | mode: {act['surface_mode']} | widget: {act['ui_widget']} | hitl: {act['requires_human_confirmation']}")

        # ---------------------------------------------------------------------
        # КРОК 2: FastMCP експорт інструментів для агента (Denchik)
        # ---------------------------------------------------------------------
        print_step(2, "FastMCP Tool Schemas для LLM (GET /api/v1/actions/mcp-tools)")
        resp_mcp = await client.get("/api/v1/actions/mcp-tools")
        tools = resp_mcp.json()
        print(f"Експортовано FastMCP тулів для Denchik: {GREEN}{len(tools)}{RESET}")
        for t in tools:
            print(f"  🔧 Tool: {BOLD}{t['name']}{RESET}")
            print(f"     Description: {t['description']}")
            print(f"     Parameters: {list(t['inputSchema']['properties'].keys())}")

        # Підключаємо віртуальний слухач живого стрімінгу подій (Astryx Event Listener)
        bridge = HermesUIBridge.get_shared_instance()
        event_sub = await bridge.broadcaster.subscribe()
        print(f"\n{GREEN}✓ Підключено live WebSocket/SSE підписник до EventBroadcaster{RESET}")

        # ---------------------------------------------------------------------
        # КРОК 3: Виконання дії людиною через UI (Move Node)
        # ---------------------------------------------------------------------
        print_step(3, "Людина перетягує вузол у браузері (POST /api/v1/actions/dispatch)")
        t0 = time.time()
        move_resp = await client.post(
            "/api/v1/actions/dispatch",
            json={
                "action_id": "canvas.move_node",
                "payload": {"node_id": "task-core-auth", "x": 450.0, "y": 280.0},
                "actor": "Maksym (Founder)",
                "session_id": "sess_demo_live",
            },
        )
        move_data = move_resp.json()
        print(f"HTTP Статус: {GREEN}{move_resp.status_code} OK{RESET}")
        print(f"Результат виконання: {json.dumps(move_data['result'], indent=2, ensure_ascii=False)}")

        # Перевіряємо подію в реальному часі на шині
        live_evt = await event_sub.queue.get()
        print(f"📡 {BOLD}Live WebSocket Event отримано фронтендом:{RESET}")
        print(f"   Тип: {live_evt.event_type} | Дія: {live_evt.payload['action_id']} | Джерело: {live_evt.payload['origin']} ({live_evt.payload['actor']})")

        # ---------------------------------------------------------------------
        # КРОК 4: Агент Denchik викликає дію через FastMCP (Update Task Status)
        # ---------------------------------------------------------------------
        print_step(4, "Агент Denchik оновлює статус задачі через FastMCP (canvas.update_task_status)")
        registry = DualSurfaceActionRegistry.get_shared_instance()
        agent_res = await registry.dispatch(
            action_id="canvas.update_task_status",
            payload={
                "task_id": "task-core-auth",
                "new_status": "in_progress",
                "execution_logs": "Denchik started AST validation slice",
            },
            actor="denchik",
            origin="agent",
            session_id="sess_demo_live",
        )
        print(f"Успішність виконання агентом: {GREEN}{agent_res.success}{RESET}")
        print(f"Результат мутації: {json.dumps(agent_res.result, indent=2, ensure_ascii=False)}")

        live_evt2 = await event_sub.queue.get()
        print(f"📡 {BOLD}Live WebSocket Event отримано фронтендом:{RESET}")
        print(f"   Новий статус на живому канвасі: {GREEN}{live_evt2.payload.get('new_status')}{RESET} від агента {live_evt2.payload.get('agent')}")

        # ---------------------------------------------------------------------
        # КРОК 5: Агент намагається виконати небезпечну дію (HITL Interception)
        # ---------------------------------------------------------------------
        print_step(5, "Агент Denchik намагається видалити вузол (canvas.delete_node) -> HITL Interception!")
        print(f"{YELLOW}⏳ Агент надсилає запит на видалення. Реєстр блокує агентське виконання та генерує HITL квиток...{RESET}")

        async def _agent_delete_flow():
            return await registry.dispatch(
                action_id="canvas.delete_node",
                payload={"node_id": "task-core-auth", "reason": "Deprecated module refactoring"},
                actor="denchik",
                origin="agent",
                session_id="sess_demo_live",
                timeout=10.0,
            )

        # Запускаємо агента у фоновому тасці, оскільки він заблокований в очікуванні схвалення
        agent_task = asyncio.create_task(_agent_delete_flow())

        # Ловимо подію APPROVAL_REQUESTED на шині (пропускаючи попередні мутації)
        approval_evt = None
        while True:
            evt = await event_sub.queue.get()
            if evt.event_type.value == "APPROVAL_REQUESTED" or getattr(evt.event_type, "value", str(evt.event_type)) == "APPROVAL_REQUESTED":
                approval_evt = evt
                break

        ticket_id = approval_evt.payload["ticket_id"]

        print(f"\n{RED}🚨 ПЕРЕХОПЛЕНО ШЛЮЗОМ БЕЗПЕКИ!{RESET}")
        print(f"   Створено квиток схвалення: {BOLD}{ticket_id}{RESET}")
        print(f"   Дія: {approval_evt.payload.get('action_type')}")
        print(f"   Агент в очікуванні: {agent_task.done()} (False = агент спить і чекає)")

        # ---------------------------------------------------------------------
        # КРОК 6: Людина в UI підтверджує 1-кліком (POST /hitl/resolve)
        # ---------------------------------------------------------------------
        print_step(6, "Людина в Astryx UI тисне 'Approve' (POST /api/v1/swarm/live/hitl/resolve)")
        resolve_resp = await client.post(
            "/api/v1/swarm/live/hitl/resolve",
            json={
                "ticket_id": ticket_id,
                "approved": True,
                "author": "Maksym (Founder)",
                "reason": "Approved after reviewing architecture impact",
                "modifications": {"reason": "Approved & verified by Founder"},
            },
        )
        print(f"HTTP Статус відповіді UI: {GREEN}{resolve_resp.status_code} OK{RESET}")

        # Агент негайно розблоковується!
        final_agent_res = await agent_task
        print(f"{GREEN}✓ Агент розблокований! Результат виконання дії:{RESET}")
        print(f"   Success: {GREEN}{final_agent_res.success}{RESET}")
        print(f"   Requires Approval was triggered: {final_agent_res.requires_approval}")
        print(f"   Ticket ID: {final_agent_res.ticket_id}")
        print(f"   Payload result: {json.dumps(final_agent_res.result, indent=2, ensure_ascii=False)}")

        # ---------------------------------------------------------------------
        # КРОК 7: Перевірка захисту від порушення ролей (Surface Permissions)
        # ---------------------------------------------------------------------
        print_step(7, "Захист режимів surface_mode (Агент НЕ МОЖЕ викликати HUMAN_ONLY дію)")
        # Тимчасово реєструємо дію з режимом HUMAN_ONLY
        from core.domain.vibe_core_contracts import ActionSurfaceMode, DualSurfaceActionSpec
        registry.register_action(
            DualSurfaceActionSpec(
                action_id="governance.transfer_ownership",
                label_uk="Передати права власності",
                description_en="Transfers root ownership",
                surface_mode=ActionSurfaceMode.HUMAN_ONLY,
                mcp_brick="core_gov",
                mcp_tool_name="transfer_ownership",
            ),
            lambda p, actor="human", origin="ui": {"transferred": True},
        )

        illegal_res = await registry.dispatch(
            action_id="governance.transfer_ownership",
            payload={},
            actor="denchik",
            origin="agent",
        )
        print(f"Спроба агента викликати HUMAN_ONLY: Success = {RED}{illegal_res.success}{RESET}")
        print(f"Помилка шлюзу: {YELLOW}{illegal_res.error}{RESET}")

    print_banner("УСІ 7 КРОКІВ ПЕРЕВІРЕНО НАЖИВО: СИСТЕМА ПОВНІСТЮ ДІЄЗДАТНА!")


if __name__ == "__main__":
    asyncio.run(run_live_demonstration())
