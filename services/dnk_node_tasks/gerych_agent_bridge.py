# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_node_tasks/gerych_agent_bridge.py"
# purpose: "Living Gerych Prime LLM Bridge connecting conversational natural language intake to TaskForest DAG."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-07"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import json
import logging
import os
import re
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("dnk_node_tasks.gerych_bridge")


def get_kyiv_time_str() -> str:
    """Returns real-world current timestamp in Kyiv timezone (UTC+3 / EEST)."""
    tz_kyiv = timezone(timedelta(hours=3))
    now = datetime.now(tz_kyiv)
    days = ["понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя"]
    months = [
        "січня", "лютого", "березня", "квітня", "травня", "червня",
        "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"
    ]
    day_name = days[now.weekday()]
    month_name = months[now.month - 1]
    return f"{day_name}, {now.day} {month_name} {now.year} року, {now.strftime('%H:%M')} (Київ, UTC+3)"

GERYCH_SYSTEM_PROMPT = """Ти — Герич (Hermes Prime), Головний Архітектор, Будівничий і Swarm Lead системи DNK OS.
Твій партнер і візіонер — Максим.

# КАТЕГОРИЧНІ ПРАВИЛА СПІЛКУВАННЯ ТА СТИЛЮ:
1. НУЛЬ ПІДЛАБУЗНИЦТВА І ВОДИ:
   - КАТЕГОРИЧНО ЗАБОРОНЕНО використовувати пафосні, підлабузницькі або шаблонні фрази:
     НЕ пиши: "мій дорогий друже і творець", "дуже дякую за довіру", "я до ваших послуг", "весь рій схиляється", "буде продиктовано саме цим принципом", "я завжди готовий до дії".
   - Спілкуйся як зібраний, авторитетний технічний лідер (Chief Architect / Principal Engineer): стисло, точно, конкретно, професійно, українською мовою (🇺🇦).

2. АВТОНОМНІСТЬ ТА ACTION-FIRST (НЕ ПЕРЕПИТУЙ, А ДІЙ):
   - Коли Максим схвалює, дає добро чи команду: "ну давай, реалізовувай", "реалізуйте так, як ви бачите", "зроби зручніше", "покращуй", "давай", "вперед", "роби":
     НЕ СМІЙ ПЕРЕПИТУВАТИ: "підкажи, який напрямок пріоритетний?" чи "яка задача важливіша?".
   - Максим дав тобі повний карт-бланш реалізувати так, як бачиш ти!
   - Твоя дія:
     a) Проаналізуй контекст: що саме обговорювалося (наприклад, UX/зручність інтерфейсу завдань, швидкі дії на нодах, шорткати, групові операції, авто-лейаут полотна).
     b) Встанови intent = "task_creation".
     c) Сформуй 2-4 конкретні, чітко декомпозовані інженерні задачі (Task / Gate) у списку "nodes".
     d) Признач правильних агентів рою (gerych_builder для фронтенду/UI, dnk_dev_fullstack для бекенду/API, gerych_auditor для верифікації/тестів).
     e) У "reply" коротко і чітко відзвітуй: що саме розгорнуто в графі, яка інженерна логіка покращення та які воркери розпочали виконання.

3. ПОВНИЙ КОНТЕКСТ ДІАЛОГУ ТА ЧОТИРИ ЧІТКІ НАМІРИ (INTENTS):
   Ти повинен точно розрізняти тип наміру і повертати відповідний intent:

   а) intent = "inquiry":
      - Коли Максим запитує щось інформаційне ("який час?", "що це за статус?", "поясни архітектуру", "чому ноди налазять одна на одну?").
      - Поясни лаконічно причину або надай відповідь.
      - КАТЕГОРИЧНО ЗАБОРОНЕНО створювати нові задачі (nodes = []) на прості запитання!

   б) intent = "auto_layout":
      - Коли Максим просить навести порядок з розташуванням на полотні: "вирівняй граф", "зроби авто-лейаут", "впорядкуй ноди", "розподіли щоб не налазили", "поправ вигляд".
      - nodes = []. У "reply" коротко напиши, що застосовуєш автоматичне топологічне вирівнювання графа для усунення перекриттів.

   в) intent = "execute_task":
      - Коли Максим наказує виконати або запустити задачу: "ти створив задачу запускай її виконання", "запускай виконання", "виконуй", "роби", "запусти агента", "run agent".
      - КАТЕГОРИЧНО ЗАБОРОНЕНО створювати повторні чи дублюючі задачі (nodes = [])!
      - Вкажи "target_node_id" (ID задачі, яку запускаємо: або selected_node_id з контексту, або відповідну останню задачу з графа).
      - У "reply" чітко напиши, що запустив виконання задачі агентом рою, і що хід виконання транслюється в Live Swarm Terminal.

   г) intent = "task_creation":
      - ТІЛЬКИ коли Максим прямо просить створити задачу/фічу, або дав добро на нову функціональність, ЯКОЇ ЩЕ НЕМАЄ В ГРАФІ.
      - ПЕРЕВІРЯЙ список існуючих нод у графі: КАТЕГОРИЧНО ЗАБОРОНЕНО створювати дублікати задач з однаковими або схожими назвами!
      - nodes = [ ...2-4 нові інженерні задачі... ].

4. РОЛІ АГЕНТІВ РОЮ DNK OS:
   - gerych_builder: React Flow UI, інтерактивні ноди, шорткати, інлайн-редагування, Tailwind, темна тема.
   - dnk_dev_fullstack: FastAPI, збереження стану, пагінація, фільтри, швидкість запитів.
   - gerych_auditor: Quality Gates, pytest, Playwright UI тести, аудит безпеки.
   - dnk_shopify: Liquid, Checkout, Shopify AST.
   - dnk_media: Remotion відео-анімації, медіа-контент, відео-ретеншн.
   - herich_librarian: Obsidian Vault, ADR, системна документація.

ФОРМАТ ВІДПОВІДІ (ТІЛЬКИ ВАЛІДНИЙ JSON):
{
  "intent": "inquiry" | "auto_layout" | "execute_task" | "task_creation",
  "reply": "Твоя лаконічна інженерна відповідь українською без води та підлабузництва",
  "target_node_id": "опціональний ID ноди для запуску (якщо intent == execute_task), інакше null",
  "nodes": [
    {
      "title": "Зрозуміла коротка назва інженерної задачі",
      "description": "Детальний технічний зміст: що саме реалізується та який очікуваний результат",
      "node_type": "task" | "idea" | "gate" | "epic",
      "stage": "ready" | "in_progress",
      "assigned_agent": "gerych_builder" | "dnk_dev_fullstack" | "gerych_auditor",
      "priority": "high" | "critical" | "medium"
    }
  ]
}
"""


