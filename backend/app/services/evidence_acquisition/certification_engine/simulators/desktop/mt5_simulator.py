"""
MT5 simulator for the Evidence Acquisition Certification Engine.

This simulator emulates MetaTrader 5 behaviour during certification.
It allows the Certification Engine to verify that the Desktop Trading
Engine correctly implements the TTL Synchronization Contract without
requiring a live MT5 terminal.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class MT5Simulator(BaseProviderSimulator):
    """
    MetaTrader 5 provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "mt5"

    @property
    def engine_name(self) -> str:
        return "desktop_trading_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:
        """
        Simulate MT5 authentication.
        """

        required = {
            "login",
            "password",
            "server",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:
        """
        Produce simulated MT5 trade evidence.
        """

        if not self.connected:
            raise RuntimeError(
                "MT5 simulator is not connected."
            )

        return [
            {
                "ticket": 100001,
                "symbol": "EURUSD",
                "side": "BUY",
                "volume": 1.00,
                "open_price": 1.10250,
                "close_price": 1.10420,
                "profit": 170.00,
                "currency": "USD",
            },
            {
                "ticket": 100002,
                "symbol": "XAUUSD",
                "side": "SELL",
                "volume": 0.50,
                "open_price": 3362.10,
                "close_price": 3358.60,
                "profit": 175.00,
                "currency": "USD",
            },
        ]


__all__ = [
    "MT5Simulator",
]