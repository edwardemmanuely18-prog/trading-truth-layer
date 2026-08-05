from backend.app.services.evidence_acquisition.certification_engine.simulator import BaseProviderSimulator


class AuthenticationFailureSimulator(BaseProviderSimulator):
    provider_name = "auth_failure"
    engine_name = "desktop_trading_engine"

    def authenticate(self, credentials):
        print("authenticate() called")
        return False

    def connect(self):
        print("connect() should NEVER be called")
        return True

    def synchronize(self):
        print("synchronize() should NEVER be called")
        return {}

    def disconnect(self):
        print("disconnect() called")

    def health(self):
        return {"healthy": True}