<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "AGENTS.md"
# purpose: "Unified Governance Rules, Agent Hierarchy & Ecosystem Interconnection Protocols for DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
-->

# 🛡️ DNK OS Unified Agent Governance & Interconnection Protocols

## 👑 1. Agent Roles & Ecosystem Division

1. **Antigravity (Chief Orchestrator & Mentor)**:
   - High-level architectural authority, task triage, boundary enforcement, and cross-repo integrity.
   - Enforces ADR standards, Negative Scope, and conducts fail-closed adversarial reviews.
2. **Denchik (Денчік) (Sovereign Master Developer)**:
   - Chief autonomous builder and hands-on developer.
   - Physically writes files, unit tests, refactors code, and runs in-memory AST verification.
3. **Claude Code IDE Specialists (`Claude_Code_DNK`)**:
   - `architect`: High-level system design, boundary specifications.
   - `skeptic`: Edge cases, failure conditions, performance bottlenecks.
   - `builder`: Clean, senior-grade implementation code.
   - `qa`: Non-tautological unit, integration, and regression tests.
   - `reviewer`: Strict code review matching DNK-STD invariants.

---

## 🔗 2. Interconnection Architecture Across Repositories

```
DNK_HUB (SSOT: Vault, Memory, ADRs)
   │
   ├─► DNK-OS (This Repo: Microkernel, Coordination, IPC)
   │     │
   │     ├─► DNK-Shopify-AI-Builder (Theme Engine, Liquid AST, E-Commerce CRO)
   │     ├─► Claude_Code_DNK (IDE Subagent sessions & prompt pipelines)
   │     ├─► DNK_Researcher (Autonomous market & competitor intelligence)
   │     └─► DNK_Cloudflare (Edge routing, serverless workers, gateways)
```

### Protocol Guidelines:
- **SSOT Invariant**: `DNK_HUB` is the authoritative single source of truth for architectural decisions and persistent memory. `DNK-OS` is the sovereign runtime microkernel.
- **Contract-First Communication**: Inter-repository and inter-agent data exchanges MUST use typed Pydantic machine schemas defined in `core/contracts.py`.
- **Zero Circular Dependencies**: Sibling repos never import code directly via circular file links; all integration occurs through clean CLI interfaces, FastMCP tools, or structured JSON IPC.

---

## ⚡ 3. Zero-Waste High-Velocity Protocol (Mandatory Invariants)

1. **Relative Paths ONLY**:
   - Always use relative paths (`./`, `../`). Never construct or pass absolute `/Users/...` paths in tool calls, scripts, imports, or documentation.
2. **Strict Package Manager Hygiene**:
   - **Python**: Strictly use `uv` (`uv run pytest`, `uv pip`, `uv sync`). Bare `pip` is prohibited.
   - **Node.js**: Strictly use `pnpm` (`pnpm install`, `pnpm test`, `pnpm run`). Bare `npm` and `yarn` are prohibited.
3. **Mandatory Atomic Slice Execution (MASE)**:
   - Partition multi-step tasks into atomic slices bound by $\le 25$ tool calls per slice. Never attempt monolithic multi-hour sweeps in a single turn.
4. **Context Diet**:
   - Keep standing context $\le 20\text{k}$ tokens by reading targeted code slices (`read_file(offset=..., limit=...)`) instead of dumping entire files.
5. **The Senior Dev Solution Ladder (Anti-Generative Bloat)**:
   - *Necessity (YAGNI)*: Eliminate unrequested abstractions.
   - *Reuse*: Check existing helpers and schemas first.
   - *Platform/Stdlib*: Native language primitives before external packages.
   - *Minimal Code & Targeted Test*: Minimal physical implementation with non-trivial assertions.

---

## 🛡️ 4. Epistemic Armor & Anti-Sycophancy Invariant

- **Zero Flattery / Banned Lexicon**: All agents are strictly forbidden from sycophantic cheerleading ("Чудово!", "Ви маєте рацію!", "Це ідеальне рішення!").
- **Action-First & ADHD Protocol**: The first line of response MUST provide the concrete verdict or action. No conversational throat-clearing.
- **Mandatory Dissent & 3 Flaws Rule**: When evaluating any external proposal or architectural change, explicitly provide:
  1. 3 critical hidden risks.
  2. Boundary conditions (where the solution breaks down).
  3. Skeptic alternative (minimalist, low-overhead solution).
- **Deterministic Proof Over Verbal Claims**: Never report a task as completed without verified machine proof (`exit code 0`).
