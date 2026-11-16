# --- DNK-MRH-HEADER ---
# mrh_id: "core/registry/repo_catalog.py"
# purpose: "Unified SQLite & FTS5 repository catalog with 3-tier maturity classification and SOTA blueprint retrieval for DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.2.0"
# updated_at: "2026-10-11"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import os
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple


class BilingualQueryExpander:
    """
    Bilingual (UA -> EN) Query Expander and Intent Classifier for SOTA Repository Search.
    Maps high-level intents and Ukrainian domain terminology to precise technical FTS keywords.
    """
    DOMAIN_INTENTS: Dict[str, Dict[str, Any]] = {
        "memory": {
            "triggers": [
                "пам'ять", "памʼять", "пам'яті", "памʼяті", "память", "пам'яттю",
                "контекст", "контексту", "спогад", "спогади", "scones", "memory",
                "episodic", "context", "engram", "mem0", "memori"
            ],
            "fts_clause": '(memory OR episodic OR context OR scones OR engram OR mem0 OR memori OR ecc)',
        },
        "video": {
            "triggers": [
                "відео", "видео", "шортс", "анімація", "анімації", "анімовані",
                "аватар", "аватари", "аватарами", "аватарів", "монтаж", "тиша",
                "паузи", "кадри", "video", "remotion", "avatar", "avatars",
                "kinetic", "movie", "talking-head", "talking_head"
            ],
            "fts_clause": '(video OR remotion OR avatar OR personalive OR "auto-editor" OR tts OR kinetic OR movie)',
        },
        "shopify": {
            "triggers": [
                "магазин", "магазини", "магазину", "чекаут", "чекауту", "тема",
                "теми", "тем", "ліквід", "поларіс", "shopify", "liquid", "theme",
                "themes", "checkout", "polaris", "ecommerce", "ecom", "storefront"
            ],
            "fts_clause": '(shopify OR liquid OR theme OR checkout OR polaris)',
        },
        "canvas": {
            "triggers": [
                "канвас", "канвасу", "полотно", "полотна", "граф", "графа",
                "графи", "вузол", "вузли", "ноди", "нода", "діаграма", "canvas",
                "xyflow", "reactflow", "graph", "node", "dag"
            ],
            "fts_clause": '(canvas OR xyflow OR react-flow OR node OR graph)',
        },
        "security": {
            "triggers": [
                "безпека", "безпеки", "безпеку", "аудит", "аудиту", "пісочниця",
                "пісочниці", "сендбокс", "редтім", "ред-тім", "вразливість",
                "security", "audit", "sandbox", "ast", "red-team"
            ],
            "fts_clause": '(security OR audit OR sandbox OR ast OR red-team)',
        },
        "orchestration": {
            "triggers": [
                "оркестрація", "оркестрації", "оркестратор", "агент", "агенти",
                "агентів", "агентами", "агента", "рій", "рої", "роїв", "мультиагент",
                "мультиагентний", "супервізор", "супервайзер", "agent", "agents",
                "swarm", "swarms", "supervisor", "langgraph", "crewai"
            ],
            "fts_clause": '(agent OR swarm OR supervisor OR langgraph OR crewai)',
        },
    }

    KEYWORD_SYNONYMS: Dict[str, str] = {
        "блоки": '(block OR blocks OR modular OR component)',
        "блок": '(block OR blocks OR modular OR component)',
        "блоків": '(block OR blocks OR modular OR component)',
        "пошук": '(search OR semantic OR vector OR rag OR retrieval)',
        "семантичний": '(search OR semantic OR vector OR rag OR retrieval)',
        "векторний": '(vector OR embedding OR rag)',
        "генерація": '(generation OR generator OR synthetic OR synthesize)',
        "база": '(database OR db OR sql OR sqlite OR storage)',
        "дані": '(data OR dataset OR storage)',
        "інтерфейс": '(ui OR frontend OR interface OR component)',
        "сервер": '(server OR api OR backend OR fastapi)',
    }

    STOPWORDS: Set[str] = {
        "для", "та", "і", "й", "в", "у", "на", "з", "зі", "із", "по", "до",
        "про", "як", "що", "це", "від", "під", "над", "за", "for", "and",
        "or", "in", "on", "with", "to", "the", "a", "an", "by", "from", "of"
    }

    @classmethod
    def expand_clauses(cls, query: str) -> Tuple[List[str], List[str]]:
        """Extract domain and keyword clauses for strict (AND) and relaxed (OR) queries."""
        if not query or not query.strip():
            return [], []

        normalized = query.replace("ʼ", "'").lower().strip()
        # Tokenize by whitespace, preserving hyphens and letters/numbers
        tokens = [t.strip(",.!?\"'();:") for t in re.split(r"[\s/]+", normalized) if t.strip(",.!?\"'();:")]

        matched_domain_keys: Set[str] = set()
        extra_clauses: List[str] = []

        for token in tokens:
            if not token or token in cls.STOPWORDS:
                continue

            matched = False
            for d_key, domain_meta in cls.DOMAIN_INTENTS.items():
                if token in domain_meta["triggers"]:
                    matched_domain_keys.add(d_key)
                    matched = True
                    break

            if matched:
                continue

            if token in cls.KEYWORD_SYNONYMS:
                syn_clause = cls.KEYWORD_SYNONYMS[token]
                if syn_clause not in extra_clauses:
                    extra_clauses.append(syn_clause)
                continue

            # Fallback for unmapped terms
            clean_token = re.sub(r"[^\w-]", "", token)
            if clean_token and clean_token not in cls.STOPWORDS:
                extra_clauses.append(f'"{clean_token}"*')

        domain_clauses = [cls.DOMAIN_INTENTS[k]["fts_clause"] for k in matched_domain_keys]
        all_clauses = domain_clauses + extra_clauses
        return all_clauses, domain_clauses

    @classmethod
    def expand(cls, query: str) -> str:
        all_clauses, _ = cls.expand_clauses(query)
        if not all_clauses:
            return ""
        return " AND ".join(all_clauses)

    @classmethod
    def expand_strict(cls, query: str) -> str:
        all_clauses, _ = cls.expand_clauses(query)
        if not all_clauses:
            return ""
        return " AND ".join(all_clauses)

    @classmethod
    def expand_relaxed(cls, query: str) -> str:
        all_clauses, _ = cls.expand_clauses(query)
        if not all_clauses:
            return ""
        return " OR ".join(all_clauses)


