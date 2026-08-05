"""
WebSocket simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class WebSocketSimulator(BaseProviderSimulator):
    """
    WebSocket simulator.
    """

    @property
    def provider_name(self) -> str:
        return "websocket"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "url",
            "access_token",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "WebSocket simulator is not connected."
            )

        return [
            {
                "channel": "trades",
                "messages": 100,
                "connected": True,
            }
        ]


__all__ = [
    "WebSocketSimulator",
]