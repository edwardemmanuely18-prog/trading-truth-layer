from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from .context_builder import (
    InvestigationContextBuilder,
)

from .models import (
    InvestigationReport,
    InvestigationScope,
    InvestigationStatus,
)

from .graph_builder import (
    InvestigationGraphBuilder,
)

from .relationship_engine import (
    RelationshipEngine,
)

from .timeline_engine import (
    TimelineEngine,
)

from .risk_engine import (
    RiskEngine,
)

from .critical_path import (
    CriticalPathEngine,
)

from .recommendation_engine import (
    RecommendationEngine,
)

from .summary_builder import (
    SummaryBuilder,
)


# ============================================================
# Institutional Investigation Service
# ============================================================


class InvestigationService:

    @staticmethod
    def build(
        *,
        db: Session,
        workspace_id: int,
        scope: InvestigationScope,
        scope_id: int,
    ) -> InvestigationReport:

        # =====================================================
        # Build canonical investigation snapshot
        # =====================================================

        context = InvestigationContextBuilder.build(
            db=db,
            workspace_id=workspace_id,
        )

        # =====================================================
        # Institutional Investigation Domains
        # =====================================================

        from .engines.execution_engine import ExecutionEngine
        from .engines.evidence_engine import EvidenceEngine
        from .engines.governance_engine import GovernanceEngine
        from .engines.broker_engine import BrokerEngine
        from .engines.sync_engine import SyncEngine
        from .engines.review_engine import ReviewEngine
        from .engines.behavior_engine import BehaviorEngine
        from .engines.verification_engine import VerificationEngine
        from .engines.allocator_engine import AllocatorEngine

        execution = ExecutionEngine.build(
            context=context,
        )

        evidence = EvidenceEngine.build(
            context=context,
        )

        governance = GovernanceEngine.build(
            context=context,
        )

        broker = BrokerEngine.build(
            context=context,
        )

        synchronization = SyncEngine.build(
            context=context,
        )

        review = ReviewEngine.build(
            context=context,
        )

        behavior = BehaviorEngine.build(
            context=context,
        )

        verification = VerificationEngine.build(
            context=context,
            execution=execution,
            evidence=evidence,
            governance=governance,
            broker=broker,
            synchronization=synchronization,
            review=review,
            behavior=behavior,
        )

        allocator = AllocatorEngine.build(
            execution=execution,
            evidence=evidence,
            governance=governance,
            broker=broker,
            synchronization=synchronization,
            review=review,
            behavior=behavior,
            verification=verification,
        )

        # =====================================================
        # Canonical Investigation Findings
        # =====================================================

        canonical_findings = []

        for domain in (
            execution,
            evidence,
            governance,
            broker,
            synchronization,
            review,
            behavior,
            verification,
        ):

            if domain is None:
                continue

            canonical_findings.extend(
                domain.findings,
            )

        severity_rank = {

            "CRITICAL": 0,

            "HIGH": 1,

            "MEDIUM": 2,

            "LOW": 3,

            "INFORMATION": 4,

        }

        canonical_findings.sort(

            key=lambda finding: severity_rank.get(

                finding.severity.value
                if hasattr(
                    finding.severity,
                    "value",
                )
                else str(
                    finding.severity,
                ),

                99,

            ),

        )

        # =====================================================
        # Investigation Graph
        # =====================================================

        from .graph_builder import (
            InvestigationGraphBuilder,
        )

        graph = InvestigationGraphBuilder.build(
            context,
        )

        # =====================================================
        # Relationships
        # =====================================================

        from .relationship_engine import (
            RelationshipEngine,
        )

        relationships = RelationshipEngine.build(
            context=context,
            graph=graph,
        )

        # =====================================================
        # Timeline
        # =====================================================

        from .timeline_engine import (
            TimelineEngine,
        )

        timeline = TimelineEngine.build(
            context,
        )

        # =====================================================
        # Risk Investigation
        # =====================================================

        from .risk_engine import (
            RiskEngine,
        )

        findings = RiskEngine.build(
            context=context,
            graph=graph,
            relationships=relationships,
            timeline=timeline,
        )

        # =====================================================
        # Critical Path Investigation
        # =====================================================

        from .critical_path import (
            CriticalPathEngine,
        )

        critical_path = CriticalPathEngine.build(

            graph=graph,

            relationships=relationships,

            findings=canonical_findings,

            timeline=timeline,

        )

        # =====================================================
        # Recommendations
        # =====================================================

        from .recommendation_engine import (
            RecommendationEngine,
        )

        recommendations = RecommendationEngine.build(

            findings=canonical_findings,

            critical_path=critical_path,

        )

        # =====================================================
        # Executive Summary
        # =====================================================

        from .summary_builder import (
            SummaryBuilder,
        )

        summary = SummaryBuilder.build(

            context=context,

            graph=graph,

            relationships=relationships,

            timeline=timeline,

            findings=canonical_findings,

            critical_path=critical_path,

            recommendations=recommendations,

            allocator=allocator,

        )

        canonical_findings.sort(

            key=lambda finding: (

                severity_rank.get(

                    finding.severity.value
                    if hasattr(
                        finding.severity,
                        "value",
                    )
                    else str(
                        finding.severity,
                    ),

                    99,

                ),

                finding.title,

            ),

        )

        generated_at = datetime.utcnow()

        # =====================================================
        # Canonical Investigation Report
        # =====================================================

        return InvestigationReport(

            workspace_id=workspace_id,

            scope=scope,

            scope_id=scope_id,

            status=InvestigationStatus.COMPLETE,

            generated_at=generated_at,

            summary=summary,

            graph=graph,

            nodes=graph.nodes,

            relationships=relationships,

            timeline=timeline,

            findings=canonical_findings,

            critical_path=critical_path,

            recommendations=recommendations,

            metadata={

                "generated_by":
                    "Institutional Investigation System",

                "scope":
                    scope.value,

                "generated_at":
                    generated_at.isoformat(),

                "provider_count":
                    len(
                        context.provider_payloads,
                    ),

                "provider_names":
                    sorted(
                        context.provider_payloads.keys(),
                    ),

                "total_nodes":
                    len(graph.nodes),

                "total_relationships":
                    len(graph.relationships),

                "total_findings":
                    len(canonical_findings),

                "allocator_decision":
                    allocator.decision,

            },

            execution=execution,
            evidence=evidence,
            verification=verification,
            governance=governance,
            broker=broker,
            synchronization=synchronization,
            review=review,
            behavior=behavior,
            allocator=allocator,

        )

    # =========================================================
    # Workspace Investigation
    # =========================================================

    @staticmethod
    def build_workspace(
        *,
        db: Session,
        workspace_id: int,
    ) -> InvestigationReport:

        return InvestigationService.build(
            db=db,
            workspace_id=workspace_id,
            scope=InvestigationScope.WORKSPACE,
            scope_id=workspace_id,
        )

    # =========================================================
    # Claim Investigation
    # =========================================================

    @staticmethod
    def build_claim(
        *,
        db: Session,
        workspace_id: int,
        claim_id: int,
    ) -> InvestigationReport:

        return InvestigationService.build(
            db=db,
            workspace_id=workspace_id,
            scope=InvestigationScope.CLAIM,
            scope_id=claim_id,
        )

    # =========================================================
    # Member Investigation
    # =========================================================

    @staticmethod
    def build_member(
        *,
        db: Session,
        workspace_id: int,
        member_id: int,
    ) -> InvestigationReport:

        return InvestigationService.build(
            db=db,
            workspace_id=workspace_id,
            scope=InvestigationScope.MEMBER,
            scope_id=member_id,
        )

    # =========================================================
    # Account Investigation
    # =========================================================

    @staticmethod
    def build_account(
        *,
        db: Session,
        workspace_id: int,
        account_id: int,
    ) -> InvestigationReport:

        return InvestigationService.build(
            db=db,
            workspace_id=workspace_id,
            scope=InvestigationScope.ACCOUNT,
            scope_id=account_id,
        )

    # =========================================================
    # Broker Investigation
    # =========================================================

    @staticmethod
    def build_broker(
        *,
        db: Session,
        workspace_id: int,
        broker_connection_id: int,
    ) -> InvestigationReport:

        return InvestigationService.build(
            db=db,
            workspace_id=workspace_id,
            scope=InvestigationScope.BROKER,
            scope_id=broker_connection_id,
        )

    # =========================================================
    # Sync Job Investigation
    # =========================================================

    @staticmethod
    def build_sync_job(
        *,
        db: Session,
        workspace_id: int,
        sync_job_id: int,
    ) -> InvestigationReport:

        return InvestigationService.build(
            db=db,
            workspace_id=workspace_id,
            scope=InvestigationScope.SYNC_JOB,
            scope_id=sync_job_id,
        )

    # =========================================================
    # Strategy Investigation
    # =========================================================

    @staticmethod
    def build_strategy(
        *,
        db: Session,
        workspace_id: int,
        strategy_id: int,
    ) -> InvestigationReport:

        return InvestigationService.build(
            db=db,
            workspace_id=workspace_id,
            scope=InvestigationScope.STRATEGY,
            scope_id=strategy_id,
        )