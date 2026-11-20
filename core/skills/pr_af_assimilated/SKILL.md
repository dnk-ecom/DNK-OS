---
name: "pr_af_assimilated"
description: "Assimilation patterns, Adversary Gate, and Blast Radius algorithms from Agent-Field/pr-af (#1 Code Reviewer)"
version: "1.0.0"
category: "software-development"
author: "Gerych SOTA Assimilation Engine"
tags: ["pr-review", "adversary", "blast-radius", "code-review", "agent-field"]
---

# PR-AF Assimilated Skill: Adversary Gate & Blast Radius Engine

This skill encodes proven architecture, schemas, and recipes assimilated from **Agent-Field/pr-af** (Apache 2.0) — the #1 Open-Source PR Reviewer on Martian Code-Review-Bench.

## 🌟 Core Concepts

1. **Blast Radius Analysis**:
   - Programmatically builds import/dependency graphs.
   - Detects external files in the workspace affected by a changeset even if not included in the PR diff.

2. **Adversary Verification Gate**:
   - Evaluates findings produced by LLM reviewers.
   - Attempts to refute each finding based on:
     - Is it mitigated by calling code?
     - Is it already covered by existing test cases?
     - Is it purely stylistic noise (nitpick)?
   - Drops or downgrades refuted findings to guarantee high precision.

3. **Deterministic Scoring**:
   - Math-based severity calculation.
   - Decouples subjective reasoning from scoring logic.
