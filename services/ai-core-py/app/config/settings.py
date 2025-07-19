# app/config/settings.py

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Manages application settings and configurations.
    Reads values from environment variables.
    """
    # --- Gemini API Configuration ---
    GEMINI_API_KEY: str

    # --- Agent Configuration ---
    HOST_AGENT_MODEL_NAME: str = "gemini-2.0-flash"
    SUB_AGENT_MODEL_NAME: str = "gemini-2.0-flash"
    
    # Maximum turns for the host agent loop to prevent infinite loops
    MAX_TURNS_HOST_AGENT: int = 5

    # --- Database/Service URLs (nếu có) ---
    CONFERENCE_API_URL: str = "https://confhub.ddns.net/database/api/v1/conference"



    # --- LangSmith Configuration ---
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str | None = None # Dùng None để có thể không có giá trị
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_PROJECT: str | None = None


    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Tạo một instance duy nhất để import và sử dụng trong toàn bộ ứng dụng
settings = Settings()