# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/repo_signals.py"
# purpose: "Rate-limit-aware, resumable collection of real GitHub health signals (stars, pushed_at, archived, license, existence) for library curation"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
The catalog knows names and descriptions, not whether a repository is alive.
This module fetches the facts: does it still exist, is it archived, when was the
last push, how many people care. Facts only: nothing here guesses.

Budget: unauthenticated GitHub allows 60 requests/hour, a token 5000/hour. scan()
stops before the limit, stores everything it learned (with ETag, so a refresh that
finds nothing new costs no quota) and continues from where it stopped next time.
"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from pydantic import BaseModel, Field

logger = logging.getLogger("dnk.git_research.signals")

_ID = re.compile(r"^[\w.\-]+/[\w.\-]+$")
_LOGIN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-]{0,38}$")
_NON_REPO_ROOTS = {"orgs", "topics", "collections", "marketplace", "sponsors", "settings", "features", "apps"}


class RepoSignals(BaseModel):
    repo_id: str                      # catalog id (the key we store under)
    api_name: str = ""                # owner/repo actually queried
    fetched_at: str = ""
    status: str = "ok"                # ok | gone | error | not_github | invalid
    http_status: int = 0
    archived: bool = False
    disabled: bool = False
    fork: bool = False
    is_template: bool = False
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    size_kb: int = 0
    created_at: Optional[str] = None
    pushed_at: Optional[str] = None
    license_spdx: Optional[str] = None
    language: Optional[str] = None
    owner_type: Optional[str] = None  # User | Organization
    topics: List[str] = Field(default_factory=list)
    description: str = ""
    kind: str = "repo"                # repo | org (organization/user page, a source of repositories)
    public_repos: int = 0             # org only


class FetchMeta(BaseModel):
    remaining: Optional[int] = None
    reset: Optional[int] = None
    etag: Optional[str] = None
    not_modified: bool = False


class RateLimited(RuntimeError):
    def __init__(self, reset: Optional[int] = None):
        super().__init__("GitHub rate limit reached")
        self.reset = reset


def github_full_name(url: Optional[str]) -> Optional[str]:
    """owner/repo from a github.com URL, or None for portals, profiles and other hosts."""
    if not url:
        return None
    p = urlparse(url if "//" in url else "https://" + url)
    if p.netloc.lower() not in ("github.com", "www.github.com"):
        return None
    parts = [x for x in p.path.split("/") if x]
    if len(parts) < 2 or parts[0].lower() in _NON_REPO_ROOTS:
        return None
    name = re.sub(r"\.git$", "", f"{parts[0]}/{parts[1]}")
    return name if _ID.match(name) else None


def github_org_login(url: Optional[str]) -> Optional[str]:
    """Login of a GitHub organization/user page: github.com/orgs/NAME, github.com/NAME(?tab=repositories)."""
    if not url:
        return None
    p = urlparse(url if "//" in url else "https://" + url)
    if p.netloc.lower() not in ("github.com", "www.github.com"):
        return None
    parts = [x for x in p.path.split("/") if x]
    login = parts[1] if len(parts) == 2 and parts[0].lower() == "orgs" else parts[0] if len(parts) == 1 else None
    return login if login and _LOGIN.match(login) and login.lower() not in _NON_REPO_ROOTS else None


def signal_target(row: Dict[str, Any]) -> Optional[Tuple[str, str]]:
    """What to ask GitHub about for a catalog row: ("repo", owner/repo) or ("org", login)."""
    name = github_full_name(row.get("url"))
    if name:
        return "repo", name
    login = github_org_login(row.get("url"))
    return ("org", login) if login else None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _meta(headers: Any, code: int) -> FetchMeta:
    def h(name: str) -> Optional[str]:
        try:
            return headers.get(name) if headers is not None else None
        except Exception:
            return None
    rem, reset = h("X-RateLimit-Remaining"), h("X-RateLimit-Reset")
    return FetchMeta(
        remaining=int(rem) if rem and rem.isdigit() else None,
        reset=int(reset) if reset and reset.isdigit() else None,
        etag=h("ETag"),
        not_modified=(code == 304),
    )


def _from_json(repo_id: str, api_name: str, code: int, d: Dict[str, Any]) -> RepoSignals:
    lic = d.get("license") or {}
    spdx = lic.get("spdx_id")
    return RepoSignals(
        repo_id=repo_id, api_name=api_name, fetched_at=_now(), status="ok", http_status=code,
        archived=bool(d.get("archived")), disabled=bool(d.get("disabled")), fork=bool(d.get("fork")),
        is_template=bool(d.get("is_template")), stars=int(d.get("stargazers_count") or 0),
        forks=int(d.get("forks_count") or 0), open_issues=int(d.get("open_issues_count") or 0),
        size_kb=int(d.get("size") or 0), created_at=d.get("created_at"), pushed_at=d.get("pushed_at"),
        license_spdx=None if spdx in (None, "NOASSERTION") else spdx, language=d.get("language"),
        owner_type=(d.get("owner") or {}).get("type"), topics=list(d.get("topics") or []),
        description=d.get("description") or "",
    )


