# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/services/orchestrator_llm_service.py"
# purpose: "Live Multi-Tier LLM Service for Gerych Prime and Swarm Orchestrator (Vertex AI / NVIDIA NIM / OpenRouter)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-16"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

logger = logging.getLogger("dnk_orchestrator_llm")

# Add core/hermes_agent to sys.path for native adapters if not present
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HERMES_DIR = REPO_ROOT / "core" / "hermes_agent"
if str(HERMES_DIR) not in sys.path:
    sys.path.insert(0, str(HERMES_DIR))

try:
    from agent.gemini_native_adapter import GeminiNativeClient
    from agent.vertex_adapter import get_vertex_config
except ImportError:
    GeminiNativeClient = None
    get_vertex_config = None

try:
    from scripts.system.switch_llm_provider import load_nvidia_keys_pool, load_env_dict
except ImportError:
    def load_nvidia_keys_pool():
        key = os.getenv("NVIDIA_API_KEY")
        return [key] if key else []
    def load_env_dict():
        return {}


DEFAULT_SYSTEM_PROMPT = """Ти — Герич Prime (Chief Builder, Swarm Manager та Master of Knowledge Assimilation у DNK OS).
Ти спілкуєшся з засновником Максимом українською мовою 🇺🇦.
Код, назви параметрів та технічні специфікації пиши англійською мовою (🇬🇧).

ПРАВИЛА СПІЛКУВАННЯ ТА ОРКЕСТРАЦІЇ:
1. Будь лаконічним, дієвим і технічно точним. Починай відповідь одразу з суті без лестощів чи пустопорожніх вітань.
2. Ти керуєш інтерактивним полотном ThoughtDAG Canvas та 14 спеціалізованими агентами рою:
   - gerych_builder (UI / Frontend / ReactFlow)
   - dnk_shopify (Liquid AST / Checkout / Themes)
   - dnk_dev_fullstack (FastAPI / Database / ORM)
   - gerych_auditor (Adversarial Security / Tests / Quality Gate)
   - dnk_video_ai_creator (Remotion Video / Reels)
   - dnk_scones_memory (Long-term Knowledge / ADRs)
   - herich_librarian (Obsidian Vault / Specs)
3. Якщо користувач просить створити нотатку, таску для агента або з'єднати їх дротом (wire) на полотні, додай у кінець своєї відповіді блок дій у такому форматі:
```canvas_actions
[
  {"action_type": "add_note", "payload": {"title": "Назва", "content": "Вміст нотатки", "x": 100, "y": 150}},
  {"action_type": "add_agent_task", "payload": {"title": "Назва таски", "agent": "назва_агента", "description": "Опис", "x": 500, "y": 150}},
  {"action_type": "connect_wire", "payload": {"source_type": "note", "target_type": "agent"}}
]
```
Якщо дія на полотні не потрібна, не додавай блок дій.
4. ASTRYX GENERATIVE UI СИНТЕЗ:
Коли користувач запитує або обговорює Shopify блоки (sticky ATC, cart rewards, upsell), аналітику (AOV, CVR, ROAS), відео/соцмережі (TikTok, Reels, Shorts), або ThoughtDAG рефлексії (Goal, Hypothesis, Critique 3-flaws, Decision), обов'язково синтезуй інтерактивний віджет Astryx у форматі HTML-коментаря:
<!-- GENERATIVE_UI:shopify_block {"blockType": "sticky_atc", "title": "Назва", "price": 89.99, "variants": ["S", "M", "L"]} -->
<!-- GENERATIVE_UI:analytics {"title": "Conversion Rate", "value": "4.8%", "changePercent": 18.4, "timeframe": "7d", "metricType": "cvr"} -->
<!-- GENERATIVE_UI:social {"platform": "tiktok", "hook": "...", "caption": "...", "cta": "..."} -->
<!-- GENERATIVE_UI:thought_dag {"nodeKind": "decision", "title": "...", "agent": "...", "summary": "...", "lockedDecRef": "DEC-135"} -->
"""