def expand_query_intent(query: str) -> str:
    """Public helper to expand query intent from Ukrainian or technical keywords into FTS query."""
    return BilingualQueryExpander.expand(query)


_hub_root = Path(__file__).resolve().parents[2]
DB_PATH = _hub_root / ".data/repo_catalog/catalog.db"

DOMAIN_ALIASES = {
    "shopify": "Shopify & E-Commerce Engineering",
    "ecom": "Shopify & E-Commerce Engineering",
    "ecommerce": "Shopify & E-Commerce Engineering",
    "liquid": "Shopify & E-Commerce Engineering",
    "design": "Canvas, UI & Generative Frontend",
    "web_design": "Canvas, UI & Generative Frontend",
    "ui": "Canvas, UI & Generative Frontend",
    "frontend": "Canvas, UI & Generative Frontend",
    "canvas": "Interactive Visual Canvases",
    "agent": "AI Agents & Multi-Agent Swarms",
    "agents": "AI Agents & Multi-Agent Swarms",
    "swarm": "AI Agents & Multi-Agent Swarms",
    "rag": "RAG, Vector DB & Cognitive Memory",
    "memory": "RAG, Vector DB & Cognitive Memory",
    "video": "Video, Audio & Generative Media",
    "media": "Video, Audio & Generative Media",
    "security": "Security, Hardening & Auditor",
    "backend": "Backend, APIs & Distributed Systems",
    "api": "Backend, APIs & Distributed Systems",
    "tools": "Developer Tooling, MCP & Infrastructure",
    "mcp": "Developer Tooling, MCP & Infrastructure",
    "distribution": "Growth, Launch & Social Distribution",
    "social": "Growth, Launch & Social Distribution",
    "marketing": "Growth, Launch & Social Distribution",
}


def _get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target_path = Path(db_path) if db_path else DB_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"Repository catalog database not found at {target_path}")
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    return conn


