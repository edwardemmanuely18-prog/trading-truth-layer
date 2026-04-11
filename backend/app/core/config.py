from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================
    # CORE APP
    # =========================
    APP_NAME: str = "Trading Truth Layer API"
    DATABASE_URL: str = "sqlite:///./trading_truth_layer.db"

    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    FRONTEND_BASE_URL: str = "http://localhost:3000"

    # =========================
    # STRIPE (OPTIONAL / FALLBACK)
    # =========================
    STRIPE_BILLING_ENABLED: bool = False
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None

    # =========================
    # PADDLE (PRIMARY AUTOMATED BILLING - LEGACY / OPTIONAL)
    # =========================
    PADDLE_BILLING_ENABLED: bool = False
    PADDLE_API_KEY: str | None = None
    PADDLE_WEBHOOK_SECRET: str | None = None
    PADDLE_API_BASE_URL: str = "https://api.paddle.com"

    # =========================
    # MANUAL BILLING MODE (FALLBACK)
    # =========================
    MANUAL_BILLING_ENABLED: bool = True

    # =========================
    # MANUAL PAYMENT DETAILS
    # =========================
    MANUAL_PAYMENT_METHOD: str | None = None
    MANUAL_PAYMENT_ACCOUNT_NAME: str | None = None
    MANUAL_PAYMENT_ACCOUNT_NUMBER: str | None = None
    MANUAL_PAYMENT_BANK_NAME: str | None = None
    MANUAL_PAYMENT_PHONE_NUMBER: str | None = None
    MANUAL_PAYMENT_NOTES: str | None = None

    # =========================
    # PYDANTIC CONFIG
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()