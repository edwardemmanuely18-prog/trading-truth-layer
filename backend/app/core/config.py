from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Trading Truth Layer API"
    DATABASE_URL: str = "sqlite:///./trading_truth_layer.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()