def _org_from_json(repo_id: str, login: str, code: int, d: Dict[str, Any]) -> RepoSignals:
    return RepoSignals(
        repo_id=repo_id, api_name=login, fetched_at=_now(), status="ok", http_status=code, kind="org",
        owner_type=d.get("type"), public_repos=int(d.get("public_repos") or 0), stars=0,
        created_at=d.get("created_at"), pushed_at=d.get("updated_at"), description=d.get("bio") or d.get("description") or "",
    )


def fetch_signals(
    repo_id: str,
    api_name: str,
    token: Optional[str] = None,
    etag: Optional[str] = None,
    timeout: float = 10.0,
    urlopen: Callable[..., Any] = urllib.request.urlopen,
    kind: str = "repo",
) -> Tuple[Optional[RepoSignals], FetchMeta]:
    """One API call. Returns (signals | None when 304, meta). Raises RateLimited."""
    valid = _LOGIN.match(api_name or "") if kind == "org" else _ID.match(api_name or "")
    if not valid:
        return RepoSignals(repo_id=repo_id, api_name=api_name or "", fetched_at=_now(), status="invalid"), FetchMeta()
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "DNK-OS-GitResearcher/2.6"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if etag:
        headers["If-None-Match"] = etag
    endpoint = f"users/{api_name}" if kind == "org" else f"repos/{api_name}"
    req = urllib.request.Request(f"https://api.github.com/{endpoint}", headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", 200)
            meta = _meta(getattr(resp, "headers", None), code)
            payload = json.loads(resp.read().decode("utf-8"))
            parse = _org_from_json if kind == "org" else _from_json
            return parse(repo_id, api_name, code, payload), meta
    except urllib.error.HTTPError as exc:
        meta = _meta(exc.headers, exc.code)
        if exc.code == 304:
            meta.not_modified = True
            return None, meta
        if exc.code in (403, 429) and (meta.remaining == 0 or exc.code == 429):
            raise RateLimited(meta.reset) from exc
        status = "gone" if exc.code in (404, 410, 451) else "error"
        return RepoSignals(repo_id=repo_id, api_name=api_name, fetched_at=_now(), status=status, http_status=exc.code, kind=kind), meta
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        logger.warning("signals fetch failed for %s: %s", api_name, exc)
        return RepoSignals(repo_id=repo_id, api_name=api_name, fetched_at=_now(), status="error", http_status=0), FetchMeta()


def scan(
    rows: List[Dict[str, Any]],
    store: Any,
    token: Optional[str] = None,
    max_requests: int = 50,
    reserve: int = 3,
    refresh_days: int = 14,
    urlopen: Callable[..., Any] = urllib.request.urlopen,
) -> Dict[str, Any]:
    """Fetch signals for the least-recently-checked repos. Resumable: run it again to continue."""
    fetched = store.fetched_map()
    cutoff = datetime.now(timezone.utc) - timedelta(days=refresh_days)
    todo: List[Tuple[str, Dict[str, Any], str, str]] = []
    skipped_nongit = 0
    for row in rows:
        target = signal_target(row)
        if not target:
            skipped_nongit += 1
            continue
        kind, name = target
        last = fetched.get(row["id"].lower())
        if last and kind == "org":
            old = store.get_signals(row["id"])
            if old is None or old[0].kind != "org":
                last = None          # an earlier scan asked the wrong endpoint: ask again
        if last:
            try:
                if datetime.fromisoformat(last) > cutoff:
                    continue
            except ValueError:
                pass
        todo.append((last or "", row, name, kind))
    todo.sort(key=lambda t: t[0])  # never-fetched ("") first, then the oldest

    summary = {"requests": 0, "ok": 0, "gone": 0, "error": 0, "not_modified": 0,
               "pending": len(todo), "skipped_non_github": skipped_nongit, "stopped": "done",
               "remaining_quota": None}
    for _, row, name, kind in todo:
        if summary["requests"] >= max_requests:
            summary["stopped"] = "max_requests"
            break
        prev = store.get_signals(row["id"])
        try:
            sig, meta = fetch_signals(row["id"], name, token, prev[1] if prev and prev[0].kind == kind else None,
                                      urlopen=urlopen, kind=kind)
        except RateLimited as exc:
            summary["stopped"] = "rate_limit"
            summary["resume_after_epoch"] = exc.reset
            break
        summary["requests"] += 1
        summary["pending"] -= 1
        summary["remaining_quota"] = meta.remaining
        if meta.not_modified or sig is None:
            store.touch_signals(row["id"])
            summary["not_modified"] += 1
        else:
            store.put_signals(sig, meta.etag)
            summary[sig.status if sig.status in ("ok", "gone") else "error"] += 1
        if meta.remaining is not None and meta.remaining <= reserve:
            summary["stopped"] = "rate_limit"
            summary["resume_after_epoch"] = meta.reset
            break
    return summary
