"""
MT940 simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MT940Simulator(BaseProviderSimulator):
    """
    MT940 account statement simulator.
    """

    @property
    def provider_name(self) -> str:
        return "mt940"

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
                "MT940 simulator is not connected."
            )

        return [
            {
                "message_type": "MT940",
                "statement_reference": "STM-940001",
                "account": "100000001",
                "opening_balance": 1200000.00,
                "closing_balance": 1250000.00,
                "currency": "USD",
            }
        ]


__all__ = [
    "MT940Simulator",
]