"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Raw Evidence Engine

Transforms DesktopEvidencePackage into broker-neutral RawEvidence
objects exchanged between the Evidence Acquisition subsystem and the
Universal Evidence Adapter.
"""

from __future__ import annotations

from typing import Any

from backend.app.services.evidence_acquisition.desktop_trading_engine.models import (
    DesktopEvidencePackage,
)

from backend.app.services.universal_evidence_adapter.domain.transport.raw_evidence import (
    EvidenceStatus,
    EvidenceType,
    RawEvidence,
)

from backend.app.services.universal_evidence_adapter.domain.transport.raw_metadata import (
    RawMetadata,
)

from backend.app.services.universal_evidence_adapter.domain.transport.raw_metadata_builder import (
    RawMetadataBuilder,
    raw_metadata_builder,
)


# ============================================================================
# Raw Evidence Engine
# ============================================================================


class RawEvidenceEngine:
    """
    Converts DesktopEvidencePackage into RawEvidence.

    This engine contains no provider-specific acquisition logic.

    Provider acquisition has already completed inside the Desktop
    Trading Engine.

    The responsibility of this engine is to transform canonical desktop
    evidence into broker-neutral RawEvidence transport objects for the
    Universal Evidence Adapter.
    """

    def __init__(
        self,
        metadata_builder: RawMetadataBuilder | None = None,
    ) -> None:

        self.metadata_builder = (
            metadata_builder
            or raw_metadata_builder
        )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def _build_metadata(
        self,
        *,
        package: DesktopEvidencePackage,
        payload: Any,
    ) -> RawMetadata:
        """
        Build the canonical RawMetadata transport envelope.
        """

        broker = package.broker
        server = package.server
        account = package.account

        return self.metadata_builder.build_defaults(

            provider_name=package.connector_name,

            provider_platform="Desktop Trading Engine",

            provider_version=package.connector_version,

            broker_company=(
                broker.legal_name
                if broker is not None
                else None
            ),

            broker_server=(
                server.server_name
                if server is not None
                else None
            ),

            broker_account_id=(
                account.broker_account_id
                if account is not None
                else "unknown"
            ),

            broker_account_name=(
                account.account_name
                if account is not None
                else None
            ),

            broker_account_type=(
                account.account_type
                if account is not None
                else None
            ),

            account_state=(
                account.account_state.value
                if account is not None
                else "UNKNOWN"
            ),

            account_currency=(
                account.currency
                if account is not None
                else None
            ),

            leverage=(
                str(account.leverage)
                if (
                    account is not None
                    and account.leverage is not None
                )
                else None
            ),

            desktop_engine_version=package.connector_version,

            payload=payload,

            additional_metadata={

                "connector_name": package.connector_name,

                "connector_version": package.connector_version,

                "schema_version": package.schema_version,

                "synchronization_id": package.synchronization_id,
            },
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(
        self,
        package: DesktopEvidencePackage,
    ) -> list[RawEvidence]:
        """
        Convert a DesktopEvidencePackage into RawEvidence.
        """

        evidence: list[RawEvidence] = []

        evidence.extend(
            self._build_infrastructure(package)
        )

        evidence.extend(
            self._build_financial(package)
        )

        evidence.extend(
            self._build_market(package)
        )

        evidence.extend(
            self._build_trading(package)
        )

        return evidence

        # ------------------------------------------------------------------
    # Terminal
    # ------------------------------------------------------------------

    def _build_terminal(
        self,
        package: DesktopEvidencePackage,
    ) -> list[RawEvidence]:

        terminal = package.terminal

        if terminal is None:
            return []

        payload = {

            "terminal_id": terminal.terminal_id,
            "terminal_name": terminal.terminal_name,
            "platform_build": terminal.platform_build,
            "platform_version": terminal.platform_version,
            "executable_path": terminal.executable_path,
            "installation_directory": terminal.installation_directory,
            "operating_system": terminal.operating_system,
            "architecture": terminal.architecture,
            "language": terminal.language,
            "timezone": terminal.timezone,
            "connection_status": terminal.connection_status.value,
            "session_id": terminal.session_id,
            "session_active": terminal.session_active,
            "ping": terminal.ping,
            "raw": terminal.raw,
        }

        metadata = self._build_metadata(
            package=package,
            payload=payload,
        )

        return [

            RawEvidence(

                evidence_type=EvidenceType.CUSTOM,

                status=EvidenceStatus.NEW,

                metadata=metadata,

                raw_payload=payload,
            )

        ]

    # ------------------------------------------------------------------
    # Broker
    # ------------------------------------------------------------------

    def _build_broker(
        self,
        package: DesktopEvidencePackage,
    ) -> list[RawEvidence]:

        broker = package.broker

        if broker is None:
            return []

        payload = {

            "broker_id": broker.broker_id,
            "broker_name": broker.broker_name,
            "legal_name": broker.legal_name,
            "country": broker.country,
            "regulator": broker.regulator,
            "website": broker.website,
            "support_email": broker.support_email,
            "support_phone": broker.support_phone,
            "raw": broker.raw,
        }

        metadata = self._build_metadata(
            package=package,
            payload=payload,
        )

        return [

            RawEvidence(

                evidence_type=EvidenceType.CUSTOM,

                status=EvidenceStatus.NEW,

                metadata=metadata,

                raw_payload=payload,
            )

        ]

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------

    def _build_server(
        self,
        package: DesktopEvidencePackage,
    ) -> list[RawEvidence]:

        server = package.server

        if server is None:
            return []

        payload = {

            "server_id": server.server_id,
            "server_name": server.server_name,
            "server_location": server.server_location,
            "server_timezone": server.server_timezone,
            "trade_server": server.trade_server,
            "access_server": server.access_server,
            "raw": server.raw,
        }

        metadata = self._build_metadata(
            package=package,
            payload=payload,
        )

        return [

            RawEvidence(

                evidence_type=EvidenceType.CUSTOM,

                status=EvidenceStatus.NEW,

                metadata=metadata,

                raw_payload=payload,
            )

        ]

    # ------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------

    def _build_account(
        self,
        package: DesktopEvidencePackage,
    ) -> list[RawEvidence]:

        account = package.account

        if account is None:
            return []

        payload = {

            "broker_account_id": account.broker_account_id,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "account_state": account.account_state.value,
            "currency": account.currency,
            "leverage": account.leverage,
            "balance": account.balance,
            "equity": account.equity,
            "margin": account.margin,
            "free_margin": account.free_margin,
            "margin_level": account.margin_level,
            "credit": account.credit,
            "raw": account.raw,
        }

        metadata = self._build_metadata(
            package=package,
            payload=payload,
        )

        return [

            RawEvidence(

                evidence_type=EvidenceType.ACCOUNT,

                status=EvidenceStatus.NEW,

                metadata=metadata,

                raw_payload=payload,
            )

        ]

    # ------------------------------------------------------------------
    # Infrastructure
    # ------------------------------------------------------------------

    def _build_infrastructure(
        self,
        package: DesktopEvidencePackage,
    ) -> list[RawEvidence]:

        evidence: list[RawEvidence] = []

        evidence.extend(
            self._build_terminal(package)
        )

        evidence.extend(
            self._build_broker(package)
        )

        evidence.extend(
            self._build_server(package)
        )

        evidence.extend(
            self._build_account(package)
        )

        return evidence

        # ------------------------------------------------------------------
    # Financial
    # ------------------------------------------------------------------

    def _build_financial(
        self,
        package: DesktopEvidencePackage,
    ) -> list[RawEvidence]:
        """
        Financial evidence conversion.

        Placeholder implementation until the financial evidence
        translators are completed.
        """

        return []

    # ------------------------------------------------------------------
    # Market
    # ------------------------------------------------------------------

    def _build_market(
        self,
        package: DesktopEvidencePackage,
    ) -> list[RawEvidence]:
        """
        Market evidence conversion.

        Placeholder implementation until market evidence
        translators are completed.
        """

        return []

    # ------------------------------------------------------------------
    # Trading
    # ------------------------------------------------------------------

    def _build_trading(
        self,
        package: DesktopEvidencePackage,
    ) -> list[RawEvidence]:
        """
        Trading evidence conversion.

        Placeholder implementation until trading evidence
        translators are completed.
        """

        return []


# ============================================================================
# Global Engine
# ============================================================================

raw_evidence_engine = RawEvidenceEngine()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "RawEvidenceEngine",
    "raw_evidence_engine",
]