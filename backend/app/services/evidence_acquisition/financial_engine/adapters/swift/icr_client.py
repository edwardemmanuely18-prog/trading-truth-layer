"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Instant Cash Reporting Client

Institutional client for the SWIFT Instant Cash Reporting API.

Responsibilities
----------------
• Acquire account information
• Acquire cash balances
• Acquire account statements
• Acquire booked transactions
• Acquire pending transactions
• Normalize ISO 20022 payloads

This client intentionally returns normalized SWIFT messages.
Translation into canonical Financial Evidence is handled by
the Financial Engine.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests

from .authentication import SwiftAuthentication
from .endpoints import (
    ICR,
    SwiftEndpoints,
)
from .iso20022 import (
    ISO20022Message,
    ISO20022Normalizer,
)


# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class InstantCashReportingConfiguration:
    """
    Instant Cash Reporting configuration.
    """

    base_url: str

    timeout: int = 30


# ============================================================================
# Client
# ============================================================================


class InstantCashReportingClient:
    """
    Canonical SWIFT Instant Cash Reporting client.
    """

    def __init__(
        self,
        configuration: InstantCashReportingConfiguration,
        authentication: SwiftAuthentication,
    ) -> None:

        self.configuration = configuration

        self.authentication = authentication

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get(
        self,
        endpoint: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> List[ISO20022Message]:

        url = (
            self.configuration.base_url
            + endpoint
        )

        response = requests.get(

            url,

            headers={
                **self.authentication.authorization_header,
                "Accept": "application/json",
            },

            params=params,

            timeout=self.configuration.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        records = payload.get(
            "items",
            [],
        )

        return [

            ISO20022Normalizer.normalize(
                record
            )

            for record in records
        ]

    # ------------------------------------------------------------------
    # Accounts
    # ------------------------------------------------------------------

    def accounts(
        self,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "instant_cash_reporting",

            ICR["accounts"],
        )

        return self._get(endpoint)

    # ------------------------------------------------------------------
    # Balances
    # ------------------------------------------------------------------

    def balances(
        self,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "instant_cash_reporting",

            ICR["balances"],
        )

        return self._get(endpoint)

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def statements(
        self,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "instant_cash_reporting",

            ICR["statements"],
        )

        return self._get(endpoint)

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------

    def transactions(
        self,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "instant_cash_reporting",

            ICR["transactions"],
        )

        return self._get(endpoint)

    def booked_transactions(
        self,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "instant_cash_reporting",

            ICR["booked_transactions"],
        )

        return self._get(endpoint)

    def pending_transactions(
        self,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "instant_cash_reporting",

            ICR["pending_transactions"],
        )

        return self._get(endpoint)

    # ------------------------------------------------------------------
    # Canonical Financial Builders
    # ------------------------------------------------------------------

    def institution(self):
        """
        Institution metadata.

        Instant Cash Reporting is institution-scoped, therefore
        no separate endpoint currently exists.
        """

        return None


    def account(self):
        """
        Return the primary financial account.
        """

        accounts = self.accounts()

        if accounts:

            return accounts[0]

        return None


    def cash_balances(self):
        """
        Canonical cash balances.
        """

        return self.balances()


    def cash_transfers(self):
        """
        Canonical cash transfers.

        Pending and booked transactions are both treated as
        transfer evidence.
        """

        transfers = []

        transfers.extend(
            self.booked_transactions()
        )

        transfers.extend(
            self.pending_transactions()
        )

        return transfers


    def settlement_instructions(self):
        """
        Settlement instructions.
        """

        return []


    def settlement_confirmations(self):
        """
        Settlement confirmations.
        """

        return []


    def custody_holdings(self):
        """
        Custody holdings.

        Instant Cash Reporting does not expose holdings.
        """

        return []


    def funding_events(self):
        """
        Funding events.
        """

        return self.transactions()


    def corporate_actions(self):
        """
        Corporate actions.

        Not provided by ICR.
        """

        return []


    def bank_statements(self):
        """
        Canonical bank statements.
        """

        return self.statements()


    def collateral(self):
        """
        Collateral evidence.
        """

        return []


    def margin(self):
        """
        Margin evidence.
        """

        return []

    # ------------------------------------------------------------------
    # Synchronization
    # ------------------------------------------------------------------

    def synchronize(
        self,
    ) -> List[ISO20022Message]:
        """
        Acquire every supported evidence object.
        """

        evidence: List[
            ISO20022Message
        ] = []

        evidence.extend(
            self.accounts()
        )

        evidence.extend(
            self.balances()
        )

        evidence.extend(
            self.statements()
        )

        evidence.extend(
            self.transactions()
        )

        evidence.extend(
            self.booked_transactions()
        )

        evidence.extend(
            self.pending_transactions()
        )

        return evidence


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [
    "InstantCashReportingConfiguration",
    "InstantCashReportingClient",
]