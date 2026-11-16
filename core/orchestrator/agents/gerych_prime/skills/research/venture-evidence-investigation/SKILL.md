---
name: venture-evidence-investigation
description: "Investigate ventures with evidence logs and live audits."
version: 1.0.0
category: research
author: Gerych Prime
license: MIT
metadata:
  hermes:
    tags: [venture, audit, market-research, evidence-log, portfolio, competitors, pricing]
    related_skills: [tri-lens-sota-research, founder_skill_assimilated, comment-mining]
---

# 📊 Venture Evidence Investigation Protocol

## Overview
This skill governs evidence-first, rigorous investigations of portfolio ventures, early-stage startups, and software products. It combines internal dashboard metrics, codebase audits, live network health checks, competitor pricing benchmarks, and customer sentiment signals into a verifiable, audit-ready Evidence Log and Strategic Action Report.

## When to Use
Use when:
- Investigating an early-stage portfolio venture or evaluating a build vs pause decision.
- Conducting market, customer sentiment, or competitor pricing research.
- Running live infrastructure and SEO health audits via portfolio dashboard APIs.
- Producing a verifiable Evidence Log strictly governed by anti-hallucination and grounding rules.

Supporting files:
- `references/dashboard-opc-api.md`: Documentation for OnePersonCompany local API routes and Arctic Shift Reddit proxy.

---

## 🛑 Strict Grounding & Anti-Hallucination Invariants

When investigating ventures, every claim must adhere to these non-negotiable rules:

1. **Zero Invented Figures**: Every number cited must appear in a primary source or be mathematically derived from explicitly cited numbers. If a metric is unmeasured, report `NOT MEASURED`.
2. **Sample ≠ Measurement**: Quoting rows from an API or archive (e.g. 5 Reddit threads out of 57 matches) must be explicitly stated as a sample (`Sample of N out of Total M`), never represented as the entire population.
3. **Absent ≠ Zero & Blocked ≠ Absent**:
   - If an endpoint was never asked, report `NOT QUERIED`.
   - If a source timed out, threw an error, or was blocked (e.g. 403/SSL error), report `BLOCKED / CONNECTION FAILED` with the exact error. Never report that the source "found zero results".
4. **Currency & Deduplication Discipline**:
   - Never sum money across different currencies (e.g. USD and EUR).
   - Figures pre-deduplicated by an upstream source must never be re-summed.
5. **Exact Source Attribution**: Every observation must explicitly cite its exact source URL, API route, or workspace file path, along with retrieval timestamp.

---

## 🔍 Investigation Workflow

### Step 1: Query Portfolio Dashboard & Internal Baseline
1. Read the service key from the environment or local credentials store (e.g. `server/data/service-key`).
2. Query the portfolio dashboard API:
   - Venture Record: `GET /api/ventures/<slug>`
   - Venture Journey: `GET /api/venture-journey/<slug>`
   - Trigger Live Audit: `POST /api/audit/<slug>`
3. Check local workspace documentation:
   - Readiness specs: `docs/executive/*_READY_FOR_IMPLEMENTATION*.md`
   - Roadmaps: `docs/reports/domain_research/`
   - Commercial pitches: `docs/notes/marketing/` or `docs/notes/MY TASKS/`

### Step 2: Live Network & Domain Health Verification
1. Inspect DNS and SSL certificates:
   - Probe HTTPS and HTTP endpoints directly.
   - Verify if SSL cert alternative names match the host domain.
   - Check redirects (ensure HTTP 301 redirects to HTTPS).
2. Probe standard search engine files:
   - `sitemap.xml`
   - `robots.txt`

### Step 3: Competitor Pricing & Tier Benchmarking
1. Search primary competitor pricing pages across 3 tiers:
   - Self-hosted / Open-core / Community
   - SMB / Growth / Hosted SaaS
   - Enterprise / Dedicated license
2. Record exact prices, billing periods, included agent/user quotas, and hosting requirements.

### Step 4: Community & Customer Demand Mining
1. Query community archives (e.g. Reddit via Arctic Shift API on dashboard proxy `/api/reddit/search` and `/api/reddit/comments` with `x-opc-key`).
2. Extract direct customer quotes regarding:
   - Willingness to pay vs token expense complaints.
   - Core friction points in existing market solutions.
   - Adoption criteria (e.g. deterministic reliability vs hallucinations).

---

## 📝 Evidence Log Structure

Investigations must output a structured Evidence Log organized into:
1. **Current Venture Status & Metrics**: ID, stage, website, brand measurements, search console / analytics status.
2. **Infrastructure & Live Audit Findings**: HTTP/HTTPS status, SSL certificate validity, sitemap/robots status, error codes.
3. **Internal Product Specifications & Readiness**: Slices completed, test pass rates, architectural capabilities, compute grants.
4. **Competitive Landscape & Pricing Benchmarks**: Competitor names, tiers, exact prices, billing cycles, feature quotas.
5. **Customer Demand & Market Feedback**: Sampled community posts, pain points, token cost complaints, adoption criteria.
6. **Observations, Inferences & Untested Hypotheses**: Strict separation of empirical facts from analytical deductions.
7. **Ranked Board Action Suggestions**: Concrete, prioritized, source-linked recommendations.

---

## ⚠️ Common Pitfalls

- **Confusing Codebase Readiness with Market Launch**: Having 180 passing tests does not mean the product has live users. Distinguish engineering maturity from commercial traction.
- **Scraping Direct Sites that Block Bots**: Never query reddit.com or cloudflare-protected endpoints directly if a dashboard proxy (like Arctic Shift) is available.
- **Omitting SSL Details**: Reporting "the site is down" is insufficient; verify whether the failure is DNS, port 80/443 rejection, or an SSL SAN mismatch.
