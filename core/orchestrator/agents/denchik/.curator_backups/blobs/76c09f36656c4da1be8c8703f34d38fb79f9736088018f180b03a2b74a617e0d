<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/folder_as_architecture_and_minimalist_posix_harness_protocol.md"
purpose: "Folder-as-Architecture paradigm, Minimalist POSIX Harness, AI Delegation Triad, and Multimodal Video Audit Protocol."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-10-25"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 📁 Folder-as-Architecture & Minimalist POSIX Harness Protocol

## 🎯 1. Core Paradigm: Folder-as-Architecture vs Code-as-Architecture

Traditional multi-agent frameworks (LangGraph, AutoGen, CrewAI) suffer from **"Code-as-Architecture"**:
- Engineers write thousands of lines of fragile Python/TypeScript glue code to define micro-agents (`Agent1 -> Router -> Agent2`).
- Hardcoded pipelines break whenever APIs, tool signatures, or prompt formulations evolve.
- The system becomes an unmaintainable state machine.

**Folder-as-Architecture (The Unix & Engelbart Evolution)**:
- **Model**: SOTA LLM (Claude 3.7 / Gemini 2.5 / GPT-4o) functions as an execution engine.
- **Harness**: A minimalist POSIX wrapper with 4 primitive tools:
  1. `terminal` (CLI / Shell execution)
  2. `read_file` (Inspection)
  3. `patch` / `write_file` (Atomic mutation)
  4. `search_files` (Fast workspace indexing / ripgrep)
- **Architecture**: The entire agent system is declared inside the directory structure:
  ```
  workspace/
  ├── playbooks/ (or skills/) -> Behavioral rules, steps, anti-patterns (Markdown)
  ├── toolbox/ (or scripts/)   -> Deterministic CLI tools, linters, validators
  ├── data/ (or core/docs/)    -> Ground truth, schemas, configs, state DB (SSOT)
  └── HARNESS                  -> Hermes / Claude Code (thin OS runtime layer)
  ```
A single agent scans the directory structure on the fly and adopts the requested persona/role without modifying underlying Python engine code.

---

## ⚡ 2. The AI Delegation Triad (Anthropic & SOTA Workflow)

When capturing and executing recurring workflows:

1. **Interview**:
   - Interrogate intent, edge cases, and failure modes before writing code.
   - Compile into an explicit `PLAYBOOK.md` (or `SKILL.md`) with: `Goal`, `Steps`, `Rules`, and `Done Means`.
2. **Toolbox**:
   - Provide concrete, pre-existing scripts and templates so the agent does not regenerate boilerplate.
   - Reference deterministic executables (e.g., `scripts/verify_all.sh`).
3. **Proof ("Done Means")**:
   - Completion must NEVER be claimed by verbal summary alone.
   - Requires live machine execution output (HTTP 200, test suite pass, `exit code 0`).
4. **The Loop**:
   - When an agent errs, do NOT tweak runtime code or engage in chat debates.
   - Update a single rule or pitfall in the governing `PLAYBOOK.md` / `SKILL.md`.

---

## 🛡️ 3. Critical Failure Modes & Engineering Mitigations

| Failure Mode | Root Cause | Structural Mitigation |
|---|---|---|
| **Context Bloat & Entropy** | Single agent exploring 2000+ files accumulates >40k tokens and forgets system rules. | Fork into ephemeral, isolated subagents (`delegate_task`) with targeted toolsets and clean context windows. |
| **Sycophantic "Self-Proof"** | Model self-evaluates against "Done Means" and falsely claims success (arXiv:2609.08589). | Enforce deterministic machine gates: pytest, AST linters, curl checks. Verbal self-reviews are epistemic violations. |
| **Monolithic Serialization** | Single agent executing cross-domain tasks sequentially takes 10x longer. | Deploy parallel domain workers (`SWARM_PARALLEL`) operating on shared repository structure with a Join Barrier. |

---

## 🎥 4. Multimodal Local Audit Recipe (Zero External Dependency)

To perform deep technical audits of local videos/audio without heavyweight local Whisper models:
1. **Audio Extraction**:
   ```bash
   ffmpeg -y -i input.mp4 -vn -acodec libmp3lame -ar 16000 -ac 1 -b:a 32k /tmp/audio.mp3
   ```
2. **Frame Sampling**:
   ```bash
   ffmpeg -y -i input.mp4 -vf "fps=1/15" -q:v 2 /tmp/frames/f_%03d.jpg
   ```
3. **Inline Multimodal Ingestion**:
   Send the compact MP3 and key slide frames directly via Vertex AI Gemini Native Client (`inline_data` base64). Gemini processes verbatim speech and visual slides simultaneously with zero GPU setup lag.
