---
title: "Board Session Business Marketing"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/skills/roast_room_assimilated/references/templates/board_session_business_marketing.md"
> purpose: "Document: Board Session Business Marketing"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/skills/roast_room_assimilated/references/templates/board_session_business_marketing.md"
purpose: "Board of Directors Adversarial Session Template for Business Plan & Marketing Strategy"
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-10-26"
author: "DNK OS Architecture & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🏛️ Board of Directors Session Template: Business Plan & Marketing Strategy

This template orchestrates a rigorous 3-Round Adversarial Review of a proposed **Business Plan & Marketing Strategy** using the 12-Entrepreneur Roster of the Roast Room.

---

## 📋 Phase 0: Session Brief & Context Ingestion

Before convening the board, fill out the business plan and marketing brief below. Every assumption must be marked `(assumed)`.

```markdown
# Session Brief: [Company/Product Name] — Business Plan & Marketing Strategy
Date: [YYYY-MM-DD]
Chair: [Gerych Prime / dnk_mentor]
Founder / Project Lead: [Founder Name]

### 1. The Core Decision & Options
- Decision in 1 line: [e.g. Launching enterprise tier at $4,900/mo vs self-serve product at $99/mo]
- Option A: [Primary proposed path]
- Option B: [Alternative path / conservative / lower capex]
- Option C: [Status quo / Keep doing current motion / Don't do it]

### 2. Business Plan Fundamentals
- Value Proposition: [What problem is solved, for whom, and what is the dream outcome?]
- Revenue Model: [Subscription, usage-based, one-time fee, retainers]
- Target Pricing & Margins: [Price point, COGS, target gross margin %]
- Break-Even & Financial Runway: [Monthly burn, cash on hand, months of runway]

### 3. Marketing & Distribution Architecture
- Primary Acquisition Channel: [Organic content, cold outbound, paid performance ads, SEO, partnerships]
- Value Equation & Lead Magnet: [Grand Slam Offer, Free tool, Case study, Trial]
- Unit Economics Target: [Target CAC, 30-day cash recovery, expected LTV]
- Organic Attention Engine: [Short-form video, thought-leadership essays, newsletters, community]

### 4. Operations & Execution Realities
- Team Size & Capabilities: [Number of full-time, contractors, AI swarm capacity]
- Founder Calendar Allocation: [Hours per week spent on sales vs delivery vs product]
- Operational Bottleneck: [Current single point of failure / bottleneck]

### 5. Founder Lean & Conviction
- Current Preference: [Which option the founder leans toward]
- Core Hypothesis: [Why the founder believes this will work]
```

---

## 👥 Phase 1: Board Seat Selection & Weighting

Select between **7 seats (Default Core Board)** or **12 seats (Full Comprehensive Board)**. Set relevance weights (1 to 3) based on the specific strategic focus:

| Seat | Entrepreneur | Pillar | Focus for Business Plan & Marketing | Weight (1-3) |
|---|---|---|---|---|
| **Hormozi** | Alex Hormozi | Offers & Sales | Value equation, pricing power, Grand Slam offer, 30-day cash recovery | 3 |
| **GaryVee** | Gary Vaynerchuk | Attention & Brand | Underpriced attention, content volume, organic distribution, cultural relevance | 3 |
| **Bezos** | Jeff Bezos | Strategy & Scale | Day 1 thinking, flywheel acceleration, customer obsession, 2-way vs 1-way doors | 2 |
| **Graham** | Paul Graham | Product & Demand | Do things that don't scale, talking to users, organic pull vs forced sales | 2 |
| **Buffett** | Warren Buffett | Capital & Moats | Durable competitive moat, pricing power without loss of customers, downside risk | 2 |
| **Martell** | Dan Martell | Founder Time & Leverage | Buy Back Your Time, DRIP matrix, calendar tax of the business model | 2 |
| **Wickman** | Gino Wickman | Operations & EOS | Traction, Scorecard, Rocks, repeatable systems without founder bottleneck | 1 |
| **Naval** | Naval Ravikant | Equity & Leverage | Permissionless leverage (code & media), specific knowledge, recurring vs renting | 2 |
| **Codie** | Codie Sanchez | Cash Flow & SMB Moats | Sweat equity, boring business moats, cash-flow stability, buy vs build | 1 |
| **Leila** | Leila Hormozi | Team & Leadership | Talent density, management infrastructure, hiring capacity to execute the plan | 1 |
| **Sara** | Sara Blakely | Self-Funded Virality | Organic word-of-mouth, bootstrapping, product so good customers sell it | 2 |
| **Musk** | Elon Musk | First Principles & Speed | Deleting unneeded steps, radical cost reduction, rapid iteration cycle | 2 |

