from backend.app.services.evidence_acquisition.certification_engine.simulator import BaseProviderSimulator


class DisconnectExceptionSimulator(BaseProviderSimulator):
    provider_name = "disconnect_exception"
    engine_name = "desktop_trading_engine"

    def authenticate(self, credentials):
        print("authenticate() called")
        return True

    def connect(self):
        print("connect() called")
        return True

    def synchronize(self):
        print("synchronize() called")
        return {
            "trades": [],
            "positions": [],
        }

    def disconnect(self):
        print("disconnect() called")
        raise RuntimeError("Simulated disconnect failure")

    def health(self):
        return {"healthy": True}