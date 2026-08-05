"""
Binance simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class BinanceSimulator(BaseProviderSimulator):

    @property
    def provider_name(self) -> str:
        return "binance"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        return {
            "api_key",
            "secret_key",
        }.issubset(credentials)

    def synchronize(self) -> List[Dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("Binance simulator is not connected.")

        return [{
            "exchange": "Binance",
            "symbol": "BTCUSDT",
            "orders": 20,
        }]


__all__ = ["BinanceSimulator"]