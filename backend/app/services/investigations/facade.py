from __future__ import annotations

from sqlalchemy.orm import Session

from .models import InvestigationScope
from .service import InvestigationService


class InvestigationFacade:
    """
    Canonical public interface for IIS.

    All external consumers should call this class.

    InvestigationService remains the internal orchestration
    engine.
    """

    @staticmethod
    def workspace(
        *,
        db: Session,
        workspace_id: int,
    ):
        return InvestigationService.build_workspace(
            db=db,
            workspace_id=workspace_id,
        )

    @staticmethod
    def claim(
        *,
        db: Session,
        workspace_id: int,
        claim_id: int,
    ):
        return InvestigationService.build_claim(
            db=db,
            workspace_id=workspace_id,
            claim_id=claim_id,
        )

    @staticmethod
    def member(
        *,
        db: Session,
        workspace_id: int,
        member_id: int,
    ):
        return InvestigationService.build_member(
            db=db,
            workspace_id=workspace_id,
            member_id=member_id,
        )

    @staticmethod
    def account(
        *,
        db: Session,
        workspace_id: int,
        account_id: int,
    ):
        return InvestigationService.build_account(
            db=db,
            workspace_id=workspace_id,
            account_id=account_id,
        )

    @staticmethod
    def broker(
        *,
        db: Session,
        workspace_id: int,
        broker_connection_id: int,
    ):
        return InvestigationService.build_broker(
            db=db,
            workspace_id=workspace_id,
            broker_connection_id=broker_connection_id,
        )

    @staticmethod
    def sync_job(
        *,
        db: Session,
        workspace_id: int,
        sync_job_id: int,
    ):
        return InvestigationService.build_sync_job(
            db=db,
            workspace_id=workspace_id,
            sync_job_id=sync_job_id,
        )

    @staticmethod
    def strategy(
        *,
        db: Session,
        workspace_id: int,
        strategy_id: int,
    ):
        return InvestigationService.build_strategy(
            db=db,
            workspace_id=workspace_id,
            strategy_id=strategy_id,
        )