# Institutional Market Interview

## Interview Information

**Date:** 2026-08-04

**Interviewee:** Patrick Hidalgo

**Role:** Hedge Fund Manager

**Current Position:** Managing an Incubator Fund

**Source:** LinkedIn Direct Conversation

---

# Conversation Context

After Patrick accepted my LinkedIn connection request, I introduced Trading Truth Layer (TTL) as an institutional trust infrastructure focused on independently governed and verifiable evidence for capital markets.

I asked:

> "If you could improve one aspect of how allocators evaluate hedge funds today, what would it be?"

Patrick replied:

> "I am managing an incubator fund at the moment and can't exactly tell you. My guess is that the hardest part is finding them."

---

# Direct Observation

Patrick did not identify due diligence, verification, or reporting as the primary challenge.

Instead, he immediately pointed to an earlier stage of the investment lifecycle:

**Finding investment opportunities.**

This suggests that from the perspective of an incubator fund manager, deal sourcing may represent a greater operational constraint than allocator due diligence.

---

# Research Insight

Different participants within capital markets experience "trust" at different stages of the investment lifecycle.

For example:

- Incubator Funds → Finding promising investment opportunities.
- Allocators → Assessing whether managers can be trusted.
- Hedge Funds → Demonstrating credibility to potential investors.
- Auditors → Verifying controls and evidence.
- Compliance Teams → Ensuring governance and regulatory adherence.

This reinforces that trust is not a single problem.

It is experienced differently depending on the participant's role.

---

# Implications for Trading Truth Layer

The conversation reinforces an important architectural principle:

Trading Truth Layer should not assume that every participant enters the trust process at the same point.

Different institutional participants require different trust services.

Examples include:

- Discovery Trust
- Verification Trust
- Due Diligence Trust
- Governance Trust
- Operational Trust
- Ongoing Monitoring Trust

The platform architecture should ultimately support trust across the entire institutional lifecycle rather than focusing exclusively on post-discovery due diligence.

---

# Key Quote

> "My guess is that the hardest part is finding them."

---

# TTL Research Notes

This conversation contributes to a growing body of institutional interviews indicating that trust challenges vary significantly across ecosystem participants.

Rather than treating "trust" as a single capability, TTL should continue mapping trust requirements by participant type.

Future interviews should continue documenting:

- Participant role
- Primary pain points
- Current workflows
- Existing trust mechanisms
- Remaining trust gaps
- Architectural implications for TTL

---

# Interview Status

Type: Exploratory Market Discovery

Relationship Status: First Connection

Potential Future Engagement:
- Continue relationship through LinkedIn.
- Share future TTL thought leadership where relevant.
- Explore deeper discussion if Patrick's incubator fund begins evaluating managers or institutional verification workflows.




# Architectural Insights Derived from the Conversation

The following insights were derived from reflecting on Patrick's response and its implications for the long-term evolution of Trading Truth Layer.

---

## Insight 1 — Verification Is Not Always the First Problem

Patrick's response did not focus on due diligence, reporting, governance, or verification.

Instead, he immediately identified an earlier challenge:

> "The hardest part is finding them."

This highlights an important institutional reality.

For many capital allocators and incubator funds, the first challenge is not determining whether evidence can be trusted—it is discovering investment opportunities in the first place.

This reinforces that verification is only one stage within a much larger institutional workflow.

Institutional lifecycle:

```
Discover Opportunities
        ↓
Screen Opportunities
        ↓
Perform Due Diligence
        ↓
Verify Evidence
        ↓
Allocate Capital
        ↓
Monitor Continuously
```

Trading Truth Layer currently operates primarily from the Due Diligence and Verification stages onward.

---

## Insight 2 — Clearly Defining Where TTL Operates

This conversation reinforces the importance of precisely defining where Trading Truth Layer fits within institutional workflows.

Rather than positioning TTL as solving every trust problem in capital markets, it should be viewed as infrastructure that begins once an institution has identified an opportunity requiring evaluation.

A simplified institutional workflow becomes:

```
Institutional Discovery
        ↓
Institutional Screening
        ↓
Trading Truth Layer
        ↓
Evidence Collection
        ↓
Evidence Verification
        ↓
Governance Assessment
        ↓
Allocator Decision
        ↓
Continuous Monitoring
```

This positioning provides significantly greater architectural clarity and avoids attempting to solve problems outside TTL's current scope.

---

## Insight 3 — Long-Term Expansion Toward Institutional Discovery

Although Patrick's response focused on discovery rather than verification, it revealed a potential long-term evolution for TTL.

Once a global verification infrastructure exists, TTL could eventually support trusted discovery itself.

For example, instead of manually searching for investment managers, an allocator could discover institutions that already possess independently verified evidence.

Potential future capabilities include:

- Verified Hedge Funds
- Verified Asset Managers
- Verified Prop Firms
- Verified Traders
- Verified Brokers
- Verified Administrators
- Verified Auditors
- Verified Due Diligence Providers

Rather than simply verifying entities after discovery, TTL could ultimately become infrastructure that enables trusted institutional discovery.

---

## Insight 4 — A Verified Institutional Discovery Network

Building on the previous insight, a mature version of TTL could allow allocators to search the global verification network using institutional-quality filters.

Example:

```
Find investment managers satisfying:

• Maximum Drawdown < 8%
• Verified Broker
• Verified Execution Records
• Verified Governance
• No Outstanding Disputes
• Verification Score > 92
• Evidence Freshness < 7 Days
```

TTL could then return institutions satisfying these criteria.

At this stage, Trading Truth Layer evolves beyond a verification platform.

It becomes a searchable global trust infrastructure for institutional capital allocation.

---

## Insight 5 — Improving Future Institutional Interviews

Patrick's response also highlights an opportunity to improve the institutional interview process itself.

Rather than only asking participants:

> "What is the biggest challenge?"

Future interviews should also determine where that challenge occurs within the institutional lifecycle.

Example research question:

```
At which stage does your greatest challenge occur?

□ Discovery

□ Opportunity Screening

□ Due Diligence

□ Evidence Verification

□ Governance

□ Capital Allocation

□ Monitoring

□ Reporting
```

Collecting structured responses from hedge fund managers, allocators, auditors, compliance officers, brokers, fund administrators, and other institutional participants will allow TTL to build an evidence-based understanding of where trust problems actually exist across the capital markets ecosystem.

This approach transforms qualitative interviews into structured research capable of directly informing future product architecture.