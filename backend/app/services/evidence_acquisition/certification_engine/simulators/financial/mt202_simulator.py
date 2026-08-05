"""
MT202 simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MT202Simulator(BaseProviderSimulator):
    """
    MT202 bank transfer simulator.
    """

    @property
    def provider_name(self) -> str:
        return "mt202"

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
                "MT202 simulator is not connected."
            )

        return [
            {
                "message_type": "MT202",
                "transaction_reference": "TRX-202001",
                "ordering_bank": "TTL BANK",
                "beneficiary_bank": "AURUM BANK",
                "amount": 1000000.00,
                "currency": "USD",
            }
        ]


__all__ = [
    "MT202Simulator",
]