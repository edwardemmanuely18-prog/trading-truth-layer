"""
MultiCharts simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MultiChartsSimulator(BaseProviderSimulator):
    """
    MultiCharts provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "multicharts"

    @property
    def engine_name(self) -> str:
        return "desktop_trading_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "workspace",
            "username",
            "password",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "MultiCharts simulator is not connected."
            )

        return [
            {
                "execution_id": "MC-10001",
                "symbol": "ESU26",
                "side": "BUY",
                "quantity": 1,
                "price": 6495.25,
                "currency": "USD",
            }
        ]


__all__ = [
    "MultiChartsSimulator",
]