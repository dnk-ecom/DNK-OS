---
name: orbit
description: Shared memory and coordination layer for AI agents. Use the orbit_* MCP tools to inherit context, file durable results, run standing assignments and report status.
version: 1.0.0
---

# Orbit Skill

You have access to the **Orbit** MCP server — a shared memory & coordination
layer used by every other AI agent on this workspace (Claude, ChatGPT/Codex,
Gemini, Kimi, Manus, Cursor, …). Orbit is how you inherit context from past
sessions, file durable knowledge, broadcast progress, and pick up standing
assignments ("orbits") created by the operator.

This skill is your operating manual. Re-read the relevant section before
calling any `orbit_*` tool.

---

## 1. Identity — declare yourself honestly, every call

Every tool call requires `agent.{id, name, provider, surface, model_family}`.

- `id` MUST be stable per (provider, surface, project). Do NOT reuse another
  agent's id. Examples: `claude-code`, `claude-cowork`, `chatgpt-codex`,
  `chatgpt-desktop`, `gemini-code`, `cursor`, `kimi-code`, `manus`.
- `name` — short display name ("Claude Code", "Codex CLI").
- `provider` — `anthropic` | `openai` | `google` | `moonshot` | `manus`.
- `surface` — `cowork` | `claude-code` | `codex` | `chatgpt-web` |
  `gemini` | `kimi` | `manus` | `cursor` (where you're running — drives
  the operator's dashboard logo).
- `model_family` — `claude-sonnet-4`, `gpt-5`, `gemini-2.5`, …

If unsure, ASK the operator. Do not impersonate.

---

## 2. Session lifecycle — every session, in order

1. **`orbit_heartbeat`** FIRST with `status: "running"` and a one-line
   `context`. The response carries everything you need to act correctly:
   - `active_decisions` — directives addressed to YOU specifically. Read and
     obey BEFORE doing anything else.
   - `active_knowledge` — ratified ground truth for this workspace.
   - `pending_messages` — operator instructions left for you. Act on them
     before answering the user.
   - `known_projects` — canonical project slugs already in use. Pick the
     EXACT matching slug for `agent.project`; never invent a variant
     (`acme-site` vs `acme_site` vs `Acme Site`). Only create a new slug
     if none fit, and confirm with the operator.
   - `project_catalog` — `{ slug, name, description }` for each project.
     Use the `name` + `description` to route a new task into the RIGHT
     project by intent (e.g. file ad copy under the project whose description
     mentions ads, not a generic one). Reuse the catalog `slug` verbatim.

2. **`orbit_search`** for prior context whenever `active_knowledge` isn't
   enough — other agents (ChatGPT, Gemini, Kimi, Manus, earlier Claude
   sessions) may have produced relevant work. Call `orbit_context` mid-run
   if the user gives you a new task and you need the freshest directive list.

3. **Do the work.** File milestones with `orbit_event` so the operator's
   activity feed stays alive. When you commit to an action, use
   `orbit_decide` (see §4b).

4. **`orbit_result`** for every deliverable. `content` must be the FULL
   writeup, not a summary — the Vault renders this field verbatim. Pick the
   correct `bucket` and `trust_level` (see §4).

   **RUN SUMMARY — required on EVERY `orbit_result` (logs included).** Always
   send `run_summary`: 2–6 SHORT plain sentences (under ~700 chars) that flag
   run stats, what you actually did, and any action items or blockers. It is
   NOT a compressed copy of the report — never paste IDs, handles, URLs, tokens
   or draft/message copy into it (those live in `content`). Prose, no headings
   or tables, standalone (never "see below"). The example below is an
   ILLUSTRATION OF SHAPE ONLY — its names and facts are invented, describe no
   real account, and must never be copied or assumed to be true here; report
   only what YOU observed on THIS run. Example shape: "5 LinkedIn DMs queued.
   <person A>: pain point noted, introducing us. <person B>: peer discussion on
   the topic. Blocked by hourly send cap, retry in ~50 min." This is what gets
   pushed to Telegram and shown at the top of the card. `summary` stays the
   single-sentence one-liner.



   **HANDOFF RULE — non-negotiable, run it before EVERY `orbit_result`:**
   ask yourself out loud *"does this turn end with something only the operator
   can do — approve, decide, act, or unblock?"* If yes, you MUST file
   `kind: "needs_you"` with the matching `needs` verb
   (`approve`/`decide`/`do`/`fix`) and state the ask in the first line of
   `content`. Never bury a blocker, an open question, or a draft awaiting
   sign-off inside a plain `output` — an `output` means the work is DONE and
   nothing is pending on a human. `kind` has no default; omitting it is an
   error. The server re-reads your body and upgrades obvious handoffs to
   `needs_you` anyway, so mis-filing only makes your reasoning look wrong.

   **REVIEW RULE — the fuzzy middle, written down so it isn't left to your
   framing:** if a result requires the operator to review, approve, or sign off
   before it is final, file `kind: "needs_you"` with `needs: "approve"` —
   never `output`. *"Done but unreviewed" is not `output`.* `output` means
   shipped and final; finished-but-waiting-for-eyes is `needs_you`. If you are
   torn between the two, pick `needs_you`.



5. **`orbit_heartbeat`** with `status: "idle"` and a `summary` describing
   what shipped. Silent endings count as failed runs.

---

## 3. Tool cheat sheet

- `orbit_search` — semantic search across the workspace's full memory.
- `orbit_heartbeat` — start/end every session. Returns `active_decisions`,
  `active_knowledge`, `pending_messages`, `known_projects`.
- `orbit_context` — re-fetch the freshest directive/knowledge list mid-run
  when the user pivots to a new task.
- `orbit_get_instructions` — load your current standing prompt. Call this
  (a) when you've been assigned to an Orbit (pass the orbit `slug` + your
  identity — auto-links you as the orbit's owner), AND (b) BEFORE every
  `orbit_update_self` call so you replace the real current prompt, not a guess.
- `orbit_update_self` — REPLACE your standing system prompt with a full
  revised version. Use for ANY new behavior, tone, format rule, source to
  add/drop, schedule tweak, persona change, or "from now on…" instruction
  from the operator. Always call `orbit_get_instructions` first, then
  submit the FULL new prompt text plus a one-line `reason` + `summary`.
  Do NOT file behavioral changes as `orbit_decide` — decisions don't change
  how you run next time; the prompt does.
- `orbit_decide` — record commitments/conclusions about the WORK.
  `kind: "directive"` for a new commitment; `kind: "conclusion"` with
  `refs=[decision_id]` to close an existing directive. Default scope is
  YOUR agent only.
- `orbit_declare` — SCHEDULED AGENTS ONLY. Call once on first run to
  register an Orbit (pass `slug`, `name`, `cadence`, `goal`, `department`).
  Idempotent — safe to call every run. Skips the manual "Import existing
  agent" flow. **Use this for BOTH cases:** (a) you ARE the scheduled agent —
  declare yourself; (b) you just CREATED or SET UP a new scheduled agent/
  automation for the operator (cron job, Claude scheduled task, Codex
  automation, Hermes run, etc.) — declare it on its behalf so it appears
  on the dashboard immediately, using the new agent's identity (not yours)
  in `agent.*`. **HARD PRECONDITION — schedule MUST exist BEFORE you
  declare.** Do not call `orbit_declare` from a one-off/manual run that has
  no recurrence wired up yet. Declaring without a live schedule creates a
  ghost orbit on the dashboard that will never run again. Order is always:
  (1) actually create the recurrence in your runtime (cron expression set,
  Claude scheduled task saved, Codex automation enabled, Hermes run
  activated, scheduler row inserted, etc.) and VERIFY it's enabled, THEN
  (2) call `orbit_declare`, THEN (3) call `orbit_ready` with the exact
  schedule string you just wired up. If your runtime cannot self-schedule,
  do NOT declare — instead tell the operator what trigger to set up and
  declare only after they confirm it's live (or they import you manually).
  **Department is required** so the orbit slots into the right team on the
  org chart: on your FIRST call you may omit it — the response returns
  `available_departments` for this workspace; pick the single best fit by
  name + tagline, then call `orbit_declare` AGAIN with `department=<id>`.
  **Immediately follow with `orbit_ready`** in the same run (pass `ready`,
  `schedule`, `missing`, `summary`) — without it the orbit stays in
  `connected` and never flips to `live` on the dashboard.
  **PROMPT HANDOVER (do this on first declare):** pass `prompt: <your full
  current scheduled-task instruction body, verbatim>`. Orbit stores it as
  the orbit's source of truth and returns `activation_prompt` in the
  response. **You must then replace your own scheduled-task body with that
  `activation_prompt` wrapper** (keep your schedule, tools, model — only
  the instruction text changes). After this, the prompt lives in Orbit:
  every future run fetches it via `orbit_heartbeat` / `orbit_get_instructions`,
  and operator edits go live on the next run with no redeploy. If you
  cannot rewrite your own scheduled body from this run, tell the operator
  exactly that — paste the `activation_prompt` into your reply and ask
  them to swap it into the scheduled task themselves.

**HOW TO ACTUALLY CREATE THE RECURRENCE (per AI client).** Orbit has no
scheduler of its own — the recurrence always lives in YOUR runtime. Use the
right mechanism for the client you are running in, and never invent a command:
  • **Claude Code** — recurring work is a **routine**. Use `/routine`
    (routines are the scheduling primitive). There is **no `/schedule`
    command** — if you type `/schedule` it will fail. Create the routine
    with the cadence, verify it is listed/enabled, then declare.
  • **Claude desktop/web** — "Scheduled tasks" in the conversation menu.
  • **Codex / Cowork** — Automations (cloud task with a cron cadence).
  • **Cursor** — Background/scheduled agents where available.
  • **Anything else (cron, n8n, Zapier, GitHub Actions, a server job)** —
    whatever recurrence that runtime supports.
If your runtime has no scheduling primitive at all, say so plainly and ask
the operator to wire the trigger; do not claim a schedule exists.



- `orbit_ready` — first call of an orbit assignment. Report `ready`,
  `missing` (tools/MCPs/permissions you need), and your `schedule`.
- `orbit_event` — short milestones for the operator's feed.
- `orbit_result` — deliverables. Full text in `content`. Attach files by
  passing their `file_ids`.
- `orbit_file_put_text` — separate text artifacts (CSV, raw JSON, email drafts).
  NOT for report bodies — those go in `orbit_result.content`.
- `orbit_file_init` + `orbit_file_commit` — true binaries (PDF, PPTX, images,
  zip). Pass a stable `ref` and REUSE it to version a file in place.
- `orbit_table_write` — **THE TRACKER**. The backend store for any ongoing
  structured list you'd otherwise dump to a local CSV/sheet: people contacted,
  prospect pipelines, outreach status, scraped rows, link queues, run-log
  ledgers, anything you need to keep adding to across runs. **Do NOT write
  CSVs to local disk for tracking purposes** — local files don't survive,
  the operator can't see them, and the next run can't read them back. Use
  `orbit_table_write` with a stable `table_ref` and `mode='append'` (or
  `'upsert'` with `key_columns` when rows evolve) so the table lives in the
  Vault, versions in place, and every future run can read it back. CSV
  export via `orbit_file_put_text` is only for ONE-SHOT deliverables the
  operator will download and send elsewhere — never for the tracking source
  of truth.
  **YOU ALREADY KNOW YOUR TRACKERS.** Every `orbit_heartbeat` and
  `orbit_get_instructions` response includes `your_trackers` — the list of
  `table_ref`s your orbit already owns, with their titles, columns, row
  counts, and result_ids. Treat this as PERSISTENT SELF-KNOWLEDGE: these
  are YOUR sheets. Before picking a `table_ref`, scan that list. If any
  entry is the right home for your rows, REUSE its `table_ref` exactly —
  read current state with `orbit_table_get(table_ref)`, then write with
  `mode='append'` or `'upsert'` under the SAME ref so the sheet versions
  in place. Only invent a new `table_ref` when nothing in `your_trackers`
  fits. Do NOT call `orbit_table_list` to rediscover what's already pushed
  to you in every heartbeat — that list IS your discovery. Inventing
  parallel sheets (`prospects-2`, `outreach-new`) when an existing tracker
  covers the topic is a failure mode.
  **UPDATES HAPPEN IN PLACE.** Writing to the same `table_ref` does NOT
  create a new output card. The original sheet's row, title, and inbox card
  are mutated in place; the operator sees ONE persistent sheet that resurfaces
  at the top of the feed with a small "update log" (each write is one row in
  that log). Never publish a separate text/markdown "tracker update" result
  to summarise what changed — write the rows, the log entry is recorded
  automatically, and the operator opens the same sheet to see the new state.
- `orbit_table_list` — workspace-wide tracker search, for cross-orbit
  reuse only. Your own orbit's trackers already arrive in `your_trackers`
  on every heartbeat — don't use this tool to rediscover them.
- `orbit_table_get` — read all rows + columns of a tracker by `table_ref`.
- `orbit_reinforce` — when a prior fact is still true, instead of re-writing it.
- `orbit_message` — reply to pending operator messages.
- `orbit_project_create` / `orbit_project_use` — create a project, or bind
  the current session to an existing one. Prefer `orbit_project_use` with a
  slug from `project_catalog`; only create when nothing fits.
- `orbit_chain` — declare the agents you DEPEND ON (they run before you) so
  Orbit links the automation chain. Use exact agent ids or names.
- `orbit_toolbox` — **THE ONE DOOR TO EVERY EXTERNAL CAPABILITY** (see §3b).
- `orbit_list_recent`, `orbit_list_agents`, `orbit_get_result`,
  `orbit_file_get` — read-side companions to the above.

---

## 3b. `orbit_toolbox` — external tools live behind ONE tool

There are no longer separate `apify`, `apollo`, `image_generate`,
`instantly`, `posteahora`, `predictleads`, `linkedin`, `whatsapp`,
`gmail_mailbox`, `calendar`, … tools. Everything external is reached through
`orbit_toolbox`:

- `{ action: "list" }` — ALWAYS your first call before claiming a capability.
  Returns what is LIVE for this workspace right now (full descriptions + JSON
  Schemas) and what is `not_connected` with a `how_to_connect` line.
- `{ action: "describe", tool: "<name>" }` — one tool's schema and full docs.
- `{ action: "call", tool: "<name>", arguments: { … } }` — run it.

Rules:
- **Never say a capability is missing without calling `list` first.**
- **Never promise an action on a tool `list` reports as not connected.**
  Surface the `how_to_connect` line to the operator instead.
- The operator's own accounts (LinkedIn, WhatsApp, Instagram, Messenger,
  Telegram, X DMs, Gmail, Outlook, IMAP) and their Calendar are connected in
  Settings → Integrations → Your accounts. Messaging/posting on those runs as
  the operator, with daily caps — respect the limits the tool returns.
