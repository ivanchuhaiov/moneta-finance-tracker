from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Moneta"
    debug: bool = False
    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    supported_currencies: list[str] = ["EUR", "USD", "UAH"]

    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    anthropic_max_tokens: int = 1024
    anthropic_temperature: float = 0.3

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()