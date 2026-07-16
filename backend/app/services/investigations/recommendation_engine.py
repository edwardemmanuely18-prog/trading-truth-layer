from __future__ import annotations

from .critical_path import CriticalPath

from .risk_engine import RiskFinding

from .models import InvestigationRecommendation




# ============================================================
# Recommendation Engine
# ============================================================

class RecommendationEngine:

    @staticmethod
    def build(

        *,

        findings: list[RiskFinding],

        critical_path: CriticalPath,

    ) -> list[InvestigationRecommendation]:

        recommendations: list[
            InvestigationRecommendation
        ] = []

        seen = set()

        priority = 1

        # -----------------------------------------------
        # Root Cause Recommendation
        # -----------------------------------------------

        if critical_path.root_cause:

            recommendations.append(

                InvestigationRecommendation(

                    priority=priority,

                    title=f"Resolve {critical_path.root_cause}",

                    rationale=(
                        "This issue was identified as the primary root cause "
                        "during institutional investigation."
                    ),

                    action=(
                        "Resolve the identified root cause before relying on "
                        "investigation outputs."
                    ),

                    automated=False,

                )

            )

            priority += 1

        # -----------------------------------------------
        # Risk Findings
        # -----------------------------------------------

        severity_rank = {

            "critical": 1,

            "high": 2,

            "medium": 3,

            "low": 4,

        }

        findings = sorted(

            findings,

            key=lambda f: severity_rank.get(

                f.severity,

                5,

            ),

        )

        for finding in findings:

            if finding.recommendation in seen:

                continue

            seen.add(

                finding.recommendation

            )

            impact = {

                "critical": "Very High",

                "high": "High",

                "medium": "Medium",

                "low": "Low",

            }.get(

                finding.severity,

                "Low",

            )

            effort = {

                "critical": "High",

                "high": "Medium",

                "medium": "Medium",

                "low": "Low",

            }.get(

                finding.severity,

                "Medium",

            )

            recommendations.append(

                InvestigationRecommendation(

                    priority=priority,

                    title=finding.title,

                    rationale=(
                        finding.description
                        if finding.description
                        else "Institutional investigation identified this issue."
                    ),

                    action=(
                        finding.recommendation
                        if finding.recommendation
                        else "Review this finding before proceeding."
                    ),

                    automated=False,

                )

            )

            priority += 1

        return recommendations