# Public AI Harness Skills & Lead-Magnet Skill Distribution Protocol

## Context & Objectives
Public web AI harnesses (Google Gemini Web Chat / Gems, Anthropic Claude Projects, ChatGPT Custom GPTs, xAI Grok) represent a zero-friction distribution channel and tripwire lead-magnet for DNK OS capabilities.

## The Sandboxing Constraint (Gemini / Public Web Chats)
Public web chat interfaces enforce strict security boundaries against executable code.
- **Specific Error**: *"Користувацьку навичку <name> неможливо запустити в середовищі Gemini Chat, оскільки вона містить виконуваний код або скрипти, які тут не підтримуються."*
- **Root Cause**: Any skill package or zip bundle containing Python (`.py`), shell (`.sh`), nested `scripts/` directories, or inline terminal execution instructions is blocked by the harness safety filter.

## Two-Tier Skill Architecture
1. **Tier 1 — Core DNK OS Harness**:
   - Resides in `core/skills/<skill_name>/`.
   - Rich environment with Python scripts (`scripts/`), test suites (`tests/unit/`), CLI integrations (`pbpaste`/`pbcopy`), and structured references (`references/`).
2. **Tier 2 — Public No-Code / Zero-Script Bundle**:
   - Exported to `packages/public_skills/<skill_slug>/SKILL.md` (and optional clean `.zip`).
   - Clean YAML frontmatter containing ONLY `name:` and `description:`.
   - 100% declarative instructions, contrasting Bad/Good examples, and explicit heuristic tables.
   - Zero script references or code execution instructions.
   - Built-in subtle brand attribution / next-step bridge to DNK OS advanced capabilities.

## Dual-Track Localization Standards
- **Ukrainian (UK)**:
  - Eliminates Russian calques, surzhyk, and active participles (`-учий/-ючий`).
  - Converts bureaucratic passive voice (`було проведено`) to active forms (`провели`).
  - Normalizes Ukrainian typography: chevron quotes («...») and correct apostrophes (`’`).
- **English (EN)**:
  - Strips synthetic AI-slop vocabulary (`delve`, `tapestry`, `testament`, `beacon`, `revolutionize`).
  - Normalizes sentence length variance (burstiness) and active voice.
