"""Application configuration, read fresh from environment variables on
every call (no caching) so tests can monkeypatch env vars per-test without
fighting stale state."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./resolve.db")
        self.max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "5"))
        # Rough per-1K-token cost estimates in USD, used only for the
        # per-request cost-tracking feature. Leave at 0 on Gemini's free tier.
        self.cost_per_1k_input_tokens = float(os.getenv("COST_PER_1K_INPUT", "0.0"))
        self.cost_per_1k_output_tokens = float(os.getenv("COST_PER_1K_OUTPUT", "0.0"))
        # Usage cap for a public deployment: protects Gemini's free-tier
        # request quota from being exhausted by strangers hitting the demo
        # link. See app/rate_limit.py.
        self.rate_limit_per_ip_per_hour = int(os.getenv("RATE_LIMIT_PER_IP_PER_HOUR", "5"))
        self.rate_limit_global_per_day = int(os.getenv("RATE_LIMIT_GLOBAL_PER_DAY", "50"))

    def validate(self) -> None:
        if not self.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Copy backend/.env.example to "
                "backend/.env and add your key from https://aistudio.google.com/apikey"
            )


def get_settings() -> Settings:
    return Settings()
