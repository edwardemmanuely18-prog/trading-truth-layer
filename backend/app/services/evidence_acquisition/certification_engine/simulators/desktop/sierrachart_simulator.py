"""
Sierra Chart simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class SierraChartSimulator(BaseProviderSimulator):
    """
    Sierra Chart provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "sierrachart"

    @property
    def engine_name(self) -> str:
        return "desktop_trading_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "username",
            "password",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "Sierra Chart simulator is not connected."
            )

        return [
            {
                "order_id": 50001,
                "symbol": "NQU26",
                "side": "SELL",
                "quantity": 3,
                "price": 24486.25,
                "currency": "USD",
            }
        ]


__all__ = [
    "SierraChartSimulator",
]