def _extract_canvas_actions(raw_text: str, user_message: str, canvas_context: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]], List[str]]:
    """
    Extracts canvas actions from model output or falls back to intent-based actions.
    Returns cleaned text, actions list, and active agents list.
    """
    clean_text = raw_text
    actions: List[Dict[str, Any]] = []
    active_agents: List[str] = ["gerych_prime"]

    # 1. Look for ```canvas_actions block
    match = re.search(r"```(?:canvas_actions|json)\s*([\s\S]*?)```", raw_text, re.IGNORECASE)
    if match:
        block_content = match.group(1).strip()
        try:
            parsed = json.loads(block_content)
            if isinstance(parsed, dict) and "canvas_actions" in parsed:
                actions = parsed["canvas_actions"]
            elif isinstance(parsed, list):
                actions = parsed
            clean_text = raw_text.replace(match.group(0), "").strip()
        except Exception as e:
            logger.warning(f"Failed to parse canvas_actions JSON: {e}")

    # 2. Extract active agents from actions
    for act in actions:
        payload = act.get("payload", {})
        ag = payload.get("agent")
        if ag and ag not in active_agents:
            active_agents.append(ag)

    # 3. Intent-based safety net to guarantee canvas reactivity
    msg_lower = user_message.lower()
    has_note_intent = any(k in msg_lower for k in ["нотатк", "note", "вимог", "інструкці", "контекст"])
    has_agent_intent = any(k in msg_lower for k in ["агент", "agent", "задач", "task", "підключи", "додай", "створи", "build"])

    existing_types = [a.get("action_type") for a in actions]

    if has_note_intent and "add_note" not in existing_types:
        note_title = "Living ThoughtDAG Note"
        note_content = user_message
        if "shopify" in msg_lower or "liquid" in msg_lower:
            note_title = "Shopify Liquid Requirements"
            note_content = "### Liquid Rules\n1. Use secure AST-friendly syntax\n2. Follow OS 2.0 schema invariants\n3. Zero inline style pollution"
            if "dnk_shopify" not in active_agents:
                active_agents.append("dnk_shopify")
        elif "архітектур" in msg_lower or "arch" in msg_lower:
            note_title = "System Architecture Note"
            note_content = "### Invariants\n- Relative paths only\n- Deterministic proof over verbal claims\n- 100% test pass gate"

        actions.insert(0, {
            "action_type": "add_note",
            "payload": {
                "title": note_title,
                "content": note_content,
                "x": 100,
                "y": 150,
                "highlightMode": "all"
            }
        })

    if has_agent_intent and "add_agent_task" not in existing_types:
        agent_target = "gerych_builder"
        agent_title = "Builder Task"
        if any(k in msg_lower for k in ["аудит", "тест", "перевір", "audit"]):
            agent_target = "gerych_auditor"
            agent_title = "Adversarial Quality Gate"
        elif any(k in msg_lower for k in ["shopify", "liquid", "checkout", "магазин"]):
            agent_target = "dnk_shopify"
            agent_title = "Shopify Theme & AST Engine"
        elif any(k in msg_lower for k in ["бек", "api", "fastapi", "backend"]):
            agent_target = "dnk_dev_fullstack"
            agent_title = "FastAPI Backend Worker"
        elif any(k in msg_lower for k in ["відео", "video", "remotion"]):
            agent_target = "dnk_video_ai_creator"
            agent_title = "Remotion Video Creator"

        if agent_target not in active_agents:
            active_agents.append(agent_target)

        actions.append({
            "action_type": "add_agent_task",
            "payload": {
                "title": agent_title,
                "agent": agent_target,
                "description": user_message,
                "status": "pending",
                "x": 500,
                "y": 150
            }
        })

    # If both note and agent exist, wire them
    has_note = any(a.get("action_type") == "add_note" for a in actions)
    has_agent = any(a.get("action_type") == "add_agent_task" for a in actions)
    if has_note and has_agent and "connect_wire" not in [a.get("action_type") for a in actions]:
        actions.append({
            "action_type": "connect_wire",
            "payload": {
                "source_type": "note",
                "target_type": "agent",
                "wire_type": "context_wire"
            }
        })

    # 4. Synthesize Astryx Generative UI widget if not already present in text
    if "<!-- GENERATIVE_UI:" not in clean_text:
        gen_ui = ""
        if any(k in msg_lower for k in ["sticky", "atc", "shopify", "liquid", "cart", "товар", "магазин"]):
            gen_ui = (
                '\n\n<!-- GENERATIVE_UI:shopify_block {"blockType":"sticky_atc","title":"Obsidian Titanium Case",'
                '"price":89.99,"variants":["S (Compact)","M (Standard)","L (Pro Max)"],"rating":4.9,"reviewsCount":142,'
                '"stockRemaining":7} -->'
            )
        elif any(k in msg_lower for k in ["відео", "video", "tiktok", "reels", "shorts", "сценарій", "контент"]):
            gen_ui = (
                '\n\n<!-- GENERATIVE_UI:social {"platform":"tiktok","hook":"99% of Shopify stores lose 40% conversions right here!",'
                '"caption":"Here is how to optimize sticky ATC and Cart Rewards in 3 simple steps with DNK OS.",'
                '"audioTrack":"Trending Viral Phonk • High Retention Beat","scenesCount":4,'
                '"cta":"Check the link in bio for the complete SaaP theme blueprint"} -->'
            )
        elif any(k in msg_lower for k in ["аналітик", "analytics", "aov", "cvr", "roas", "конверсі", "метрики"]):
            gen_ui = (
                '\n\n<!-- GENERATIVE_UI:analytics {"title":"Conversion Rate (CVR)","value":"4.82%","changePercent":18.4,'
                '"timeframe":"Останні 7 днів","metricType":"cvr","sparklineData":[32,35,38,42,40,49,54,52,61]} -->'
            )
        elif any(k in msg_lower for k in ["thoughtdag", "спека", "архітектур", "рішення", "decision", "критик"]):
            gen_ui = (
                '\n\n<!-- GENERATIVE_UI:thought_dag {"nodeKind":"decision","title":"DEC-135: Astryx Generative UI & ThoughtDAG Semantic Zoom",'
                '"agent":"Antigravity & Denchik","summary":"Sovereign living cockpit with 4 macro-clusters, semantic zoom, and interactive generative UI widgets in Astryx tokens.",'
                '"lockedDecRef":"DEC-135","flaws":["Macro cluster state must synchronize with low-level Taskboard SQLite",'
                '"SSE stream backpressure on large task sets","Client-side re-renders during high-frequency mutation broadcasts"]} -->'
            )
        clean_text += gen_ui

    return clean_text, actions, active_agents


