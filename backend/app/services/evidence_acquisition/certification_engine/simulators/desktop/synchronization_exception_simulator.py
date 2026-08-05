from backend.app.services.evidence_acquisition.certification_engine.simulator import BaseProviderSimulator


class SynchronizationExceptionSimulator(BaseProviderSimulator):
    provider_name = "sync_exception"
    engine_name = "desktop_trading_engine"

    def authenticate(self, credentials):
        print("authenticate() called")
        return True

    def connect(self):
        print("connect() called")
        return True

    def synchronize(self):
        print("synchronize() called")
        raise RuntimeError("Simulated synchronization failure")

    def disconnect(self):
        print("disconnect() called")

    def health(self):
        return {"healthy": True}