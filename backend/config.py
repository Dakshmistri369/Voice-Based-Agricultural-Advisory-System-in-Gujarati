"""
config.py — Centralised settings loaded from .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent  # project root

load_dotenv(BASE_DIR / ".env")

# ── Hugging Face ──────────────────────────────────────────────
HF_TOKEN_VOICE: str = os.getenv("HF_TOKEN_VOICE", "")   # STT + TTS
HF_TOKEN_LLM: str   = os.getenv("HF_TOKEN_LLM",   "")   # LLM

HF_STT_MODEL = "openai/whisper-large-v3"
HF_TTS_MODEL = "facebook/mms-tts-guj"
HF_LLM_MODEL = "meta-llama/Llama-3.2-3B-Instruct"

HF_API_BASE  = "https://api-inference.huggingface.co/models"

# ── Supabase (optional) ───────────────────────────────────────
USE_SUPABASE: bool  = os.getenv("USE_SUPABASE", "false").lower() == "true"
SUPABASE_URL: str   = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str   = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_DB_URL: str = os.getenv("SUPABASE_DB_URL", "")

# ── App ───────────────────────────────────────────────────────
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
CORS_ORIGINS: list  = os.getenv("CORS_ORIGINS", "*").split(",")

# ── Defaults ──────────────────────────────────────────────────
DEFAULT_LAT: float = float(os.getenv("DEFAULT_LAT", "22.3039"))
DEFAULT_LON: float = float(os.getenv("DEFAULT_LON", "70.8022"))
DEFAULT_CITY: str  = os.getenv("DEFAULT_CITY", "Rajkot")

# ── Data paths ────────────────────────────────────────────────
SCHEMES_FILE  = BASE_DIR / "data" / "schemes" / "gujarat_schemes.json"
CROPS_FILE    = BASE_DIR / "data" / "crops"   / "gujarat_crop_calendar.json"
PRICES_FILE   = BASE_DIR / "data" / "prices"  / "gujarat_prices.json"
WEATHER_CACHE = BASE_DIR / "data" / "weather_cache.json"
AUDIO_DIR     = BASE_DIR / "backend" / "static" / "audio"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