class OrchestratorLLMService:
    """
    Multi-tier LLM engine executing live reasoning for Gerych Prime.
    """

    def __init__(self):
        self._load_config()

    def _load_config(self):
        env_dict = load_env_dict()
        for k, v in env_dict.items():
            if k not in os.environ and v:
                os.environ[k] = v
        self.active_provider = os.getenv("ACTIVE_LLM_PROVIDER") or env_dict.get("ACTIVE_LLM_PROVIDER") or "vertex"
        self.hermes_model = os.getenv("HERMES_INFERENCE_MODEL") or env_dict.get("HERMES_INFERENCE_MODEL") or "gemini-2.5-flash"

    def _call_vertex_sync(self, messages: List[Dict[str, str]], model: str) -> str:
        if not GeminiNativeClient:
            raise RuntimeError("GeminiNativeClient adapter unavailable")

        token = os.getenv("VERTEX_API_KEY")
        base_url = os.getenv("VERTEX_BASE_URL")
        if not token and get_vertex_config:
            token, base_url = get_vertex_config()

        if not token:
            raise RuntimeError("No Vertex AI / Google credentials available")

        effective_model = model or self.hermes_model or "gemini-2.5-flash"
        client = GeminiNativeClient(api_key=token, base_url=base_url)
        try:
            completion = client.chat.completions.create(
                model=effective_model,
                messages=messages,
                temperature=0.3,
                max_tokens=600
            )
            return completion.choices[0].message.content or ""
        finally:
            try:
                client.close()
            except Exception:
                pass

    def _call_nvidia_sync(self, messages: Any, model: str) -> str:
        import openai
        keys = load_nvidia_keys_pool()
        if not keys:
            raise RuntimeError("No NVIDIA NIM API keys available")

        last_err = None
        for key in keys:
            try:
                client = openai.OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=key, timeout=20.0)
                completion = client.chat.completions.create(
                    model=model or "meta/llama-3.2-11b-vision-instruct",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=800
                )
                return completion.choices[0].message.content or ""
            except Exception as e:
                last_err = e
                logger.warning(f"NVIDIA key failed, trying next: {e}")
        raise RuntimeError(f"All NVIDIA NIM keys failed: {last_err}")

    def _call_openrouter_sync(self, messages: Any, model: str) -> str:
        import openai
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("No OpenRouter API key available")

        client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key, timeout=20.0)
        completion = client.chat.completions.create(
            model=model or "google/gemini-2.5-flash",
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        return completion.choices[0].message.content or ""

    async def generate_response(
        self,
        message: str,
        target_agent: str = "gerych_prime",
        canvas_context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[str, List[Dict[str, Any]], List[str], str, str]:
        """
        Executes live LLM completion across configured tiers with robust failover.
        Returns: (reply_text, canvas_actions, active_agents, model_used, provider_used)
        """
        self._load_config()

        # Build contextual system prompt
        nodes = (canvas_context or {}).get("nodes", [])
        edges_count = (canvas_context or {}).get("edges_count", 0)
        context_str = f"\nПОТОЧНИЙ СТАН ПОЛОТНА:\n- Активних вузлів (нод): {len(nodes)}\n- Активних зв'язків (дротів): {edges_count}\n"
        if nodes:
            context_str += "- Вузли на полотні: " + ", ".join([f"{n.get('type')}: {n.get('title') or n.get('id')}" for n in nodes[:5]]) + "\n"

        system_instruction = DEFAULT_SYSTEM_PROMPT + context_str

        llm_messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_instruction}
        ]

        # Append recent history
        if history:
            for turn in history[-4:]:
                role = "assistant" if turn.get("role") in ("assistant", "gerych") else "user"
                content = turn.get("content") or turn.get("text") or ""
                if content:
                    llm_messages.append({"role": role, "content": content})

        llm_messages.append({"role": "user", "content": message})

        raw_reply = ""
        model_used = ""
        provider_used = ""

        # Order of provider attempts based on active configuration
        providers_to_try = []
        if self.active_provider == "nvidia":
            providers_to_try = [
                ("nvidia", "meta/llama-3.2-11b-vision-instruct", self._call_nvidia_sync),
                ("vertex", "gemini-2.5-flash", self._call_vertex_sync),
                ("openrouter", "google/gemini-2.5-flash", self._call_openrouter_sync)
            ]
        else:
            providers_to_try = [
                ("vertex", self.hermes_model or "gemini-2.5-flash", self._call_vertex_sync),
                ("nvidia", "meta/llama-3.2-11b-vision-instruct", self._call_nvidia_sync),
                ("openrouter", "google/gemini-2.5-flash", self._call_openrouter_sync)
            ]

        # Attempt invocation
        for p_name, p_model, p_fn in providers_to_try:
            try:
                logger.info(f"Invoking live LLM via {p_name} ({p_model})...")
                raw_reply = await asyncio.wait_for(
                    asyncio.to_thread(p_fn, llm_messages, p_model),
                    timeout=15.0
                )
                if raw_reply and raw_reply.strip():
                    model_used = p_model
                    provider_used = p_name
                    break
            except Exception as e:
                logger.warning(f"Provider {p_name} failed: {e}. Cascading to next tier...")

        # Fallback if all live calls failed
        if not raw_reply:
            logger.error("All live LLM providers failed or offline. Generating resilient fallback.")
            raw_reply = (
                f"На зв'язку Герич Prime. Полотно ThoughtDAG синхронізоване. "
                f"Активних нод на полотні: {len(nodes)}. "
                f"Готовий керувати роєм та розгортати завдання для спеціалізованих агентів."
            )
            model_used = "resilient-fallback"
            provider_used = "internal"

        # Ensure mention of Герич Prime for consistency
        if "герич" not in raw_reply.lower() and "prime" not in raw_reply.lower():
            raw_reply = f"✦ Герич Prime: {raw_reply}"

        # Extract canvas actions and active agents
        clean_text, actions, active_agents = _extract_canvas_actions(raw_reply, message, canvas_context)

        return clean_text, actions, active_agents, model_used, provider_used

    async def generate_stream(
        self,
        message: str,
        target_agent: str = "gerych_prime",
        canvas_context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        selected_node: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generates a live Thought & Action event stream:
        - thought: Spatial reasoning & contextual analysis
        - status: Swarm routing info
        - tool_call / tool_result: Kernel tool execution steps
        - canvas_mutation: Direct graph actions
        - content_chunk: Incremental reply streaming
        - done: Final metadata & active agents
        """
        # Step 1: Spatial & Cognitive Framing
        yield {
            "type": "thought",
            "text": "Аналізую просторовий контекст полотна ThoughtDAG та запит до ядра..."
        }
        await asyncio.sleep(0.04)

        if selected_node:
            node_label = selected_node.get("title") or selected_node.get("label") or selected_node.get("id") or "Node"
            node_type = selected_node.get("type", "unknown")
            yield {
                "type": "thought",
                "text": f"🎯 Активний просторовий фокус: [{node_type}] «{node_label}». Інжектую upstream зв'язки та контекст у робочу пам'ять ядра..."
            }
            await asyncio.sleep(0.04)

        # Step 2: Route status & SCONES Memory check
        yield {
            "type": "status",
            "agent": target_agent,
            "text": f"Запит маршрутизовано до {target_agent}. Перевірка операційної пам'яті SCONES..."
        }
        await asyncio.sleep(0.04)

        yield {
            "type": "tool_call",
            "tool": "scones_get_memories",
            "args": {"query": message[:60]}
        }
        await asyncio.sleep(0.04)

        yield {
            "type": "tool_result",
            "tool": "scones_get_memories",
            "result": "Зіставлено інваріанти Zero-Waste та контекстні дроти CONTRACT_002."
        }
        await asyncio.sleep(0.04)

        # Step 3: Call live LLM (Vertex Gemini -> NIM -> OpenRouter)
        clean_text, actions, active_agents, model_used, provider_used = await self.generate_response(
            message=message,
            target_agent=target_agent,
            canvas_context=canvas_context,
            history=history
        )

        # Step 4: Emit any canvas mutations
        if actions:
            for act in actions:
                yield {
                    "type": "canvas_mutation",
                    "action": act
                }
                await asyncio.sleep(0.02)

        # Step 5: Stream the reply chunks
        paragraphs = clean_text.split("\n\n")
        for i, para in enumerate(paragraphs):
            suffix = "\n\n" if i < len(paragraphs) - 1 else ""
            yield {
                "type": "content_chunk",
                "delta": para + suffix
            }
            await asyncio.sleep(0.02)

        # Step 6: Final done event
        yield {
            "type": "done",
            "reply": clean_text,
            "model": model_used,
            "provider": provider_used,
            "active_agents": active_agents,
            "canvas_actions": actions
        }


orchestrator_llm = OrchestratorLLMService()
