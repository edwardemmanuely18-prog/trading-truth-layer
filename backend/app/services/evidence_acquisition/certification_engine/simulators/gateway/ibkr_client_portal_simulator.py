"""
IBKR Client Portal simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class IBKRClientPortalSimulator(BaseProviderSimulator):

    @property
    def provider_name(self) -> str:
        return "ibkr_client_portal"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        return {
            "base_url",
            "session_token",
        }.issubset(credentials)

    def synchronize(self) -> List[Dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("IBKR Client Portal simulator is not connected.")

        return [{
            "gateway": "IBKR Client Portal",
            "accounts": 2,
            "positions": 14,
        }]


__all__ = ["IBKRClientPortalSimulator"]