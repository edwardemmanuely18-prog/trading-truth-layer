from backend.app.services.evidence_acquisition.certification_engine.simulator import BaseProviderSimulator


class ConnectionFailureSimulator(BaseProviderSimulator):
    provider_name = "connection_failure"
    engine_name = "desktop_trading_engine"

    def authenticate(self, credentials):
        print("authenticate() called")
        return True

    def connect(self):
        print("connect() called")
        return False

    def synchronize(self):
        print("synchronize() SHOULD NEVER BE CALLED")
        return {}

    def disconnect(self):
        print("disconnect() called")

    def health(self):
        return {"healthy": True}