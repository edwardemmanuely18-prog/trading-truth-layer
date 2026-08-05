"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Institutional Bank Adapter

Canonical banking acquisition adapter.

The Bank Adapter provides the Financial Engine entry point for
banking evidence acquisition.

Protocol-specific processing is delegated to the canonical
SWIFT Adapter.

The adapter itself contains no protocol parsing logic.
"""

from __future__ import annotations

from typing import Any

from .base_adapter import FinancialAdapter

from .swift.swift_adapter import SwiftAdapter


# ============================================================================
# Bank Adapter
# ============================================================================


class BankAdapter(FinancialAdapter):
    """
    Canonical banking acquisition adapter.

    Current Providers
    -----------------

    • SWIFT
        • MT940

    Future
    ------

    • SWIFT MT942
    • ISO20022 CAMT.052
    • ISO20022 CAMT.053
    • ISO20022 CAMT.054
    • Open Banking APIs
    • Bank Statement CSV
    • Bank Statement PDF
    """

    PROVIDER = "BANK"

    DESCRIPTION = (
        "Institutional Banking Adapter"
    )

    def __init__(
        self,
        connector,
    ) -> None:

        super().__init__(
            connector,
        )

        self._swift = SwiftAdapter(
            connector,
        )

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
    # Provider Discovery
    # ------------------------------------------------------------------

    def supported_message_types(
        self,
    ) -> list[str]:

        return [

            message_type

            for message_type in self._swift.supported_message_types()

            if message_type in {

                "MT940",

            }

        ]

    def supports(
        self,
        message_type: str,
    ) -> bool:

        return (
            message_type
            in self.supported_message_types()
        )

    # ------------------------------------------------------------------
    # Acquisition
    # ------------------------------------------------------------------

    def acquire(
        self,
        *,
        message_type: str,
        raw_message: str,
    ) -> list[Any]:
        """
        Acquire canonical banking evidence.

        Processing is delegated to the canonical
        SWIFT Adapter.
        """

        if not self.supports(
            message_type,
        ):

            raise ValueError(

                f"Unsupported banking message: {message_type}"

            )

        return self._swift.acquire(

            message_type=message_type,

            raw_message=raw_message,

        )


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "BankAdapter",
]