# Strategy Brief: Scaling the Internal AI Assistant, Q1 2027

**To:** Business Technology, People, Finance and Legal leadership · **Company:** Wazobia Corp *(fictional)* · **Data:** synthetic, as of Nov 20, 2026

## Bottom line

Six months after launch, *Ask Wazobia* already resolves **73%** of the questions it receives and recovers about **246 support hours a quarter**. But it only covers **half** of support demand, and adoption is concentrated in the two teams whose content is live. The next phase is not more promotion. It is **content ownership, sequencing, and a governance lane for high-risk topics.**

## Where we are

| Area | Finding | Implication |
|---|---|---|
| **Adoption** | **41%** of employees use the assistant weekly. Business Technology and Security are at **74%**; Finance, People and Legal are at **~10%**. | Usage follows content. Departments without live topics have little reason to use the assistant. |
| **Value** | **15 of 35** knowledge-base topics are live, covering **51%** of support ticket volume and deflecting about **850 tickets** a quarter. | Live content works: **90%** of rated answers are marked helpful. The constraint is coverage, not quality. |
| **Ownership** | **62%** of topics with a named curator are live; **none** of the 11 topics without one are. Those 11 hold about **130 support hours** a quarter. | Without an owner, content doesn't get built. Ownership is the single strongest predictor of delivery. |
| **Risk** | All **7** Tier 1 topics (benefits, payroll, leave, privacy requests, legal hold, card disputes, commissions) are blocked, with **20** governance controls open. They carry **705 tickets** a quarter. | High-risk topics need a dedicated review path, or they will stay blocked indefinitely. |

## Recommendations

1. **Assign a curator to every topic before building new content.** Prioritize the unowned topics with the highest demand: contract intake, expense reports, CRM access, vendor invoices. *Owner: each department head. Measure: 100% of topics owned within 30 days.*
2. **Run Wave 1: the 13 remaining Tier 2 and 3 topics**, mostly in Finance, People and Legal. They would recover about **144 hours a quarter** and lift demand coverage from 51% to about **84%**, without new governance work. *Owner: AI enablement lead. Measure: 80%+ demand coverage by end of Q1.*
3. **Stand up a Tier 1 review lane** with Legal, People and Security: weekly review, a fixed set of required controls (PII review, legal approval, escalation path, accuracy test), and no Tier 1 topic goes live until every control is complete. *Owner: Legal + People. Measure: first 3 Tier 1 topics live in Q1, with zero incidents.*
4. **Launch to each department with its content, not before.** Pair each Wave 1 release with a 15-minute demo for that team. *Owner: department champions. Measure: Finance, People and Legal reach 40% weekly active within 8 weeks of their launch.*

## How the numbers are produced

Every figure comes from [`analysis/analyze.py`](analysis/analyze.py) running on the synthetic datasets in [`data/`](data/). Support hours recoverable = tickets per quarter × the share the assistant can resolve for that risk tier × average handle time. The [live demo](https://k-b-c-04.github.io/ai-adoption-enablement/) shows the same views with filters.
