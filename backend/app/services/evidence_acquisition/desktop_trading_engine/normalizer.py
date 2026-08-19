"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Desktop Trading Engine

Evidence Normalizer

Normalizes the canonical Desktop Trading Engine acquisition contract.

This component is provider-independent.

Responsibilities
----------------

• Normalize acquisition payloads
• Apply generic defaults
• Normalize collection types
• Preserve provider-native objects
• Produce a consistent acquisition contract

This module MUST NOT contain broker-specific logic.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


# ============================================================================
# Desktop Evidence Normalizer
# ============================================================================


class DesktopEvidenceNormalizer:
    """
    Provider-independent Desktop acquisition normalizer.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def normalize(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize the Desktop acquisition payload.
        """

        normalized = deepcopy(payload)

        normalized["terminal"] = self.normalize_terminal(
            normalized.get("terminal"),
        )

        normalized["user"] = self.normalize_user(
            normalized.get("user"),
            normalized.get("account"),
        )

        normalized["broker"] = self.normalize_broker(
            normalized.get("broker"),
            normalized.get("account"),
        )

        normalized["server"] = self.normalize_server(
            normalized.get("server"),
            normalized.get("account"),
        )

        normalized["account"] = self.normalize_account(
            normalized.get("account"),
        )

        normalized["financial"] = self.normalize_financial(
            normalized.get("financial"),
        )

        normalized["symbols"] = self.normalize_symbols(
            normalized.get("symbols"),
        )

        normalized["prices"] = self.normalize_prices(
            normalized.get("prices"),
        )

        normalized["orders"] = self.normalize_orders(
            normalized.get("orders"),
        )

        normalized["executions"] = self.normalize_executions(
            normalized.get("executions"),
        )

        normalized["deals"] = self.normalize_deals(
            normalized.get("deals"),
        )

        normalized["trades"] = self.normalize_trades(
            normalized.get("trades"),
        )

        normalized["positions"] = self.normalize_positions(
            normalized.get("positions"),
        )

        normalized["account"] = self._enrich_account_identity(
            normalized.get("account"),
            normalized.get("orders"),
            normalized.get("executions"),
            normalized.get("trades"),
            normalized.get("positions"),
        )

        normalized["history"] = self.normalize_history(
            normalized.get("history"),
        )

        normalized["activity"] = self.normalize_activity(
            normalized.get("activity"),
        )

        return normalized

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get(
        source: Any,
        attribute: str,
        default: Any = None,
    ) -> Any:
        """
        Provider-neutral attribute accessor.

        Supports dictionaries, SDK objects,
        dataclasses and future providers.
        """

        if source is None:
            return default

        if isinstance(source, dict):
            return source.get(
                attribute,
                default,
            )

        return getattr(
            source,
            attribute,
            default,
        )

    # ------------------------------------------------------------------
    # Infrastructure
    # ------------------------------------------------------------------

    def normalize_terminal(
        self,
        terminal: Any,
    ) -> dict[str, Any]:

        if terminal is None:
            return {}

        return {

            "terminal_id": self._get(
                terminal,
                "terminal_id",
            ),

            "terminal_name": (
                self._get(
                    terminal,
                    "terminal_name",
                )
                or
                self._get(
                    terminal,
                    "name",
                )
            ),

            "platform_build": (
                self._get(
                    terminal,
                    "platform_build",
                )
                or
                self._get(
                    terminal,
                    "build",
                )
            ),

            "executable_path": (
                self._get(
                    terminal,
                    "executable_path",
                )
                or
                self._get(
                    terminal,
                    "path",
                )
            ),

            "installation_directory": (
                self._get(
                    terminal,
                    "installation_directory",
                )
                or
                self._get(
                    terminal,
                    "data_path",
                )
            ),

            "operating_system": self._get(
                terminal,
                "operating_system",
            ),

            "architecture": self._get(
                terminal,
                "architecture",
            ),

            "language": self._get(
                terminal,
                "language",
            ),

            "timezone": self._get(
                terminal,
                "timezone",
            ),

            "connected": (
                self._get(
                    terminal,
                    "connected",
                    False,
                )
            ),

            "session_id": self._get(
                terminal,
                "session_id",
            ),

            "session_active": (
                self._get(
                    terminal,
                    "session_active",
                    self._get(
                        terminal,
                        "connected",
                        False,
                    ),
                )
            ),
        }

    def normalize_user(
        self,
        user: Any,
        account: Any = None,
    ) -> dict[str, Any]:
        """
        Normalize canonical user information.
        """

        if user is None and account is None:
            return {}

        source = user or account

        return {

            "user_id": self._get(
                source,
                "login",
            ),

            "user_name": self._get(
                source,
                "name",
            ),

            "full_name": self._get(
                source,
                "name",
            ),

            "email": self._get(
                source,
                "email",
            ),

            "country": self._get(
                source,
                "country",
            ),

            "timezone": self._get(
                source,
                "timezone",
            ),
        }

    def normalize_broker(
        self,
        broker: Any,
        account: Any = None,
    ) -> dict[str, Any]:
        """
        Normalize canonical broker information.
        """

        if broker is None and account is None:
            return {}

        source = broker or account

        return {

            "broker_id": self._get(
                source,
                "broker_id",
            ),

            "broker_name": self._get(
                source,
                "server",
            ),

            "broker_company": self._get(
                source,
                "company",
            ),

            "broker_type": self._get(
                source,
                "broker_type",
            ),

            "broker_country": self._get(
                source,
                "broker_country",
            ),
        }

    def normalize_server(
        self,
        server: Any,
        account: Any = None,
    ) -> dict[str, Any]:
        """
        Normalize canonical server information.
        """

        if server is None and account is None:
            return {}

        source = server or account

        return {

            "server_id": self._get(
                source,
                "server_id",
            ),

            "server_name": self._get(
                source,
                "server",
            ),

            "server_region": self._get(
                source,
                "server_region",
            ),

            "server_timezone": self._get(
                source,
                "server_timezone",
            ),

            "server_location": self._get(
                source,
                "server_location",
            ),
        }

    @staticmethod
    def _enrich_account_identity(
        account: Any,
        orders: Any,
        executions: Any,
        trades: Any,
        positions: Any,
    ) -> dict[str, Any]:
        """
        Enrich account identity from provider-observed trading evidence.

        MotiveWave does not expose the account identifier through the
        active account metadata surface, but the provider exposes the
        same account identifier on native orders/executions and the
        derived position/trade evidence.

        Identity is therefore observed, never hardcoded.
        """

        account = dict(account or {})

        # Preserve an identity already supplied directly by the provider.
        existing_id = (
            account.get("broker_account_id")
            or account.get("account_id")
            or account.get("login")
        )

        if existing_id is not None:
            account["broker_account_id"] = str(existing_id)
            return account

        candidates = (
            ("execution", executions),
            ("order", orders),
            ("trade", trades),
            ("position", positions),
        )

        for source_name, values in candidates:
            for value in values or []:
                if not isinstance(value, dict):
                    continue

                observed_id = (
                    value.get("account_id")
                    or value.get("broker_account_id")
                )

                if observed_id is None:
                    continue

                account["broker_account_id"] = str(observed_id)
                account["account_identity_source"] = (
                    f"MotiveWave {source_name.title()}"
                )
                account["account_identity_confidence"] = "observed"

                return account

        account["account_identity_source"] = None
        account["account_identity_confidence"] = "unavailable"

        return account


    def normalize_account(
        self,
        account: Any,
    ) -> dict[str, Any]:

        if account is None:
            return {}

        return {

            "broker_account_id": (
                self._get(account, "broker_account_id")
                or
                self._get(account, "login")
            ),

            "account_name": (
                self._get(account, "account_name")
                or
                self._get(account, "name")
            ),

            "account_type": self._get(
                account,
                "trade_mode",
            ),

            "account_state": self._get(
                account,
                "account_state",
            ),

            "currency": self._get(
                account,
                "currency",
            ),

            "leverage": self._get(
                account,
                "leverage",
            ),

            "balance": self._get(
                account,
                "balance",
            ),

            "equity": self._get(
                account,
                "equity",
            ),

            "margin": self._get(
                account,
                "margin",
            ),

            "buying_power": (
                self._get(
                    account,
                    "margin_free",
                )
            ),

            "server_name": (
                self._get(
                    account,
                    "server",
                )
            ),

            "broker_company": (
                self._get(
                    account,
                    "company",
                )
            ),
        }

    # ------------------------------------------------------------------
    # Financial
    # ------------------------------------------------------------------

    def normalize_financial(
        self,
        financial: Any,
    ) -> dict[str, Any]:

        if financial is None:
            return {}

        return dict(financial)


    @staticmethod
    def _normalize_collection(
        value: Any,
    ) -> list[Any]:
        """
        Normalize provider collection responses without
        accidentally converting dictionary metadata into
        a list of dictionary keys.

        Supported provider response forms:

            list/tuple:
                [item, item, ...]

            dict with data:
                {
                    "supported": True,
                    "data": [...]
                }

            dict with no data:
                metadata/status object; return [] because
                there is no evidence collection to normalize.
        """

        if value is None:
            return []

        if isinstance(value, dict):
            data = value.get("data")

            if data is None:
                return []

            if isinstance(data, (list, tuple)):
                return list(data)

            return [data]

        if isinstance(value, (list, tuple)):
            return list(value)

        return [value]

    # ------------------------------------------------------------------
    # Market
    # ------------------------------------------------------------------

    def normalize_symbols(
        self,
        symbols: Any,
    ) -> list[Any]:
        return self._normalize_collection(symbols)

    def normalize_prices(
        self,
        prices: Any,
    ) -> list[Any]:
        return self._normalize_collection(prices)

    # ------------------------------------------------------------------
    # Trading
    # ------------------------------------------------------------------

    def normalize_orders(
        self,
        orders: Any,
    ) -> list[Any]:
        return self._normalize_collection(orders)

    def normalize_executions(
        self,
        executions: Any,
    ) -> list[Any]:
        return self._normalize_collection(executions)

    def normalize_deals(
        self,
        deals: Any,
    ) -> list[Any]:
        return self._normalize_collection(deals)

    def normalize_trades(
        self,
        trades: Any,
    ) -> list[Any]:
        return self._normalize_collection(trades)

    def normalize_positions(
        self,
        positions: Any,
    ) -> list[Any]:
        return self._normalize_collection(positions)

    def normalize_history(
        self,
        history: Any,
    ) -> list[Any]:
        return self._normalize_collection(history)

    def normalize_activity(
        self,
        activity: Any,
    ) -> list[Any]:
        return self._normalize_collection(activity)


# ============================================================================
# Global Normalizer
# ============================================================================

desktop_evidence_normalizer = DesktopEvidenceNormalizer()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "DesktopEvidenceNormalizer",
    "desktop_evidence_normalizer",
]