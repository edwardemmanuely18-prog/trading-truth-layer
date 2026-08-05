"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Institutional Custodian Adapter

Canonical custodian acquisition adapter.

The Custodian Adapter provides the Financial Engine entry
point for custody evidence acquisition.

Provider-specific processing is delegated to registered
custodian adapters.

The adapter itself contains no provider-specific parsing
or transformation logic.
"""

from __future__ import annotations

from typing import Any

from .base_adapter import FinancialAdapter


# ============================================================================
# Custodian Adapter
# ============================================================================


class CustodianAdapter(FinancialAdapter):
    """
    Canonical custodian acquisition adapter.

    Current Providers
    -----------------

    (Registered dynamically)

    Future
    ------

    • State Street
    • BNY Mellon
    • Northern Trust
    • J.P. Morgan Custody
    • Citi Custody
    • HSBC Custody
    • Euroclear
    • Clearstream
    • Custodian REST APIs
    • Custodian CSV
    • Custodian FIX
    """

    PROVIDER = "CUSTODIAN"

    DESCRIPTION = (
        "Institutional Custodian Adapter"
    )

    def __init__(
        self,
        connector,
    ) -> None:

        super().__init__(
            connector,
        )

        self._providers: dict[
            str,
            FinancialAdapter,
        ] = {}

    # ------------------------------------------------------------------
    # Adapter Metadata
    # ------------------------------------------------------------------

    @property
    def provider(
        self,
    ) -> str:

        return self.PROVIDER

    @property
    def description(
        self,
    ) -> str:

        return self.DESCRIPTION

    # ------------------------------------------------------------------
    # Provider Registration
    # ------------------------------------------------------------------

    def register_provider(
        self,
        provider_name: str,
        adapter: FinancialAdapter,
    ) -> None:
        """
        Register a provider-specific custodian adapter.
        """

        self._providers[
            provider_name
        ] = adapter

    # ------------------------------------------------------------------
    # Provider Discovery
    # ------------------------------------------------------------------

    def supported_providers(
        self,
    ) -> list[str]:

        return sorted(

            self._providers.keys()

        )

    def supports(
        self,
        provider_name: str,
    ) -> bool:

        return (
            provider_name
            in self._providers
        )

    # ------------------------------------------------------------------
    # Evidence Acquisition
    # ------------------------------------------------------------------

    def acquire(
        self,
        *,
        provider_name: str,
        payload: Any,
    ) -> list[Any]:
        """
        Acquire canonical custody evidence.
        """

        adapter = self._providers.get(
            provider_name,
        )

        if adapter is None:

            raise ValueError(

                f"Unsupported custodian provider: {provider_name}"

            )

        return adapter.acquire(

            payload=payload,

        )


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "CustodianAdapter",
]