"""
Interactive Brokers simulator for the Evidence Acquisition
Certification Engine.

This simulator emulates Interactive Brokers behaviour during
certification. It enables the Certification Engine to validate the
Desktop Trading Engine without requiring an active TWS or IB Gateway
connection.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class IBKRSimulator(BaseProviderSimulator):
    """
    Interactive Brokers provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "interactive_brokers"

    @property
    def engine_name(self) -> str:
        return "desktop_trading_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:
        """
        Simulate Interactive Brokers authentication.
        """

        required = {
            "host",
            "port",
            "client_id",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:
        """
        Produce simulated Interactive Brokers trade evidence.
        """

        if not self.connected:
            raise RuntimeError(
                "Interactive Brokers simulator is not connected."
            )

        return [
            {
                "account": "DU123456",
                "execution_id": "000001",
                "symbol": "EUR.USD",
                "asset_class": "FOREX",
                "side": "BUY",
                "quantity": 100000,
                "price": 1.10325,
                "currency": "USD",
            },
            {
                "account": "DU123456",
                "execution_id": "000002",
                "symbol": "XAUUSD",
                "asset_class": "METAL",
                "side": "SELL",
                "quantity": 50,
                "price": 3364.50,
                "currency": "USD",
            },
        ]


__all__ = [
    "IBKRSimulator",
]