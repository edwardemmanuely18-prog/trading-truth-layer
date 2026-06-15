from app.services.broker_connectors.base_connector import (
    BaseBrokerConnector,
)

from app.services.broker_connectors.account_models import (
    BrokerAccount,
)


class MT5Connector(BaseBrokerConnector):

    def __init__(
        self,
        credential,
    ):
        self.credential = credential

    def verify(
        self,
        payload: dict,
    ):

        import MetaTrader5 as mt5

        initialized = mt5.initialize(
            login=int(payload["login"]),
            password=payload["password"],
            server=payload["server"],
        )

        if not initialized:
            return {
                "success": False,
                "error": str(mt5.last_error()),
            }

        try:

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

                "account_id":
                    str(account.login),

                "account_name":
                    account.name,

                "account_environment":
                    environment,

                "broker_account_id":
                    str(account.login),

                "broker_server":
                    account.server,

                "currency":
                    account.currency,

                "leverage":
                    account.leverage,

                "balance":
                    float(account.balance),

                "equity":
                    float(account.equity),

                "broker":
                    account.company,
            }

        finally:

            mt5.shutdown()

    def discover_accounts(
        self,
    ) -> list[BrokerAccount]:

        import MetaTrader5 as mt5

        if not mt5.initialize():
            return {}

        authorized = mt5.login(
            login=int(self.credential.username),
            password=self.credential.password_encrypted,
            server=self.credential.server_name,
        )

        if not authorized:
            return {}

        try:

            account = mt5.account_info()

            if not account:
                return []

            environment = "demo"

            if (
                account.trade_mode
                == mt5.ACCOUNT_TRADE_MODE_REAL
            ):
                environment = "live"

            return [
                BrokerAccount(
                    account_id=str(account.login),
                    account_name=account.name,
                    environment=environment,
                    currency=account.currency,
                    broker_server=account.server,
                    leverage=account.leverage,
                    balance=float(account.balance),
                    equity=float(account.equity),
                    broker_name=account.company,
                )
            ]

        finally:

            mt5.shutdown()

    def sync_trades(
        self,
    ):
        return []

    def sync_positions(
        self,
    ):
        import MetaTrader5 as mt5

        if not mt5.initialize():
            return []

        authorized = mt5.login(
            login=int(self.credential.username),
            password=self.credential.password_encrypted,
            server=self.credential.server_name,
        )

        if not authorized:
            return []

        try:

            positions = mt5.positions_get()

            if positions is None:
                return []

            return positions

        finally:

            mt5.shutdown()

    def sync_account_state(
        self,
    ):
        import MetaTrader5 as mt5

        if not mt5.initialize():
            return {}

        authorized = mt5.login(
            login=int(self.credential.username),
            password=self.credential.password_encrypted,
            server=self.credential.server_name,
        )

        if not authorized:
            return {}

        try:

            account = mt5.account_info()

            if not account:
                return {}

            return {

                "account_id":
                    str(account.login),

                "balance":
                    float(account.balance),

                "equity":
                    float(account.equity),

                "margin":
                    float(account.margin),

                "free_margin":
                    float(account.margin_free),

                "currency":
                    account.currency,

                "leverage":
                    account.leverage,

                "server":
                    account.server,
            }

        finally:

            mt5.shutdown()