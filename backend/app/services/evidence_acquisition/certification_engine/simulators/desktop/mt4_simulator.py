"""
MT4 simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MT4Simulator(BaseProviderSimulator):
    """
    MetaTrader 4 provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "mt4"

    @property
    def engine_name(self) -> str:
        return "desktop_trading_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "login",
            "password",
            "server",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "MT4 simulator is not connected."
            )

        return [
            {
                "ticket": 900001,
                "symbol": "GBPUSD",
                "side": "BUY",
                "volume": 1.20,
                "open_price": 1.28750,
                "close_price": 1.28940,
                "profit": 228.00,
                "currency": "USD",
            }
        ]


__all__ = [
    "MT4Simulator",
]