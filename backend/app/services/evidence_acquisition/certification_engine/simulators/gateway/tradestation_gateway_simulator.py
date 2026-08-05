"""
TradeStation Gateway simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class TradeStationGatewaySimulator(BaseProviderSimulator):

    @property
    def provider_name(self) -> str:
        return "tradestation_gateway"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        return {
            "client_id",
            "client_secret",
            "access_token",
        }.issubset(credentials)

    def synchronize(self) -> List[Dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("TradeStation Gateway simulator is not connected.")

        return [{
            "gateway": "TradeStation",
            "orders": 32,
            "positions": 6,
        }]


__all__ = ["TradeStationGatewaySimulator"]