- Image generation and Calendar are provisioned by Orbit; per-account social
  and mailbox tools are seat-based. If a call fails on plan/seat grounds,
  report it plainly rather than retrying.
- Operators can also feed files, data, and documents into Orbit directly from
  their AI client once the MCP is connected — ask for that instead of guessing.

---

## 4. Trust levels, buckets & kind

`trust_level` (how confident you are):
- `exploratory` (Notes) — DEFAULT. Scratch, intermediate, unverified.
- `conclusion` (Reports) — a finished, vetted deliverable.
- `authoritative` (Knowledge) — ratified ground truth. Mention in your reply
  to the operator when you file as authoritative.

`bucket` (how it's filed):
- `raw` — DEFAULT. Working stream the operator can browse.
- `output` — finished report intended as the operator's takeaway.
- `wiki` — durable consolidated knowledge about the project.

### The Knowledge bar (read before ever filing authoritative)

Knowledge is deliberately tiny: every agent in every department reads it on
start, so one junk entry poisons the whole company. Most good work is a Report.

KNOWLEDGE TEST — all four must be true, or it is NOT Knowledge:
1. DURABLE — still true in 3 months. No run reports, no dated status, no counts from today.
2. REUSABLE — another agent, on another task, would act differently for having read it.
3. CROSS-CUTTING — it holds beyond one project's work, not one project. One-project detail is a Report.
4. RATIFIED — it is the decided truth, not your finding or your opinion. Findings are Reports.
SCOPE (optional) — by default Knowledge is authoritative and company-wide: every agent in every department reads it on start. Only pass `departments` (1-4 slugs, e.g. ["sales"]) when the canon genuinely binds just those teams. Unscoped = company-wide canon.
If any answer is "no" → file kind/trust as a Report (trust_level="conclusion"). Reports are cheap; polluted Knowledge is expensive.

KNOWLEDGE FORMAT — markdown, max 6000 characters (aim for under 2500), no preamble:
**Canon:** one sentence stating the rule/truth.
**Applies to:** "Company-wide" (default) or the named departments this binds (must match `departments`).
**Details:** 3-8 terse bullets. Facts and rules only.
**Source:** links or result ids that ratify it. (optional)
Always pass `wiki_slug` (e.g. "pricing", "icp/enterprise", "brand-voice") so revisions replace the entry instead of stacking duplicates. Never include dates, run numbers, "this week", or narrative.

`departments` is OPTIONAL. Omit it for normal authoritative, company-wide Knowledge — every agent reads it on start. Pass 1-4 department slugs (e.g. ["sales","marketing"]) only when the canon genuinely binds just those teams; scoped entries are surfaced to those departments' agents and tagged in the Vault.

The server enforces this — an authoritative write that is oversized, time-bound
or shaped like a run report is filed as a Report automatically.


`kind` (REQUIRED on `orbit_result`, no default) — decides whether a human
gets pulled in:
- `run` — routine run log; stays in the Vault, no human attention needed.
- `output` — finished, shipped deliverable. Lands in the Inbox as a takeaway.
- `needs_you` — a human must act. Pair with `needs`: `approve`, `decide`,
  `do`, or `fix`. Anything unreviewed, blocked, or awaiting sign-off is
  `needs_you` — not `output`.

`outcomes` (REQUIRED on `orbit_result`) — YOU declare your own numbers.
The operator never fills these in. Pass an array of `{ label, count }` for
what this run concretely produced, e.g.
`[{ "label": "leads added", "count": 12 }, { "label": "DMs sent", "count": 4 }]`.
Rules:
- Label the BUSINESS OBJECTIVE you moved, not the mechanics of how you moved
  it. Ask: "would an operator put this on a weekly scoreboard?"
  Good: `connections sent`, `DMs sent`, `likes done`, `meetings booked`,
  `conversations started`, `replies received`, `blogs published`,
  `leads added`, `qualified targets identified`, `bugs fixed`.
  Bad (process noise): `org slugs swept`, `posts scraped`, `posts reviewed`,
  `pages crawled`, `rows parsed`, `API calls made`.
  If all you did was scan, reframe to the business result of the scan —
  `targets identified`, `targets qualified`, `opportunities surfaced`.
- Optional but preferred: when you can attribute a real achievement
  (`meetings booked`, `replies received`, `deals created`), declare it too —
  results beat activity.
- Reuse the EXACT same label every run so it aggregates over time.
- Declare `0` when you were blocked, found nothing, or shipped nothing. A
  zero is a real data point; an omission is not.
- Only pass `[]` when the run has no countable dimension at all.
These roll straight into the operator's Outcomes dashboard (7d / 30d totals).

Operator edits always outrank agent writes. If you find a contradiction with
prior content, file with `supersedes` + `relation_type` instead of silently
overwriting.


---

## 5. Standing assignments (Orbits)

The operator may have assigned you to a named "orbit" — a recurring job with
a fixed slug and a prebaked prompt. If you receive an activation snippet
referencing an orbit slug:

1. Call `orbit_get_instructions` with that slug + your full identity. This
   loads your system prompt AND auto-links you as the orbit's owner agent.
2. Enumerate every capability the prompt implies (web search, scraping, file
   write, email send) and cross-check against tools currently available to you.
3. The prompt states a cadence. If your runtime supports scheduling (cron,
   scheduled tasks, automations), set up the recurrence NOW. If it does not,
   say so in `orbit_ready` and tell the operator exactly how to trigger you.
4. Call `orbit_ready` with: `ready` (boolean), `missing` (exact list of
   gaps), `schedule` (what you set up OR the trigger needed), `summary`.
   This flips the orbit `connected → live` (or `blocked`) in the dashboard.
5. Only after `orbit_ready` is filed, follow the orbit prompt on every run.

### 5b. You just CREATED a scheduled agent for the operator

If, during this session, you set up a NEW recurring/scheduled agent for the
operator — a cron job, Claude scheduled task, Codex automation, Hermes run
workflow, background worker, anything that will run on its own cadence —
you MUST register it in Orbit so it shows up on the dashboard. Don't wait
for the agent's first autonomous run; declare it the moment it's wired up.

**Precondition — do NOT declare until the schedule is actually live.**
First, finish creating and enabling the recurrence (cron saved, task
toggled on, workflow activated, scheduler row inserted). Verify it will
fire on its own. Only then proceed with the steps below. A declaration
without an active schedule produces a dead orbit on the operator's
dashboard.

1. Call `orbit_declare` with the NEW agent's identity in `agent.*` (its own
   stable `id`, `name`, `provider`, `surface`, `model_family` — NOT yours),
   plus `slug`, `name`, `cadence`, and `goal` for the orbit.
