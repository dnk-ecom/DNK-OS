---
name: roast_room_assimilated
description: "Assimilated SOTA Roast Room & 12-Entrepreneur Board of Directors Engine from nateherkai/roast-room."
version: "1.0.0"
category: "research"
assimilated_at: "2026-10-26"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "dnk_mentor"
---

<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/skills/roast_room_assimilated/SKILL.md"
purpose: "Assimilated SOTA 12-Entrepreneur Board of Directors & Roast Room Protocol"
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-10-26"
author: "DNK OS Architecture & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🏛️ ROAST-ROOM SOTA Assimilation Index & Board Orchestration Engine

Meta-index and execution engine assimilated from **[nateherkai/roast-room](https://github.com/nateherkai/roast-room)** (MIT License).

Provides an adversarial **Board of Directors** and **Roast Room** simulation comprising **12 world-class entrepreneur minds** compiled from primary sources (interviews, letters, books, speeches, frameworks). Delivers non-sycophantic stress-testing, pricing roast, unit-economics auditing, marketing distribution teardowns, and strategic decision scoring.

---

## 📌 Repository Intel & Legal Boundary
- **Upstream Repository**: `nateherkai/roast-room`
- **License**: `MIT` (Commercial-Safe / Permissive)
- **Assimilation Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Primary Swarm Agents**: `dnk_mentor` (Chief Architect / Chair), `gerych_auditor` (Adversarial Security & Rigor), `dnk_shopify` (Ecom Strategy), `dnk_dev_fullstack` (Backend/FastAPI integration)
- **Status**: 🟢 **ACTIVE & PRODUCTION READY**

---

## 👥 The 12 Entrepreneur Brains & Pillars

Every entrepreneur is backed by a dedicated knowledge brain under `./brains/<slug>/` containing `_hot.md`, `frameworks.md`, `positions.md`, `principles.md`, `voice.md`, and primary citations.

| # | Seat Key | Entrepreneur | Primary Pillar & Dimension | Core Question Owned | Brain Path |
|---|---|---|---|---|---|
| 1 | `hormozi` | **Alex Hormozi** | Offers, Pricing & Sales | *"Will people pay, how much, and how do we close?"* | `./brains/alex-hormozi/` |
| 2 | `bezos` | **Jeff Bezos** | Strategy, Reversibility & Scale | *"Is this the right bet, and how reversible is it (1-way vs 2-way door)?"* | `./brains/jeff-bezos/` |
| 3 | `graham` | **Paul Graham** | Product Demand & Startups | *"Is this something people actually want, and is it growing?"* | `./brains/paul-graham/` |
| 4 | `garyvee` | **Gary Vaynerchuk** | Attention, Media & Brand | *"Where does the attention come from, and is it underpriced?"* | `./brains/gary-vaynerchuk/` |
| 5 | `martell` | **Dan Martell** | Founder Time & Operational Leverage | *"Who does this, and what does it cost the founder's calendar?"* | `./brains/dan-martell/` |
| 6 | `wickman` | **Gino Wickman** | Operations, Cadence & EOS | *"Can the business run this without the founder holding it together?"* | `./brains/gino-wickman/` |
| 7 | `buffett` | **Warren Buffett** | Capital Allocation & Economic Moats | *"What does it do to cash, risk, and durable long-term value?"* | `./brains/warren-buffett/` |
| 8 | `musk` | **Elon Musk** | First Principles & Iteration Velocity | *"What is the real constraint here, and can we cut steps and build it faster?"* | `./brains/elon-musk/` |
| 9 | `naval` | **Naval Ravikant** | Permissionless Leverage & Equity | *"Does this build equity/code/media leverage you own, or rent out time?"* | `./brains/naval-ravikant/` |
| 10 | `sanchez` | **Codie Sanchez** | Small Business Cash Flows & M&A | *"Should you build this from scratch, or buy cash flow that works?"* | `./brains/codie-sanchez/` |
| 11 | `leila` | **Leila Hormozi** | Team Density & Leadership Systems | *"Can your team and leadership carry this, and who has to change?"* | `./brains/leila-hormozi/` |
| 12 | `blakely` | **Sara Blakely** | Bootstrapping & Consumer Love | *"Will customers love it enough to sell it for you without outside money?"* | `./brains/sara-blakely/` |

---

## ⚙️ Board Orchestration Modes

1. **Full Strategic Council (Default, 7 or 12 Seats)**:
   - 3 full rounds (Open -> Debate Cruxes -> Ratify/Vote).
   - Used for non-reversible, high-stakes decisions: launching a company, pricing architecture, funding/equity, major product pivot.
2. **Quick Council (`--quick`, 4 Seats)**:
   - 4 seats: Two top-weighted domain seats + Downside guard (Buffett/Bezos) + Prime Dissenter.
   - Rounds 1 and 2 only (Round 3 only if spread $\ge 4$).
   - Used for reversible 2-way door decisions: ad campaign angle, single feature scope, email sequence.
3. **Domain Consult (`ask <seat> <question>`)**:
   - Single-seat direct inquiry (e.g. `ask hormozi "Audit my high-ticket onboarding offer"`).
   - Fast, focused synthesis using that entrepreneur's `_hot.md` and core heuristics.

---

## 📋 Board Session Protocols & Templates

The complete, production-ready meeting structure for business plan and marketing teardowns is documented in:
👉 **`./references/templates/board_session_business_marketing.md`**

### Three-Round Progression:
1. **Round 1: Opening Position & Independent Roast**:
   - Each seat receives the Brief and independently evaluates options $A, B, C$.
   - Output fields: `STANCE`, `OPTION SCORES`, `PILLAR SCORE`, `CONFIDENCE`, `RUIN RISK`, `DOOR`, `THE CALL`, `WHY`, `THE RISK I SEE`, `WHAT WOULD CHANGE MY MIND`, `WHAT I'D DO THIS WEEK`, `QUESTION FOR THE FOUNDER`.
2. **Round 2: Debate on Identified Cruxes**:
   - Chair isolates top 2-3 tensions (e.g. Hormozi direct CAC vs GaryVee organic flywheel; Buffett capital preservation vs Musk hyper-iteration).
   - Seats must directly challenge their top adversary, state what they concede, and outline conditions for approval.
3. **Round 3: Draft Resolution & Ratification Vote**:
   - Chair publishes the synthesized resolution with binding prerequisites.
   - Seats vote: `Endorse`, `Endorse with amendment`, or `Dissent`.

---

## 🧮 Quantitative Decision Scoring & Downside Caps

### Math:
$$\text{Option Score} = \frac{\sum (\text{weight}_i \times \text{seat\_score}_i)}{\sum \text{weight}_i}$$

### Verdict Bands:
- **7.5 – 10.0**: `GO`
- **6.0 – 7.4**: `GO WITH CONDITIONS`
- **4.5 – 5.9**: `RESHAPE`
- **< 4.5**: `DON'T DO IT`
- Special: `WAIT` (Gated on an unmet prerequisite).

### Mandatory Downside Caps:
- **Ruin Risk Cap**: If ANY seat records `RUIN RISK: likely` on the winning option, the verdict is capped at `RESHAPE` until an explicit mitigation is adopted.
- **One-Way Door Cap**: If the decision is a 1-way door and score spread $\ge 4.0$, cap at `GO WITH CONDITIONS`.
- **Unanimity Circuit Breaker**: If all seats agree in Round 1, the Chair forces Round 2 to vigorously attack the weakest assumption.

---

## 🧪 Quick Recipes (How to Run in DNK OS)

### Recipe A: Run a Business Plan & Marketing Council with dnk_mentor
```python
from core.orchestrator.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
res = coordinator.dispatch(
    agent="dnk_mentor",
    action="convene_roast_council",
    payload={
        "topic": "Business Plan & Marketing Strategy Review",
        "template": "core/skills/roast_room_assimilated/references/templates/board_session_business_marketing.md",
        "seats": ["hormozi", "garyvee", "bezos", "buffett", "martell", "musk", "naval"],
        "options": {
            "A": "High-Ticket B2B Service ($5k/mo) with outbound & direct response",
            "B": "Self-serve AI SaaS ($49/mo) with viral organic short-form marketing",
            "C": "Hybrid: Agency wedge to finance SaaS development"
        }
    }
)
```

### Recipe B: Verify Quotes Against Primary Brains
Run the quote verification script to ensure AI agents do not hallucinate quotes or numbers:
```bash
python3 core/skills/roast_room_assimilated/scripts/check_quotes.py sessions/<session-folder>
```

---

## 📁 Level-of-Detail (LoD) References
- **Seat Registry**: `./roster.json`
- **Council Agent Prompts**: `./references/agents/council-*.md`
- **Round Prompts**: `./references/round-prompts.md`
- **Seat Weighting & Tensions**: `./references/seats.md`
- **Scoring Formulas & Overrides**: `./references/scoring.md`
- **Verdict Report Template**: `./references/report-template.md`
- **Quote Verification Tool**: `./scripts/check_quotes.py`
- **Business Plan & Marketing Template**: `./references/templates/board_session_business_marketing.md`
- **All 12 Brains**: `./brains/`

## ⚠️ Pitfalls & Invariants
1. **[ANTI_SYCOPHANCY]**: Strictly forbid flattering openers or soft compromises. Board members must speak with their expert's sharpest edge.
2. **[QUOTE_INTEGRITY]**: Never invent quotes or data points. Quotations must map to exact brain source IDs (e.g. `(Value Equation, S014)`).
3. **[NO_EM_DASHES]**: Adhere strictly to the house writing standard (plain punctuation, no em dashes).
4. **[RUIN_OVERRIDE]**: A single seat flagging irreversible ruin risk overrules majority consensus.
