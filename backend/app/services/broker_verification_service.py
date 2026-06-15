from typing import Dict


def verify_mt5_connection(
    login: str,
    password: str,
    server: str,
) -> Dict:
    try:
        import MetaTrader5 as mt5

        initialized = mt5.initialize(
            login=int(login),
            password=password,
            server=server,
        )

        if not initialized:
            return {
                "success": False,
                "error": mt5.last_error(),
            }

        account = mt5.account_info()

        if not account:
            return {
                "success": False,
                "error": "Unable to load account",
            }

        environment = "demo"

        if (
            account.trade_mode
            == mt5.ACCOUNT_TRADE_MODE_REAL
        ):
            environment = "live"

        return {
            "success": True,

            "account_id": str(account.login),
            "account_name": account.name,

            "account_environment": environment,

            "broker_account_id": str(account.login),

            "broker_server": account.server,

            "currency": account.currency,

            "leverage": str(account.leverage),

            "balance": float(account.balance),

            "equity": float(account.equity),

            "broker": account.company,
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }


def verify_ibkr_connection(
    api_key: str,
    api_secret: str,
):

    from app.services.broker_connectors.ibkr_gateway_client import (
        IBKRGatewayClient,
    )

    client = IBKRGatewayClient(
        host="127.0.0.1",
        port=7497,
        client_id=1,
    )

    connected = client.connect()

    if not connected:
        return {
            "success": False,
            "error":
                "Unable to connect to IBKR Gateway",
        }

    try:

        accounts = client.list_accounts()

        if not accounts:
            return {
                "success": False,
                "error":
                    "No IBKR accounts discovered",
            }

        account = accounts[0]

        return {
            "success": True,

            "account_id":
                account["account_id"],

            "account_name":
                account["account_name"],

            "account_environment":
                account["environment"],

            "broker_account_id":
                account["account_id"],

            "broker_server":
                "IBKR Gateway",

            "currency":
                account["currency"],

            "leverage":
                None,

            "balance":
                None,

            "equity":
                None,
        }

    finally:

        client.disconnect()


def verify_connection(
    provider: str,
    payload: dict,
):
    provider = provider.lower()

    if provider in [
        "metatrader 5",
        "metatrader 4",
        "mt5",
        "mt4",
    ]:
        return verify_mt5_connection(
            login=payload["login"],
            password=payload["password"],
            server=payload["server"],
        )

    if provider in [
        "interactive brokers",
        "interactive_brokers",
        "ibkr",
    ]:
        return verify_ibkr_connection(
            payload.get(
                "api_key",
                "",
            ),
            payload.get(
                "api_secret",
                "",
            ),
        )

    return {
        "success": False,
        "error":
            f"Unsupported provider: {provider}",
    }