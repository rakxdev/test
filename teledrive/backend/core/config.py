from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- Database Settings ---
    DATABASE_URL: str = "sqlite:///./teledrive.db"

    # --- Telegram API Credentials ---
    # Get these from my.telegram.org
    API_ID: int
    API_HASH: str

    # Your phone number with country code, required for first-time login.
    PHONE_NUMBER: str

    # The name of the .session file that Telethon will create to stay logged in.
    SESSION_NAME: str = "teledrive_session"

    # The ID of the private Telegram channel to use for storage.
    CHANNEL_ID: int

    class Config:
        # Path to the .env file.
        # Assumes the application is run from the project root.
        env_file = "teledrive/.env"

# Create a single, accessible settings instance
settings = Settings()
