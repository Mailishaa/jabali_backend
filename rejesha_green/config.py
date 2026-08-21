from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    USSD_API_KEY: str
    AT_SHORTCODE:str
   

    model_config = SettingsConfigDict(
        env_file=".env"
    )


settings = Settings()