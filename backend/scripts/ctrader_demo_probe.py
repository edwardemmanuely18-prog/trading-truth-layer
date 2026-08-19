"""
TTL cTrader Demo Connectivity / Authentication Probe

Purpose:
    1. Connect to the cTrader DEMO Open API endpoint.
    2. Authenticate the Trading Truth Layer application.
    3. Discover accounts authorized by the supplied access token.
    4. Print non-secret account metadata only.

Credentials are read from environment variables:
    CTRADER_CLIENT_ID
    CTRADER_CLIENT_SECRET
    CTRADER_ACCESS_TOKEN

Do NOT hard-code credentials into this file.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from ctrader_open_api import Client, EndPoints, Protobuf, TcpProtocol
from ctrader_open_api.messages.OpenApiMessages_pb2 import (
    ProtoOAApplicationAuthReq,
    ProtoOAGetAccountListByAccessTokenReq,
)
from twisted.internet import reactor


CLIENT_ID_ENV = "CTRADER_CLIENT_ID"
CLIENT_SECRET_ENV = "CTRADER_CLIENT_SECRET"
ACCESS_TOKEN_ENV = "CTRADER_ACCESS_TOKEN"


def require_environment_variable(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable {name!r} is not set."
        )
    return value.strip()


CLIENT_ID = require_environment_variable(CLIENT_ID_ENV)
CLIENT_SECRET = require_environment_variable(CLIENT_SECRET_ENV)
ACCESS_TOKEN = require_environment_variable(ACCESS_TOKEN_ENV)


client = Client(
    EndPoints.PROTOBUF_DEMO_HOST,
    EndPoints.PROTOBUF_PORT,
    TcpProtocol,
)

_stop_requested = False


def stop_reactor() -> None:
    """Stop Twisted's reactor exactly once."""
    global _stop_requested

    if _stop_requested:
        return

    _stop_requested = True

    try:
        if reactor.running:
            reactor.stop()
    except Exception:
        pass


def print_failure(failure: Any) -> None:
    """Print a useful Twisted failure without exposing credentials."""
    print()
    print("=== CTRADER ERROR ===")

    try:
        failure.printTraceback()
    except Exception:
        print(failure)

    stop_reactor()


def on_accounts(message: Any) -> None:
    """Process ProtoOAGetAccountListByAccessToken response."""
    print()
    print("=== ACCOUNT DISCOVERY ===")

    try:
        response = Protobuf.extract(message)
    except Exception as exc:
        print("ACCOUNT_DISCOVERY: FAILED")
        print(f"Unable to extract protobuf response: {exc}")
        stop_reactor()
        return

    accounts = list(getattr(response, "ctidTraderAccount", []))

    if not accounts:
        print("ACCOUNT_DISCOVERY: PASS")
        print("NO_ACCOUNTS_RETURNED")
        stop_reactor()
        return

    print("ACCOUNT_DISCOVERY: PASS")
    print(f"AUTHORIZED_ACCOUNT_COUNT: {len(accounts)}")

    for index, account in enumerate(accounts, start=1):
        account_id = getattr(account, "ctidTraderAccountId", None)
        is_live = getattr(account, "isLive", None)
        trader_login = getattr(account, "traderLogin", None)
        broker_title = getattr(account, "brokerTitleShort", None)

        print(
            {
                "index": index,
                "ctidTraderAccountId": account_id,
                "isLive": is_live,
                "traderLogin": trader_login,
                "brokerTitleShort": broker_title,
            }
        )

    print()
    print("EXPECTED_DEMO_ENVIRONMENT: isLive=False")
    stop_reactor()


def on_application_auth(_message: Any) -> None:
    """Application authorization succeeded."""
    print("APPLICATION_AUTH: PASS")

    request = ProtoOAGetAccountListByAccessTokenReq()
    request.accessToken = ACCESS_TOKEN

    try:
        deferred = client.send(request)
    except Exception as exc:
        print("ACCOUNT_DISCOVERY_REQUEST: FAILED")
        print(exc)
        stop_reactor()
        return

    deferred.addCallback(on_accounts)
    deferred.addErrback(print_failure)


def on_connected(_client: Any) -> None:
    """TCP/TLS connection succeeded."""
    print("TCP_CONNECTION: PASS")

    request = ProtoOAApplicationAuthReq()
    request.clientId = CLIENT_ID
    request.clientSecret = CLIENT_SECRET

    try:
        deferred = client.send(request)
    except Exception as exc:
        print("APPLICATION_AUTH_REQUEST: FAILED")
        print(exc)
        stop_reactor()
        return

    deferred.addCallback(on_application_auth)
    deferred.addErrback(print_failure)


def on_disconnected(_client: Any, reason: Any) -> None:
    """Report unexpected disconnection."""
    if reason:
        print(f"DISCONNECTED: {reason}")


def main() -> int:
    print("=" * 72)
    print("TRADING TRUTH LAYER — cTrader DEMO OPEN API PROBE")
    print("=" * 72)
    print(f"Endpoint: {EndPoints.PROTOBUF_DEMO_HOST}:{EndPoints.PROTOBUF_PORT}")
    print(f"{CLIENT_ID_ENV}: SET")
    print(f"{CLIENT_SECRET_ENV}: SET")
    print(f"{ACCESS_TOKEN_ENV}: SET")
    print("=" * 72)

    client.setConnectedCallback(on_connected)
    client.setDisconnectedCallback(on_disconnected)

    try:
        client.startService()
        reactor.run()
    except KeyboardInterrupt:
        print()
        print("INTERRUPTED")
        stop_reactor()
        return 130
    except Exception as exc:
        print()
        print("PROBE_FAILED:", exc)
        stop_reactor()
        return 1

    print()
    print("PROBE_FINISHED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"CONFIGURATION_ERROR: {exc}")
        sys.exit(2)
