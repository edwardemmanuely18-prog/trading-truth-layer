"""
Bank simulator for the Evidence Acquisition Certification Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ...simulator import BaseProviderSimulator


class BankSimulator(BaseProviderSimulator):
    """
    Bank provider simulator.
    """

    @property
    def provider_name(self) -> str:
        return "bank"

    @property
    def engine_name(self) -> str:
        return "financial_engine"

    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:

        required = {
            "institution_id",
            "username",
            "password",
        }

        return required.issubset(credentials.keys())

    def synchronize(self) -> List[Dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "Bank simulator is not connected."
            )

        return [
            {
                "account_number": "100000001",
                "currency": "USD",
                "balance": 1250000.00,
                "available_balance": 1225000.00,
                "institution": "TTL Bank",
            }
        ]


__all__ = [
    "BankSimulator",
]