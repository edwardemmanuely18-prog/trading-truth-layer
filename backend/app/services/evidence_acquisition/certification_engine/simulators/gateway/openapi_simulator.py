"""
OpenAPI simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class OpenAPISimulator(BaseProviderSimulator):
    """
    OpenAPI gateway simulator.
    """

    @property
    def provider_name(self) -> str:
        return "openapi"

    @property
    def engine_name(self) -> str:
        return "gateway_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "base_url",
            "client_id",
            "client_secret",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "OpenAPI simulator is not connected."
            )

        return [
            {
                "endpoint": "/api/v1/trades",
                "method": "GET",
                "status": 200,
                "records": 18,
            }
        ]


__all__ = [
    "OpenAPISimulator",
]