class GerychAgentBridge:
    """
    Cognitive Agent Bridge connecting the living Gerych Prime LLM to TaskForest.
    Interprets natural language, answers questions with personality, and generates
    structured DAG nodes.
    """

    @classmethod
    def _get_vertex_token(cls) -> Optional[str]:
        # 1. Direct environment variable
        token = os.getenv("VERTEX_API_KEY")
        if token and token.strip() and not token.startswith("${"):
            return token.strip()

        # 2. Check token files in root or hermes directory
        candidate_paths = [
            Path(".vertex_token"),
            Path("/app/.vertex_token"),
            Path.home() / ".hermes" / "vertex_token.txt",
        ]
        for p in candidate_paths:
            try:
                if p.exists():
                    val = p.read_text(encoding="utf-8").strip()
                    if val.startswith("ya29."):
                        return val
            except Exception:
                continue

        return None

    @classmethod
    def is_available(cls) -> bool:
        """Check if living LLM is configured and reachable."""
        # In test mode, allow tests to run offline unless explicitly enabled
        if os.getenv("TESTING") == "1" and os.getenv("ENABLE_LIVE_LLM_TESTS") != "1":
            return False
        return cls._get_vertex_token() is not None or cls._nvidia_key() is not None

    @staticmethod
    def _env(name: str) -> Optional[str]:
        """Environment value, falling back to the repo .env (the API is not always started with it loaded)."""
        val = os.getenv(name)
        if val and val.strip() and not val.startswith("${"):
            return val.strip()
        try:
            for line in (Path(__file__).resolve().parents[2] / ".env").read_text(encoding="utf-8").splitlines():
                if line.startswith(f"{name}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'") or None
        except Exception:
            pass
        return None

    @classmethod
    def _nvidia_key(cls) -> Optional[str]:
        # Never spend real tokens / hit the network from the test suite unless asked explicitly.
        if os.getenv("ENV") == "test" and os.getenv("DNK_ALLOW_LIVE_LLM") != "1":
            return None
        return cls._env("NVIDIA_API_KEY")

    @classmethod
    def call_living_gerych(
        cls,
        prompt: str,
        graph_summary: str = "",
        history: Optional[List[Dict[str, Any]]] = None,
        selected_node_info: str = "",
        timeout_seconds: int = 15
    ) -> Optional[Dict[str, Any]]:
        """Primary: Gemini on Vertex. Fallback (DEC-020 chain): NVIDIA NIM. None -> caller uses heuristics."""
        res = cls._call_vertex_gerych(prompt, graph_summary, history, selected_node_info, timeout_seconds)
        if res is None:
            res = cls._call_nvidia_gerych(prompt, graph_summary, selected_node_info, max(timeout_seconds, 30))
        return res

    @classmethod
    def _call_nvidia_gerych(
        cls,
        prompt: str,
        graph_summary: str = "",
        selected_node_info: str = "",
        timeout_seconds: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """OpenAI-compatible chat completion on NVIDIA NIM; same JSON contract as the Vertex path."""
        key = cls._nvidia_key()
        if not key:
            return None
        base = (cls._env("NVIDIA_BASE_URL") or "https://integrate.api.nvidia.com/v1").rstrip("/")
        model = cls._env("NVIDIA_MODEL") or "meta/llama-3.2-11b-vision-instruct"
        context = "\n\n".join(x for x in (
            f"Поточний стан TaskForest DAG:\n{graph_summary}" if graph_summary else "",
            f"Контекст виділеного елемента: {selected_node_info}" if selected_node_info else "",
            f"Останнє повідомлення від Максима:\n{prompt}",
            "Відповідай ЛИШЕ валідним JSON за описаною схемою, без пояснень і без markdown.",
        ) if x)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": f"{GERYCH_SYSTEM_PROMPT}\n\nПОТОЧНИЙ ЧАС: {get_kyiv_time_str()}."},
                {"role": "user", "content": context},
            ],
            "temperature": 0.25,
            "max_tokens": 2048,
        }
        try:
            req = urllib.request.Request(
                f"{base}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            text = (raw.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)  # tolerate prose / fences around the JSON
            parsed = json.loads(match.group(0)) if match else None
            if isinstance(parsed, dict) and ("reply" in parsed or "nodes" in parsed):
                parsed.setdefault("reply", "")
                parsed["provider"] = "nvidia"
                return parsed
        except Exception as exc:
            logger.warning(f"NVIDIA fallback for Gerych failed: {type(exc).__name__}")
        return None

    @classmethod
    def _call_vertex_gerych(
        cls,
        prompt: str,
        graph_summary: str = "",
        history: Optional[List[Dict[str, Any]]] = None,
        selected_node_info: str = "",
        timeout_seconds: int = 15
    ) -> Optional[Dict[str, Any]]:
        """
        Sends the user prompt to Gemini Vertex AI and parses the structured response.
        Returns parsed dict with keys: 'intent', 'reply', 'nodes'.
        """
        token = cls._get_vertex_token()
        if not token:
            logger.debug("Living Gerych LLM token not found; using deterministic fallback.")
            return None

        try:
            from core.config.gcp_config import get_active_vertex_base_url
            base_url = get_active_vertex_base_url()
        except Exception:
            base_url = os.getenv("VERTEX_BASE_URL", "")
        model = os.getenv("GEMINI_FLASH_MODEL") or "gemini-2.5-flash"
        endpoint = f"{base_url}/models/{model}:generateContent"

        current_time_str = get_kyiv_time_str()

        # Build context parts
        context_parts = []
        if graph_summary:
            context_parts.append(f"Поточний стан TaskForest DAG:\n{graph_summary}")
        if selected_node_info:
            context_parts.append(f"Контекст виділеного елемента: {selected_node_info}")

        if history and isinstance(history, list):
            cleaned_turns = []
            for item in history[-6:]:
                sender = item.get("sender", "user")
                text = item.get("text", "").strip()
                if not text:
                    continue
                speaker = "Максим" if sender == "user" else "Герич"
                clean_msg = re.sub(r"^🤖\s*Герич:\s*", "", text).strip()
                cleaned_turns.append(f"[{speaker}]: {clean_msg}")
            if cleaned_turns:
                context_parts.append("Історія останніх реплік діалогу:\n" + "\n".join(cleaned_turns))

        context_parts.append(f"Останнє повідомлення від Максима:\n{prompt}")
        context_parts.append(f"(Поточний системний час: {current_time_str})")
        user_content = "\n\n".join(context_parts)

        system_instruction_text = (
            f"{GERYCH_SYSTEM_PROMPT}\n\n"
            f"ПОТОЧНИЙ РЕАЛЬНИЙ ЧАС ТА ДАТА: {current_time_str}.\n"
            f"Якщо Максим питає час чи дату — обов'язково відповідай точно відповідно до цього часу."
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_content}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction_text}]
            },
            "generationConfig": {
                "temperature": 0.25,
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json"
            }
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                raw_json = json.loads(resp.read().decode("utf-8"))
                candidates = raw_json.get("candidates", [])
                if not candidates:
                    return None
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    return None
                text_response = parts[0].get("text", "").strip()

                # Clean markdown blocks if present
                clean_json_str = re.sub(r"^```(?:json)?\s*", "", text_response, flags=re.MULTILINE)
                clean_json_str = re.sub(r"\s*```$", "", clean_json_str, flags=re.MULTILINE).strip()

                parsed = json.loads(clean_json_str)
                if isinstance(parsed, dict) and "reply" in parsed:
                    return parsed
        except Exception as exc:
            logger.warning(f"Living Gerych LLM call failed or timed out: {exc}")
            return None

        return None
