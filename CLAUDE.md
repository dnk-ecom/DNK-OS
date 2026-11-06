# CLAUDE.md — DNK OS Workspace Guide for Claude Code & AI Coding Agents

## ⚡ Project Overview
**DNK OS** is the autonomous agentic operating system microkernel and coordination layer of the DNK Ecosystem. It manages task distribution, inter-agent IPC, deterministic quality gates, and seamless bridges across sister repositories (`DNK_HUB`, `DNK-Shopify-AI-Builder`, `Claude_Code_DNK`, `DNK_Researcher`).

---

## 🛠️ Toolchain & Commands

### Python (uv mandatory)
- **Run tests**: `uv run pytest`
- **Run specific test**: `uv run pytest tests/test_contracts.py -v`
- **Linter & formatting**: `uv run ruff check .` / `uv run ruff format .`
- **Type check**: `uv run mypy core`
- **Install dependencies**: `uv sync` / `uv pip install <package>`
- **STRICT**: Never use bare `pip` or `python -m pip`.

### Node.js / Frontend (pnpm mandatory)
- **Install**: `pnpm install`
- **Build**: `pnpm build`
- **Test**: `pnpm test`
- **STRICT**: Never use bare `npm` or `yarn`.

---

## 📐 Architecture & Coding Standards

1. **Language & Conventions**:
   - Communicate with Maxim in Ukrainian (🇺🇦).
   - Write all code, comments, docstrings, commits, and tests in clean English (🇬🇧).
   - Python 3.12+ with strict type annotations (`typing`, `Pydantic v2`).
2. **Path Hygiene**:
   - **Relative paths ONLY** (`./`, `../`). Absolute `/Users/...` paths are strictly forbidden in code, tests, and tool commands.
3. **Machine-Readable Headers (MRH)**:
   - Every file must have an MRH block (YAML frontmatter / comments) per `DNK-STD-0075`.
4. **Deterministic Testing (TDD & Anti-Tautology)**:
   - Always write non-tautological tests with real assertions before marking tasks done.
   - Fake mocks or empty assertions (`assert True`) are strictly prohibited.
5. **Ecosystem Interconnection**:
   - For inter-agent contracts, use schemas from `core/contracts.py`.
   - Never create circular dependencies with sibling repositories.
