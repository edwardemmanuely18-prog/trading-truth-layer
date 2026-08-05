"""
REST simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class RestSimulator(BaseProviderSimulator):
    """
    REST API simulator.
    """

    @property
    def provider_name(self) -> str:
        return "rest"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "base_url",
            "api_key",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "REST simulator is not connected."
            )

        return [
            {
                "endpoint": "/trades",
                "method": "GET",
                "status": 200,
                "records": 25,
            }
        ]


__all__ = [
    "RestSimulator",
]