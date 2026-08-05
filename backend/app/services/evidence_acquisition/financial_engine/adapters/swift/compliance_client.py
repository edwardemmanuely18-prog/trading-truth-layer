"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Compliance Client

Institutional client for SWIFT Compliance services.

Responsibilities
----------------
• Acquire compliance analytics
• Acquire sanctions insights
• Acquire AML insights
• Acquire KYC analytics
• Acquire alerts
• Normalize compliance responses

This client acquires compliance intelligence only.

Compliance decisions remain the responsibility of downstream
TTL investigation and governance engines.
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
    COMPLIANCE,
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
class ComplianceConfiguration:

    base_url: str

    timeout: int = 30


# ============================================================================
# Client
# ============================================================================


class ComplianceClient:
    """
    SWIFT Compliance Analytics client.
    """

    def __init__(
        self,
        configuration: ComplianceConfiguration,
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
    # Compliance Analytics
    # ------------------------------------------------------------------

    def analytics(
        self,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "compliance",

            COMPLIANCE["analytics"],
        )

        return self._get(endpoint)

    # ------------------------------------------------------------------
    # Alerts
    # ------------------------------------------------------------------

    def alerts(
        self,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "compliance",

            COMPLIANCE["alerts"],
        )

        return self._get(endpoint)

    # ------------------------------------------------------------------
    # Screening
    # ------------------------------------------------------------------

    def screening(
        self,
    ) -> List[ISO20022Message]:

        endpoint = SwiftEndpoints.endpoint(

            "compliance",

            COMPLIANCE["screening"],
        )

        return self._get(endpoint)

    # ------------------------------------------------------------------
    # Risk Summary
    # ------------------------------------------------------------------

    def risk_summary(
        self,
    ) -> Dict[str, int]:

        analytics = self.analytics()

        alerts = self.alerts()

        return {

            "analytics": len(
                analytics
            ),

            "alerts": len(
                alerts
            ),

            "screening": len(
                self.screening()
            ),
        }

    # ------------------------------------------------------------------
    # Canonical Financial Builders
    # ------------------------------------------------------------------

    def compliance_analytics(
        self,
    ):
        """
        Canonical compliance analytics.
        """

        return self.analytics()


    def compliance_alerts(
        self,
    ):
        """
        Canonical compliance alerts.
        """

        return self.alerts()


    def sanctions_screening(
        self,
    ):
        """
        Canonical sanctions screening evidence.
        """

        return self.screening()


    def aml_screening(
        self,
    ):
        """
        Canonical AML screening evidence.

        Current SWIFT screening results are used as the
        AML evidence source.
        """

        return self.screening()


    def kyc_analytics(
        self,
    ):
        """
        Canonical KYC analytics.

        Compliance analytics are reused until a dedicated
        KYC analytics endpoint is available.
        """

        return self.analytics()


    def letters_of_credit(
        self,
    ):
        """
        Letter of Credit evidence.

        Not provided by the Compliance API.
        """

        return []


    def bank_guarantees(
        self,
    ):
        """
        Bank Guarantee evidence.

        Not provided by the Compliance API.
        """

        return []


    def compliance_summary(
        self,
    ):
        """
        Canonical compliance summary.
        """

        return self.risk_summary()

    # ------------------------------------------------------------------
    # Synchronization
    # ------------------------------------------------------------------

    def synchronize(
        self,
    ) -> List[ISO20022Message]:

        evidence = []

        evidence.extend(
            self.analytics()
        )

        evidence.extend(
            self.alerts()
        )

        evidence.extend(
            self.screening()
        )

        return evidence


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "ComplianceConfiguration",

    "ComplianceClient",
]