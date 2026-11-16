# Git-Native Diff Overlay, BM25 Locus Scoping & Anchor Verification

## Overview
When autonomous coding agents modify dynamic codebases across rapid multi-turn cycles, two major memory failure modes occur:
1. **Semantic Staleness / Lag**: The agent cannot see uncommitted modifications to AST signatures without re-parsing the entire repository or relying on stale pre-turn index caches.
2. **Heavy Vector Embeddings Overhead & Drift**: Running local neural embedders (e.g. all-MiniLM-L6-v2) consumes hundreds of MBs of RSS and GPU memory, fails to match precise symbol identifiers, and suffers from semantic drift when names change.
3. **Dead / Hallucinated Anchors**: Skills, ADRs, and durable memory facts cite file paths and functions that have been renamed, moved, or deleted.

---

## 1. Working-Tree Diff Overlay Pattern (`Baseline ⊕ Diff Overlay`)
### Concept
Instead of maintaining a massive live AST index that must be rebuilt or synchronized across disk watchers:
1. **Commit Baseline**: Snapshot the AST symbols of the current immutable Git commit (`HEAD`).
2. **Porcelain Diff Detection**: Run `git status --porcelain` to identify only files with modifications (`M`), additions (`A`), or deletions (`D`).
3. **Delta Overlay**: Freshly parse only the modified/added files (`ast.parse`) in sub-milliseconds (< 2ms for 1-5 files).
4. **Effective Graph**: Combine `Effective = (Baseline - Deleted) ⊕ Overlay`.

```python
class SconesOverlayEngine:
    def get_effective_symbols(self, file_path: Optional[str] = None) -> Dict[str, ASTSymbol]:
        # Start with cached baseline
        effective = dict(self._baseline_symbols.get(file_path, {}))
        
        # Overlay fresh parse for changed files
        if file_path in self._changed_files:
            fresh_symbols = self._extractor.extract_from_file(file_path)
            effective.update(fresh_symbols)
        return effective
```

---

## 2. Deterministic FTS5 / BM25 with AST Locus Scoping
### The Invariant (`GIT_NATIVE_GRAPH_MEMORY`)
Prefer SQLite FTS5 with BM25 ranking and AST locus filters over local neural embeddings for repo-anchored agent memory:
- SQLite FTS5 runs in-process with < 15MB RSS.
- Exact symbol and identifier matching is 100% deterministic (no cosine similarity hallucination).
- Dual-key retrieval: Combine free-text query with AST locus bounds:
  `SELECT ... FROM facts_fts WHERE facts_fts MATCH :query AND symbol_anchor = :symbol;`

---

## 3. Anchor Verification Engine
### Verifying Memory & Knowledge against Disk State
To prevent knowledge corruption, memory facts and documentation references must be audited continuously against the live working tree:
1. **AnchorRef**: Tuple of `(file_path, symbol, line, source_doc)`.
2. **Tri-State Classification**:
   - `VERIFIED`: Target file exists on disk and contains the expected AST symbol or valid line bounds.
   - `STALE`: File exists, but symbol was renamed/removed or line is out of range.
   - `BROKEN`: File does not exist on disk.
3. **Audit Execution**: Run automated verification (e.g. `scripts/system/verify_scones_anchors.py --skills`) in CI/pre-commit gates. Any dead file or drifted symbol reference fails the gate.
