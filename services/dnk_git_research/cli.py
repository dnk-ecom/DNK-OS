#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/cli.py"
# purpose: "CLI Interface for DNK Git Research Engine"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.1.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Denchik Prime"
# --- END DNK-MRH-HEADER ---

import os
import sys
import json
import argparse
from services.dnk_git_research.src.git_researcher import GitResearchEngine


def main():
    parser = argparse.ArgumentParser(description="DNK Git Research & Codebase Mining CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search
    search_p = subparsers.add_parser("search", help="Search repositories")
    search_p.add_argument("query", type=str, help="Search query")
    search_p.add_argument("--limit", type=int, default=5, help="Result limit")

    # Assimilate
    assimilate_p = subparsers.add_parser("assimilate", help="Assimilate repository into DNK OS")
    assimilate_p.add_argument("repo", type=str, help="Repository owner/name")
    assimilate_p.add_argument("--target", type=str, default="core/engine", help="Target DNK context")

    # Reuse brief (JIT prior-art search, gated: simple/repetitive tasks are skipped)
    brief_p = subparsers.add_parser("brief", help="Reuse brief: has the world already solved this task?")
    brief_p.add_argument("task", nargs="?", default="", help="Task description (or use --task-file)")
    brief_p.add_argument("--task-file", type=str, help="Read the task description from a file")
    brief_p.add_argument("--file", action="append", default=[], dest="files", help="Target file of the task (repeatable)")
    brief_p.add_argument("--tag", action="append", default=[], dest="tags", help="Task tag, e.g. force_research / skip_research")
    brief_p.add_argument("--force", action="store_true", help="Skip triage and always research")
    brief_p.add_argument("--refresh", action="store_true", help="Ignore the cached brief")
    brief_p.add_argument("--no-live", action="store_true", help="Catalog only, no GitHub requests")
    brief_p.add_argument("--verify-licenses", action="store_true", help="Confirm catalog licenses via GitHub")
    brief_p.add_argument("--text", action="store_true", help="Human-readable output instead of JSON")

    # Library curation: verify health of the catalog, quarantine/remove dead or risky entries (reversible)
    cur_p = subparsers.add_parser("curate", help="Library health: scan, plan, apply, restore, status")
    cur_sub = cur_p.add_subparsers(dest="curate_command", required=True)
    scan_p = cur_sub.add_parser("scan", help="Fetch real GitHub signals (resumable, rate-limit aware)")
    scan_p.add_argument("--max-requests", type=int, default=50)
    scan_p.add_argument("--refresh-days", type=int, default=14)
    deep_p = cur_sub.add_parser("deepscan", help="Read file trees of niche repos (Shopify themes, coding assets, defense) to judge content, not fame")
    deep_p.add_argument("--max-requests", type=int, default=100)
    deep_p.add_argument("--refresh-days", type=int, default=30)
    plan_p = cur_sub.add_parser("plan", help="Score every repo and write a removal plan (changes nothing)")
    plan_p.add_argument("--out", type=str, help="Where to save the plan JSON")
    plan_p.add_argument("--show", type=int, default=15, help="Rows to list per tier")
    apply_p = cur_sub.add_parser("apply", help="Move planned repos to quarantine (dry run unless --confirm)")
    apply_p.add_argument("plan", type=str)
    apply_p.add_argument("--tiers", type=str, default="REMOVE,QUARANTINE")
    apply_p.add_argument("--confirm", action="store_true")
    rest_p = cur_sub.add_parser("restore", help="Return a quarantined repo to the catalog")
    rest_p.add_argument("repo_id", type=str)
    cur_sub.add_parser("status", help="Coverage of signals and size of the quarantine")

    # Dossier: evidence for one repository (pinned commit, files to read, hints) and verification of the agent's result
    led_p = subparsers.add_parser("ledger", help="Assimilation ledger: environments, modules, gaps, donors")
    led_sub = led_p.add_subparsers(dest="ledger_command", required=True)
    led_sub.add_parser("check", help="Validate curated records (licenses, citations, paths)")
    led_sub.add_parser("stats", help="Counts: modules, gaps, indexed vs verified donors")
    ctx_p = led_sub.add_parser("context", help="Text block for the agent prompt")
    ctx_p.add_argument("--module", type=str, default="")
    fit_p = led_sub.add_parser("fit", help="What does a finding give DNK: fills a gap, already have, adjacent, nothing")
    fit_p.add_argument("--dossier", type=str, help="Dossier JSON (or markdown with a ```json block)")
    fit_p.add_argument("--text", action="append", default=[], help="A mechanic described in words (repeatable)")
    fit_p.add_argument("--donor", type=str, default="")

    au_p = subparsers.add_parser("audit", help="Model-agnostic repository audit: start, next, submit, skip, status, finish, promote")
    au_sub = au_p.add_subparsers(dest="audit_command", required=True)
    aus = au_sub.add_parser("start", help="Triage + pin commit + read evidence; creates a run")
    aus.add_argument("repo", type=str)
    aus.add_argument("--task", type=str, default="", help="DNK task the audit serves")
    aus.add_argument("--module", type=str, default="")
    aus.add_argument("--focus", type=str, default="")
    aus.add_argument("--claim", action="append", default=[])
    aus.add_argument("--no-clone", action="store_true", help="Use the GitHub API (a few files) instead of scanning a shallow clone")
    aus.add_argument("--clone-dir", type=str, default="", help="Reuse an existing shallow clone")
    aus.add_argument("--budget", type=int, default=40000, help="Characters of evidence per step (lower for small-context models)")
    aun = au_sub.add_parser("next", help="Print the self-contained prompt for the next step")
    aun.add_argument("run", type=str)
    aun.add_argument("--repair", action="store_true", help="Prompt with the last rejection reasons")
    auu = au_sub.add_parser("submit", help="Submit the agent's answer for a step (file or - for stdin)")
    auu.add_argument("run", type=str)
    auu.add_argument("step", type=str, choices=["identity", "claims", "mechanics", "risks", "verdict"], help="Step NAME, not a number")
    auu.add_argument("file", type=str)
    auk = au_sub.add_parser("skip", help="Skip a step with a reason (lowers the grade)")
    auk.add_argument("run", type=str)
    auk.add_argument("step", type=str, choices=["identity", "claims", "mechanics", "risks", "verdict"])
    auk.add_argument("--reason", required=True)
    aut = au_sub.add_parser("status", help="Where the run stands")
    aut.add_argument("run", type=str)
    auf = au_sub.add_parser("finish", help="Assemble, verify, grade, write audit.md, dossier.json, ledger_draft.yaml")
    auf.add_argument("run", type=str)
    aup = au_sub.add_parser("promote", help="Copy the checked ledger draft into ledger/donors (needs --confirm)")
    aup.add_argument("run", type=str)
    aup.add_argument("--confirm", action="store_true")

    pk_p = subparsers.add_parser("pack", help="Grounding pack for an agent task; record outcomes to measure the benefit")
    pk_sub = pk_p.add_subparsers(dest="pack_command", required=True)
    pkb = pk_sub.add_parser("build", help="Build the pack (markdown) for a task")
    pkb.add_argument("task", nargs="?", default="")
    pkb.add_argument("--task-file", type=str)
    pkb.add_argument("--module", type=str, default="")
    pkb.add_argument("--file", action="append", default=[], dest="files")
    pkb.add_argument("--tag", action="append", default=[], dest="tags")
    pkb.add_argument("--force", action="store_true")
    pkb.add_argument("--out", type=str, help="Write markdown here (default: stdout)")
    pkb.add_argument("--json", action="store_true", help="Print the pack as JSON")
    pkr = pk_sub.add_parser("record", help="Record an outcome of a task run")
    pkr.add_argument("--pack-id", required=True)
    pkr.add_argument("--task-id", required=True)
    pkr.add_argument("--arm", required=True, choices=["with_pack", "without_pack"])
    pkr.add_argument("--first-pass", required=True, choices=["yes", "no"])
    pkr.add_argument("--fixes", type=int, default=0)
    pkr.add_argument("--notes", default="")
    pk_sub.add_parser("report", help="First-pass rate with and without a pack")

    dos_p = subparsers.add_parser("dossier", help="Repository dossier: prepare evidence for the agent, check its result")
    dos_sub = dos_p.add_subparsers(dest="dossier_command", required=True)
    prep_p = dos_sub.add_parser("prepare", help="Pin HEAD, fetch the files worth reading, write dossier_input.json and WORKORDER.md")
    prep_p.add_argument("repo", type=str, help="owner/name or GitHub URL")
    prep_p.add_argument("--out", type=str, help="Output folder (default: next to health.db)")
    prep_p.add_argument("--focus", type=str, default="", help="Comma-separated path words of the area the task is about (e.g. dag,walk,plan,lock)")
    prep_p.add_argument("--claim", action="append", default=[], help="A statement to verify against code (repeatable); replaces README claims")
    check_p = dos_sub.add_parser("check", help="Verify the agent's dossier against what was actually read")
    check_p.add_argument("dossier", type=str, help="Dossier JSON (or markdown with a ```json block)")
    check_p.add_argument("--input", type=str, required=True, help="dossier_input.json from prepare")

    args = parser.parse_args()

    if args.command == "audit":
        import re as _re
        from pathlib import Path
        from services.dnk_git_research.src import audit_flow as af
        from services.dnk_git_research.src import dossier as dos
        from services.dnk_git_research.src import ledger as lg
        from services.dnk_git_research.src.health_store import HealthStore
        base = HealthStore().path.parent
        cmd = args.audit_command
        if cmd == "start":
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
            local = None
            if not args.no_clone:
                from services.dnk_git_research.src import repo_map as rmap
                from services.dnk_git_research.src.repo_signals import github_full_name
                nm = github_full_name(args.repo if "github.com" in args.repo else f"https://github.com/{args.repo}")
                try:
                    local = Path(args.clone_dir) if args.clone_dir else rmap.clone(nm, base / "_clones" / nm.replace("/", "__"), token)
                except Exception as e:  # noqa: BLE001  fall back to the API sampling, loudly
                    print(f"⚠ клонування не вдалося ({e}); використовую GitHub API: буде прочитано лише кілька файлів", file=sys.stderr)
            inp = dos.collect(args.repo, None, token, None, focus=[f for f in args.focus.split(",") if f], claims_in=args.claim,
                              local=local, task=args.task)
            st = af.start(base, inp, args.task, args.module, budget=args.budget)
            print(json.dumps({"run": st.run_id, "repo": st.repo, "sha": st.sha[:7], "license": inp.license.get("spdx"), "action": inp.license.get("action"),
                              "files_read": len(inp.files), "tree_files": inp.tree_files, "scanned_symbols": inp.scan.get("symbols"),
                              "scan_counts": inp.scan.get("counts"), "assets": len(inp.assets), "next": af.next_step(st),
                              "hint": f"python services/dnk_git_research/cli.py audit next {st.run_id}"}, ensure_ascii=False, indent=1))
        elif cmd == "next":
            st, inp = af.load(base, args.run)
            step = af.next_step(st)
            if not step:
                nh = [s for s, x in st.steps.items() if x.status == "needs_human"]
                print("Усі кроки виконано. Далі: audit finish " + st.run_id if not nh else f"Потрібна людина: {', '.join(nh)}. Або audit skip {st.run_id} <крок> --reason …")
            else:
                print(af.render_prompt(st, inp, step, repair=args.repair))
        elif cmd == "submit":
            text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
            r = af.submit(base, args.run, args.step, text)
            if r["accepted"]:
                print(f"✅ крок {args.step} прийнято. Далі: " + (f"audit next {args.run}" if r["next"] else f"audit finish {args.run}"))
            else:
                print(f"❌ крок {args.step} відхилено (залишилось спроб: {r.get('left', 0)}):\n- " + "\n- ".join(r["issues"][:12]))
                print(f"Виправ і подай знову; промпт із помилками: audit next {args.run} --repair" if r.get("status") != "needs_human" else
                      f"Спроби вичерпано. Людина вирішує, або: audit skip {args.run} {args.step} --reason …")
            sys.exit(0 if r["accepted"] else 1)
        elif cmd == "skip":
            af.skip(base, args.run, args.step, args.reason)
            print(f"⚠️ крок {args.step} пропущено: {args.reason}")
        elif cmd == "status":
            st, inp = af.load(base, args.run)
            print(json.dumps({"run": st.run_id, "repo": st.repo, "next": af.next_step(st), "finished": st.finished,
                              "steps": {k: {"status": v.status, "attempts": v.attempts, "issues": v.issues[:3]} for k, v in st.steps.items()}}, ensure_ascii=False, indent=1))
        elif cmd == "finish":
            r = af.finish(base, args.run)
            print(json.dumps(r, ensure_ascii=False, indent=1))
            sys.exit(0 if r.get("done") else 1)
        else:
            d = af.run_dir(base, args.run)
            draft = d / "ledger_draft.yaml"
            if not draft.exists():
                print("❌ спершу audit finish")
                sys.exit(1)
            import yaml
            data = yaml.safe_load(draft.read_text(encoding="utf-8"))
            led = lg.load_ledger()
            trial = lg.Ledger(**led.model_dump())
            trial.donors = [x for x in trial.donors if x.id.lower() != data["id"]] + [lg.Donor.model_validate(data)]
            issues = [i for i in lg.check_ledger(trial) if data["id"] in i]
            if issues:
                print("❌ чернетка не проходить перевірку реєстру:\n- " + "\n- ".join(issues))
                sys.exit(1)
            target = lg.default_ledger_dir() / "donors" / (data["id"].replace("/", "__") + ".yaml")
            if not args.confirm:
                print(f"Сухий запуск: {'файл ВЖЕ ІСНУЄ, онови вручну' if target.exists() else 'буде створено'} {target}. Додай --confirm.")
            elif target.exists():
                print(f"❌ {target.name} уже існує: онови вручну, щоб не втратити статуси")
                sys.exit(1)
            else:
                target.write_text(draft.read_text(encoding="utf-8"), encoding="utf-8")
                print(f"✅ записано {target}")
        return

    if args.command == "pack":
        from pathlib import Path
        from services.dnk_git_research.src import grounding as gr
        from services.dnk_git_research.src import ledger as lg
        if args.pack_command == "build":
            text = Path(args.task_file).read_text(encoding="utf-8") if args.task_file else args.task
            if not text.strip():
                print("❌ Provide a task description or --task-file.")
                sys.exit(2)
            pk = gr.build_pack(text, lg.load_ledger(), args.module, args.files, args.tags, args.force)
            if args.out:
                Path(args.out).write_text(pk.markdown, encoding="utf-8")
                print(json.dumps({"pack_id": pk.pack_id, "mode": pk.mode, "module": pk.module, "grounded": pk.grounded,
                                  "mechanics": len(pk.mechanics), "out": args.out}, ensure_ascii=False))
            else:
                print(pk.model_dump_json(indent=1) if args.json else pk.markdown)
        elif args.pack_command == "record":
            print(json.dumps(gr.record_outcome(args.pack_id, args.task_id, args.arm, args.first_pass == "yes", args.fixes, args.notes), ensure_ascii=False))
        else:
            print(json.dumps(gr.report(), indent=2, ensure_ascii=False))
        return

    if args.command == "ledger":
        import re as _re
        from pathlib import Path
        from services.dnk_git_research.src import ledger as lg
        led = lg.load_ledger()
        if args.ledger_command == "check":
            issues = lg.check_ledger(led)
            print("✅ реєстр узгоджений" if not issues else "❌ знайдено проблеми:\n- " + "\n- ".join(issues))
            sys.exit(1 if issues else 0)
        if args.ledger_command == "stats":
            print(json.dumps(lg.stats(led), indent=2, ensure_ascii=False))
        elif args.ledger_command == "context":
            print(lg.render_context(led, args.module))
        else:
            mech, donor = list(args.text), args.donor
            if args.dossier:
                text = Path(args.dossier).read_text(encoding="utf-8")
                m = _re.search(r"```json\n(.*?)\n```", text, _re.S)
                data = json.loads(m.group(1) if m else text)
                mech += lg.mechanics_from_dossier(data)
                donor = donor or data.get("repo", "")
            rep = lg.fit(led, mech, donor)
            print(json.dumps(rep.model_dump(), indent=2, ensure_ascii=False))
        return

    if args.command == "dossier":
        import re as _re
        from pathlib import Path
        from services.dnk_git_research.src import dossier as dos
        from services.dnk_git_research.src.catalog_reader import default_catalog_path
        from services.dnk_git_research.src.health_store import HealthStore

        if args.dossier_command == "prepare":
            from services.dnk_git_research.src import curation
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
            store = HealthStore()
            rid = args.repo.replace("https://github.com/", "").strip("/").lower()
            row = next((r for r in curation.load_rows(default_catalog_path()) if r["id"].lower() == rid), None)
            plan_file = store.path.with_name("plan.json")
            cur = None
            if plan_file.exists():
                plan = curation.Plan.model_validate_json(plan_file.read_text(encoding="utf-8"))
                a = next((x for x in plan.items if x.repo_id.lower() == rid), None)
                cur = a.model_dump(mode="json") if a else None
            inp = dos.collect(args.repo, row, token, cur, focus=[f for f in args.focus.split(",") if f], claims_in=args.claim)
            out = Path(args.out) if args.out else store.path.parent / "dossiers" / inp.repo.replace("/", "__")
            out.mkdir(parents=True, exist_ok=True)
            (out / "dossier_input.json").write_text(inp.model_dump_json(indent=1), encoding="utf-8")
            prompt = (Path(__file__).parent / "docs" / "DOSSIER_PROMPT.md").read_text(encoding="utf-8")
            (out / "WORKORDER.md").write_text(dos.render_workorder(inp, prompt), encoding="utf-8")
            print(json.dumps({"repo": inp.repo, "sha": inp.sha[:7], "files_read": len(inp.files), "tree_files": inp.tree_files,
                              "license": inp.license.get("spdx"), "action": inp.license.get("action"), "niches": inp.niches,
                              "risk_hints": len(inp.risk_hints), "folder": str(out)}, indent=2, ensure_ascii=False))
        else:
            text = Path(args.dossier).read_text(encoding="utf-8")
            m = _re.search(r"```json\n(.*?)\n```", text, _re.S)
            data = json.loads(m.group(1) if m else text)
            inp = dos.DossierInput.model_validate_json(Path(args.input).read_text(encoding="utf-8"))
            issues = dos.check_dossier(data, inp)
            print("✅ досьє узгоджене з прочитаним" if not issues else "❌ знайдено проблеми:\n- " + "\n- ".join(issues))
            sys.exit(1 if issues else 0)
        return

    if args.command == "curate":
        from pathlib import Path
        from services.dnk_git_research.src import curation
        from services.dnk_git_research.src.catalog_reader import default_catalog_path
        from services.dnk_git_research.src.health_store import HealthStore
        from services.dnk_git_research.src.repo_signals import scan

        catalog, store = default_catalog_path(), HealthStore()
        if args.curate_command == "scan":
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
            result = scan(curation.load_rows(catalog), store, token, args.max_requests, refresh_days=args.refresh_days)
            result["authenticated"] = bool(token)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.curate_command == "deepscan":
            from services.dnk_git_research.src import content_scan
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
            rows, sigs = curation.load_rows(catalog), store.all_signals()
            first = curation.build_plan(rows, sigs, content=store.all_content())
            cands = content_scan.candidates(rows, sigs, {a.repo_id.lower(): a for a in first.items})
            result = content_scan.deep_scan(cands, store, token, args.max_requests, refresh_days=args.refresh_days)
            result["candidates"] = len(cands)
            result["authenticated"] = bool(token)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.curate_command == "plan":
            plan = curation.build_plan(curation.load_rows(catalog), store.all_signals(), content=store.all_content())
            out = Path(args.out) if args.out else store.path.with_name("plan.json")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
            print(json.dumps({"total": plan.total, "counts": plan.counts, "plan_file": str(out)}, indent=2, ensure_ascii=False))
            for tier in ("REMOVE", "QUARANTINE", "WATCH"):
                rows = [a for a in plan.items if a.tier.value == tier][: args.show]
                if rows:
                    print(f"\n== {tier} (перші {len(rows)})")
                    for a in rows:
                        why = a.reasons[0] if a.reasons else ", ".join(a.flags)
                        print(f"  {a.repo_id}  score={a.score}  {why}")
        elif args.curate_command == "apply":
            plan = curation.Plan.model_validate_json(Path(args.plan).read_text(encoding="utf-8"))
            tiers = [curation.Tier(t.strip().upper()) for t in args.tiers.split(",") if t.strip()]
            print(json.dumps(curation.apply_plan(plan, catalog, store, tiers, confirm=args.confirm),
                             indent=2, ensure_ascii=False))
        elif args.curate_command == "restore":
            ok = curation.restore(args.repo_id, catalog, store)
            print("✅ restored" if ok else f"❌ {args.repo_id} is not in quarantine")
            sys.exit(0 if ok else 1)
        elif args.curate_command == "status":
            rows = curation.load_rows(catalog)
            signals = store.all_signals()
            print(json.dumps({
                "catalog_rows": len(rows),
                "with_signals": sum(1 for r in rows if r["id"].lower() in signals),
                "quarantined": len(store.quarantine_list()),
                "health_db": str(store.path),
            }, indent=2, ensure_ascii=False))
        return

    if args.command == "brief":
        from pathlib import Path
        from services.dnk_git_research.src.reuse_brief import ReuseBriefService, format_brief_text

        task_text = Path(args.task_file).read_text(encoding="utf-8") if args.task_file else args.task
        if not task_text.strip():
            print("❌ Provide a task description or --task-file.")
            sys.exit(2)
        brief = ReuseBriefService(live=not args.no_live).build(
            task_text,
            target_files=args.files,
            tags=args.tags,
            force=args.force,
            refresh=args.refresh,
            verify_licenses=args.verify_licenses,
        )
        if args.text:
            print(format_brief_text(brief))
        else:
            print(brief.model_dump_json(indent=2))
        return

    engine = GitResearchEngine()

    if args.command == "search":
        results = engine.search_repositories(args.query, limit=args.limit)
        print(json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False))

    elif args.command == "assimilate":
        repos = engine.search_repositories(args.repo, limit=1)
        if not repos:
            print(f"❌ Repo {args.repo} not found.")
            sys.exit(1)
        output = engine.assimilate_into_dnk(repos[0], custom_target=args.target)
        print(f"✅ Spec generated: {output.spec_path}")


if __name__ == "__main__":
    main()
