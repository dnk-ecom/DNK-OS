# --- DNK-MRH-HEADER ---
# mrh_id: "references/swarm_dynamic_routing_parallel_pipeline_and_subscriber_task_safety.md"
# purpose: "Reference guide for Swarm Dynamic Routing, Parallel/Pipeline Execution, and Asyncio Task Safety."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "Gerych Prime & Maxim Kuzmenko"
# --- END DNK-MRH-HEADER ---

# 🐝 Swarm Dynamic Routing, Parallel/Pipeline Execution & Subscriber Task Safety

## 1. Asyncio Subscriber Fire-and-Forget Safety Pattern
When dispatching events to background coroutine subscribers in an event bus:
```python
# ANTI-PATTERN: Unhandled task exceptions log warnings to stderr and risk memory leaks
t = asyncio.create_task(subscriber_coroutine(event))

# BEST PRACTICE: Attach a done callback to inspect and safely handle exceptions
def _handle_subscriber_task_result(task: asyncio.Task) -> None:
    try:
        exc = task.exception()
        if exc:
            logger.warning("Subscriber task failed with exception: %s", exc)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.warning("Failed to inspect subscriber task result: %s", e)

t = asyncio.create_task(subscriber_coroutine(event))
t.add_done_callback(_handle_subscriber_task_result)
```

## 2. Dynamic Swarm Task Router Pattern
Dynamic routing matches incoming tasks across the 14 specialized DNK OS agents based on capability keywords:
- `gerych_prime`: Lead orchestrator, planner, triage.
- `gerych_builder`: UI & frontend, React, Tailwind, canvas components.
- `gerych_researcher`: Deep R&D, GitHub assimilation, AST parsing.
- `gerych_auditor`: Adversarial security, test gates, QA review.
- `dnk_dev_fullstack`: Backend services, FastAPI, SQLAlchemy, migrations.
- `dnk_shopify`: Liquid templates, checkout UI, Shopify functions.
- `dnk_video_ai_creator`: Remotion compositions, media generation.
- `dnk_security_guard`: Vault, secrets, firewalls, permissions.
- `dnk_scones_memory`: Cognitive memory, SCONES vectors.
- `dnk_analytics`: Metrics, telemetry, reporting.
- `dnk_erp_supply`: Supply chain, ERP, inventory.
- `dnk_finance_cfo`: CFO budgeting, pricing, COGS.
- `dnk_marketing_cmo`: Marketing campaigns, copy, growth.
- `herich_librarian`: Obsidian vault, Markdown curation, ADRs.

## 3. Parallel & Pipeline Coordination Over ActionBus
1. **Parallel Execution (`dispatch_swarm_parallel`)**:
   - Accepts multiple `ActionTask` instances.
   - Automatically resolves target agent via `SwarmTaskRouter` if unset.
   - Executes concurrently via `asyncio.gather(*[bus.dispatch_task(t) for t in tasks])`.
   - Records `SWARM_PARALLEL_STARTED` and `SWARM_PARALLEL_COMPLETED` audit events.
2. **Sequential Pipeline Execution (`dispatch_swarm_pipeline`)**:
   - Executes staged tasks in sequence.
   - Forwards output from stage N-1 into stage N payload (`payload['prior_output']` and `payload['prior_stage_output']`).
   - Supports `stop_on_failure` to abort downstream stages on early failure.
3. **Agent-to-Agent Delegation (`delegate_task`)**:
   - Sets `task.delegated_by = from_agent` and `task.target_agent = to_agent`.
   - Records `TASK_DELEGATED` event in SQLite WAL persistence journal.
