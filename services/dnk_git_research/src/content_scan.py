# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/content_scan.py"
# purpose: "Rate-limit-aware, resumable fetch of repository file trees (one API call per repo) for content-based evaluation of niche repositories"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Deep scan = for niche repositories (see niche_profiles) read the file tree and judge the content.
One GET /repos/{o}/{r}/git/trees/HEAD?recursive=1 per repository. Nothing is downloaded or executed.
Results are stored in health.db (table `content`) so the scan resumes where it stopped.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence

from services.dnk_git_research.src.niche_profiles import ANALYSIS_VERSION, ContentSignals, analyse_tree, detect_niches
from services.dnk_git_research.src.repo_signals import RateLimited, _ID, _meta, github_full_name

logger = logging.getLogger("dnk.git_research.content")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_tree(
    repo_id: str,
    api_name: str,
    niches: Sequence[str],
    token: Optional[str] = None,
    timeout: float = 15.0,
    urlopen: Callable[..., Any] = urllib.request.urlopen,
) -> ContentSignals:
    """One API call. Raises RateLimited. A failure becomes status=error (retried on the next scan)."""
    if not _ID.match(api_name or ""):
        return ContentSignals(repo_id=repo_id, fetched_at=_now(), status="error", niches=list(niches))
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "DNK-OS-GitResearcher/2.6"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/repos/{api_name}/git/trees/HEAD?recursive=1", headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        meta = _meta(exc.headers, exc.code)
        if exc.code in (403, 429) and (meta.remaining == 0 or exc.code == 429):
            raise RateLimited(meta.reset) from exc
        if exc.code == 409:   # empty repository: no commits, no tree
            return analyse_tree(repo_id, niches, [], fetched_at=_now())
        return ContentSignals(repo_id=repo_id, fetched_at=_now(),
                              status="error" if exc.code >= 500 else "empty", niches=list(niches))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        logger.warning("tree fetch failed for %s: %s", api_name, exc)
        return ContentSignals(repo_id=repo_id, fetched_at=_now(), status="error", niches=list(niches))
    blobs = [t for t in data.get("tree", []) if t.get("type") == "blob"]
    paths = [t.get("path", "") for t in blobs]
    sizes = {t.get("path", ""): int(t.get("size") or 0) for t in blobs}
    return analyse_tree(repo_id, niches, paths, truncated=bool(data.get("truncated")), fetched_at=_now(), sizes=sizes)


def candidates(rows: Sequence[Dict[str, Any]], signals: Dict[str, Any], assessments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Niche entries that are alive and would otherwise be judged on fame alone."""
    out = []
    for r in rows:
        rid = r["id"].lower()
        s = signals.get(rid)
        a = assessments.get(rid)
        if s is None or s.status != "ok" or not github_full_name(r.get("url")):
            continue
        if not detect_niches(r, s):
            continue
        if a is not None and a.tier.value in ("KEEP",):
            continue          # already healthy by fame: no need to spend a request
        if a is not None and any(f.startswith("DUPLICATE_OF") for f in a.flags):
            continue
        out.append(r)
    return out


def deep_scan(
    rows: Sequence[Dict[str, Any]],
    store: Any,
    token: Optional[str] = None,
    max_requests: int = 100,
    refresh_days: int = 30,
    urlopen: Callable[..., Any] = urllib.request.urlopen,
) -> Dict[str, Any]:
    """Fetch trees for the given (already filtered) rows, oldest first, within the request budget."""
    done = store.content_fetched_map()
    old = store.all_content()
    sigs = store.all_signals()
    cutoff = datetime.now(timezone.utc).timestamp() - refresh_days * 86400

    def stale_row(r: Dict[str, Any]) -> bool:
        rid = r["id"].lower()
        prev = old.get(rid)
        # rules changed, or the entry joined a new niche since the last read: the old facts are not enough
        if prev is not None and (prev.version < ANALYSIS_VERSION or set(prev.niches) != set(detect_niches(r, sigs.get(rid)))):
            return True
        ts = done.get(rid)
        if not ts:
            return True
        try:
            return datetime.fromisoformat(ts).timestamp() < cutoff
        except ValueError:
            return True

    todo = [r for r in rows if stale_row(r)]
    todo.sort(key=lambda r: (done.get(r["id"].lower(), ""), r["id"]))
    stats = {"requests": 0, "ok": 0, "empty": 0, "error": 0, "pending": 0, "stopped": "done"}
    for i, r in enumerate(todo):
        if stats["requests"] >= max_requests:
            stats["stopped"] = "budget"
            stats["pending"] = len(todo) - i
            break
        try:
            c = fetch_tree(r["id"].lower(), github_full_name(r.get("url")) or "", detect_niches(r, sigs.get(r["id"].lower())), token, urlopen=urlopen)
        except RateLimited:
            stats["stopped"] = "rate_limited"
            stats["pending"] = len(todo) - i
            break
        stats["requests"] += 1
        stats[c.status if c.status in ("ok", "empty", "error") else "error"] += 1
        if c.status != "error":
            store.put_content(c)
    return stats
