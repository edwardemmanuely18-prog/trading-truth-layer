from __future__ import annotations

from datetime import datetime

from .context_builder import InvestigationContext

from .models import (
    InvestigationTimelineEvent,
    InvestigationSeverity,
)


# ============================================================
# Institutional Timeline Builder
# ============================================================

class TimelineEngine:

    @staticmethod
    def build(
        context: InvestigationContext,
    ) -> list[InvestigationTimelineEvent]:

        payloads = context.provider_payloads

        execution = payloads.get("execution")

        audit = payloads.get("audit", [])

        reviews = payloads.get("reviews", [])

        sync_jobs = payloads.get("sync_jobs", [])

        timeline: list[InvestigationTimelineEvent] = []

        # ----------------------------------------------------
        # Execution Replay
        # ----------------------------------------------------

        if execution:

            for trade in getattr(
                execution,
                "executions",
                [],
            ):

                timeline.append(

                    InvestigationTimelineEvent(

                        timestamp=getattr(
                            trade,
                            "opened_at",
                            None,
                        ),

                        category="Execution",

                        title=f"{trade.symbol} Position Opened",

                        description=(
                            f"{trade.side} position opened on "
                            f"{trade.symbol}."
                        ),

                        severity=InvestigationSeverity.INFORMATION,

                        evidence_reference=f"trade:{trade.id}",

                        metadata={

                            "trade_id": trade.id,

                            "symbol": trade.symbol,

                            "side": getattr(
                                trade,
                                "side",
                                None,
                            ),

                        },

                    )

                )

                closed = getattr(
                    trade,
                    "closed_at",
                    None,
                )

                if closed:

                    timeline.append(

                        InvestigationTimelineEvent(

                            timestamp=closed,

                            category="Execution",

                            title=f"{trade.symbol} Position Closed",

                            description=(
                                f"Position on {trade.symbol} "
                                "was closed."
                            ),

                            severity=InvestigationSeverity.INFORMATION,

                            evidence_reference=f"trade:{trade.id}",

                            metadata={

                                "trade_id": trade.id,

                                "symbol": trade.symbol,

                            },

                        )

                    )

        # ----------------------------------------------------
        # Sync Jobs
        # ----------------------------------------------------

        for job in sync_jobs:

            timeline.append(

                InvestigationTimelineEvent(

                    timestamp=getattr(
                        job,
                        "created_at",
                        None,
                    ),

                    category="Synchronization",

                    title=getattr(
                        job,
                        "job_type",
                        "Synchronization Job",
                    ),

                    description=(
                        "Broker synchronization event."
                    ),

                    severity=InvestigationSeverity.INFORMATION,

                    evidence_reference=None,

                    metadata={

                        "status": getattr(
                            job,
                            "status",
                            None,
                        ),

                    },

                )

            )

        # ----------------------------------------------------
        # Audit Events
        # ----------------------------------------------------

        for event in audit:

            timeline.append(

                InvestigationTimelineEvent(

                    timestamp=getattr(
                        event,
                        "created_at",
                        None,
                    ),

                    category="Audit",

                    title=getattr(
                        event,
                        "event_type",
                        "Audit Event",
                    ),

                    description=getattr(
                        event,
                        "description",
                        "Audit event recorded.",
                    ),

                    severity=InvestigationSeverity.INFORMATION,

                    evidence_reference=None,

                    metadata={},

                )

            )

        # ----------------------------------------------------
        # Reviews
        # ----------------------------------------------------

        for review in reviews:

            timeline.append(

                InvestigationTimelineEvent(

                    timestamp=getattr(
                        review,
                        "created_at",
                        None,
                    ),

                    category="Review",

                    title=getattr(
                        review,
                        "title",
                        "Institutional Review",
                    ),

                    description=getattr(
                        review,
                        "summary",
                        "Review activity recorded.",
                    ),

                    severity=InvestigationSeverity.INFORMATION,

                    evidence_reference=None,

                    metadata={},

                )

            )

        # ----------------------------------------------------
        # Sort
        # ----------------------------------------------------

        timeline.sort(

            key=lambda x: (
                x.timestamp is None,
                x.timestamp,
            )

        )

        return timeline