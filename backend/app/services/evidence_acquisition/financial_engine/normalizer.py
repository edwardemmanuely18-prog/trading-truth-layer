"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Canonical Financial Evidence Normalizer

Normalizes provider acquisition payloads into the canonical
Financial Engine acquisition contract.

The normalizer performs NO:

    • Translation
    • Validation
    • Verification
    • Business Logic

It only guarantees a provider-independent acquisition surface.
"""

from __future__ import annotations

from typing import Any, Dict


class FinancialEvidenceNormalizer:
    """
    Canonical Financial Evidence Normalizer.

    Every financial provider must pass through this layer before
    translation.

    This guarantees that every downstream component receives an
    identical acquisition payload regardless of provider.
    """

    DEFAULT_SCHEMA_VERSION = "1.0"

    def normalize(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize a provider acquisition payload.

        Missing sections are replaced with sensible defaults while
        preserving native provider objects.
        """

        payload = dict(payload)

        return {

            # ----------------------------------------------------------
            # Connector Metadata
            # ----------------------------------------------------------

            "connector_name": payload.get(
                "connector_name"
            ),

            "connector_version": payload.get(
                "connector_version"
            ),

            "schema_version": payload.get(
                "schema_version",
                self.DEFAULT_SCHEMA_VERSION,
            ),

            # ----------------------------------------------------------
            # Institution
            # ----------------------------------------------------------

            "institution": payload.get(
                "institution"
            ),

            "account": payload.get(
                "account"
            ),

            # ----------------------------------------------------------
            # Financial Evidence
            # ----------------------------------------------------------

            "cash_balances": payload.get(
                "cash_balances"
            ) or [],

            "cash_transfers": payload.get(
                "cash_transfers"
            ) or [],

            "settlement_instructions": payload.get(
                "settlement_instructions"
            ) or [],

            "settlement_confirmations": payload.get(
                "settlement_confirmations"
            ) or [],

            "custody_holdings": payload.get(
                "custody_holdings"
            ) or [],

            "funding_events": payload.get(
                "funding_events"
            ) or [],

            "corporate_actions": payload.get(
                "corporate_actions"
            ) or [],

            "bank_statements": payload.get(
                "bank_statements"
            ) or [],

            "letters_of_credit": payload.get(
                "letters_of_credit"
            ) or [],

            "bank_guarantees": payload.get(
                "bank_guarantees"
            ) or [],

            "collateral": payload.get(
                "collateral"
            ) or [],

            "margin": payload.get(
                "margin"
            ) or [],

            "payments": payload.get(
                "payments"
            ) or [],

            # ----------------------------------------------------------
            # Replay Metadata
            # ----------------------------------------------------------

            "replay_session": payload.get(
                "replay_session"
            ),
            }
       


financial_evidence_normalizer = FinancialEvidenceNormalizer()


__all__ = [
    "FinancialEvidenceNormalizer",
    "financial_evidence_normalizer",
]