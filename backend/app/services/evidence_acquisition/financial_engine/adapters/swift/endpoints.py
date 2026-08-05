"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Endpoints

Canonical registry of SWIFT API endpoints.

This module centralizes all service base URLs and endpoint
definitions used throughout the SWIFT adapter.

Responsibilities
----------------
• Service base URLs
• Endpoint paths
• API versioning
• Endpoint resolution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# ============================================================================
# API Versions
# ============================================================================


SWIFT_API_VERSION = "v1"


# ============================================================================
# Service Base URLs
# ============================================================================


@dataclass(frozen=True, slots=True)
class SwiftService:
    """
    SWIFT service definition.
    """

    name: str

    base_url: str


SERVICES: Dict[str, SwiftService] = {

    "authentication": SwiftService(
        name="Authentication",
        base_url="/oauth2",
    ),

    "instant_cash_reporting": SwiftService(
        name="Instant Cash Reporting",
        base_url="/instant-cash-reporting",
    ),

    "payments": SwiftService(
        name="Payment Tracking",
        base_url="/payments",
    ),

    "kyc": SwiftService(
        name="KYC Registry",
        base_url="/kyc",
    ),

    "compliance": SwiftService(
        name="Compliance Analytics",
        base_url="/compliance",
    ),
}


# ============================================================================
# Authentication
# ============================================================================


AUTHENTICATION = {

    "token": "/token",
}


# ============================================================================
# Instant Cash Reporting
# ============================================================================


ICR = {

    "accounts": "/accounts",

    "balances": "/balances",

    "statements": "/statements",

    "transactions": "/transactions",

    "pending_transactions": "/transactions/pending",

    "booked_transactions": "/transactions/booked",
}


# ============================================================================
# Payment Tracking
# ============================================================================


PAYMENTS = {

    "payments": "/payments",

    "payment": "/payments/{payment_id}",

    "tracking": "/payments/{payment_id}/tracking",
}


# ============================================================================
# KYC Registry
# ============================================================================


KYC = {

    "institutions": "/institutions",

    "institution": "/institutions/{bic}",

    "documents": "/institutions/{bic}/documents",
}


# ============================================================================
# Compliance
# ============================================================================


COMPLIANCE = {

    "screening": "/screening",

    "analytics": "/analytics",

    "alerts": "/alerts",
}


# ============================================================================
# Endpoint Resolver
# ============================================================================


class SwiftEndpoints:
    """
    Resolves complete endpoint paths.
    """

    @staticmethod
    def service(name: str) -> SwiftService:

        return SERVICES[name]

    @staticmethod
    def endpoint(
        service: str,
        path: str,
    ) -> str:

        service_definition = SERVICES[service]

        return (
            f"{service_definition.base_url}"
            f"/{SWIFT_API_VERSION}"
            f"{path}"
        )


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "SWIFT_API_VERSION",

    "SwiftService",

    "SERVICES",

    "AUTHENTICATION",

    "ICR",

    "PAYMENTS",

    "KYC",

    "COMPLIANCE",

    "SwiftEndpoints",
]