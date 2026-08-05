"""
Settlement simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class SettlementSimulator(BaseProviderSimulator):
    """
    Settlement provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "settlement"

    @property
    def engine_name(self) -> str:
        return "financial_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "settlement_id",
            "access_token",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "Settlement simulator is not connected."
            )

        return [
            {
                "settlement_reference": "SET-100001",
                "trade_reference": "TRD-500001",
                "currency": "USD",
                "gross_amount": 100000.00,
                "net_amount": 99850.00,
                "status": "SETTLED",
            }
        ]


__all__ = [
    "SettlementSimulator",
]