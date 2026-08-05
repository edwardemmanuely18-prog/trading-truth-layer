"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Institutional Settlement Adapter

Canonical settlement acquisition adapter.

The Settlement Adapter provides the Financial Engine entry
point for settlement evidence acquisition.

Protocol-specific processing is delegated to the canonical
SWIFT Adapter.

The adapter itself contains no protocol parsing logic.
"""

from __future__ import annotations

from typing import Any

from .base_adapter import FinancialAdapter

from .swift.swift_adapter import SwiftAdapter


# ============================================================================
# Settlement Adapter
# ============================================================================


class SettlementAdapter(FinancialAdapter):
    """
    Canonical settlement acquisition adapter.

    Current Providers
    -----------------

    • SWIFT
        • MT202

    Future
    ------

    • SWIFT MT210
    • SWIFT MT900
    • SWIFT MT910
    • ISO20022 pacs.009
    • CLS
    • Euroclear
    • Clearstream
    • DTCC
    • Settlement APIs
    """

    PROVIDER = "SETTLEMENT"

    DESCRIPTION = (
        "Institutional Settlement Adapter"
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

                "MT202",

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
    # Evidence Acquisition
    # ------------------------------------------------------------------

    def acquire(
        self,
        *,
        message_type: str,
        raw_message: str,
    ) -> list[Any]:
        """
        Acquire canonical settlement evidence.

        Processing is delegated to the canonical
        SWIFT Adapter.
        """

        if not self.supports(
            message_type,
        ):

            raise ValueError(

                f"Unsupported settlement message: {message_type}"

            )

        return self._swift.acquire(

            message_type=message_type,

            raw_message=raw_message,

        )


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "SettlementAdapter",
]