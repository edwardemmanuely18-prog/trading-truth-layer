"""
Treasury simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class TreasurySimulator(BaseProviderSimulator):
    """
    Treasury provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "treasury"

    @property
    def engine_name(self) -> str:
        return "financial_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "treasury_id",
            "username",
            "password",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "Treasury simulator is not connected."
            )

        return [
            {
                "treasury_account": "TR-10001",
                "currency": "USD",
                "cash_position": 5000000.00,
                "available_liquidity": 4750000.00,
                "valuation_date": "2026-07-31",
            }
        ]


__all__ = [
    "TreasurySimulator",
]