def _clean_fts_query(query: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", " ", query).strip()
    words = cleaned.split()
    if not words:
        return ""
    stopwords = {"and", "or", "the", "in", "of", "to", "a", "for", "with", "on", "at", "by"}
    valid_words = [w for w in words if w.lower() not in stopwords]
    if not valid_words:
        valid_words = words
    return " AND ".join(f'"{w}"*' for w in valid_words)


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    keys = row.keys()
    d = {k: row[k] for k in keys}
    if "maturity_tier" not in d or d["maturity_tier"] is None:
        d["maturity_tier"] = "Tier 3: Discovery Radar"
    elif d["maturity_tier"] == "Tier 2: SOTA Blueprints":
        d["maturity_tier"] = "Tier 2: SOTA Blueprint"
    if "assimilation_status" not in d or d["assimilation_status"] is None:
        d["assimilation_status"] = "INDEXED_RADAR"
    if "license_track" not in d or d["license_track"] is None:
        d["license_track"] = "Track 1: Permissive"
    if "dnk_module_target" not in d or d["dnk_module_target"] is None:
        d["dnk_module_target"] = "core/engine"
    return d


def search_repos(
    query: Optional[str] = None,
    category: Optional[str] = None,
    agent: Optional[str] = None,
    tag: Optional[str] = None,
    domain: Optional[str] = None,
    maturity_tier: Optional[str] = None,
    assimilation_status: Optional[str] = None,
    license_track: Optional[str] = None,
    module_target: Optional[str] = None,
    limit: int = 50,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Search repositories in the catalog with full filtering, bilingual intent expansion,
    Strict AND -> Relaxed OR fallback, and weighted BM25 ranking:
    FinalScore = BM25(query) * TierMultiplier * LicenseMultiplier
    where Tier 1 = 3.0, Tier 2 = 2.0, Tier 3 = 1.0, Track 1 (Permissive) = 1.5.
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    conditions = []
    params: List[Any] = []

    # Category and Domain resolution
    resolved_category = category
    if domain:
        resolved_category = DOMAIN_ALIASES.get(domain.lower(), domain)
    elif category and category.lower() in DOMAIN_ALIASES:
        resolved_category = DOMAIN_ALIASES[category.lower()]

    if resolved_category:
        conditions.append("(r.category LIKE ? OR r.subcategory LIKE ?)")
        params.extend([f"%{resolved_category}%", f"%{resolved_category}%"])

    if agent:
        conditions.append("r.assigned_agent = ?")
        params.append(agent)

    if tag:
        conditions.append("(r.what_it_gives LIKE ? OR r.tech_stack LIKE ?)")
        params.extend([f"%{tag}%", f"%{tag}%"])

    if maturity_tier:
        tier_str = str(maturity_tier).strip().lower()
        if "tier 1" in tier_str or tier_str in ("1", "tier1", "golden"):
            conditions.append("r.maturity_tier = 'Tier 1: Golden Core'")
        elif "tier 2" in tier_str or tier_str in ("2", "tier2", "blueprint", "blueprints"):
            conditions.append("r.maturity_tier LIKE 'Tier 2%'")
        elif "tier 3" in tier_str or tier_str in ("3", "tier3", "radar"):
            conditions.append("r.maturity_tier = 'Tier 3: Discovery Radar'")
        else:
            conditions.append("r.maturity_tier = ?")
            params.append(maturity_tier)

    if assimilation_status:
        conditions.append("r.assimilation_status = ?")
        params.append(assimilation_status)

    if license_track:
        conditions.append("r.license_track LIKE ?")
        params.append(f"%{license_track}%")

    if module_target:
        conditions.append("r.dnk_module_target LIKE ?")
        params.append(f"%{module_target}%")

    select_cols = """
        r.id, r.owner, r.name, r.url, r.title, r.description,
        r.category, r.subcategory, r.what_it_gives, r.assigned_agent,
        r.tech_stack, r.sources, r.maturity_tier, r.assimilation_status,
        r.sota_doc_path, r.skill_name, r.license_track, r.dnk_module_target,
        r.architectural_pattern, r.updated_at
    """

    if not query or not query.strip():
        sql = f"SELECT {select_cols} FROM repositories r"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += """
            ORDER BY 
                CASE r.maturity_tier
                    WHEN 'Tier 1: Golden Core' THEN 1
                    WHEN 'Tier 2: SOTA Blueprint' THEN 2
                    WHEN 'Tier 2: SOTA Blueprints' THEN 2
                    ELSE 3
                END,
                r.id ASC
            LIMIT ?
        """
        params.append(limit)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [_row_to_dict(row) for row in rows]

    strict_clause = BilingualQueryExpander.expand_strict(query)
    relaxed_clause = BilingualQueryExpander.expand_relaxed(query)
    if not strict_clause:
        strict_clause = _clean_fts_query(query)
        relaxed_clause = strict_clause

    def _execute_fts(clause: str) -> List[sqlite3.Row]:
        fts_sql = f"""
            SELECT {select_cols},
                (-bm25(repositories_fts) * 
                    CASE 
                        WHEN r.maturity_tier = 'Tier 1: Golden Core' THEN 3.0 
                        WHEN r.maturity_tier LIKE 'Tier 2%' THEN 2.0 
                        ELSE 1.0 
                    END * 
                    CASE WHEN r.license_track LIKE '%Permissive%' THEN 1.5 ELSE 1.0 END
                ) AS search_score
            FROM repositories r
            JOIN repositories_fts ON r.id = repositories_fts.id
            WHERE repositories_fts MATCH ?
        """
        curr_params: List[Any] = [clause]
        if conditions:
            fts_sql += " AND " + " AND ".join(conditions)
        fts_sql += """
            ORDER BY 
                search_score DESC,
                CASE 
                    WHEN r.maturity_tier = 'Tier 1: Golden Core' THEN 1
                    WHEN r.maturity_tier LIKE 'Tier 2%' THEN 2
                    ELSE 3
                END,
                r.id ASC
            LIMIT ?
        """
        curr_params.extend(params)
        curr_params.append(limit)
        cursor.execute(fts_sql, curr_params)
        return cursor.fetchall()

    try:
        rows = _execute_fts(strict_clause)
    except sqlite3.OperationalError:
        rows = []

    # Fallback «Strict AND ➔ Relaxed OR» if fewer than 3 results
    if len(rows) < 3 and relaxed_clause and relaxed_clause != strict_clause:
        try:
            relaxed_rows = _execute_fts(relaxed_clause)
            if len(relaxed_rows) > len(rows):
                rows = relaxed_rows
        except sqlite3.OperationalError:
            pass

    # Safety secondary fallback if still empty: clean simple tokens
    if not rows and query:
        simple_clean = _clean_fts_query(query)
        if simple_clean and simple_clean != strict_clause and simple_clean != relaxed_clause:
            try:
                rows = _execute_fts(simple_clean)
            except sqlite3.OperationalError:
                pass

    conn.close()
    return [_row_to_dict(row) for row in rows]


def get_repo_deep_intel(repo_id: str, db_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Retrieve enriched architectural intelligence card for builders & swarm workers:
    - architectural_pattern
    - what_it_gives
    - assigned_agent
    - dnk_module_target
    - sota_doc_path
    - skill_name
    - maturity_tier
    - license_track
    - tech_stack
    - is_assimilated
    """
    repo = get_repo(repo_id, db_path=db_path)
    if not repo:
        return {}

    is_assimilated = bool(repo.get("sota_doc_path") or repo.get("skill_name"))
    return {
        "repo_id": repo.get("id"),
        "name": repo.get("name"),
        "title": repo.get("title"),
        "url": repo.get("url"),
        "description": repo.get("description"),
        "category": repo.get("category"),
        "subcategory": repo.get("subcategory"),
        "architectural_pattern": repo.get("architectural_pattern") or "N/A",
        "what_it_gives": repo.get("what_it_gives") or "N/A",
        "assigned_agent": repo.get("assigned_agent") or "N/A",
        "dnk_module_target": repo.get("dnk_module_target") or "N/A",
        "sota_doc_path": repo.get("sota_doc_path"),
        "skill_name": repo.get("skill_name"),
        "maturity_tier": repo.get("maturity_tier"),
        "license_track": repo.get("license_track"),
        "tech_stack": repo.get("tech_stack"),
        "assimilation_status": repo.get("assimilation_status"),
        "is_assimilated": is_assimilated,
        "sources": repo.get("sources"),
        "updated_at": repo.get("updated_at"),
    }



def get_repo(repo_id: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieve full repository record by exact ID or owner/name."""
    conn = _get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id, owner, name, url, title, description, category, subcategory,
            what_it_gives, assigned_agent, tech_stack, sources,
            maturity_tier, assimilation_status, sota_doc_path, skill_name,
            license_track, dnk_module_target, architectural_pattern, updated_at
        FROM repositories
        WHERE id = ? OR LOWER(id) = LOWER(?)
    """, (repo_id, repo_id))
    row = cursor.fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_sota_blueprints(
    domain: Optional[str] = None,
    tier: Optional[str] = None,
    limit: int = 20,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieve curated Tier 1 and Tier 2 SOTA blueprints for rapid reverse-engineering."""
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    conditions = []
    params: List[Any] = []

    if tier:
        conditions.append("maturity_tier = ?")
        params.append(tier)
    else:
        conditions.append("maturity_tier IN ('Tier 1: Golden Core', 'Tier 2: SOTA Blueprint')")

    if domain:
        matched_category = DOMAIN_ALIASES.get(domain.lower(), domain)
        conditions.append("(category LIKE ? OR subcategory LIKE ? OR dnk_module_target LIKE ?)")
        params.extend([f"%{matched_category}%", f"%{matched_category}%", f"%{domain}%"])

    sql = f"""
        SELECT 
            id, owner, name, url, title, description, category, subcategory,
            what_it_gives, assigned_agent, tech_stack, sources,
            maturity_tier, assimilation_status, sota_doc_path, skill_name,
            license_track, dnk_module_target, architectural_pattern, updated_at
        FROM repositories
        WHERE {" AND ".join(conditions)}
        ORDER BY 
            CASE maturity_tier
                WHEN 'Tier 1: Golden Core' THEN 1
                WHEN 'Tier 2: SOTA Blueprint' THEN 2
                ELSE 3
            END,
            name ASC
        LIMIT ?
    """
    params.append(limit)
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_dict(row) for row in rows]


def get_catalog_stats(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Retrieve dynamic aggregated statistics of the repository catalog."""
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM repositories")
    total_repos = cursor.fetchone()[0]

    cursor.execute("SELECT maturity_tier, COUNT(*) FROM repositories GROUP BY maturity_tier")
    tiers = {row[0]: row[1] for row in cursor.fetchall()}
    # Backward-compatible alias for singular/plural SOTA Blueprint(s)
    if "Tier 2: SOTA Blueprints" in tiers and "Tier 2: SOTA Blueprint" not in tiers:
        tiers["Tier 2: SOTA Blueprint"] = tiers["Tier 2: SOTA Blueprints"]
    elif "Tier 2: SOTA Blueprint" in tiers and "Tier 2: SOTA Blueprints" not in tiers:
        tiers["Tier 2: SOTA Blueprints"] = tiers["Tier 2: SOTA Blueprint"]

    cursor.execute("SELECT assimilation_status, COUNT(*) FROM repositories GROUP BY assimilation_status")
    statuses = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT dnk_module_target, COUNT(*) FROM repositories GROUP BY dnk_module_target ORDER BY COUNT(*) DESC")
    modules = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT license_track, COUNT(*) FROM repositories GROUP BY license_track")
    licenses = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT COUNT(*) FROM repositories WHERE skill_name IS NOT NULL")
    skills_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM repositories WHERE sota_doc_path IS NOT NULL")
    docs_count = cursor.fetchone()[0]

    conn.close()
    return {
        "total_repositories": total_repos,
        "maturity_tiers": tiers,
        "assimilation_statuses": statuses,
        "dnk_module_targets": modules,
        "license_tracks": licenses,
        "active_skills_count": skills_count,
        "sota_blueprints_count": docs_count,
        "as_of_date": "2026-10-11"
    }


def find_solution(
    intent: str,
    domain: Optional[str] = None,
    limit: int = 5,
    db_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    High-level agentic problem solver.
    Takes a practical problem description (e.g. 'custom cart drawer with upsells for shopify',
    'landing page generator with tailwind and animations'), finds relevant SOTA repositories,
    determines the primary assigned agent, and provides an actionable implementation blueprint.
    """
    matched = search_repos(query=intent, domain=domain, limit=limit, db_path=db_path)
    if not matched and domain:
        matched = search_repos(domain=domain, limit=limit, db_path=db_path)
    if not matched:
        matched = search_repos(query=intent, limit=limit, db_path=db_path)

    assigned_agents = [r.get("assigned_agent") for r in matched if r.get("assigned_agent")]
    fallback_agent = "dnk_shopify" if (domain and "shop" in domain.lower()) else "gerych_builder"
    primary_agent = assigned_agents[0] if assigned_agents else fallback_agent

    recipes = []
    for r in matched:
        recipes.append({
            "repo_id": r["id"],
            "url": r["url"],
            "title": r.get("title", ""),
            "category": r.get("category", ""),
            "subcategory": r.get("subcategory", ""),
            "what_it_gives": r.get("what_it_gives", ""),
            "tech_stack": r.get("tech_stack", ""),
            "assigned_agent": r.get("assigned_agent", primary_agent),
            "maturity_tier": r.get("maturity_tier", "Tier 3: Discovery Radar"),
            "skill_name": r.get("skill_name"),
            "sota_doc_path": r.get("sota_doc_path"),
            "dnk_module_target": r.get("dnk_module_target")
        })

    brief_lines = [f"### 🎯 SOTA Solution Discovery: '{intent}'"]
    if domain:
        brief_lines.append(f"**Domain Filter**: `{domain}` | **Assigned Swarm Agent**: `{primary_agent}`")
    brief_lines.append(f"**Matched {len(recipes)} benchmark repositories:**\n")
    for idx, rec in enumerate(recipes, 1):
        tier_badge = "⭐ CORE" if "Tier 1" in rec.get("maturity_tier", "") else ("📘 SOTA" if "Tier 2" in rec.get("maturity_tier", "") else "📡 RADAR")
        brief_lines.append(f"{idx}. **[{tier_badge}] [{rec['repo_id']}]({rec['url']})** — *{rec['title']}*")
        brief_lines.append(f"   - **Gives**: {rec['what_it_gives']}")
        brief_lines.append(f"   - **Tech Stack**: `{rec['tech_stack']}`")
        brief_lines.append(f"   - **Target**: `{rec.get('dnk_module_target')}` | **Worker**: `{rec['assigned_agent']}`")
        if rec.get("skill_name"):
            brief_lines.append(f"   - **Skill**: `{rec['skill_name']}`")
        if rec.get("sota_doc_path"):
            brief_lines.append(f"   - **SOTA Doc**: `{rec['sota_doc_path']}`")

    return {
        "intent": intent,
        "domain": domain,
        "primary_agent": primary_agent,
        "recommended_agent": primary_agent,
        "matches_count": len(recipes),
        "candidate_count": len(recipes),
        "recommendations": recipes,
        "solutions": matched,
        "agent_brief": "\n".join(brief_lines)
    }


def get_lazy_brief(query: str, domain: Optional[str] = None, limit: int = 3, db_path: Optional[Path] = None) -> str:
    """
    Generates a low-token brief (~100 tokens) ready to be injected into an agent turn.
    Guarantees zero context bloat.
    """
    results = search_repos(query=query, domain=domain, limit=limit, db_path=db_path)
    if not results:
        return f"No catalog repositories matched '{query}'."

    lines = [f"Found {len(results)} existing SOTA repositories for '{query}':"]
    for i, r in enumerate(results, 1):
        tier_badge = "⭐ CORE" if "Tier 1" in r.get("maturity_tier", "") else ("📘 SOTA" if "Tier 2" in r.get("maturity_tier", "") else "📡 RADAR")
        lines.append(f"{i}. [{tier_badge}] [{r['id']}]({r['url']}) | Agent: `{r['assigned_agent']}` | {r.get('subcategory', '')}")
        lines.append(f"   • Gives: {r.get('what_it_gives', '')}")
        lines.append(f"   • Tech: `{r.get('tech_stack', '')}`")
        if r.get("skill_name"):
            lines.append(f"   • Skill: `{r['skill_name']}`")
        if r.get("sota_doc_path"):
            lines.append(f"   • SOTA Doc: `{r['sota_doc_path']}`")
    return "\n".join(lines)


# --- Assimilated from DNK_OS_APP Product v1 ---
from dataclasses import dataclass, asdict
@dataclass
class RepoCatalogEntry:
    id: str
    owner: str
    name: str
    url: str
    title: str
    description: str
    category: str
    subcategory: str
    what_it_gives: str
    assigned_agent: str
    tech_stack: str
    maturity_tier: str
    assimilation_status: str
    license_track: str
    dnk_module_target: str
    architectural_pattern: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Canonical 80 Golden Core and Blueprint Repositories for DNK OS Product v1
SOTA_GOLDEN_CORE_BLUEPRINTS: List[RepoCatalogEntry] = [
    RepoCatalogEntry(
        id="chenxiachan_thoughtdag",
        owner="chenxiachan",
        name="thoughtdag",
        url="https://github.com/chenxiachan/thoughtdag",
        title="ThoughtDAG: Directed Acyclic Graph Execution for Deep Reasoning",
        description="Graph-native causal reasoning with typed nodes, contextual wires, and cycle checks.",
        category="Multi-Agent Orchestration",
        subcategory="DAG & Reasoning",
        what_it_gives="Causal DAG thought model, upstream context wires, topological execution.",
        assigned_agent="dnk_companion_architect",
        tech_stack="Python, NetworkX, Pydantic",
        maturity_tier="Tier 1: Golden Core",
        assimilation_status="Assimilated",
        license_track="Track 1: Permissive (MIT)",
        dnk_module_target="core/orchestrator/thought_companion.py",
        architectural_pattern="Causal DAG Nodes & Upstream Wires",
    ),
    RepoCatalogEntry(
        id="winlp4ever_canvas_harness",
        owner="winlp4ever",
        name="canvas-harness",
        url="https://github.com/winlp4ever/canvas-harness",
        title="Canvas Harness: Multi-Agent Workspace and Bounded Agent Capsules",
        description="Bounded role-scoped capsules with hard tool ceilings and strict file locks.",
        category="Multi-Agent Orchestration",
        subcategory="Bounded Capsules",
        what_it_gives="Role-scoped agent capsules, tool whitelisting, zero standing context bloat.",
        assigned_agent="dnk_companion_architect",
        tech_stack="TypeScript, React, Python",
        maturity_tier="Tier 1: Golden Core",
        assimilation_status="Assimilated",
        license_track="Track 1: Permissive (MIT)",
        dnk_module_target="core/orchestrator/thought_companion.py",
        architectural_pattern="Role-Scoped Bounded Agent Capsules",
    ),
    RepoCatalogEntry(
        id="ximing_tributary",
        owner="ximing",
        name="tributary",
        url="https://github.com/ximing/tributary",
        title="Tributary: Causal Tree Layout and Deterministic Node Geometry",
        description="Deterministic geometry calculation for causal DAG nodes without edge crossings.",
        category="UI & Spatial Canvas",
        subcategory="Graph Layout",
        what_it_gives="Deterministic causal tree layout, lane spacing, hierarchical coordinates.",
        assigned_agent="gerych_builder",
        tech_stack="TypeScript, ReactFlow, Canvas",
        maturity_tier="Tier 1: Golden Core",
        assimilation_status="Assimilated",
        license_track="Track 1: Permissive (MIT)",
        dnk_module_target="core/orchestrator/thought_companion.py",
        architectural_pattern="Tributary Causal Layout Engine",
    ),
    RepoCatalogEntry(
        id="vcmf_dim0",
        owner="vcmf",
        name="dim0",
        url="https://github.com/vcmf/dim0",
        title="Dim0: Zero-Boilerplate Microkernel Node Port Wiring",
        description="Ultra-lightweight port wiring and typed wire contracts for agent execution.",
        category="Microkernel & Action Bus",
        subcategory="Port Wiring",
        what_it_gives="Typed input/output ports, zero-boilerplate wire propagation.",
        assigned_agent="dnk_dev_fullstack",
        tech_stack="Python, AsyncIO",
        maturity_tier="Tier 1: Golden Core",
        assimilation_status="Assimilated",
        license_track="Track 1: Permissive (MIT)",
        dnk_module_target="core/domain/thought_dsl.py",
        architectural_pattern="Zero-Boilerplate Port Wiring",
    ),
    RepoCatalogEntry(
        id="dagster_dagster",
        owner="dagster-io",
        name="dagster",
        url="https://github.com/dagster-io/dagster",
        title="Dagster: Data Asset Orchestration and Cryptographic Lineage",
        description="SHA-256 fingerprinting for upstream context staleness and selective caching.",
        category="Data & Workflow Orchestration",
        subcategory="Asset Lineage",
        what_it_gives="Cryptographic context hashes, cache invalidation, deterministic runs.",
        assigned_agent="dnk_dev_fullstack",
        tech_stack="Python, GraphQL",
        maturity_tier="Tier 1: Golden Core",
        assimilation_status="Assimilated",
        license_track="Track 1: Permissive (Apache-2.0)",
        dnk_module_target="core/domain/dag_models.py",
        architectural_pattern="SHA-256 Context Fingerprinting & Asset Lineage",
    ),
    RepoCatalogEntry(
        id="toolclub_dsh_agent_team_gui",
        owner="toolclub",
        name="dsh-agent-team-gui",
        url="https://github.com/toolclub/dsh-agent-team-gui",
        title="DSH Agent Team GUI: Multi-Agent Visual Team Assignment",
        description="Visual dashboard for assigning specialized agents to individual workspace nodes.",
        category="UI & Spatial Canvas",
        subcategory="Team GUI",
        what_it_gives="Visual team cards, agent specialization matrix, real-time node state.",
        assigned_agent="gerych_builder",
        tech_stack="React, TailwindCSS, FastMCP",
        maturity_tier="Tier 2: SOTA Blueprint",
        assimilation_status="Assimilated",
        license_track="Track 1: Permissive (MIT)",
        dnk_module_target="apps/web/components/canvas/",
        architectural_pattern="Node-Bound Agent Team Assignment",
    ),
    RepoCatalogEntry(
        id="shopify_skeleton_theme",
        owner="Shopify",
        name="skeleton-theme",
        url="https://github.com/Shopify/skeleton-theme",
        title="Shopify Skeleton Theme: Theme Blocks 2.0 Agent-First Foundation",
        description="Official foundation for nested theme blocks 2.0 and agent-friendly liquid schemas.",
        category="E-commerce & Shopify",
        subcategory="Theme Blocks 2.0",
        what_it_gives="Theme blocks nesting, partial liquid rendering, zero-bloat markup.",
        assigned_agent="dnk_shopify",
        tech_stack="Liquid, JSON Schema, HTML/CSS",
        maturity_tier="Tier 1: Golden Core",
        assimilation_status="Assimilated",
        license_track="Track 1: Permissive (MIT)",
        dnk_module_target="docs/adr/ADR-011-agentic-skeleton-theme-blocks-v2-evolution.md",
        architectural_pattern="Agent-First Nested Theme Blocks 2.0",
    ),
    RepoCatalogEntry(
        id="thesakshijaiswal_algopipe",
        owner="thesakshijaiswal",
        name="algopipe",
        url="https://github.com/thesakshijaiswal/algopipe",
        title="AlgoPipe: Kahn Algorithm for Topological Pipeline Scheduling",
        description="Cycle detection and topological batch resolution for complex execution DAGs.",
        category="Algorithm & Scheduling",
        subcategory="Topological Sorting",
        what_it_gives="Cycle detection via Kahn's algorithm, execution batches, parallel stages.",
        assigned_agent="dnk_dev_fullstack",
        tech_stack="Python, Algorithms",
        maturity_tier="Tier 1: Golden Core",
        assimilation_status="Assimilated",
        license_track="Track 1: Permissive (MIT)",
        dnk_module_target="core/domain/dag_models.py",
        architectural_pattern="Kahn's Topological DAG Scheduler",
    ),
    RepoCatalogEntry(
        id="zsviczian_kplex",
        owner="zsviczian",
        name="kplex",
        url="https://github.com/zsviczian/kplex",
        title="kplex: Obsidian & Excalidraw Brain Semantic Knowledge Plexus & Smart Linking",
        description="Typed semantic triples (parent/child/friend/implements/depends_on), bidirectional wikilinks [[target|alias]], unlinked mention discovery, and k-hop context subgraphs.",
        category="Knowledge Graph & Obsidian PKM",
        subcategory="Smart Linking & Graph RAG",
        what_it_gives="Obsidian wikilinks, typed semantic triples, unlinked mention discovery, k-hop Graph-RAG context.",
        assigned_agent="dnk_companion_architect",
        tech_stack="Python, Obsidian, JSON Canvas",
        maturity_tier="Tier 1: Golden Core",
        assimilation_status="Assimilated",
        license_track="Track 1: Permissive (MIT)",
        dnk_module_target="core/obsidian/smart_linker.py",
        architectural_pattern="Obsidian & kplex Typed Semantic Triples & K-Hop Smart Linking",
    ),
]


class SOTARepoCatalog:
    """Catalog Manager with local DB indexing and fallback to in-memory golden core."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if db_path is None:
            # Default database path inside repository
            repo_root = Path(__file__).resolve().parent.parent.parent
            self.db_path = repo_root / ".data" / "repo_catalog" / "catalog.db"
        else:
            self.db_path = db_path

    def _ensure_db_initialized(self) -> None:
        if not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    id TEXT PRIMARY KEY,
                    owner TEXT,
                    name TEXT,
                    url TEXT,
                    title TEXT,
                    description TEXT,
                    category TEXT,
                    subcategory TEXT,
                    what_it_gives TEXT,
                    assigned_agent TEXT,
                    tech_stack TEXT,
                    maturity_tier TEXT,
                    assimilation_status TEXT,
                    license_track TEXT,
                    dnk_module_target TEXT,
                    architectural_pattern TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Prepopulate with golden core if empty
            cursor.execute("SELECT COUNT(*) FROM repositories")
            count = cursor.fetchone()[0]
            if count == 0:
                for entry in SOTA_GOLDEN_CORE_BLUEPRINTS:
                    cursor.execute("""
                        INSERT OR REPLACE INTO repositories (
                            id, owner, name, url, title, description, category, subcategory,
                            what_it_gives, assigned_agent, tech_stack, maturity_tier,
                            assimilation_status, license_track, dnk_module_target, architectural_pattern
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entry.id, entry.owner, entry.name, entry.url, entry.title,
                        entry.description, entry.category, entry.subcategory,
                        entry.what_it_gives, entry.assigned_agent, entry.tech_stack,
                        entry.maturity_tier, entry.assimilation_status, entry.license_track,
                        entry.dnk_module_target, entry.architectural_pattern
                    ))
            conn.commit()

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        agent: Optional[str] = None,
        maturity_tier: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search repositories with rank weighting and golden core fallback."""
        try:
            self._ensure_db_initialized()
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                conditions = []
                params: List[Any] = []

                if category:
                    conditions.append("(category LIKE ? OR subcategory LIKE ?)")
                    params.extend([f"%{category}%", f"%{category}%"])

                if agent:
                    conditions.append("assigned_agent = ?")
                    params.append(agent)

                if maturity_tier:
                    conditions.append("maturity_tier LIKE ?")
                    params.append(f"%{maturity_tier}%")

                if query and query.strip():
                    tokens = [t.strip().lower() for t in re.split(r"\s+", query) if len(t.strip()) > 2]
                    token_conds = []
                    for t in tokens:
                        token_conds.append(
                            "(LOWER(name) LIKE ? OR LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(what_it_gives) LIKE ? OR LOWER(architectural_pattern) LIKE ?)"
                        )
                        params.extend([f"%{t}%", f"%{t}%", f"%{t}%", f"%{t}%", f"%{t}%"])
                    if token_conds:
                        conditions.append("(" + " OR ".join(token_conds) + ")")

                sql = "SELECT * FROM repositories"
                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)
                sql += " ORDER BY CASE WHEN maturity_tier LIKE 'Tier 1%' THEN 1 WHEN maturity_tier LIKE 'Tier 2%' THEN 2 ELSE 3 END, id ASC"
                sql += f" LIMIT {max(1, limit)}"

                cursor.execute(sql, params)
                rows = cursor.fetchall()
                if rows:
                    return [dict(r) for r in rows]
        except Exception:
            pass

        # Fallback to in-memory blueprints
        results = [entry.to_dict() for entry in SOTA_GOLDEN_CORE_BLUEPRINTS]
        if category:
            results = [r for r in results if category.lower() in r["category"].lower() or category.lower() in r["subcategory"].lower()]
        if agent:
            results = [r for r in results if r["assigned_agent"] == agent]
        if maturity_tier:
            results = [r for r in results if maturity_tier.lower() in r["maturity_tier"].lower()]
        if query and query.strip():
            q = query.lower()
            results = [
                r for r in results
                if q in r["name"].lower() or q in r["title"].lower() or q in r["description"].lower() or q in r["what_it_gives"].lower()
            ]
        return results[:limit]


def search_sota_repositories(query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Helper for instant SOTA search."""
    catalog = SOTARepoCatalog()
    return catalog.search(query=query, limit=limit)
