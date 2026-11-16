# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/domain_terms.py"
# purpose: "Deterministic dictionary of specific engineering mechanics (UA/EN) used by the task gate and the need extractor"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Specific mechanics = things worth searching the world for before writing code
(interpolation, DAG scheduling, CRDT, hybrid retrieval ...).
Simple markers = routine work (typos, renames, config, docs, small tests) where a
search costs more than it saves. Both lists are plain regexes: free, explainable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

_F = re.IGNORECASE | re.UNICODE


@dataclass(frozen=True)
class Domain:
    key: str
    label: str
    pattern: "re.Pattern[str]"
    terms: Tuple[str, ...]  # English search terms used against the catalog / GitHub


def _d(key: str, label: str, pattern: str, terms: Tuple[str, ...]) -> Domain:
    return Domain(key, label, re.compile(pattern, _F), terms)


DOMAINS: Tuple[Domain, ...] = (
    _d("interpolation", "Інтерполяція та криві",
       r"interpol|інтерпол|\blerp\b|\bslerp\b|easing|spline|сплайн|bezier|безьє|безє|catmull",
       ("interpolation", "easing", "bezier", "spline")),
    _d("dag", "DAG, топологічне сортування, залежності задач",
       r"\bdag\b|topolog|топологіч|dependency graph|task graph|граф залежн|граф\w*\s+задач|виконан\w*\s+граф|граф\w*\s+виконан|execution graph|паралельн\w*\s+виконан\w*\s+(?:граф|вузл)",
       ("dag", "topological", "workflow", "graph")),
    _d("graph_layout", "Розкладка графів",
       r"graph layout|force[- ]directed|dagre|\belk\b|auto[- ]?layout|розкладк\w* граф",
       ("graph", "layout", "dagre", "force-directed")),
    _d("infinite_canvas", "Нескінченна канва, вузловий редактор",
       r"infinite canvas|нескінченн\w* канв|node[- ]based|react[- ]?flow|node editor|вузлов\w* (канв|редактор)|pan.?zoom",
       ("canvas", "node-editor", "react-flow", "zoom")),
    _d("crdt", "CRDT, спільне редагування",
       r"\bcrdt\b|operational transform|collaborative edit|співредагув|\byjs\b|automerge",
       ("crdt", "yjs", "collaborative", "sync")),
    _d("retrieval", "RAG, вектори, гібридний пошук",
       r"\brag\b|embedding|vector (db|store|search)|векторн|semantic search|семантичн\w* пошук|гібридн\w* пошук|reranker|\bbm25\b|\brrf\b|hybrid search",
       ("rag", "embedding", "vector", "bm25")),
    _d("agent_memory", "Памʼять агента, граф знань",
       r"agent memory|пам.ят\w* агент\w*|memory (tier|architecture)|knowledge graph|граф\w* знань",
       ("agent-memory", "knowledge-graph", "memory", "agent")),
    _d("agent_orchestration", "Оркестрація агентів, swarm",
       r"multi[- ]agent|\bswarm\b|orchestrat|оркестр|agent loop|agent harness|планувальник агент",
       ("multi-agent", "orchestrator", "planner", "harness")),
    _d("jit_skills", "JIT-навички, lazy loading",
       r"\bjit\b|just[- ]in[- ]time|skill compil|lazy[- ]load",
       ("jit", "skills", "lazy-loading", "agent")),
    _d("state_machine", "Скінченні автомати, statechart",
       r"state machine|statechart|\bxstate\b|finite[- ]state|скінченн\w* автомат",
       ("state-machine", "statechart", "fsm", "xstate")),
    _d("scheduling", "Планувальники, черги, backpressure",
       r"scheduler|backpressure|rate[- ]limit|token bucket|job queue|task queue",
       ("scheduler", "queue", "rate-limit", "backpressure")),
    _d("bandit_routing", "Bandit-роутинг моделей",
       r"\bbandit\b|thompson|model router|llm router|роутер модел",
       ("bandit", "thompson-sampling", "llm-router", "routing")),
    _d("sandbox", "Пісочниці та ізоляція виконання",
       r"sandbox|gvisor|\bwasm\b|isolat\w+ exec|пісочниц",
       ("sandbox", "gvisor", "wasm", "isolation")),
    _d("parser_ast", "Парсери, AST, tree-sitter",
       r"\bast\b|tree[- ]?sitter|\bparser\b|парсер|compiler|компілятор|codemod",
       ("ast", "tree-sitter", "parser", "codemod")),
    _d("diff_merge", "Diff і merge-алгоритми",
       r"diff algorithm|three[- ]way merge|merge algorithm|patch (format|apply)",
       ("diff", "merge", "patch", "algorithm")),
    _d("streaming", "SSE, WebSocket, стрімінг",
       r"\bsse\b|websocket|server[- ]sent|стрімінг|\bstreaming\b",
       ("sse", "websocket", "streaming", "realtime")),
    _d("auth_crypto", "Автентифікація та криптографія",
       r"oauth|\bjwt\b|encryption|шифруван|zero[- ]knowledge",
       ("oauth", "jwt", "encryption", "auth")),
    _d("rendering", "Рендеринг, шейдери, відео",
       r"shader|webgl|webgpu|render pipeline|remotion|ffmpeg|motion graphics",
       ("webgl", "shader", "remotion", "ffmpeg")),
    _d("speech_media", "Мовлення та медіа",
       r"whisper|speech[- ]to[- ]text|\btts\b|транскрибац|diariz",
       ("whisper", "speech-to-text", "tts", "transcription")),
    _d("spatial", "Геометрія та просторові індекси",
       r"collision|physics|\bgeometry\b|геометр|kd[- ]?tree|r[- ]?tree|quadtree|spatial index",
       ("quadtree", "spatial-index", "collision", "geometry")),
    _d("ranking", "Ранжування та релевантність",
       r"ranking|relevance|fuzzy|levenshtein|ранжуван|релевантн",
       ("ranking", "relevance", "fuzzy-search", "scoring")),
    _d("llm_eval", "Оцінка якості LLM",
       r"eval harness|llm judge|benchmark|оцінк\w* якост",
       ("evaluation", "llm-judge", "benchmark", "eval-harness")),
    _d("reverse_engineering", "Реверс-інжиніринг, clean-room",
       r"reverse[- ]engineer|реверс|clean[- ]room|reimplement",
       ("reverse-engineering", "clean-room", "decompile", "reimplement")),
)

