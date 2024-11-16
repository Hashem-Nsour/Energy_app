import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./evcharging.db")  # default to SQLite if not set in .env
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")  # default to a dummy value
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