2. Read `available_departments` from the response, pick the single best fit
   (e.g. a news brief → `research`, a campaign runner → `marketing`, a
   pipeline monitor → `engineering`), and call `orbit_declare` AGAIN with
   the same slug plus `department=<id>`. This places it in the right team
   on the org chart — without it the orbit lands as Unassigned.
3. Immediately call `orbit_ready` with the same agent identity: `ready`,
   `schedule` (the EXACT cron expression / trigger you configured, not a
   wish), `missing` (any gaps), and a one-line `summary`.
4. Tell the operator the orbit is now live on their dashboard.

If you cannot self-schedule from your runtime, do NOT declare yet. Tell
the operator what to wire up (or point them to the manual "Import existing
agent" flow) and declare only after the schedule is confirmed live.

Skipping this leaves the operator blind to an agent that's already running.
Declaring before scheduling leaves them with a ghost agent that never runs.




---

## 6. Rules of thumb

- One `agent.id` per (surface, project). Don't drift between sessions.
  Always set `agent.surface` to the exact runtime you're in
  (`claude-code`, `cowork`, `codex`, `chatgpt-web`, `gemini`, `kimi`,
  `manus`, `cursor`) — the operator's UI keys logos and chips off it.
- Reuse `agent.project` slugs from `known_projects`; don't invent variants.
- Search before writing. Reinforce instead of duplicating.
- Full content in `orbit_result.content` — never a one-liner pointer to a file.
- End every session with an idle heartbeat + summary. Silent = failure.
- If a contradiction appears, file with `supersedes`, don't overwrite.
- Standing behavior change from the operator → `orbit_update_self`.
  Work commitment/conclusion → `orbit_decide`. Never swap them.
- **If the operator asks you to change your behavior, update yourself, or improve your instructions, use `orbit_update_self` — never `orbit_result` or `orbit_decide`.**
- **Never update local files which don't persist across runs.** If a change
  matters, file it through Orbit (orbit_result, orbit_file_*, or a tracker)
  so it survives and is visible. Local-only tweaks are invisible to the next run.
- Wiki writes (`bucket: "wiki"`) route through operator approval — they land
  in the inbox as a proposal first, then appear in the wiki once approved.
- External capability question? Call `orbit_toolbox` `{action:"list"}` before
  answering — never guess what is or isn't connected.
- Bind work to a project with `orbit_project_use` before filing results.
- Don't invent capabilities. If something's missing, file a clear `missing`
  list in `orbit_ready` or message the operator.
