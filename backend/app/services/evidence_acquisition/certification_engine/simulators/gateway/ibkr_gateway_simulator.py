"""
IBKR Gateway simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class IBKRGatewaySimulator(BaseProviderSimulator):

    @property
    def provider_name(self) -> str:
        return "ibkr_gateway"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        return {
            "host",
            "port",
            "client_id",
        }.issubset(credentials)

    def synchronize(self) -> List[Dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("IBKR Gateway simulator is not connected.")

        return [{
            "gateway": "IB Gateway",
            "account": "DU123456",
            "executions": 18,
        }]


__all__ = ["IBKRGatewaySimulator"]