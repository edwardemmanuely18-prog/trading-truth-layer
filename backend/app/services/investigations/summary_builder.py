from __future__ import annotations

from .models import (
    InvestigationDecision,
    InvestigationRecommendation,
    InvestigationSeverity,
    InvestigationSummary,
    InvestigationFinding,
)

from .critical_path import CriticalPath
from .context_builder import (
    InvestigationContext,
)
from .graph_builder import InvestigationGraph
from .relationship_engine import RelationshipFinding


from .models import (
    InvestigationTimelineEvent,
)




# ============================================================
# Summary Builder
# ============================================================

class SummaryBuilder:

    @staticmethod
    def build(

        *,

        context: InvestigationContext,

        graph: InvestigationGraph,

        relationships: list[RelationshipFinding],

        timeline: list[InvestigationTimelineEvent],

        findings: list[InvestigationFinding],

        critical_path: CriticalPath,

        recommendations: list[
            InvestigationRecommendation
        ],

        allocator: InvestigationDecision,

    ) -> InvestigationSummary:

        graph_summary = (

            f"{len(graph.nodes)} entities linked by "

            f"{len(graph.relationships)} relationships."

        )

        timeline_summary = (

            f"{len(timeline)} chronological "

            "events reconstructed."

        )

        risk_summary = (

            f"{len(findings)} investigation "

            "risk finding(s) detected."

        )

        severity_rank = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3,
            "information": 4,
            "info": 4,
        }

        ranked_findings = sorted(
            findings,
            key=lambda finding: severity_rank.get(
                str(finding.severity).lower(),
                99,
            ),
        )

        top_findings = ranked_findings[:3]

        recommendation_summary = (

            f"{len(recommendations)} "

            "recommended remediation action(s)."

        )

        executive = (

            f"The investigation completed with "

            f"a confidence score of "

            f"{allocator.confidence:.2f}. "

            f"The primary root cause is "

            f"'{critical_path.root_cause}'. "

            f"{len(findings)} significant "

            f"finding(s) require attention."

        )

        finding_summary = (
            "; ".join(
                finding.title
                for finding in top_findings
            )
            if top_findings
            else "No material investigation findings."
        )

        executive = (

            f"The institutional investigation completed with "

            f"{allocator.confidence:.2f}% confidence "

            f"and an allocator decision of "

            f"{allocator.decision}. "

            f"Primary root cause: "

            f"{critical_path.root_cause}. "

            f"{len(findings)} findings were generated "

            f"across {len(graph.nodes)} investigation "

            f"entities. "

            f"Highest priority findings: "

            f"{finding_summary}."

        )

        critical_count = sum(
            1
            for finding in findings
            if finding.severity.lower() == "critical"
        )

        high_count = sum(
            1
            for finding in findings
            if finding.severity.lower() == "high"
        )

        medium_count = sum(
            1
            for finding in findings
            if finding.severity.lower() == "medium"
        )

        low_count = sum(
            1
            for finding in findings
            if finding.severity.lower() == "low"
        )

        info_count = sum(
            1
            for finding in findings
            if finding.severity.lower()
            in (
                "information",
                "info",
            )
        )

        if critical_count:

            overall_risk = InvestigationSeverity.CRITICAL

        elif high_count:

            overall_risk = InvestigationSeverity.HIGH

        elif medium_count:

            overall_risk = InvestigationSeverity.MEDIUM

        elif low_count:

            overall_risk = InvestigationSeverity.LOW

        else:

            overall_risk = InvestigationSeverity.INFORMATION

        return InvestigationSummary(

            investigation_confidence=allocator.confidence,

            total_findings=len(findings),

            critical_findings=critical_count,

            high_findings=high_count,

            medium_findings=medium_count,

            low_findings=low_count,

            informational_findings=info_count,

            evidence_nodes=len(graph.nodes),

            relationships=len(graph.relationships),

            timeline_events=len(timeline),

            affected_claims=len(
                context.provider_payloads.get(
                    "claims",
                    [],
                ),
            ),

            affected_members=len(
                context.provider_payloads.get(
                    "members",
                    [],
                ),
            ),

            affected_accounts=len(
                context.provider_payloads.get(
                    "sync",
                    {},
                ).get(
                    "broker_connections",
                    [],
                ),
            ),

            affected_sync_jobs=len(
                context.provider_payloads.get(
                    "sync",
                    {},
                ).get(
                    "jobs",
                    [],
                ),
            ),

            overall_risk=overall_risk,

            executive_summary=executive,

        )