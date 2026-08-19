"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

cTrader Desktop Adapter
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, Iterable
import importlib.metadata
import threading
import time
from queue import Queue

from .base_adapter import BaseDesktopAdapter
from ..normalizer import desktop_evidence_normalizer
from ..verification import VerificationSnapshot



class _CTraderOpenApiClient:
    """
    Provider-native synchronous facade over Spotware's official
    ``ctrader-open-api`` Twisted SDK.

    The rest of TTL is intentionally presented with a synchronous,
    provider-neutral surface:
        connect()
        disconnect()
        is_connected()
        terminal()
        user()
        broker()
        server()
        account()
        financial()
        symbols()
        prices()
        orders()
        executions()
        deals()
        trades()
        positions()
        history()
        activity()

    Only this class knows about Twisted, protobuf message classes,
    cTrader account authorization, cTrader symbol IDs, and cTrader's
    1/100/100000 scaling conventions.
    """

    _runtime_lock = threading.Lock()
    _client_lock = threading.RLock()

    _runtime_started = False
    _reactor = None
    _reactor_thread = None

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        access_token: str,
        account_id: str | None,
        environment: str,
        timeout: float = 20.0,
    ) -> None:
        try:
            from ctrader_open_api import Client, EndPoints, TcpProtocol
            from ctrader_open_api.messages.OpenApiMessages_pb2 import (
                ProtoOAApplicationAuthReq,
                ProtoOAAccountAuthReq,
                ProtoOAGetAccountListByAccessTokenReq,
                ProtoOAGetCtidProfileByTokenReq,
                ProtoOAReconcileReq,
                ProtoOATraderReq,
                ProtoOASymbolsListReq,
                ProtoOASymbolByIdReq,
                ProtoOASubscribeSpotsReq,
                ProtoOAUnsubscribeSpotsReq,
                ProtoOAOrderListReq,
                ProtoOADealListReq,
            )
            from ctrader_open_api.messages.OpenApiModelMessages_pb2 import ProtoOATradeSide
            from twisted.internet import reactor
        except ImportError as exc:
            raise RuntimeError(
                "cTrader integration requires the official 'ctrader-open-api' "
                "package. Install it in the TTL backend environment."
            ) from exc

        self.Client = Client
        self.EndPoints = EndPoints
        self.TcpProtocol = TcpProtocol
        self.reactor = reactor

        self.ProtoOAApplicationAuthReq = ProtoOAApplicationAuthReq
        self.ProtoOAAccountAuthReq = ProtoOAAccountAuthReq
        self.ProtoOAGetAccountListByAccessTokenReq = ProtoOAGetAccountListByAccessTokenReq
        self.ProtoOAGetCtidProfileByTokenReq = ProtoOAGetCtidProfileByTokenReq
        self.ProtoOAReconcileReq = ProtoOAReconcileReq
        self.ProtoOATraderReq = ProtoOATraderReq
        self.ProtoOASymbolsListReq = ProtoOASymbolsListReq
        self.ProtoOASymbolByIdReq = ProtoOASymbolByIdReq
        self.ProtoOASubscribeSpotsReq = ProtoOASubscribeSpotsReq
        self.ProtoOAUnsubscribeSpotsReq = ProtoOAUnsubscribeSpotsReq
        self.ProtoOAOrderListReq = ProtoOAOrderListReq
        self.ProtoOADealListReq = ProtoOADealListReq
        self.ProtoOATradeSide = ProtoOATradeSide

        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.requested_account_id = str(account_id) if account_id else None
        self.environment = (
            "demo"
            if str(environment or "live").strip().lower()
            in {"demo", "development", "sandbox", "paper"}
            else "live"
        )
        self.timeout = float(timeout)

        # cTrader native connection establishment can legitimately take
        # longer than an individual API request. Keep connection startup
        # independent from the normal request timeout.
        self.connection_timeout = max(
            self.timeout,
            60.0,
        )

        self._client = None
        self._connected = threading.Event()
        self._authorized = threading.Event()
        self._auth_error: Exception | None = None
        self._selected_account: dict[str, Any] | None = None
        self._account_list: list[dict[str, Any]] = []
        self._spot_cache: dict[int, dict[str, Any]] = {}
        self._spot_symbols_by_id: dict[int, str] = {}
        self._spot_lock = threading.RLock()
        self._version = self._sdk_version()

    @staticmethod
    def _sdk_version() -> str:
        try:
            return importlib.metadata.version("ctrader-open-api")
        except Exception:
            return "unknown"

    @classmethod
    def _ensure_reactor(cls, reactor) -> None:
        with cls._runtime_lock:
            if cls._runtime_started:
                if hasattr(cls, "_reactor_ready"):
                    cls._reactor_ready.wait(timeout=10.0)
                return

            cls._reactor = reactor
            cls._reactor_ready = threading.Event()

            def _mark_ready() -> None:
                cls._reactor_ready.set()

            def _run() -> None:
                try:
                    reactor.callWhenRunning(_mark_ready)
                    reactor.run(installSignalHandlers=False)
                finally:
                    cls._runtime_started = False
                    cls._reactor_ready.set()

            cls._reactor_thread = threading.Thread(
                target=_run,
                name="ttl-ctrader-reactor",
                daemon=True,
            )

            cls._reactor_thread.start()

            if not cls._reactor_ready.wait(timeout=10.0):
                raise TimeoutError(
                    "Timed out waiting for the cTrader Twisted reactor "
                    "to enter its running state."
                )

            cls._runtime_started = True

    @staticmethod
    def _failure_message(failure: Any) -> str:
        try:
            value = getattr(failure, "value", failure)
            return str(value)
        except Exception:
            return repr(failure)

    @staticmethod
    def _scalar(value: Any, default: Any = None) -> Any:
        if value is None:
            return default
        return value

    @classmethod
    def _dict_account(cls, account: Any) -> dict[str, Any]:
        return {
            "account_id": getattr(account, "ctidTraderAccountId", None),
            "ctid_trader_account_id": getattr(account, "ctidTraderAccountId", None),
            "is_live": getattr(account, "isLive", None),
            "trader_login": getattr(account, "traderLogin", None),
            "broker_title_short": getattr(account, "brokerTitleShort", None),
            "last_closing_deal_timestamp": getattr(
                account, "lastClosingDealTimestamp", None
            ),
            "last_balance_update_timestamp": getattr(
                account, "lastBalanceUpdateTimestamp", None
            ),
        }

    @classmethod
    def _scale_money(cls, value: Any, digits: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value) / (10 ** int(digits or 0))
        except (TypeError, ValueError, OverflowError):
            return None

    @classmethod
    def _scale_volume(cls, value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value) / 100.0
        except (TypeError, ValueError, OverflowError):
            return None

    @staticmethod
    def _scale_price(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value) / 100000.0
        except (TypeError, ValueError, OverflowError):
            return None

    @staticmethod
    def _ms_datetime(value: Any) -> datetime | None:
        if value is None:
            return None
        try:
            return datetime.fromtimestamp(float(value) / 1000.0, tz=UTC)
        except (TypeError, ValueError, OSError, OverflowError):
            return None

    def _start_client(self) -> None:
        """
        Start the provider-native cTrader client on the dedicated
        Twisted reactor thread.

        The method is safe to call repeatedly after a failed/stale
        native session. A failed connection attempt never leaves a
        half-initialized Client object behind.
        """
        with self._client_lock:
            self._connected.clear()
            self._authorized.clear()
            self._auth_error = None

            self._ensure_reactor(self.reactor)

            host = (
                self.EndPoints.PROTOBUF_LIVE_HOST
                if self.environment == "live"
                else self.EndPoints.PROTOBUF_DEMO_HOST
            )

            client_ready = threading.Event()
            client_error: list[Exception] = []

            def _start_native_client() -> None:
                try:
                    native_client = self.Client(
                        host,
                        self.EndPoints.PROTOBUF_PORT,
                        self.TcpProtocol,
                        retryPolicy=lambda _attempt: 1.0,
                    )

                    native_client.setConnectedCallback(
                        self._on_connected
                    )

                    native_client.setDisconnectedCallback(
                        self._on_disconnected
                    )

                    native_client.setMessageReceivedCallback(
                        self._on_message
                    )

                    self._client = native_client

                    native_client.startService()

                except Exception as exc:
                    self._client = None
                    client_error.append(exc)

                finally:
                    client_ready.set()

            self.reactor.callFromThread(
                _start_native_client
            )

            if not client_ready.wait(
                timeout=self.timeout
            ):
                raise TimeoutError(
                    "Timed out while initializing the cTrader "
                    "native client."
                )

            if client_error:
                raise RuntimeError(
                    "Failed to initialize cTrader native client."
                ) from client_error[0]

            if not self._connected.wait(
                self.connection_timeout
            ):
                # Capture the native client state before resetting it.
                native_connected = bool(
                    self._client is not None
                    and getattr(
                        self._client,
                        "isConnected",
                        False,
                    )
                )

                print(
                    "CTRADER_NATIVE: connection timeout "
                    f"environment={self.environment} "
                    f"native_is_connected={native_connected} "
                    f"client_initialized={self._client is not None}"
                )

                # Clean up the stale native client on the reactor thread.
                stale_client = self._client
                self._client = None

                if stale_client is not None:

                    def _stop_stale_client() -> None:
                        try:
                            stale_client.stopService()
                        except Exception:
                            pass

                    self.reactor.callFromThread(
                        _stop_stale_client
                    )

                raise TimeoutError(
                    f"Timed out waiting for cTrader "
                    f"{self.environment} API connection."
                )

    def _on_connected(self, _client) -> None:
        print(
            "CTRADER_NATIVE: connected "
            f"environment={self.environment}"
        )
        self._connected.set()

    def _on_disconnected(
        self,
        _client,
        reason: Any,
    ) -> None:
        self._connected.clear()
        self._authorized.clear()

        print(
            "CTRADER_NATIVE: disconnected "
            f"environment={self.environment} "
            f"reason={reason!r}"
        )

        if reason:
            self._auth_error = RuntimeError(
                f"cTrader Open API disconnected: {reason}"
            )

    def _on_message(self, _client: Any, message: Any) -> None:
        try:
            from ctrader_open_api import Protobuf
            from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOASpotEvent

            if message.payloadType == ProtoOASpotEvent().payloadType:
                spot = Protobuf.extract(message)
                symbol_id = int(getattr(spot, "symbolId", 0) or 0)
                if symbol_id:
                    record: dict[str, Any] = {"symbol_id": symbol_id}
                    if getattr(spot, "bid", None):
                        record["bid"] = self._scale_price(spot.bid)
                    if getattr(spot, "ask", None):
                        record["ask"] = self._scale_price(spot.ask)
                    if getattr(spot, "timestamp", None):
                        record["time"] = self._ms_datetime(spot.timestamp)
                    with self._spot_lock:
                        self._spot_cache[symbol_id] = record
        except Exception:
            # Spot events must never break the acquisition pipeline.
            return

    def _send(self, request: Any, *, timeout: float | None = None) -> Any:
        if self._client is None:
            raise RuntimeError("cTrader Open API client is not initialized.")

        timeout = float(timeout or self.timeout)
        result_queue: Queue = Queue(maxsize=1)

        def _do_send() -> None:
            try:
                deferred = self._client.send(
                    request,
                    responseTimeoutInSeconds=timeout,
                )
                deferred.addCallbacks(
                    lambda value: result_queue.put(("ok", value)),
                    lambda failure: result_queue.put(
                        ("error", self._failure_message(failure))
                    ),
                )
            except Exception as exc:
                result_queue.put(("error", exc))

        self.reactor.callFromThread(_do_send)

        try:
            status, value = result_queue.get(timeout=timeout)
        except Exception as exc:
            raise TimeoutError(
                f"Timed out waiting for cTrader response to "
                f"{type(request).__name__}."
            ) from exc

        if status != "ok":
            raise RuntimeError(
                f"cTrader Open API request {type(request).__name__} failed: {value}"
            )

        try:
            from ctrader_open_api import Protobuf

            return Protobuf.extract(value)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to extract cTrader protobuf response for "
                f"{type(request).__name__}: {exc}"
            ) from exc

        return value

    def _authorize(self) -> None:
        app_req = self.ProtoOAApplicationAuthReq()
        app_req.clientId = self.client_id
        app_req.clientSecret = self.client_secret
        self._send(app_req)

        account_req = self.ProtoOAGetAccountListByAccessTokenReq()
        account_req.accessToken = self.access_token
        response = self._send(account_req)

        accounts = [
            self._dict_account(value)
            for value in getattr(response, "ctidTraderAccount", [])
        ]
        if not accounts:
            raise RuntimeError(
                "cTrader access token returned no authorized trader accounts."
            )

        self._account_list = accounts

        selected: dict[str, Any] | None = None
        if self.requested_account_id:
            requested = str(self.requested_account_id)
            selected = next(
                (
                    item
                    for item in accounts
                    if str(item.get("account_id")) == requested
                ),
                None,
            )
            if selected is None:
                available = ", ".join(
                    str(item.get("account_id"))
                    for item in accounts
                    if item.get("account_id") is not None
                )
                raise RuntimeError(
                    f"Configured cTrader account_id {requested} is not authorized "
                    f"for the supplied access token. Authorized accounts: {available}"
                )

        if selected is None:
            want_live = self.environment == "live"
            selected = next(
                (
                    item
                    for item in accounts
                    if bool(item.get("is_live")) == want_live
                ),
                accounts[0],
            )

        is_live = selected.get("is_live")
        if is_live is not None and bool(is_live) != (self.environment == "live"):
            raise RuntimeError(
                "Selected cTrader account environment does not match the connection "
                f"environment ({self.environment})."
            )

        self._selected_account = selected

        auth_req = self.ProtoOAAccountAuthReq()
        auth_req.ctidTraderAccountId = int(selected["account_id"])
        auth_req.accessToken = self.access_token
        self._send(auth_req)
        self._authorized.set()

    def connect(self) -> None:
        """
        Establish and authorize the cTrader Open API session.

        Rebuilds the native client when the previous attempt left
        a stale/disconnected client object.
        """
        with self._client_lock:

            if (
                self._client is not None
                and getattr(
                    self._client,
                    "isConnected",
                    False,
                )
                and self._authorized.is_set()
            ):
                return

            if (
                self._client is None
                or not getattr(
                    self._client,
                    "isConnected",
                    False,
                )
            ):
                if self._client is not None:

                    stale_client = self._client
                    self._client = None

                    def _stop_stale_client() -> None:
                        try:
                            stale_client.stopService()
                        except Exception:
                            pass

                    self._ensure_reactor(self.reactor)

                    self.reactor.callFromThread(
                        _stop_stale_client
                    )

                self._start_client()

            self._authorize()

    def disconnect(self) -> None:
        if self._client is None:
            return

        def _stop() -> None:
            try:
                self._client.stopService()
            finally:
                self._connected.clear()
                self._authorized.clear()

        self.reactor.callFromThread(_stop)

    def is_connected(self) -> bool:
        return bool(
            self._client is not None
            and getattr(self._client, "isConnected", False)
            and self._authorized.is_set()
        )

    def terminal(self) -> dict[str, Any]:
        host = (
            self.EndPoints.PROTOBUF_LIVE_HOST
            if self.environment == "live"
            else self.EndPoints.PROTOBUF_DEMO_HOST
        )
        return {
            "name": "cTrader Open API",
            "provider": "cTrader",
            "version": self._version,
            "environment": self.environment,
            "host": host,
            "port": self.EndPoints.PROTOBUF_PORT,
        }

    def user(self) -> dict[str, Any]:
        request = self.ProtoOAGetCtidProfileByTokenReq()
        request.accessToken = self.access_token
        response = self._send(request)
        profile = getattr(response, "profile", None)
        return {
            "user_id": getattr(profile, "userId", None),
            "account_id": (
                self._selected_account.get("account_id")
                if self._selected_account
                else None
            ),
        }

    def broker(self) -> dict[str, Any]:
        return {
            "name": (
                self._selected_account.get("broker_title_short")
                if self._selected_account
                else None
            ),
            "broker_title_short": (
                self._selected_account.get("broker_title_short")
                if self._selected_account
                else None
            ),
        }

    def server(self) -> dict[str, Any]:
        return {
            "name": (
                self.EndPoints.PROTOBUF_LIVE_HOST
                if self.environment == "live"
                else self.EndPoints.PROTOBUF_DEMO_HOST
            ),
            "environment": self.environment,
        }

    def account(self) -> dict[str, Any]:
        request = self.ProtoOATraderReq()
        request.ctidTraderAccountId = int(self._selected_account["account_id"])
        response = self._send(request)
        trader = getattr(response, "trader", response)

        money_digits = getattr(trader, "moneyDigits", 0)
        balance = self._scale_money(getattr(trader, "balance", None), money_digits)

        return {
            # Canonical Desktop Trading Engine identity.
            # cTrader's native identity is ctidTraderAccountId.
            "broker_account_id": str(
                getattr(
                    trader,
                    "ctidTraderAccountId",
                    self._selected_account["account_id"],
                )
            ),

            # Preserve the native/provider-specific representation as well.
            "account_id": getattr(
                trader,
                "ctidTraderAccountId",
                self._selected_account["account_id"],
            ),

            "ctid_trader_account_id": getattr(
                trader,
                "ctidTraderAccountId",
                self._selected_account["account_id"],
            ),

            "trader_login": (
                self._selected_account.get("trader_login")
                if isinstance(self._selected_account, dict)
                else None
            ),

            "balance": balance,
            "money_digits": money_digits,
            "deposit_asset_id": getattr(
                trader,
                "depositAssetId",
                None,
            ),
            "account_type": getattr(
                trader,
                "accountType",
                None,
            ),
            "trading_mode": getattr(
                trader,
                "tradingMode",
                None,
            ),
            "access_rights": getattr(
                trader,
                "accessRights",
                None,
            ),
            "is_limited_risk": getattr(
                trader,
                "isLimitedRisk",
                None,
            ),
            "is_swap_free": getattr(
                trader,
                "isSwapFree",
                None,
            ),
        }

    def financial(self) -> dict[str, Any]:
        account = self.account()
        balance = account.get("balance")
        # cTrader Open API does not expose an MT5-style equity/margin tuple.
        # Equity can be derived from balance + current net unrealized PnL.
        unrealized = self._unrealized_pnl_total()
        equity = (
            balance + unrealized
            if balance is not None and unrealized is not None
            else None
        )
        return {
            "balance": balance,
            "equity": equity,
            "margin": None,
            "buying_power": None,
            "unrealized_pnl": unrealized,
        }

    def _unrealized_pnl_total(self) -> float | None:
        try:
            from ctrader_open_api.messages.OpenApiMessages_pb2 import (
                ProtoOAGetPositionUnrealizedPnLReq,
            )
        except ImportError:
            return None

        request = ProtoOAGetPositionUnrealizedPnLReq()
        request.ctidTraderAccountId = int(self._selected_account["account_id"])
        response = self._send(request)
        money_digits = getattr(response, "moneyDigits", 0)

        total = 0.0
        seen = False
        for item in getattr(response, "positionUnrealizedPnL", []):
            value = getattr(item, "netUnrealizedPnL", None)
            if value is None:
                value = getattr(item, "grossUnrealizedPnL", None)
            scaled = self._scale_money(value, money_digits)
            if scaled is not None:
                total += scaled
                seen = True

        return total if seen else 0.0

    def symbols(self) -> list[dict[str, Any]]:
        request = self.ProtoOASymbolsListReq()
        request.ctidTraderAccountId = int(self._selected_account["account_id"])
        request.includeArchivedSymbols = False
        response = self._send(request)

        result = []
        for symbol in getattr(response, "symbol", []):
            symbol_id = getattr(symbol, "symbolId", None)
            symbol_name = getattr(symbol, "symbolName", None)
            result.append(
                {
                    "symbol_id": symbol_id,
                    "name": symbol_name,
                    "symbol": symbol_name,
                    "description": getattr(symbol, "description", None),
                    "base_asset_id": getattr(symbol, "baseAssetId", None),
                    "quote_asset_id": getattr(symbol, "quoteAssetId", None),
                    "symbol_category_id": getattr(symbol, "symbolCategoryId", None),
                    "enabled": getattr(symbol, "enabled", None),
                }
            )
        return result

    def _full_symbols(self, symbol_ids: list[int]) -> list[Any]:
        if not symbol_ids:
            return []

        request = self.ProtoOASymbolByIdReq()
        request.ctidTraderAccountId = int(self._selected_account["account_id"])
        request.symbolId.extend(int(item) for item in symbol_ids)

        try:
            response = self._send(request)
            return list(getattr(response, "symbol", []))
        except Exception:
            return []

    def prices(self) -> list[dict[str, Any]]:
        symbols = self.symbols()
        symbol_ids = [
            int(item["symbol_id"])
            for item in symbols
            if item.get("symbol_id") is not None
        ]

        # The Open API delivers live quote data through ProtoOASpotEvent.
        # Subscribe, allow the initial events to arrive, then unsubscribe.
        if symbol_ids:
            request = self.ProtoOASubscribeSpotsReq()
            request.ctidTraderAccountId = int(self._selected_account["account_id"])
            request.symbolId.extend(symbol_ids)
            request.subscribeToSpotTimestamp = True

            self._spot_symbols_by_id = {
                int(item["symbol_id"]): str(item.get("name") or item["symbol_id"])
                for item in symbols
                if item.get("symbol_id") is not None
            }

            self._send(request)
            deadline = time.monotonic() + min(self.timeout, 5.0)
            while time.monotonic() < deadline:
                with self._spot_lock:
                    if len(self._spot_cache) >= len(symbol_ids):
                        break
                time.sleep(0.05)

            try:
                unsubscribe = self.ProtoOAUnsubscribeSpotsReq()
                unsubscribe.ctidTraderAccountId = int(
                    self._selected_account["account_id"]
                )
                unsubscribe.symbolId.extend(symbol_ids)
                self._send(unsubscribe, timeout=min(self.timeout, 10.0))
            except Exception:
                pass

        result = []
        with self._spot_lock:
            cache = dict(self._spot_cache)

        for symbol_id, symbol_name in self._spot_symbols_by_id.items():
            spot = cache.get(symbol_id)
            if not spot:
                continue
            result.append(
                {
                    "name": symbol_name,
                    "time": spot.get("time"),
                    "bid": spot.get("bid"),
                    "ask": spot.get("ask"),
                }
            )
        return result

    @staticmethod
    def _enum_name(model: Any, field_name: str) -> Any:
        value = getattr(model, field_name, None)
        return value

    def _reconcile(self) -> tuple[list[Any], list[Any]]:
        request = self.ProtoOAReconcileReq()

        request.ctidTraderAccountId = int(
            self._selected_account["account_id"]
        )

        response = self._send(request)

        return (
            list(getattr(response, "position", [])),
            list(getattr(response, "order", [])),
        )

    def orders(self) -> list[dict[str, Any]]:
        _, orders = self._reconcile()
        result = []
        for order in orders:
            trade_data = getattr(order, "tradeData", None)
            result.append(
                {
                    "order_id": getattr(order, "orderId", None),
                    "client_order_id": getattr(order, "clientOrderId", None),
                    "order_type": getattr(order, "orderType", None),
                    "side": getattr(trade_data, "tradeSide", None),
                    "status": getattr(order, "orderStatus", None),
                    "time_in_force": getattr(order, "timeInForce", None),
                    "symbol": self._symbol_name(
                        getattr(trade_data, "symbolId", None)
                    ),
                    "volume_initial": self._scale_volume(
                        getattr(trade_data, "volume", None)
                    ),
                    "volume_current": self._scale_volume(
                        getattr(order, "executedVolume", None)
                    ),
                    "price_open": getattr(order, "limitPrice", None),
                    "price_current": None,
                    "price_stoplimit": getattr(order, "stopPrice", None),
                    "stop_loss": getattr(trade_data, "stopLoss", None),
                    "take_profit": getattr(trade_data, "takeProfit", None),
                    "comment": getattr(trade_data, "comment", None),
                    "time": self._ms_datetime(
                        getattr(trade_data, "openTimestamp", None)
                    ),
                    "time_done": self._ms_datetime(
                        getattr(order, "utcLastUpdateTimestamp", None)
                    ),
                }
            )
        return result

    def positions(self) -> list[dict[str, Any]]:
        positions, _ = self._reconcile()
        result = []
        for position in positions:
            trade_data = getattr(position, "tradeData", None)
            result.append(
                {
                    "position_id": getattr(position, "positionId", None),
                    "broker_position_id": getattr(position, "positionId", None),
                    "trade_id": None,
                    "side": getattr(trade_data, "tradeSide", None),
                    "position_status": "OPEN",
                    "symbol": self._symbol_name(
                        getattr(trade_data, "symbolId", None)
                    ),
                    "volume": self._scale_volume(
                        getattr(trade_data, "volume", None)
                    ),
                    "open_price": getattr(position, "price", None),
                    "current_price": None,
                    "average_price": getattr(position, "price", None),
                    "stop_loss": getattr(position, "stopLoss", None),
                    "take_profit": getattr(position, "takeProfit", None),
                    "unrealized_pnl": None,
                    "realized_pnl": None,
                    "gross_pnl": None,
                    "net_pnl": None,
                    "margin_used": None,
                    "exposure": None,
                    "overnight_swap": None,
                    "liquidation_price": None,
                    "risk_percentage": None,
                    "account_exposure_pct": None,
                    "floating_drawdown": None,
                    "highest_profit": None,
                    "maximum_drawdown": None,
                    "hedge_group": None,
                    "time": self._ms_datetime(
                        getattr(trade_data, "openTimestamp", None)
                    ),
                    "time_update": self._ms_datetime(
                        getattr(position, "utcLastUpdateTimestamp", None)
                    ),
                    "time_close": self._ms_datetime(
                        getattr(trade_data, "closeTimestamp", None)
                    ),
                }
            )

        # Populate live PnL where available.
        return result

    def deals(self) -> list[dict[str, Any]]:
        from_timestamp = 0
        to_timestamp = int(time.time() * 1000)

        request = self.ProtoOADealListReq()
        request.ctidTraderAccountId = int(self._selected_account["account_id"])
        request.fromTimestamp = from_timestamp
        request.toTimestamp = to_timestamp
        request.maxRows = 1000

        response = self._send(request)
        money_digits = getattr(response, "moneyDigits", 0)
        result = []

        for deal in getattr(response, "deal", []):
            result.append(
                {
                    "deal_id": getattr(deal, "dealId", None),
                    "execution_id": getattr(deal, "dealId", None),
                    "order_id": getattr(deal, "orderId", None),
                    "deal_type": getattr(deal, "executionType", None),
                    "side": getattr(deal, "tradeSide", None),
                    "symbol": self._symbol_name(
                        getattr(deal, "symbolId", None)
                    ),
                    "volume": self._scale_volume(
                        getattr(deal, "filledVolume", None)
                        or getattr(deal, "volume", None)
                    ),
                    "price": getattr(deal, "executionPrice", None),
                    "profit": self._scale_money(
                        getattr(deal, "grossProfit", None),
                        money_digits,
                    ),
                    "realized_pnl": self._scale_money(
                        getattr(deal, "netProfit", None)
                        if getattr(deal, "netProfit", None) is not None
                        else getattr(deal, "grossProfit", None),
                        money_digits,
                    ),
                    "commission": self._scale_money(
                        getattr(deal, "commission", None),
                        money_digits,
                    ),
                    "swap": self._scale_money(
                        getattr(deal, "swap", None),
                        money_digits,
                    ),
                    "fee": self._scale_money(
                        getattr(deal, "fee", None),
                        money_digits,
                    ),
                    "deal_time": self._ms_datetime(
                        getattr(deal, "executionTimestamp", None)
                        or getattr(deal, "createTimestamp", None)
                    ),
                    "external_reference": getattr(
                        deal,
                        "label",
                        None,
                    ),
                }
            )

        return result

    def executions(self) -> list[dict[str, Any]]:
        # cTrader's execution entity is the Deal. Returning a second
        # representation would duplicate provider evidence, so keep the
        # separate canonical executions collection legitimately unavailable.
        return []

    def trades(self) -> list[dict[str, Any]]:
        # cTrader Open API does not expose a distinct "trade" entity that
        # corresponds 1:1 with the TTL canonical trade collection.
        return []

    def history(self) -> list[dict[str, Any]]:
        from_timestamp = 0
        to_timestamp = int(time.time() * 1000)

        request = self.ProtoOAOrderListReq()
        request.ctidTraderAccountId = int(self._selected_account["account_id"])
        request.fromTimestamp = from_timestamp
        request.toTimestamp = to_timestamp
        response = self._send(request)

        return list(getattr(response, "order", []))

    def activity(self) -> list[dict[str, Any]]:
        # No single native cTrader activity feed maps cleanly to the current
        # TTL activity contract without manufacturing semantics.
        return []

    def _symbol_name(self, symbol_id: Any) -> str | None:
        if symbol_id is None:
            return None

        try:
            symbol_id = int(symbol_id)
        except (TypeError, ValueError):
            return None

        cached = self._spot_symbols_by_id.get(symbol_id)
        if cached:
            return cached

        try:
            for item in self.symbols():
                if item.get("symbol_id") == symbol_id:
                    name = item.get("name")
                    if name:
                        self._spot_symbols_by_id[symbol_id] = name
                        return str(name)
        except Exception:
            return None

        return None

