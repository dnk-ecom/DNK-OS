# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/eval_driven_differential_skill_architecture.md"
# purpose: "Assimilated patterns from GoogleChrome/modern-web-guidance-src and passkey-skills-demo for 10-year self-evolving agentic skills."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Eval-Driven Differential Skill Architecture (Google Chrome Modern Web Guidance)

Source repositories audited:
- Sandbox & E2E Benchmark: `GoogleChromeLabs/passkey-skills-demo` (Apache-2.0)
- Upstream Skill Factory & Compiler: `GoogleChrome/modern-web-guidance-src` (Apache-2.0)

---

## 1. Core Problem Solved: Pre-Training Corpus Lag & Statistical Gravity

Even frontier LLMs experience a 40–60% failure rate (e.g., 32 failed assertions out of 80 in WebAuthn/Passkeys) when implementing rapidly evolving specifications or SDKs with breaking major versions:
1. **API Generation Drift**: Pre-training weights heavily favor legacy idioms (e.g., manual `ArrayBuffer <-> Base64URL` helpers and `isUserVerifyingPlatformAuthenticatorAvailable()`) over modern standards (`PublicKeyCredential.parseCreationOptionsFromJSON()`, `getClientCapabilities()`, WebAuthn Signal API, Conditional Create).
2. **SDK Version Drift**: Models generate code for older major versions (e.g., `@simplewebauthn/server` v7–v8 instead of v10–v13 where `userID` requires `Uint8Array` and options are flat objects).
3. **Unsafe Heuristic Hallucinations**: Without explicit negative constraints, models misuse UX metadata (such as `AAGUID` provider identifiers) as server-side security assertions.

---

## 2. Two-Tier Upstream Discovery Rule (Wrapper vs. Factory Audit)

When auditing a demo or sandbox repository (such as `GoogleChromeLabs/passkey-skills-demo`), never stop at the surface README:
1. Inspect `package.json`, CLI installers (`npx modern-web-guidance@latest install`), or `.agents/skills/` to trace the **upstream source factory** (e.g., `GoogleChrome/modern-web-guidance-src`).
2. Audit the upstream compiler/pipeline (`CONTEXT.md`, `SKILL.md`, build scripts) to extract the meta-architecture rather than just copying static markdown rules.

---

## 3. Pattern 1: Differential Knowledge Mirroring (`mirror.md` Inverse Filter)

To prevent skill bloat and context fossilization over a 10-year horizon, skills must contain **only the delta** between what models natively know and what the specification requires:
1. **Multi-Model Baseline Probe**: Query 3 distinct frontier models (e.g., Gemini, Claude, Codex) with: *"What are the standard best practices and APIs for [Topic]?"*
2. **Lowest Common Denominator Intersection (`mirror.md`)**: Compute the intersection of concepts that all models already know natively without guidance.
3. **Surgical Pruning**: Strip everything present in `mirror.md` from the target `SKILL.md` / `guide.md`. Retain **only** the differential knowledge (new APIs, breaking SDK signatures, counter-intuitive security traps).
4. **Lifecycle Auto-Pruning**: When upgrading to a new model generation, re-run the unguided baseline eval. Any rule in `SKILL.md` that the new model now passes at 100% unguided is pruned from active context.

---

## 4. Pattern 2: The Triad Skill Capsule (`guide.md` + `expectations.md` + `grader.ts`)

A production engineering skill is not a standalone prose document; it is a verifiable capsule consisting of three coupled artifacts:
1. **`guide.md` (Imperative Contract)**: Strict `DO / DO NOT` rules and minimal canonical code snippets. Zero conversational filler or historical background.
2. **`expectations.md` (Human-Authored Assertions)**: Plain-language behavioral requirements grouped by feature slice.
3. **`grader.ts` (Calibrated Deterministic Oracle)**: An automated test suite (e.g., Playwright + CDP virtual authenticators) calibrated against:
   - **3 Guided Reference Patches** (Claude, Codex, Gemini solutions) -> **MUST score 100%**.
   - **1 Unguided Baseline / Zero-Passrate Patch** -> **MUST fail (0% on target delta)**.
   - If calibration fails, an automated loop regenerates and refines `grader.ts` (up to 3 iterations) before sealing the skill.

---

## 5. Pattern 3: Real Protocol Virtual Oracles (Zero-Mock E2E Verification)

For hardware-backed or browser-native protocols (WebAuthn, payments, permissions, canvas rendering), synthetic unit mocks hide real serialization and lifecycle bugs:
- Use Chrome DevTools Protocol (`page.context().newCDPSession(page)`) in headless E2E tests (e.g., `WebAuthn.enable`, `WebAuthn.addVirtualAuthenticator`, `WebAuthn.getCredentials`) to verify real end-to-end state transitions between the browser authenticator and the backend database.
