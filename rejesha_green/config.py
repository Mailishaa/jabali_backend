from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str


    SMS_API_URL: str
    SMS_API_KEY: str
    SMS_SENDER_ID: str
    SMS_API_SECRET:str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",


    )


settings = Settings()