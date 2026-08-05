from __future__ import annotations

"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Raw Metadata Builder

Constructs the institutional RawMetadata transport envelope used by every
RawEvidence object entering the Universal Evidence Adapter.

This builder is acquisition-engine agnostic and can therefore be reused by:

    • Desktop Trading Engine
    • Financial Engine
    • Gateway Engine

Responsibilities
----------------

• Build SynchronizationInformation
• Build ProviderInformation
• Build BrokerAccountInformation
• Build WorkspaceInformation
• Build TransportInformation
• Build SynchronizationQuality
• Produce institutional RawMetadata

The builder intentionally contains NO trading logic.
"""

from datetime import datetime
from hashlib import sha256
from typing import Any
from uuid import uuid4

from .raw_metadata import (
    BrokerAccountInformation,
    ProviderInformation,
    RawMetadata,
    SynchronizationInformation,
    SynchronizationQuality,
    TransportInformation,
    WorkspaceInformation,
)


# ============================================================================
# Raw Metadata Builder
# ============================================================================


class RawMetadataBuilder:
    """
    Canonical RawMetadata builder.

    Shared by every Evidence Acquisition engine.
    """

    TRANSPORT_VERSION = "1.0"

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self) -> None:

        pass

    # ------------------------------------------------------------------
    # Synchronization
    # ------------------------------------------------------------------

    def _build_synchronization(
        self,
        *,
        synchronization_id: str,
        synchronization_session: str,
        synchronization_batch: str,
        synchronization_sequence: int,
        synchronization_method: str,
    ) -> SynchronizationInformation:

        return SynchronizationInformation(

            synchronization_id=synchronization_id,

            synchronization_session=synchronization_session,

            synchronization_batch=synchronization_batch,

            synchronization_sequence=synchronization_sequence,

            synchronization_method=synchronization_method,
        )

    # ------------------------------------------------------------------
    # Provider
    # ------------------------------------------------------------------

    def _build_provider(
        self,
        *,
        provider_name: str,
        provider_platform: str,
        provider_version: str | None,
        broker_company: str | None,
        broker_server: str | None,
    ) -> ProviderInformation:

        return ProviderInformation(

            provider_name=provider_name,

            provider_platform=provider_platform,

            provider_version=provider_version,

            broker_company=broker_company,

            broker_server=broker_server,
        )

    # ------------------------------------------------------------------
    # Broker Account
    # ------------------------------------------------------------------

    def _build_account(
        self,
        *,
        broker_account_id: str,
        broker_account_name: str | None,
        broker_account_type: str | None,
        account_state: str,
        account_currency: str | None,
        leverage: str | None,
    ) -> BrokerAccountInformation:

        return BrokerAccountInformation(

            broker_account_id=broker_account_id,

            broker_account_name=broker_account_name,

            broker_account_type=broker_account_type,

            account_state=account_state,

            account_currency=account_currency,

            leverage=leverage,
        )

    # ------------------------------------------------------------------
    # Workspace
    # ------------------------------------------------------------------

    def _build_workspace(
        self,
        *,
        workspace_id: int | None,
        workspace_name: str | None,
        organization_id: str | None,
        provider_id: str | None,
    ) -> WorkspaceInformation:

        return WorkspaceInformation(

            workspace_id=workspace_id,

            workspace_name=workspace_name,

            organization_id=organization_id,

            provider_id=provider_id,
        )

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    def _build_transport(
        self,
        *,
        desktop_engine_version: str | None,
        payload_hash: str | None,
        evidence_hash: str | None,
        payload_size: int | None,
    ) -> TransportInformation:

        return TransportInformation(

            transport_version=self.TRANSPORT_VERSION,

            desktop_engine_version=desktop_engine_version,

            payload_hash=payload_hash,

            evidence_hash=evidence_hash,

            payload_size=payload_size,
        )

    # ------------------------------------------------------------------
    # Quality
    # ------------------------------------------------------------------

    def _build_quality(
        self,
    ) -> SynchronizationQuality:

        return SynchronizationQuality()

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def generate_identifier() -> str:
        """
        Generate a canonical UUID identifier.
        """

        return str(uuid4())

    @staticmethod
    def hash_payload(
        payload: Any,
    ) -> str:
        """
        Compute a SHA-256 hash for transport payloads.
        """

        return sha256(
            repr(payload).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def payload_size(
        payload: Any,
    ) -> int:
        """
        Compute serialized payload size in bytes.
        """

        return len(
            repr(payload).encode("utf-8")
        )

    @staticmethod
    def utcnow() -> datetime:
        """
        Canonical UTC timestamp helper.
        """

        return datetime.utcnow()

        # ------------------------------------------------------------------
    # Public Builder
    # ------------------------------------------------------------------

    def build(
        self,
        *,
        provider_name: str,
        provider_platform: str,
        provider_version: str | None,
        broker_company: str |None,
        broker_server: str | None,
        broker_account_id: str,
        broker_account_name: str | None,
        broker_account_type: str | None,
        account_state: str,
        account_currency: str | None,
        leverage: str | None,
        workspace_id: int | None,
        workspace_name: str | None,
        organization_id: str | None,
        provider_id: str | None,
        synchronization_id: str,
        synchronization_session: str,
        synchronization_batch: str,
        synchronization_sequence: int,
        synchronization_method: str,
        desktop_engine_version: str | None,
        payload_hash: str | None,
        evidence_hash: str | None,
        payload_size: int | None,
        additional_metadata: dict[str, Any] | None = None,
    ) -> RawMetadata:
        """
        Construct a complete RawMetadata object.
        """

        metadata = RawMetadata(

            synchronization=self._build_synchronization(

                synchronization_id=synchronization_id,

                synchronization_session=synchronization_session,

                synchronization_batch=synchronization_batch,

                synchronization_sequence=synchronization_sequence,

                synchronization_method=synchronization_method,
            ),

            provider=self._build_provider(

                provider_name=provider_name,

                provider_platform=provider_platform,

                provider_version=provider_version,

                broker_company=broker_company,

                broker_server=broker_server,
            ),

            account=self._build_account(

                broker_account_id=broker_account_id,

                broker_account_name=broker_account_name,

                broker_account_type=broker_account_type,

                account_state=account_state,

                account_currency=account_currency,

                leverage=leverage,
            ),

            workspace=self._build_workspace(

                workspace_id=workspace_id,

                workspace_name=workspace_name,

                organization_id=organization_id,

                provider_id=provider_id,
            ),

            transport=self._build_transport(

                desktop_engine_version=desktop_engine_version,

                payload_hash=payload_hash,

                evidence_hash=evidence_hash,

                payload_size=payload_size,
            ),

            quality=self._build_quality(),

            additional_metadata=additional_metadata or {},
        )

        issues = metadata.validate()

        if issues:

            raise ValueError(

                "Invalid RawMetadata:\n"

                + "\n".join(issues)

            )

        return metadata

    # ------------------------------------------------------------------
    # Default Builder
    # ------------------------------------------------------------------

    def build_defaults(
        self,
        *,
        provider_name: str,
        provider_platform: str,
        provider_version: str | None,
        broker_company: str | None,
        broker_server: str | None,
        broker_account_id: str,
        broker_account_name: str | None,
        broker_account_type: str | None,
        account_state: str,
        account_currency: str | None,
        leverage: str | None,
        desktop_engine_version: str | None,
        payload: Any,
        workspace_id: int | None = None,
        workspace_name: str | None = None,
        organization_id: str | None = None,
        provider_id: str | None = None,
        synchronization_method: str = "desktop_sync",
        additional_metadata: dict[str, Any] | None = None,
    ) -> RawMetadata:
        """
        Build RawMetadata using automatically generated
        synchronization identifiers and transport metrics.
        """

        payload_hash = self.hash_payload(
            payload,
        )

        return self.build(

            provider_name=provider_name,

            provider_platform=provider_platform,

            provider_version=provider_version,

            broker_company=broker_company,

            broker_server=broker_server,

            broker_account_id=broker_account_id,

            broker_account_name=broker_account_name,

            broker_account_type=broker_account_type,

            account_state=account_state,

            account_currency=account_currency,

            leverage=leverage,

            workspace_id=workspace_id,

            workspace_name=workspace_name,

            organization_id=organization_id,

            provider_id=provider_id,

            synchronization_id=self.generate_identifier(),

            synchronization_session=self.generate_identifier(),

            synchronization_batch=self.generate_identifier(),

            synchronization_sequence=1,

            synchronization_method=synchronization_method,

            desktop_engine_version=desktop_engine_version,

            payload_hash=payload_hash,

            evidence_hash=payload_hash,

            payload_size=self.payload_size(
                payload,
            ),

            additional_metadata=additional_metadata,
        )


# ============================================================================
# Global Builder
# ============================================================================

raw_metadata_builder = RawMetadataBuilder()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [

    "RawMetadataBuilder",

    "raw_metadata_builder",
]