---

## ⚔️ Phase 2: 3-Round Adversarial Protocol

### Round 1: Opening Positions & Independent Roast
Each seated entrepreneur independently reviews the brief and returns their initial roast card without seeing other seats' answers.

**Prompt Template for Round 1:**
```text
ROAST ROOM COUNCIL, ROUND 1 OF 3: OPENING POSITION (BUSINESS & MARKETING)
Repo root: ./
You hold the [SEAT] seat ([pillar]). Read your brain's _hot.md and relevant frameworks.
Read the brief: [session folder]/brief.md

Your weight on this decision: [w]/3.

Answer in your seat's authentic voice, plain text, under 350 words, in this exact shape:

SEAT: [SEAT] ([pillar])
STANCE: Strong yes | Yes | Conditional yes | No | Strong no (on your recommended option)
OPTION SCORES: [A] n/10 · [B] n/10 · [C] n/10
PILLAR SCORE: n/10 ([dimension]: recommended option on your pillar alone)
CONFIDENCE: n/5
RUIN RISK: none | possible | likely
DOOR: one-way | two-way

THE CALL: one sentence, naming the option or a variant.
WHY:
1. [Core argument citing your brain framework, e.g. (Value Equation, S014)]
2. [Second argument with numbers / CAC / cash]
3. [Third argument regarding execution reality]
THE RISK I SEE: the single fatal flaw in the proposed plan.
WHAT WOULD CHANGE MY MIND: concrete metric, test result, or customer signal.
WHAT I'D DO THIS WEEK: one high-leverage immediate action.
QUESTION FOR THE FOUNDER: the burning question before signing off.
```

### Round 2: Crux Debate & Cross-Fire
The Chair compiles Round 1, extracts the 2-3 core **Cruxes** (ideological or tactical splits), and forces seats to confront their direct adversaries:
- **Hormozi vs GaryVee**: Direct response unit economics & immediate cash vs long-term organic brand and underpriced social attention.
- **Buffett vs Musk**: Capital preservation & risk minimization vs aggressive first-principles capital deployment and rapid iteration.
- **Graham vs Wickman**: Early-stage unscalable founder hacking vs rigid EOS operational cadences and process documentation.
- **Martell vs Leila**: Outsourcing/buying back time immediately vs elevating internal leadership density and fixing conversion before hiring.
- **Naval vs Codie**: High-margin digital leverage (code/media) vs unsexy physical asset cash flows and service roll-ups.

**Prompt Template for Round 2:**
```text
ROAST ROOM COUNCIL, ROUND 2 OF 3: DEBATE
You hold the [SEAT] seat. Read your brain's _hot.md and Round 1 cards.
Read: [session folder]/brief.md and [session folder]/round-1.md

THE CRUXES THE CHAIR SEES:
1. [Crux 1: e.g., Direct Sales CAC vs Organic Content Horizon]
2. [Crux 2: e.g., High-Ticket Retainer vs Scalable Low-Touch Software]

Answer in your seat's voice, plain text, under 300 words:

SEAT: [SEAT]
I DISAGREE MOST WITH: [seat] — their point in 1 line, then your rebuttal.
I CONCEDE: strongest critique made against your position.
ON THE CRUXES: your stance on Crux 1 and Crux 2 in 1-2 lines each.
STANCE: ...
OPTION SCORES: [A] n/10 · [B] n/10 · [C] n/10
PILLAR SCORE: n/10
CONFIDENCE: n/5
RUIN RISK: none | possible | likely
MOVED: no | yes, from X to Y, because [reason]
MY CONDITIONS FOR YES: up to 3 measurable prerequisites (CAC threshold, conversion rate, deposit amount).
```

### Round 3: Ratification & Final Vote
The Chair drafts the **Draft Resolution**, synthesizing the compromise, required preconditions, and risk mitigations. Each seat votes:

