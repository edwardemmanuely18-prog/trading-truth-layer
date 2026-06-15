from dataclasses import dataclass


@dataclass
class BrokerAccount:

    account_id: str

    account_name: str

    environment: str

    currency: str | None = None

    broker_server: str | None = None