class CTraderAdapter(BaseDesktopAdapter):
    """
    Thin adapter over the official cTrader Open API.

    This adapter performs only native evidence acquisition.

    It does not perform:

        • Translation
        • Validation
        • Verification
        • Business Logic
    """

    # ------------------------------------------------------------------
    # Provider-boundary normalization helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get(
        source: Any,
        *names: str,
        default: Any = None,
    ) -> Any:
        """
        Read the first available value from a dictionary or SDK object.
        """

        if source is None:
            return default

        for name in names:
            if isinstance(source, dict):
                value = source.get(name)
            else:
                value = getattr(
                    source,
                    name,
                    None,
                )

            if value is not None:
                return value

        return default

    @classmethod
    def _identifier(
        cls,
        source: Any,
        *names: str,
    ) -> str | None:
        value = cls._get(
            source,
            *names,
        )

        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if not value or value == "0":
                return None

            return value

        if isinstance(value, (int, float)):
            if value == 0:
                return None

            return str(value)

        value = str(value).strip()

        if not value or value == "0":
            return None

        return value

    @classmethod
    def _float(
        cls,
        source: Any,
        *names: str,
    ) -> float | None:
        value = cls._get(
            source,
            *names,
        )

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _string(
        cls,
        source: Any,
        *names: str,
    ) -> str | None:
        value = cls._get(
            source,
            *names,
        )

        if value is None:
            return None

        value = str(value).strip()

        return value or None

    @classmethod
    def _datetime(
        cls,
        source: Any,
        *names: str,
    ) -> datetime | None:
        value = cls._get(
            source,
            *names,
        )

        if value is None:
            return None

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(
                    tzinfo=UTC
                )

            return value.astimezone(UTC)

        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(
                    float(value),
                    tz=UTC,
                )
            except (
                TypeError,
                ValueError,
                OSError,
                OverflowError,
            ):
                return None

        if isinstance(value, str):
            normalized = value.strip()

            if not normalized:
                return None

            try:
                parsed = datetime.fromisoformat(
                    normalized.replace(
                        "Z",
                        "+00:00",
                    )
                )

                if parsed.tzinfo is None:
                    parsed = parsed.replace(
                        tzinfo=UTC
                    )

                return parsed.astimezone(UTC)

            except ValueError:
                return None

        return None

    @classmethod
    def _side(
        cls,
        source: Any,
    ) -> str | None:
        value = cls._get(
            source,
            "side",
            "direction",
            "trade_side",
            "order_side",
        )

        if value is None:
            return None

        normalized = str(value).strip().upper()

        if "BUY" in normalized:
            return "BUY"

        if "SELL" in normalized:
            return "SELL"

        return None

    def __init__(
        self,
        *,
        client: Any,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
        account_id: str | None = None,
        environment: str = "live",
    ) -> None:

        self.client = client

        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.requested_account_id = account_id

        normalized_environment = (
            str(environment or "live")
            .strip()
            .lower()
        )

        self.environment = (
            "demo"
            if normalized_environment in {
                "demo",
                "development",
                "sandbox",
                "paper",
            }
            else "live"
        )

    @classmethod
    def from_connection_config(
        cls,
        *,
        credentials: dict[str, Any],
        environment: str,
    ) -> "CTraderAdapter":
        """
        Construct a cTrader adapter from canonical Provider Connection
        credentials.

        cTrader authentication is OAuth/Open API based; no MT-style
        login/password/server/terminal executable is used.
        """

        client_id = (
            credentials.get("client_id")
            or credentials.get("clientId")
        )

        client_secret = (
            credentials.get("client_secret")
            or credentials.get("clientSecret")
        )

        access_token = (
            credentials.get("access_token")
            or credentials.get("accessToken")
        )

        account_id = (
            credentials.get("account_id")
            or credentials.get("ctid_trader_account_id")
            or credentials.get("ctidTraderAccountId")
        )

        if not client_id:
            raise ValueError(
                "cTrader client_id is required."
            )

        if not client_secret:
            raise ValueError(
                "cTrader client_secret is required."
            )

        # The actual official cTrader Open API client construction
        # is intentionally isolated here.
        client = cls._build_open_api_client(
            client_id=str(client_id),
            client_secret=str(client_secret),
            access_token=(
                str(access_token)
                if access_token
                else None
            ),
            account_id=(
                str(account_id)
                if account_id
                else None
            ),
            environment=environment,
        )

        return cls(
            client=client,
            client_id=str(client_id),
            client_secret=str(client_secret),
            access_token=(
                str(access_token)
                if access_token
                else None
            ),
            account_id=(
                str(account_id)
                if account_id
                else None
            ),
            environment=environment,
        )

    @staticmethod
    def _build_open_api_client(
        *,
        client_id: str,
        client_secret: str,
        access_token: str | None,
        account_id: str | None,
        environment: str,
    ) -> Any:
        """
        Build the provider-native cTrader Open API client.

        The frontend connection form supplies client_id, client_secret,
        access_token and optionally account_id. The native facade performs
        application authentication, account discovery and account
        authorization during connect().
        """
        if not access_token:
            raise ValueError(
                "cTrader access_token is required. Complete cTrader OAuth "
                "authorization and store the issued access token before "
                "connecting the provider."
            )

        return _CTraderOpenApiClient(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            account_id=account_id,
            environment=environment,
        )

    # ------------------------------------------------------------------
    # Provider Information
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "cTrader"

    @property
    def provider_version(self) -> str:

        version = getattr(
            self.client,
            "version",
            None,
        )

        return version or "unknown"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """
        Connect to the cTrader Open API.
        """

        if self.client is None:
            raise RuntimeError(
                "cTrader client has not been initialized."
            )

        self.client.connect()

    def disconnect(self) -> None:
        """
        Disconnect from cTrader.
        """

        self.client.disconnect()

    def is_connected(self) -> bool:
        """
        Determine connection status.
        """

        return self.client.is_connected()

    # ------------------------------------------------------------------
    # Infrastructure Builders
    # ------------------------------------------------------------------

    def _build_terminal(self):

        return self.client.terminal()

    def _build_user(self):

        return getattr(
            self.client,
            "user",
            lambda: None,
        )()

    def _build_broker(self):

        return getattr(
            self.client,
            "broker",
            lambda: None,
        )()

    def _build_server(self):

        return getattr(
            self.client,
            "server",
            lambda: None,
        )()

    def _build_account(self):

        return self.client.account()

    # ------------------------------------------------------------------
    # Financial Builders
    # ------------------------------------------------------------------

    def _build_financial(self):
        value = self.client.financial()

        return {
            "balance": self._float(
                value,
                "balance",
                "cash_balance",
            ),

            "equity": self._float(
                value,
                "equity",
                "account_value",
            ),

            "margin": self._float(
                value,
                "margin",
                "margin_used",
            ),

            "buying_power": self._float(
                value,
                "buying_power",
                "available_margin",
                "free_margin",
                "margin_free",
            ),
        }

    # ------------------------------------------------------------------
    # Market Builders
    # ------------------------------------------------------------------

    def _build_symbols(self):
        values = self.client.symbols()

        normalized = []

        for value in values or []:
            symbol_name = self._string(
                value,
                "name",
                "symbol",
                "symbol_name",
                "code",
            )

            normalized.append(
                {
                    "name": symbol_name,

                    "description": self._string(
                        value,
                        "description",
                    ),

                    "path": self._string(
                        value,
                        "path",
                    ),

                    "currency_base": self._string(
                        value,
                        "currency_base",
                        "base_currency",
                    ),

                    "currency_profit": self._string(
                        value,
                        "currency_profit",
                        "quote_currency",
                    ),

                    "currency_margin": self._string(
                        value,
                        "currency_margin",
                        "margin_currency",
                    ),

                    "trade_mode": self._get(
                        value,
                        "trade_mode",
                        "trading_mode",
                    ),

                    "digits": self._get(
                        value,
                        "digits",
                    ),

                    "point": self._float(
                        value,
                        "point",
                        "point_size",
                    ),

                    "trade_contract_size": self._float(
                        value,
                        "trade_contract_size",
                        "contract_size",
                    ),

                    "trade_tick_size": self._float(
                        value,
                        "trade_tick_size",
                        "tick_size",
                    ),

                    "trade_tick_value": self._float(
                        value,
                        "trade_tick_value",
                        "tick_value",
                    ),

                    "volume_min": self._float(
                        value,
                        "volume_min",
                        "minimum_volume",
                    ),

                    "volume_max": self._float(
                        value,
                        "volume_max",
                        "maximum_volume",
                    ),

                    "volume_step": self._float(
                        value,
                        "volume_step",
                        "volume_step_size",
                    ),
                }
            )

        return normalized

    def _build_prices(self):
        values = self.client.prices()

        normalized = []

        for value in values or []:
            symbol_name = self._string(
                value,
                "name",
                "symbol",
                "symbol_name",
                "code",
            )

            if not symbol_name:
                continue

            normalized.append(
                {
                    "name": symbol_name,

                    "time": self._datetime(
                        value,
                        "time",
                        "timestamp",
                        "updated_at",
                    ),

                    "bid": self._float(
                        value,
                        "bid",
                    ),

                    "ask": self._float(
                        value,
                        "ask",
                    ),

                    "last": self._float(
                        value,
                        "last",
                        "last_price",
                    ),

                    "volume": self._float(
                        value,
                        "volume",
                        "volume_real",
                    ),

                    "volume_real": self._float(
                        value,
                        "volume_real",
                        "volume",
                    ),

                    "askhigh": self._float(
                        value,
                        "askhigh",
                        "high",
                    ),

                    "asklow": self._float(
                        value,
                        "asklow",
                        "low",
                    ),

                    "spread": self._float(
                        value,
                        "spread",
                    ),
                }
            )

        return normalized

    # ------------------------------------------------------------------
    # Trading Builders
    # ------------------------------------------------------------------

    def _build_orders(self):
        values = self.client.orders()

        normalized = []

        for value in values or []:
            volume_initial = self._float(
                value,
                "volume_initial",
                "quantity",
                "volume",
            )

            volume_current = self._float(
                value,
                "volume_current",
                "remaining_quantity",
                "remaining_volume",
            )

            normalized.append(
                {
                    "order_id": self._identifier(
                        value,
                        "order_id",
                        "id",
                        "orderId",
                        "ticket",
                    ),

                    "client_order_id": self._identifier(
                        value,
                        "client_order_id",
                        "clientOrderId",
                    ),

                    "parent_order_id": self._identifier(
                        value,
                        "parent_order_id",
                        "parentOrderId",
                    ),

                    "order_type": self._string(
                        value,
                        "order_type",
                        "type",
                        "orderType",
                    ),

                    "side": self._side(
                        value,
                    ),

                    "status": self._string(
                        value,
                        "status",
                        "state",
                    ),

                    "time_in_force": self._string(
                        value,
                        "time_in_force",
                        "timeInForce",
                    ),

                    "symbol": self._string(
                        value,
                        "symbol",
                        "symbol_name",
                        "name",
                    ),

                    "volume_initial": volume_initial,

                    "volume_current": volume_current,

                    "price_open": self._float(
                        value,
                        "price_open",
                        "open_price",
                        "price",
                    ),

                    "price_current": self._float(
                        value,
                        "price_current",
                        "current_price",
                    ),

                    "price_stoplimit": self._float(
                        value,
                        "price_stoplimit",
                        "stop_limit_price",
                    ),

                    "stop_loss": self._float(
                        value,
                        "stop_loss",
                        "sl",
                    ),

                    "take_profit": self._float(
                        value,
                        "take_profit",
                        "tp",
                    ),

                    "comment": self._string(
                        value,
                        "comment",
                    ),

                    "time": self._datetime(
                        value,
                        "time",
                        "created_at",
                        "setup_time",
                        "time_setup",
                    ),

                    "time_done": self._datetime(
                        value,
                        "time_done",
                        "closed_at",
                        "updated_at",
                    ),
                }
            )

        return normalized

    def _build_executions(self):
        values = self.client.executions()

        normalized = []

        for value in values or []:
            normalized.append(
                {
                    "execution_id": self._identifier(
                        value,
                        "execution_id",
                        "executionId",
                        "id",
                        "ticket",
                    ),

                    "order_id": self._identifier(
                        value,
                        "order_id",
                        "orderId",
                        "order",
                    ),

                    "execution_type": self._string(
                        value,
                        "execution_type",
                        "type",
                    ),

                    "execution_price": self._float(
                        value,
                        "execution_price",
                        "price",
                    ),

                    "execution_quantity": self._float(
                        value,
                        "execution_quantity",
                        "quantity",
                        "volume",
                    ),

                    "execution_time": self._datetime(
                        value,
                        "execution_time",
                        "time",
                        "executed_at",
                        "timestamp",
                    ),

                    "side": self._side(
                        value,
                    ),

                    "liquidity": self._string(
                        value,
                        "liquidity",
                    ),

                    "venue": self._string(
                        value,
                        "venue",
                    ),

                    "execution_reference": self._identifier(
                        value,
                        "execution_reference",
                        "reference",
                    ),

                    "commission": self._float(
                        value,
                        "commission",
                    ),

                    "fees": self._float(
                        value,
                        "fees",
                        "fee",
                    ),

                    "slippage": self._float(
                        value,
                        "slippage",
                    ),
                }
            )

        return normalized

    def _build_deals(self):
        values = self.client.deals()

        normalized = []

        for value in values or []:
            normalized.append(
                {
                    "deal_id": self._identifier(
                        value,
                        "deal_id",
                        "dealId",
                        "id",
                        "ticket",
                    ),

                    "execution_id": self._identifier(
                        value,
                        "execution_id",
                        "executionId",
                    ),

                    "order_id": self._identifier(
                        value,
                        "order_id",
                        "orderId",
                        "order",
                    ),

                    "deal_type": self._string(
                        value,
                        "deal_type",
                        "type",
                        "dealType",
                    ),

                    "side": self._side(
                        value,
                    ),

                    "symbol": self._string(
                        value,
                        "symbol",
                        "symbol_name",
                        "name",
                    ),

                    "volume": self._float(
                        value,
                        "volume",
                        "quantity",
                    ),

                    "price": self._float(
                        value,
                        "price",
                        "execution_price",
                    ),

                    "profit": self._float(
                        value,
                        "profit",
                        "pnl",
                    ),

                    "realized_pnl": self._float(
                        value,
                        "realized_pnl",
                        "profit",
                        "pnl",
                    ),

                    "commission": self._float(
                        value,
                        "commission",
                    ),

                    "swap": self._float(
                        value,
                        "swap",
                    ),

                    "fee": self._float(
                        value,
                        "fee",
                        "fees",
                    ),

                    "deal_time": self._datetime(
                        value,
                        "deal_time",
                        "time",
                        "executed_at",
                        "timestamp",
                    ),

                    "external_reference": self._identifier(
                        value,
                        "external_reference",
                        "external_id",
                    ),
                }
            )

        return normalized

    def _build_trades(self):
        values = self.client.trades()

        normalized = []

        for value in values or []:
            normalized.append(
                {
                    "trade_id": self._identifier(
                        value,
                        "trade_id",
                        "tradeId",
                        "id",
                        "ticket",
                    ),

                    "broker_trade_id": self._identifier(
                        value,
                        "broker_trade_id",
                        "brokerTradeId",
                    ),

                    "order_id": self._identifier(
                        value,
                        "order_id",
                        "orderId",
                    ),

                    "execution_id": self._identifier(
                        value,
                        "execution_id",
                        "executionId",
                    ),

                    "deal_id": self._identifier(
                        value,
                        "deal_id",
                        "dealId",
                    ),

                    "broker_ticket": self._identifier(
                        value,
                        "broker_ticket",
                        "ticket",
                    ),

                    "symbol": self._string(
                        value,
                        "symbol",
                        "symbol_name",
                        "name",
                    ),

                    "side": self._side(
                        value,
                    ),

                    "trade_status": self._string(
                        value,
                        "trade_status",
                        "status",
                        "state",
                    ),

                    "volume": self._float(
                        value,
                        "volume",
                        "quantity",
                    ),

                    "entry_price": self._float(
                        value,
                        "entry_price",
                        "open_price",
                        "price",
                    ),

                    "exit_price": self._float(
                        value,
                        "exit_price",
                        "close_price",
                    ),

                    "average_entry_price": self._float(
                        value,
                        "average_entry_price",
                    ),

                    "average_exit_price": self._float(
                        value,
                        "average_exit_price",
                    ),

                    "stop_loss": self._float(
                        value,
                        "stop_loss",
                        "sl",
                    ),

                    "take_profit": self._float(
                        value,
                        "take_profit",
                        "tp",
                    ),

                    "realized_pnl": self._float(
                        value,
                        "realized_pnl",
                        "profit",
                        "pnl",
                    ),

                    "unrealized_pnl": self._float(
                        value,
                        "unrealized_pnl",
                    ),

                    "gross_pnl": self._float(
                        value,
                        "gross_pnl",
                    ),

                    "net_pnl": self._float(
                        value,
                        "net_pnl",
                    ),

                    "commission": self._float(
                        value,
                        "commission",
                    ),

                    "swap": self._float(
                        value,
                        "swap",
                    ),

                    "fees": self._float(
                        value,
                        "fees",
                        "fee",
                    ),

                    "slippage": self._float(
                        value,
                        "slippage",
                    ),

                    "strategy_id": self._identifier(
                        value,
                        "strategy_id",
                        "strategyId",
                    ),

                    "strategy_name": self._string(
                        value,
                        "strategy_name",
                        "strategyName",
                    ),

                    "trade_reference": self._identifier(
                        value,
                        "trade_reference",
                        "reference",
                    ),
                }
            )

        return normalized

    def _build_positions(self):
        values = self.client.positions()

        normalized = []

        for value in values or []:
            normalized.append(
                {
                    "position_id": self._identifier(
                        value,
                        "position_id",
                        "positionId",
                        "id",
                        "ticket",
                    ),

                    "broker_position_id": self._identifier(
                        value,
                        "broker_position_id",
                        "brokerPositionId",
                        "identifier",
                    ),

                    "trade_id": self._identifier(
                        value,
                        "trade_id",
                        "tradeId",
                    ),

                    "side": self._side(
                        value,
                    ),

                    "position_status": self._string(
                        value,
                        "position_status",
                        "status",
                        "state",
                    ),

                    "symbol": self._string(
                        value,
                        "symbol",
                        "symbol_name",
                        "name",
                    ),

                    "volume": self._float(
                        value,
                        "volume",
                        "quantity",
                    ),

                    "open_price": self._float(
                        value,
                        "open_price",
                        "entry_price",
                        "price_open",
                    ),

                    "current_price": self._float(
                        value,
                        "current_price",
                        "price_current",
                        "market_price",
                    ),

                    "average_price": self._float(
                        value,
                        "average_price",
                    ),

                    "stop_loss": self._float(
                        value,
                        "stop_loss",
                        "sl",
                    ),

                    "take_profit": self._float(
                        value,
                        "take_profit",
                        "tp",
                    ),

                    "unrealized_pnl": self._float(
                        value,
                        "unrealized_pnl",
                        "profit",
                        "pnl",
                    ),

                    "realized_pnl": self._float(
                        value,
                        "realized_pnl",
                    ),

                    "gross_pnl": self._float(
                        value,
                        "gross_pnl",
                    ),

                    "net_pnl": self._float(
                        value,
                        "net_pnl",
                    ),

                    "margin_used": self._float(
                        value,
                        "margin_used",
                        "margin",
                    ),

                    "exposure": self._float(
                        value,
                        "exposure",
                    ),

                    "overnight_swap": self._float(
                        value,
                        "overnight_swap",
                        "swap",
                    ),

                    "liquidation_price": self._float(
                        value,
                        "liquidation_price",
                    ),

                    "risk_percentage": self._float(
                        value,
                        "risk_percentage",
                    ),

                    "account_exposure_pct": self._float(
                        value,
                        "account_exposure_pct",
                    ),

                    "floating_drawdown": self._float(
                        value,
                        "floating_drawdown",
                    ),

                    "highest_profit": self._float(
                        value,
                        "highest_profit",
                    ),

                    "maximum_drawdown": self._float(
                        value,
                        "maximum_drawdown",
                    ),

                    "hedge_group": self._string(
                        value,
                        "hedge_group",
                    ),

                    "time": self._datetime(
                        value,
                        "time",
                        "opened_at",
                        "created_at",
                    ),

                    "time_update": self._datetime(
                        value,
                        "time_update",
                        "updated_at",
                        "modified_at",
                    ),

                    "time_close": self._datetime(
                        value,
                        "time_close",
                        "closed_at",
                    ),
                }
            )

        return normalized

    # ------------------------------------------------------------------
    # History Builders
    # ------------------------------------------------------------------

    def _build_history(self):
        values = self.client.history()

        return list(values or [])

    def _build_activity(self):
        values = self.client.activity()

        normalized = []

        for value in values or []:
            normalized.append(
                {
                    "comment": self._string(
                        value,
                        "comment",
                        "message",
                        "description",
                    ),

                    "activity_type": self._string(
                        value,
                        "activity_type",
                        "type",
                    ),

                    "category": self._string(
                        value,
                        "category",
                    ),

                    "time": self._datetime(
                        value,
                        "time",
                        "timestamp",
                        "created_at",
                    ),
                }
            )

        return normalized

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def get_verification_snapshot(
        self,
    ) -> VerificationSnapshot:
        """
        Return provider-neutral verification facts.

        This method performs provider-native observation only.
        Verification decisions remain in the shared
        Desktop Verification Engine.
        """

        terminal = self._build_terminal()
        user = self._build_user()
        broker = self._build_broker()
        server = self._build_server()
        account = self._build_account()

        connected = self.is_connected()

        def read_value(source, *keys):
            if source is None:
                return None

            if isinstance(source, dict):
                for key in keys:
                    value = source.get(key)
                    if value is not None:
                        return value

            for key in keys:
                value = getattr(source, key, None)
                if value is not None:
                    return value

            if isinstance(source, (str, int)):
                return source

            return None

        account_id = read_value(
            account,
            "account_id",
            "account_number",
            "login",
            "id",
            "number",
        )

        if account_id is None:
            account_id = read_value(
                user,
                "account_id",
                "account_number",
                "login",
                "id",
                "number",
            )

        broker_value = read_value(
            broker,
            "name",
            "company",
            "broker",
            "broker_name",
        )

        if broker_value is None and isinstance(
            broker,
            (str, int),
        ):
            broker_value = str(broker)

        server_value = read_value(
            server,
            "name",
            "server",
            "server_name",
        )

        if server_value is None and isinstance(
            server,
            (str, int),
        ):
            server_value = str(server)

        terminal_version = read_value(
            terminal,
            "version",
            "version_string",
            "terminal_version",
            "build",
        )

        if terminal_version is None:
            terminal_version = self.provider_version

        return VerificationSnapshot(
            provider=self.provider_name,
            provider_version=self.provider_version,
            connected=connected,
            account_id=(
                str(account_id)
                if account_id is not None
                else None
            ),
            broker=(
                str(broker_value)
                if broker_value is not None
                else None
            ),
            server=(
                str(server_value)
                if server_value is not None
                else None
            ),
            terminal=self.provider_name,
            terminal_version=(
                str(terminal_version)
                if terminal_version is not None
                else None
            ),
            metadata={
                "terminal_available": terminal is not None,
                "user_available": user is not None,
                "broker_available": broker is not None,
                "server_available": server is not None,
                "account_available": account is not None,
            },
        )

    # ------------------------------------------------------------------
    # Evidence Acquisition
    # ------------------------------------------------------------------

    def acquire(self) -> Dict[str, Any]:
        """
        Acquire the complete native cTrader evidence surface.

        The returned payload is broker-independent and follows
        the canonical Desktop Trading Engine acquisition contract.
        """

        terminal = self._build_terminal()

        user = self._build_user()

        broker = self._build_broker()

        server = self._build_server()

        account = self._build_account()

        financial = self._build_financial()

        symbols = self._build_symbols()

        prices = self._build_prices()

        orders = self._build_orders()

        executions = self._build_executions()

        deals = self._build_deals()

        trades = self._build_trades()

        positions = self._build_positions()

        history = self._build_history()

        activity = self._build_activity()

        payload = {

            # ----------------------------------------------------------
            # Connector Metadata
            # ----------------------------------------------------------

            "connector_name": self.provider_name,

            "connector_version": self.provider_version,

            "schema_version": "1.0",

            # ----------------------------------------------------------
            # Infrastructure
            # ----------------------------------------------------------

            "terminal": terminal,

            "user": user,

            "broker": broker,

            "server": server,

            "account": account,

            # ----------------------------------------------------------
            # Financial
            # ----------------------------------------------------------

            "financial": financial,

            # ----------------------------------------------------------
            # Market
            # ----------------------------------------------------------

            "symbols": symbols,

            "prices": prices,

            # ----------------------------------------------------------
            # Trading
            # ----------------------------------------------------------

            "orders": orders,

            "executions": executions,

            "deals": deals,

            "trades": trades,

            "positions": positions,

            # ----------------------------------------------------------
            # History
            # ----------------------------------------------------------

            "history": history,

            "activity": activity,
        }

        return desktop_evidence_normalizer.normalize(
            payload,
        )