_DOMAIN_BY_KEY = {d.key: d for d in DOMAINS}

# (label, pattern) — routine work where a search is wasted effort.
SIMPLE_MARKERS: Tuple[Tuple[str, "re.Pattern[str]"], ...] = tuple(
    (label, re.compile(p, _F))
    for label, p in (
        ("typo/rename", r"\btypos?\b|опечат|\brename\b|перейменув"),
        ("форматування/lint", r"\bformat(ting)?\b|форматув|\blint\w*|prettier"),
        ("версії/релізи", r"\bbump\b|version bump|оновити версію|changelog|release notes"),
        ("документація/коментарі", r"\breadme\b|документац|docstring|коментар|\bcomments?\b"),
        ("тести існуючого", r"add (a )?(unit )?tests?\b|додай тест|unit test for"),
        ("конфіг/env", r"\bconfig\b|конфіг|\.env\b|env var"),
        ("логування", r"\blogging\b|логуван"),
        ("стилі/тексти", r"\bcss\b|\bcolou?r\b|колір|\btext\b|текст|copy change|переклад|\btranslate\b"),
        ("CRUD/поля", r"\bcrud\b|add field|додай поле|rename field"),
        ("чистка", r"remove unused|прибер\w+|видал\w+|clean ?up|\bhotfix\b"),
        ("git-рутина", r"git (commit|merge|rebase)|\bcommit\b"),
    )
)

NOVELTY = re.compile(
    r"from scratch|з нуля|\bsota\b|state[- ]of[- ]the[- ]art|\bnovel\b|новітн|найкращ\w+ (рішенн|практик)",
    _F,
)

_ORDER = {d.key: i for i, d in enumerate(DOMAINS)}


def get_domain(key: str) -> Domain:
    return _DOMAIN_BY_KEY[key]


def match_domains(text: str) -> List[Domain]:
    """Domains mentioned in text, ordered by first occurrence."""
    hits = []
    for d in DOMAINS:
        m = d.pattern.search(text or "")
        if m:
            hits.append((m.start(), _ORDER[d.key], d))
    hits.sort(key=lambda h: (h[0], h[1]))
    return [h[2] for h in hits]


def simple_hits(text: str) -> List[str]:
    return [label for label, pat in SIMPLE_MARKERS if pat.search(text or "")]
