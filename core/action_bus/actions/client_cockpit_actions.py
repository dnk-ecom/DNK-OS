# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/actions/client_cockpit_actions.py"
# purpose: "Dual-Surface Actions for Ring 2 (Client Cockpit) & Ring 4 (Execution Loop) in ACIE."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import logging
from typing import Any, Dict

from core.action_bus.dual_surface_registry import (
    ActionExecutionContext,
    ActionExecutionResult,
    DualSurfaceActionRegistry,
)
from core.client_cockpit.engine import ClientCockpitEngine
from core.domain.vibe_core_contracts import ActionSurfaceMode, DualSurfaceActionSpec

logger = logging.getLogger("dnk.actions.cockpit")


async def handle_init_deal(ctx: ActionExecutionContext) -> ActionExecutionResult:
    engine = ClientCockpitEngine()
    deal_id = ctx.payload.get("deal_id", "deal_noku_2026")
    client_name = ctx.payload.get("client_name", "Андрій Ніколаєв")
    brand = ctx.payload.get("brand", "NOKU")
    tier = ctx.payload.get("tier", "scale_1500")
    total_amount = float(ctx.payload.get("total_amount", 1500.0))

    state = engine.init_deal(
        deal_id=deal_id,
        client_name=client_name,
        brand=brand,
        tier=tier,
        total_amount=total_amount,
    )
    return ActionExecutionResult(
        success=True,
        result={"deal_id": deal_id, "state": state},
        broadcast_events=[{"event": "cockpit_deal_initialized", "deal_id": deal_id}],
    )


async def handle_submit_ticket(ctx: ActionExecutionContext) -> ActionExecutionResult:
    engine = ClientCockpitEngine()
    deal_id = ctx.payload.get("deal_id", "deal_noku_2026")
    title = ctx.payload.get("title", "Правка по дизайну")
    comment = ctx.payload.get("comment", "")
    category = ctx.payload.get("category", "auto")
    selector = ctx.payload.get("selector")
    section_id = ctx.payload.get("section_id")
    block_id = ctx.payload.get("block_id")
    screenshot_url = ctx.payload.get("screenshot_url")

    ticket = engine.submit_ticket(
        deal_id=deal_id,
        title=title,
        comment=comment,
        category=category,
        selector=selector,
        section_id=section_id,
        block_id=block_id,
        screenshot_url=screenshot_url,
    )

    return ActionExecutionResult(
        success=True,
        result={"ticket": ticket.model_dump()},
        broadcast_events=[
            {
                "event": "cockpit_ticket_submitted",
                "deal_id": deal_id,
                "ticket_id": ticket.ticket_id,
                "category": ticket.category,
            }
        ],
    )


async def handle_advance_stage(ctx: ActionExecutionContext) -> ActionExecutionResult:
    engine = ClientCockpitEngine()
    deal_id = ctx.payload.get("deal_id", "deal_noku_2026")
    stage_num = int(ctx.payload.get("stage_num", 1))
    new_status = ctx.payload.get("status", "completed")

    engine.update_stage_status(deal_id=deal_id, stage_num=stage_num, new_status=new_status)
    return ActionExecutionResult(
        success=True,
        result={"deal_id": deal_id, "stage_num": stage_num, "status": new_status},
        broadcast_events=[{"event": "cockpit_stage_advanced", "deal_id": deal_id, "stage_num": stage_num}],
    )


def register_client_cockpit_actions() -> None:
    registry = DualSurfaceActionRegistry.get_shared_instance()

    registry.register_action(
        DualSurfaceActionSpec(
            action_id="cockpit.init_deal",
            label_uk="Ініціалізувати угоду клієнта",
            description_en="Activates the 6-stage roadmap and client workspace in the Cockpit.",
            surface_mode=ActionSurfaceMode.DUAL,
            mcp_brick="core_kernel",
            mcp_tool_name="cockpit_init_deal",
            input_json_schema={
                "type": "object",
                "properties": {
                    "deal_id": {"type": "string"},
                    "client_name": {"type": "string"},
                    "brand": {"type": "string"},
                    "tier": {"type": "string"},
                    "total_amount": {"type": "number"},
                },
                "required": ["deal_id"],
            },
        ),
        handler=handle_init_deal,
    )

    registry.register_action(
        DualSurfaceActionSpec(
            action_id="cockpit.submit_ticket",
            label_uk="Подати правку / тікет",
            description_en="In-context ticket submission from the client sensor with automatic scope triage.",
            surface_mode=ActionSurfaceMode.DUAL,
            mcp_brick="core_kernel",
            mcp_tool_name="cockpit_submit_ticket",
            input_json_schema={
                "type": "object",
                "properties": {
                    "deal_id": {"type": "string"},
                    "title": {"type": "string"},
                    "comment": {"type": "string"},
                    "category": {"type": "string", "enum": ["auto", "question", "in_scope_revision", "out_of_scope_upsell"]},
                    "selector": {"type": "string"},
                    "section_id": {"type": "string"},
                    "block_id": {"type": "string"},
                    "screenshot_url": {"type": "string"},
                },
                "required": ["deal_id", "title", "comment"],
            },
        ),
        handler=handle_submit_ticket,
    )

    registry.register_action(
        DualSurfaceActionSpec(
            action_id="cockpit.advance_stage",
            label_uk="Просунути етап роадмапу",
            description_en="Updates status of one of the 6 canonical project stages.",
            surface_mode=ActionSurfaceMode.DUAL,
            mcp_brick="core_kernel",
            mcp_tool_name="cockpit_advance_stage",
            input_json_schema={
                "type": "object",
                "properties": {
                    "deal_id": {"type": "string"},
                    "stage_num": {"type": "integer"},
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                },
                "required": ["deal_id", "stage_num", "status"],
            },
        ),
        handler=handle_advance_stage,
    )
