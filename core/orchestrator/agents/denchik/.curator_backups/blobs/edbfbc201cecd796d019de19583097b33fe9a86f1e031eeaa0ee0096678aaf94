# --- DNK-MRH-HEADER ---
# mrh_id: "skills/sota-repository-assimilation/references/creator_os_starter_and_spend_gate_media_architecture.md"
# purpose: "Architectural extraction notes and recipes from kevinbadi/creator-os-starter (Creator OS, spend guard, prompt router, media pipeline, local deployment quirks)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-10-09"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# Creator OS Starter Architecture & Spend-Gate Media Extraction

## 1. Fast Repository Inspection via GitHub Trees API
When remote MCP servers time out or face transport dropouts, execute high-speed full-tree introspection in one shot using GitHub's recursive Git tree API:
```bash
gh api repos/:owner/:repo/git/trees/main?recursive=1 | jq -r '.tree[].path'
```
Extract targeted critical files (configs, hooks, schemas, gates) via base64 decoding in Python without pulling bulky git history:
```python
import subprocess, json, base64

def get_file(repo, path):
    out = subprocess.check_output(['gh', 'api', f'repos/{repo}/contents/{path}'])
    return base64.b64decode(json.loads(out)['content']).decode('utf-8', errors='ignore')
```

## 2. Zero-Token Prompt Router Hook (Jev Architecture)
Intercept user prompts before LLM invocation (e.g. in CLI or pre-tool hooks):
- **Execution window**: ~200ms latency budget.
- **Classification target**: 
  - `lane`: `tool` | `build` | `produce` | `assess` | `conversation`
  - `skill`: Target skill ID or specialized swarm worker
  - `risk`: `read_only` | `local_files` | `publishes` | `destructive`
  - `confidence`: When confidence >= 0.85 and intent is a direct query/command, route directly to system or domain engine without consuming main reasoning model tokens.

## 3. Generative SpendGuard (Fal Gate Pattern)
Block accidental runaway billing when autonomous agents trigger image/video/audio generation APIs:
```javascript
// Strict pre-execution gate before calling costly generative endpoints
const ALLOWED_RUNWAYS = ['flux-pro', 'recraft-v3'];
export function assertSpendAuthorized(model, userConsent, currentBudgetUsd) {
  if (currentBudgetUsd <= 0) {
    throw new Error('SPENDGUARD_EXHAUSTED: Budget limit reached.');
  }
  if (!ALLOWED_RUNWAYS.includes(model) && !userConsent) {
    throw new Error(`SPENDGUARD_INTERCEPT: Model ${model} requires explicit approval.`);
  }
}
```

## 4. 55/45 Split Animated Media Composition Pattern
For high-retention vertical short-form video generation:
- **Top 55%**: Talking head / Primary avatar (video loop or HeyGen stream).
- **Bottom 45%**: Visual proof / Hyperframes kinetic canvas (code snippets, charts, dynamic graphics, motion stickers).
- **Audio Synchronization**: Mark beat timestamps via audio amplitude spikes and align bottom layer frame transitions directly to phonemes/beats.

## 5. SSOT Content Registry Pattern
Unify scheduled cron jobs and dashboard timeline displays into a single declarative array (`ContentJob`):
- Avoid separate cron schedules and UI display metadata.
- Track DST timezone offset directly against source target platforms (e.g. `America/New_York` publication slots).

## 6. Local Deployment & Runtime Quirks (Full Stack Setup)
When deploying `creator-os-starter` or similar Next.js 16 + Postgres + Python sidecar stacks locally:

### A. Ambient Shell `DATABASE_URL` vs Node `--env-file`
Node.js `--env-file=.env.local` does **not** override existing environment variables in `process.env`. If the parent terminal exports `DATABASE_URL`, Next.js and `npm run db:setup` connect to the parent URL rather than `.env.local`. Always verify or unset `DATABASE_URL` before running migration/seed scripts.

### B. Postgres Local SSL Connection Refusal
`src/lib/insforge/db.ts` hardcodes `ssl: { rejectUnauthorized: false }`. On local unencrypted PostgreSQL (Docker or Homebrew), connections fail with `The server does not support SSL connections`.
**Remedy**:
```ts
const isLocal = /localhost|127\.0\.0\.1/i.test(dbUrl) || process.env.PGSSLMODE === 'disable';
const pool = new Pool({
  connectionString: dbUrl,
  ssl: isLocal ? false : { rejectUnauthorized: false },
});
```

### C. Password URL Encoding in Database Connection String
Characters such as `@` or `:` in the database password corrupt URL segment parsing. URL-encode components before assembling `DATABASE_URL`.

### D. Single-User Session Cookie Derivation
Session tokens are derived deterministically:
```ts
// sha256("${APP_PASSWORD}::${APP_AUTH_SECRET}")
const token = crypto.createHash('sha256').update(`${pw}::${secret}`).digest('hex');
// Pass as cookie: mos_session=<token>
```

### E. Laya Decision Brain Sidecar (:8000)
Python 3.12 service serving `convaiinnovations/laya/typed-decisions` (~268MB weights on Hugging Face).
Requires `uv venv --python 3.12 .venv && uv pip install laya fastapi "uvicorn>=0.30"`. Runs with `LAYA_DEVICE=cpu` on `http://127.0.0.1:8000` exposing `GET /health` and `POST /evaluate`.
