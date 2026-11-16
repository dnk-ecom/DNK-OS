# Anti-Bloat Evaluation & Calibrated 5-Vector Service Filter (Anti-Frankenstein Protocol)

## 📌 Context and Purpose
When evaluating external SaaS platforms, libraries, cloud headless services, or viral tooling (e.g. Sanity.io, Strapi, external CMSs, proprietary vector DB clouds):
Never allow "Frankenstein Architecture" — creating brittle layers of glue code around fashionable third-party services that duplicate native capabilities or introduce vendor lock-in.

At the same time, avoid the **NIH (Not Invented Here) trap** — do not attempt to write complex low-level infrastructure (payment processing, transactional email, SOTA generative video models, global CDN distribution) from scratch.

---

## 🛡️ The Calibrated 5-Vector Anti-Bloat Gate

Apply these 5 vectors deterministically before adding any external service, microservice, or paid dependency:

```
                  [ External Service / Tool Proposal ]
                                    │
                                    ▼
       Vector 1: Knowledge Sovereignty (SSOT) ──────────► [Fails? REJECT]
                                    │ (Passes)
                                    ▼
       Vector 2: Zero-Glue Efficiency (Code Tax) ────────► [Fails? REJECT]
                                    │ (Passes)
                                    ▼
       Vector 3: Agent-First & Headless Readiness ──────► [Fails? REJECT]
                                    │ (Passes)
                                    ▼
       Vector 4: Concrete Utility vs Vanity Shell ──────► [Fails? REJECT]
                                    │ (Passes)
                                    ▼
       Vector 5: 3 Core Workhorses Compliance ──────────► [Fails? REJECT]
                                    │ (Passes)
                                    ▼
                     [ ADMITTED / ASSIMILATED ]
```

### 1. Knowledge & Logic Sovereignty (SSOT)
- **Question:** Does the service attempt to monopolize business logic, content, prompts, or architecture rules inside its proprietary cloud?
- **Rule:** 
  - **Knowledge, Architecture, Prompts & Content SSOT MUST remain Local-First** (`Obsidian/Git` flat files, Markdown, AST).
  - External platforms may manage *dynamic transactional operational state* (e.g., Shopify checkouts, Stripe payments, warehouse stock, webhook events), but NEVER internal business cognition.

### 2. Zero-Glue Efficiency (Code Tax Calculation)
- **Question:** Does the time and complexity required to write integration glue code, schemas, and API migrations exceed the business value or speed gained?
- **Rule:** If maintaining schemas, sync jobs, and webhook retry handlers costs more developer hours than building or running native capabilities, the tool is a parasite and must be rejected.

### 3. Agent-First & Headless Readiness (Programmatic Control)
- **Question:** Does the service have a stable, robust CLI/REST/gRPC interface that autonomous agents (`Gerych Prime`) can drive without human intervention?
- **Rule:**
  - Services requiring manual web UI clicking, CAPTCHAs, or anti-bot hurdles are strictly rejected.
  - External paid APIs (Runway/Kling for video, ElevenLabs for voice, high-tier LLM inference) are **fully permitted** provided they are 100% headless and programmatic.

### 4. Concrete Utility vs Vanity Shell (Reality Check)
- **Question:** Does this tool directly generate revenue/conversions OR solve a deep, non-trivial engineering challenge (low latency, CDN bandwidth, video rendering, PCI compliance)?
- **Rule:** Reject "vanity shells" (pretty wrappers around databases, no-code landing builders lacking payment logic, "Composable Content Clouds" that don't execute transactions). Accept pure infrastructure (Redis, Cloudflare R2, SQLite, FastMCP) that demonstrably accelerates throughput.

### 5. 3 Core Workhorses Compliance (Zero Proliferation)
- **Question:** Can this requirement be satisfied natively by one of the 3 Workhorses (`services/dnk_shopify`, `services/dnk_media`, `services/dnk_distribution`) or `core/`?
- **Rule:** Prohibit spinning up new standalone microservices or adopting external SaaS if native Shopify OS 2.0 (Metaobjects, Liquid, Shopify Functions), local Remotion engines, or existing distribution dispatchers already cover the use case.

---

## 📝 Documenting Decisions
Whenever an external service is reviewed and rejected:
1. Append it to `docs/notes/MY TASKS/0. Питання Архітектури/Журнал/REJECTED_SERVICES_REGISTRY.md`.
2. Specify the category, audit date, concrete failure points against the 5 vectors, and the native DNK OS alternative.
