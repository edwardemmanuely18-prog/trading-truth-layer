"""
MT103 simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MT103Simulator(BaseProviderSimulator):
    """
    MT103 customer transfer simulator.
    """

    @property
    def provider_name(self) -> str:
        return "mt103"

    @property
    def engine_name(self) -> str:
        return "financial_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "bic",
            "session",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "MT103 simulator is not connected."
            )

        return [
            {
                "message_type": "MT103",
                "transaction_reference": "TRX-103001",
                "ordering_customer": "TTL CAPITAL",
                "beneficiary": "AURUM MACRO",
                "amount": 250000.00,
                "currency": "USD",
            }
        ]


__all__ = [
    "MT103Simulator",
]