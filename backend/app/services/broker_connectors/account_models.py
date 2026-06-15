from dataclasses import dataclass


@dataclass
class BrokerAccount:

    account_id: str

    account_name: str

    environment: str

    currency: str | None = None

    broker_server: str | None = None

    leverage: int | None = None

    balance: float | None = None

    equity: float | None = None

    broker_name: str | None = None