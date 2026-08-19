"""
Trading Truth Layer (TTL)

Desktop Trading Engine

Canonical Provider Connection Verification Engine.

This module is provider-neutral.

Provider-specific implementation belongs exclusively
to the adapter layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ============================================================================
# Verification Snapshot
# ============================================================================


@dataclass(frozen=True, slots=True)
class VerificationSnapshot:
    """
    Provider-neutral facts supplied by a desktop adapter.

    The adapter is responsible for obtaining these facts from
    the native provider.

    This engine is responsible only for evaluating them.
    """

    provider: str
    provider_version: str | None = None

    connected: bool = False

    account_id: str | None = None
    broker: str | None = None
    server: str | None = None

    terminal: str | None = None
    terminal_version: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


# ============================================================================
# Verification Check
# ============================================================================


@dataclass(frozen=True, slots=True)
class VerificationCheck:
    """
    One deterministic verification check.
    """

    name: str
    passed: bool
    message: str

    observed: Any = None
    expected: Any = None


# ============================================================================
# Verification Result
# ============================================================================


@dataclass(frozen=True, slots=True)
class VerificationResult:
    """
    Canonical result of a desktop provider verification attempt.
    """

    provider: str

    verified: bool

    checks: tuple[VerificationCheck, ...] = ()

    error: str | None = None

    snapshot: VerificationSnapshot | None = None

    @property
    def failed_checks(
        self,
    ) -> tuple[VerificationCheck, ...]:
        return tuple(
            check
            for check in self.checks
            if not check.passed
        )

    @property
    def passed_checks(
        self,
    ) -> tuple[VerificationCheck, ...]:
        return tuple(
            check
            for check in self.checks
            if check.passed
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "verified": self.verified,
            "checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "message": check.message,
                    "observed": check.observed,
                    "expected": check.expected,
                }
                for check in self.checks
            ],
            "error": self.error,
            "snapshot": (
                {
                    "provider": self.snapshot.provider,
                    "provider_version": (
                        self.snapshot.provider_version
                    ),
                    "connected": self.snapshot.connected,
                    "account_id": self.snapshot.account_id,
                    "broker": self.snapshot.broker,
                    "server": self.snapshot.server,
                    "terminal": self.snapshot.terminal,
                    "terminal_version": (
                        self.snapshot.terminal_version
                    ),
                    "metadata": self.snapshot.metadata,
                }
                if self.snapshot is not None
                else None
            ),
        }


# ============================================================================
# Verification Engine
# ============================================================================


class DesktopVerificationEngine:
    """
    Provider-neutral Desktop Verification Engine.

    This class does not know how any provider works.

    Adapters provide VerificationSnapshot instances.
    """

    def verify(
        self,
        snapshot: VerificationSnapshot,
        *,
        expected_account_id: str | None = None,
        expected_server: str | None = None,
        expected_provider: str | None = None,
    ) -> VerificationResult:

        checks: list[VerificationCheck] = []

        # ------------------------------------------------------------------
        # Connectivity
        # ------------------------------------------------------------------

        checks.append(
            VerificationCheck(
                name="connectivity",
                passed=snapshot.connected,
                message=(
                    "Desktop provider is connected."
                    if snapshot.connected
                    else "Desktop provider is not connected."
                ),
                observed=snapshot.connected,
                expected=True,
            )
        )

        # ------------------------------------------------------------------
        # Provider Identity
        # ------------------------------------------------------------------

        provider_match = (
            expected_provider is None
            or snapshot.provider.strip().lower()
            == expected_provider.strip().lower()
        )

        checks.append(
            VerificationCheck(
                name="provider_identity",
                passed=provider_match,
                message=(
                    "Provider identity matches the configured provider."
                    if provider_match
                    else (
                        "Provider identity does not match "
                        "the configured provider."
                    )
                ),
                observed=snapshot.provider,
                expected=expected_provider,
            )
        )

        # ------------------------------------------------------------------
        # Account Identity
        # ------------------------------------------------------------------

        account_match = (
            expected_account_id is None
            or (
                snapshot.account_id is not None
                and str(snapshot.account_id)
                == str(expected_account_id)
            )
        )

        checks.append(
            VerificationCheck(
                name="account_identity",
                passed=account_match,
                message=(
                    "Account identity matches the configured account."
                    if account_match
                    else (
                        "Account identity does not match "
                        "the configured account."
                    )
                ),
                observed=snapshot.account_id,
                expected=expected_account_id,
            )
        )

        # ------------------------------------------------------------------
        # Server Identity
        # ------------------------------------------------------------------

        server_match = (
            expected_server is None
            or (
                snapshot.server is not None
                and snapshot.server == expected_server
            )
        )

        checks.append(
            VerificationCheck(
                name="server_identity",
                passed=server_match,
                message=(
                    "Server identity matches the configured server."
                    if server_match
                    else (
                        "Server identity does not match "
                        "the configured server."
                    )
                ),
                observed=snapshot.server,
                expected=expected_server,
            )
        )

        verified = all(
            check.passed
            for check in checks
        )

        return VerificationResult(
            provider=snapshot.provider,
            verified=verified,
            checks=tuple(checks),
            error=(
                None
                if verified
                else "One or more verification checks failed."
            ),
            snapshot=snapshot,
        )


# ============================================================================
# Singleton
# ============================================================================


desktop_verification_engine = DesktopVerificationEngine()


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [
    "VerificationSnapshot",
    "VerificationCheck",
    "VerificationResult",
    "DesktopVerificationEngine",
    "desktop_verification_engine",
]