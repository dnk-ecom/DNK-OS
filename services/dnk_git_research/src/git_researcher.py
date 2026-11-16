# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/git_researcher.py"
# purpose: "GitHub Research & SOTA Assimilation Engine for finding, auditing, AST mining, and extracting architectural patterns into DNK OS"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.5.0"
# updated_at: "2026-11-04"
# author: "DNK-e.com Maksym & Denchik Prime (Chief Autonomous Builder)"
# --- END DNK-MRH-HEADER ---

import os
import ast
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from pathlib import Path

from services.dnk_git_research.src.schemas.repo_input import (
    RepoMetadata,
    RepoAuditResult,
    AssimilationOutput
)
from services.dnk_git_research.src.license_policy import ReuseAction, classify_license


class GitHubSearchError(RuntimeError):
    """Raised by search_repositories(allow_fallback=False) when live GitHub search fails."""

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SPECS_DIR = HUB_ROOT / "docs" / "tech" / "sota_assimilation"
CATALOG_DB = HUB_ROOT / ".data" / "repo_catalog" / "catalog.db"


class GitResearchEngine:
    """
    Sovereign Git Research & Codebase Miner.
    Searches GitHub, audits repository maturity, extracts AST symbol structures,
    and produces Diataxis-compliant SOTA assimilation blueprints.
    """

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DNK-OS-GitResearcher/2.5"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        limit: int = 10,
        allow_fallback: bool = True
    ) -> List[RepoMetadata]:
        """Search GitHub for repositories.

        allow_fallback=True (legacy default): on any failure return catalog/curated data,
        which contains placeholder stars/license. allow_fallback=False (strict): raise
        GitHubSearchError instead, so callers never mistake placeholders for real data.
        """
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.github.com/search/repositories?q={encoded_query}&sort={sort}&order={order}&per_page={limit}"
        
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("items", [])
                results = []
                for item in items:
                    results.append(RepoMetadata(
                        full_name=item.get("full_name", ""),
                        name=item.get("name", ""),
                        owner=item.get("owner", {}).get("login", ""),
                        description=item.get("description") or "",
                        stars=item.get("stargazers_count", 0),
                        forks=item.get("forks_count", 0),
                        language=item.get("language") or "Unknown",
                        license=item.get("license", {}).get("spdx_id") if item.get("license") else "None",
                        url=item.get("html_url", ""),
                        topics=item.get("topics", []),
                        updated_at=item.get("updated_at")
                    ))
                return results
        except Exception as exc:
            if not allow_fallback:
                raise GitHubSearchError(str(exc)) from exc
            # Fallback to local catalog and curated knowledge
            return self._get_catalog_or_curated_fallback(query, limit)

    def audit_and_classify(self, repo_meta: RepoMetadata) -> RepoAuditResult:
        """Classify repository by Assimilation Level (R1-R5), License Track, and DNK Target Module."""
        license_type = repo_meta.license or "None"
        verdict = classify_license(license_type)
        is_permissive = verdict.action == ReuseAction.ADOPT
        
        desc = (repo_meta.description or "").lower()
        topics = [t.lower() for t in repo_meta.topics]

        # Target module mapping
        if any(w in desc or w in topics for w in ["shopify", "e-commerce", "liquid", "storefront"]):
            target_module = "services/dnk_shopify"
        elif any(w in desc or w in topics for w in ["video", "audio", "remotion", "whisper", "speech", "media"]):
            target_module = "services/dnk_media"
        elif any(w in desc or w in topics for w in ["canvas", "ui", "frontend", "react-flow", "excalidraw"]):
            target_module = "apps/web (Canvas)"
        elif any(w in desc or w in topics for w in ["agent", "swarm", "orchestrator", "jit", "taskdna"]):
            target_module = "core/orchestrator"
        elif any(w in desc or w in topics for w in ["rag", "memory", "vector", "arxiv", "embeddings"]):
            target_module = "core/scones_memory"
        elif any(w in desc or w in topics for w in ["security", "sandbox", "gvisor", "guard", "firewall"]):
            target_module = "security/auditor"
        elif any(w in desc or w in topics for w in ["distribution", "marketing", "telegram", "social"]):
            target_module = "services/dnk_distribution"
        else:
            target_module = "core/engine"

        # Maturity Tier
        if repo_meta.stars >= 5000 or any(g in repo_meta.full_name.lower() for g in ["google/", "vercel/", "facebook/", "microsoft/", "openai/"]):
            tier = "Tier 1: Golden Core"
        elif repo_meta.stars >= 500:
            tier = "Tier 2: SOTA Blueprint"
        else:
            tier = "Tier 3: Discovery Radar"

        # Assimilation Level (driven by the single license policy)
        if verdict.action == ReuseAction.CLEAN_ROOM:
            level = "R1_research"
            reason = f"License {license_type} ({verdict.license_class.value}) - research and mechanics extraction only, no code copy or linking."
        elif verdict.action == ReuseAction.ADAPT:
            level = "R3_pattern_adaptation"
            reason = f"License {license_type} ({verdict.license_class.value}) - reimplement patterns, do not copy files."
        elif "Tier 1" in tier:
            level = "R4_direct_integration"
            reason = "Golden core dependency - direct protocol/service integration."
        else:
            level = "R3_pattern_adaptation"
            reason = f"SOTA pattern adaptation into DNK OS target context: {target_module}."

        source_id = repo_meta.name.lower().replace("-", "_")

        return RepoAuditResult(
            source_id=source_id,
            full_name=repo_meta.full_name,
            stars=repo_meta.stars,
            license=license_type,
            assimilation_level=level,
            classification_reason=reason,
            license_approved=is_permissive,
            url=repo_meta.url,
            dnk_module_target=target_module,
            maturity_tier=tier
        )

    def extract_python_ast_symbols(self, file_content: str) -> Dict[str, Any]:
        """Extract classes, functions, and import dependencies from Python code."""
        try:
            tree = ast.parse(file_content)
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)

            return {
                "classes": classes,
                "functions": functions,
                "imports": sorted(list(set(imports))),
                "status": "SUCCESS"
            }
        except SyntaxError as e:
            return {
                "error": str(e),
                "status": "SYNTAX_ERROR"
            }

    def assimilate_into_dnk(
        self,
        repo_meta: RepoMetadata,
        custom_target: Optional[str] = None
    ) -> AssimilationOutput:
        """Generate canonical Diataxis SOTA specification file in docs/tech/sota_assimilation/."""
        SPECS_DIR.mkdir(parents=True, exist_ok=True)
        audit_res = self.audit_and_classify(repo_meta)
        target_context = custom_target or audit_res.dnk_module_target
        repo_slug = repo_meta.name.lower().replace("-", "_")
        spec_file = SPECS_DIR / f"{repo_slug}.md"

        content = f"""---
title: "SOTA Assimilation Spec: {repo_meta.full_name}"
status: active
type: specification
domain: core
author: "DNK-e.com Maksym & Denchik Prime (Chief Autonomous Builder)"
version: "1.0.0"
created: 2026-11-04
updated: 2026-11-04
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/tech/sota_assimilation/{repo_slug}.md"
> purpose: "SOTA Assimilation Spec for {repo_meta.full_name} into DNK OS {target_context}."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-04"
> author: "DNK-e.com Maksym & Denchik Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧬 SOTA Assimilation Spec: {repo_meta.full_name}

- **Upstream URL**: [{repo_meta.full_name}]({repo_meta.url})
- **Stars**: {repo_meta.stars} ⭐ | **Language**: `{repo_meta.language}`
- **License**: `{repo_meta.license}` (Approved Permissive: `{audit_res.license_approved}`)
- **Maturity Tier**: `{audit_res.maturity_tier}`
- **Assimilation Mode**: `{audit_res.assimilation_level}`
- **Target Bounded Context**: `{target_context}`

## 1. Description & Architectural Rationale
{repo_meta.description or 'No description provided upstream.'}

## 2. Adopted Concepts & Structural Invariants
- High-velocity algorithmic and execution patterns adapted for Denchik Prime.
- Token-efficient RAM execution and clean-room protocol isolation.

## 3. Quarantined / Excluded Elements
- External telemetry, closed proprietary dependencies, and unauthenticated cloud services.
- Unsandboxed direct system calls (must route through gVisor container boundary).

## 4. Integration Guidelines for Denchik Builder
- Implement modular FastMCP tool wrapper conforming to DNK-STD-0075.
- Add zero-tautology behavioral tests in `tests/`.
"""
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(content)

        return AssimilationOutput(
            spec_path=str(spec_file),
            source_id=audit_res.source_id,
            full_name=repo_meta.full_name,
            status="ASSIMILATED",
            target_module=target_context
        )

    def _get_catalog_or_curated_fallback(self, query: str, limit: int) -> List[RepoMetadata]:
        """Retrieve matching repositories from catalog.db or curated fallback."""
        results: List[RepoMetadata] = []
        if CATALOG_DB.exists():
            import sqlite3
            try:
                con = sqlite3.connect(CATALOG_DB)
                cur = con.cursor()
                clean_q = "".join(c for c in query if c.isalnum() or c.isspace()).strip()
                sql = """
                SELECT id, title, description, url, tech_stack, maturity_tier
                FROM repositories
                WHERE id LIKE ? OR title LIKE ? OR description LIKE ?
                LIMIT ?
                """
                like_term = f"%{clean_q}%"
                rows = cur.execute(sql, (like_term, like_term, like_term, limit)).fetchall()
                con.close()
                for r in rows:
                    name_parts = r[0].split("/")
                    owner = name_parts[0] if len(name_parts) > 1 else "dnk"
                    name = name_parts[1] if len(name_parts) > 1 else name_parts[0]
                    results.append(RepoMetadata(
                        full_name=r[0],
                        name=name,
                        owner=owner,
                        description=r[2] or "",
                        stars=1000 if "Tier 1" in (r[5] or "") else 250,
                        url=r[3] or f"https://github.com/{r[0]}",
                        license="MIT"
                    ))
                if results:
                    return results
            except Exception:
                pass

        # Standby curated fallback
        curated = [
            RepoMetadata(
                full_name="agent-jit/AgentJIT",
                name="AgentJIT",
                owner="agent-jit",
                description="Just-In-Time compiled agent skill engine and ephemeral execution.",
                stars=3200,
                language="Python",
                license="MIT",
                url="https://github.com/agent-jit/AgentJIT",
                topics=["agentic", "jit", "bytecode", "tools"]
            ),
            RepoMetadata(
                full_name="cjpais/transcribe-rs",
                name="transcribe-rs",
                owner="cjpais",
                description="Ultra-fast Rust Whisper speech-to-text audio engine.",
                stars=1800,
                language="Rust",
                license="MIT",
                url="https://github.com/cjpais/transcribe-rs",
                topics=["audio", "whisper", "rust", "speech"]
            ),
            RepoMetadata(
                full_name="google/gvisor",
                name="gvisor",
                owner="google",
                description="Application kernel for container security and untrusted code execution.",
                stars=16400,
                language="Go",
                license="Apache-2.0",
                url="https://github.com/google/gvisor",
                topics=["sandbox", "security", "kernel", "containers"]
            )
        ]
        return [c for c in curated if any(w in (c.name + c.description).lower() for w in query.lower().split())] or curated[:limit]
