<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/obsidian_visual_shell_harness/references/runtime_lifecycle_and_troubleshooting.md"
# purpose: "Operational Runbook for Obsidian Electron Lifecycle, Memory Caches, and Diagnostics."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-26"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
-->

# 🩺 Runtime Lifecycle, Memory Caching & Troubleshooting

This runbook resolves runtime frictions encountered when pair-programming with autonomous agents while Obsidian is actively running.

---

## ⚡ The Electron In-Memory Lag Invariant

### The Failure Mode
Obsidian is built on the Electron framework. Electron boots a Node.js main process and an isolated Chromium renderer process. When community plugins or CSS snippets are injected or updated on disk (via bash, python, or git pull), **Obsidian does NOT dynamically watch or re-evaluate the `.obsidian/plugins/` directory**.

If files are copied while Obsidian is running:
- New plugins will **not** appear in Settings.
- Excalidraw files will render as raw markdown text with the banner:
  `==⚠ Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==`
- CSS rules will remain inactive.

### The Deterministic Fix
Always execute one of the following two actions after any file modification under `.obsidian/`:

1. **Headless Hot-Reload (Preferred)**:
   ```bash
   curl -s -X POST -H "Authorization: Bearer 1dc2362c168969e165c56a216137db69788189bb9dfc5e1071d3025ded21a42f" \
     http://127.0.0.1:27123/commands/app:reload/
   ```
2. **Clean Process Cycle (If app is unresponsive)**:
   ```bash
   osascript -e 'tell application "Obsidian" to quit'
   sleep 2
   open -a Obsidian
   ```

---

## 🔍 Diagnostic Triage Matrix

| Symptom | Root Cause | Exact Resolution |
| :--- | :--- | :--- |
| Excalidraw shows raw markdown and compressed JSON | Plugin files were modified on disk while Electron was running. | Execute `POST /commands/app:reload/` or press `Cmd + R` in Obsidian. |
| Plugin commands missing from command palette | Plugin not present in `.obsidian/community-plugins.json`. | Add plugin ID to `community-plugins.json` and trigger `app:reload`. |
| CSS styling (Flat Green / Polaris) not applied | Snippets omitted from `.obsidian/appearance.json`. | Add snippet names without `.css` to `"enabledCssSnippets"` array. |
| Broken links `[[whiteboards/...]]` | Excalidraw drawings moved into `docs/notes/` but link has root prefix. | Set Obsidian "New link format" to shortest path or update link to relative path. |
| "Safe Mode Enabled" blocking plugins | `community-plugins.json` is missing or empty `[]`. | Restore the 11-plugin list to `.obsidian/community-plugins.json`. |

---

## 🛡️ Repository Root Hygiene Guard

Remember: Per the **Canonical 8-Root Directory Invariant**, agents must NEVER create top-level directories (`Excalidraw/`, `whiteboards/`, etc.) in the root of `DNK_HUB`. All user visual assets reside under `docs/notes/`.

Always verify compliance with:
```bash
python3 scripts/system/root_hygiene_guard.py
```
Expected output:
```
✅ ROOT HYGIENE PASSED: Repository root complies 100% with the Canonical Directory standard.
```
