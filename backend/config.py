"""
SkillSync Configuration Module.

Loads environment variables safely and defines provider-agnostic configuration
with sensible defaults. Never logs or prints secrets.
"""

import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Load environment variables
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path, override=True)
else:
    load_dotenv(BASE_DIR / ".env", override=True)


class Config:
    """Base application configuration."""

    BASE_DIR = BASE_DIR
    DATA_DIR = DATA_DIR

    # Server Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "skillsync-dev-secret-key-change-in-prod")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    # AI Provider Settings
    # Supported: 'gemini' (default), 'openai'
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").strip().lower()

    # Gemini Settings (Primary Provider)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # OpenAI Settings (Optional Provider)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Database & Integrations
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'skillsync.db'}")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    # Taxonomy & Data Settings
    SKILLS_DATA_PATH = DATA_DIR / "skills.csv"

    @classmethod
    def get_provider_credentials(cls, provider: str = None) -> dict:
        """Returns provider credentials without exposing secrets in logs."""
        target = (provider or cls.AI_PROVIDER).lower()
        if target == "gemini":
            return {
                "provider": "gemini",
                "api_key_configured": bool(cls.GEMINI_API_KEY),
                "model": cls.GEMINI_MODEL,
            }
        elif target == "openai":
            return {
                "provider": "openai",
                "api_key_configured": bool(cls.OPENAI_API_KEY),
                "model": cls.OPENAI_MODEL,
            }
        else:
            return {
                "provider": target,
                "api_key_configured": False,
                "model": None,
            }