**Prompt Template for Round 3:**
```text
ROAST ROOM COUNCIL, ROUND 3 OF 3: VOTE ON THE DRAFT RESOLUTION
You hold the [SEAT] seat. Read [session folder]/draft-resolution.md.

Answer in your seat's voice, under 150 words:

SEAT: [SEAT]
VOTE: Endorse | Endorse with amendment | Dissent
OPTION SCORES: [A] n/10 · [B] n/10 · [C] n/10
FINAL SCORE: n/10 (support for draft resolution)
FINAL PILLAR SCORE: n/10
AMENDMENT OR DISSENT: [1-2 sentences on what must change, or why you dissent]
ONE LINE FOR THE FOUNDER: [The non-negotiable rule from your pillar]
```

---

## 📊 Phase 3: Scoring Math & Downside Overrides

### 1. Weighted Option Score
For each option ($A, B, C$):
$$\text{Score} = \frac{\sum (w_i \times s_i)}{\sum w_i}$$

### 2. Verdict Decision Bands
- **7.5 to 10.0**: `GO` (Execute with high conviction)
- **6.0 to 7.4**: `GO WITH CONDITIONS` (Execute only after prerequisites are met)
- **4.5 to 5.9**: `RESHAPE` (Core idea has promise, but offer/distribution mechanics must be rebuilt)
- **Below 4.5**: `DON'T DO IT` (Kill the initiative; capital and time better spent elsewhere)
- **WAIT**: Promising plan blocked by an unverified dependency (e.g. key hire, beta conversion data).

### 3. Hard Downside Overrides (Non-Negotiable)
1. **Ruin Risk Cap**: If ANY seat (especially Buffett, Bezos, or Hormozi) marks `RUIN RISK: likely` on the winning option, the verdict is capped at `RESHAPE` until a binding mitigation is included.
2. **One-Way Door Cap**: If the option is an irreversible one-way door and score spread is $\ge 4.0$, cap at `GO WITH CONDITIONS` and mandate a micro-experiment first.
3. **Unanimity Circuit Breaker**: If all seats agree in Round 1, the Chair MUST force an adversarial stress-test on the hidden assumptions in Round 2.

---

## 📄 Phase 4: Final Board Verdict Output Format

The output of the session is stored in `sessions/[DATE]-[DECISION-SLUG]/verdict.md`:

```markdown
# Board Verdict: [Decision Title]

Date: [Date] · Mode: [Full Board | Quick 4-Seat] · Attendance: [List of Seats]

## Final Verdict: [GO | GO WITH CONDITIONS | RESHAPE | WAIT | DON'T DO IT]

**The Core Directive:** [1-2 sentences of unambiguous, actionable direction]

**Quantitative Metrics:**
- Option A Score: [X.X/10] · Option B Score: [X.X/10] · Option C: [X.X/10]
- Resolution Support: [X.X/10]
- Council Confidence: [X/10] · Disagreement Spread: [X]
- Final Vote: [N] Endorse · [N] Amend · [N] Dissent

### 🏛️ Detailed Scorecard by Seat
| Seat | Weight | Stance | Option A | Option B | Option C | Pillar Score | Crux Position | Non-Negotiable Rule |
|---|---|---|---|---|---|---|---|---|
| Hormozi | 3 | ... | ... | ... | ... | ... | ... | "..." |
| GaryVee | 3 | ... | ... | ... | ... | ... | ... | "..." |
| Bezos | 2 | ... | ... | ... | ... | ... | ... | "..." |
| Buffett | 2 | ... | ... | ... | ... | ... | ... | "..." |

### 🔍 Key Arguments That Won the Room
1. **[Framework Name] (Seat)**: [Key insight]
2. **[Framework Name] (Seat)**: [Key insight]
3. **[Framework Name] (Seat)**: [Key insight]

### 🥊 Major Debate Clashes & Resolutions
- **[Crux 1 Name]**: [Who clashed, what evidence shifted the consensus]
- **[Crux 2 Name]**: [Who clashed, what compromise was ratified]

### ⚠️ Pre-Conditions Before Launch (Checkable Gates)
1. [Condition 1: e.g. Pre-sell 5 deposits before building feature X]
2. [Condition 2: e.g. Organic CAC verified < $120 over 30 days]
3. [Condition 3: e.g. Founder delivery time capped at 10 hrs/week]

### 🚀 Immediate 30-Day Execution Roadmap
- **Week 1**: [Smallest test / offer validation] (Lead: Founder)
- **Week 2**: [Acquisition channel sprint] (Lead: Marketing)
- **Week 3**: [Unit economics review & conversion audit]
- **Week 4**: [Board Revisit date with real telemetry]

**Cheapest Test:** [Smallest $0-$100 test to invalidate the core assumption]
**Kill Trigger:** [Specific metric that cancels the initiative]
```
