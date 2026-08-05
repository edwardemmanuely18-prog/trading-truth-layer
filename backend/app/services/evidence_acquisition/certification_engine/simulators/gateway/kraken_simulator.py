"""
Kraken simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class KrakenSimulator(BaseProviderSimulator):

    @property
    def provider_name(self) -> str:
        return "kraken"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        return {
            "api_key",
            "private_key",
        }.issubset(credentials)

    def synchronize(self) -> List[Dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("Kraken simulator is not connected.")

        return [{
            "exchange": "Kraken",
            "symbol": "XBTUSD",
            "balances": 8,
        }]


__all__ = ["KrakenSimulator"]