---
name: mac-hygiene
description: Audit, monitor, optimize, and safely maintain MacBook Pro (Apple Silicon M1/M2/M3) system health, SSD storage, RAM, and developer runtime environments.
---

# 💻 Mac Hygiene & Performance Skill

Use this skill when the user asks to:
- Audit MacBook RAM, Swap, Memory Pressure, or SSD storage health.
- Safely clean developer and browser caches without losing passwords, sessions, or project code.
- Optimize macOS developer responsiveness (Git FSMonitor, Dock latency, key repeat, Spotlight exclusions).
- Export or restore the declarative workstation state (`Brewfile`).

---

## ⚡ Core CLI Commands (`mac-station`)

All canonical scripts live in the `mac-station` repository:
Path: `../DNK_Vibe/mac-station/scripts/` (or `~/.config/mac-station/` when linked).

### 1. Full System Audit (Read-Only)
```bash
/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_GitHub_Vibe/mac-station/scripts/mac_audit.sh
```
*Outputs: RAM allocation, Swap usage (alert if > 3GB), Memory Pressure zone, top 5 RAM consumer processes, APFS SSD capacity & free space, and developer cache directory sizes.*

### 2. Safe Zero-Data-Loss Hygiene
```bash
/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_GitHub_Vibe/mac-station/scripts/mac_clean.sh
```
*Safely purges: Google Chrome shaders/Service Workers/File System blobs (preserves passwords, cookies, bookmarks), Python bytecode `pycache`, temporary `next_ecom_os` builds, `uv` package wheels, QuickLook thumbnails, and DNS cache.*

### 3. Purge Orphaned Deleted Apps Remnants
```bash
/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_GitHub_Vibe/mac-station/scripts/mac_purge_orphans.sh
```
*Alias: `dnk-purge-orphans`. Purges orphaned containers, group containers, application support data, updater caches, and preferences of uninstalled applications.*

### 4. Apply macOS Engineering Defaults
```bash
/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_GitHub_Vibe/mac-station/scripts/macos_defaults.sh
```
*Applies: KeyRepeat: 2, InitialKeyRepeat: 15, ApplePressAndHoldEnabled: false, Dock autohide-delay: 0, Finder ShowAllExtensions: true, Git fsmonitor & untrackedCache, global gitignore, and Spotlight `.metadata_never_index` markers.*

### 4. Update Workstation State (`Brewfile`)
```bash
brew bundle dump --force --file=/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_GitHub_Vibe/mac-station/Brewfile
```

---

## 🛡️ Negative Scope & Invariants (Strictly Enforced)

1. **NEVER delete user session or credential data:**
   - Prohibited targets: `Login Data`, `Cookies`, `Bookmarks`, `History`, `Preferences`, `Keychains`.
2. **NEVER modify or delete active project source code:**
   - Prohibited targets: `~/Kuzmenko/MY_LIFE_WORK/DNK_HUB`, active git branches, uncommitted files.
3. **NEVER create top-level directories in `DNK_HUB`:**
   - All external utilities and benchmarks must remain in `../DNK_Vibe/`.
4. **Interactive `sudo` boundary:**
   - For commands requiring elevated privileges in protected system directories (`/etc/pam.d`), always instruct the user to run `mo touchid enable` in their native macOS Terminal.
