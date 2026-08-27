"""Configuration settings and environment loaders for Gujarati Kisaan Mitra AI."""

import os
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel, Field

# Base Directory
BASE_DIR = Path(__file__).resolve().parent


class AppSettings(BaseModel):
    """Application setting parameters and model configurations."""

    # General App Settings
    APP_NAME: str = "ગુજરાતી કિસાન મિત્ર AI"
    APP_SUBTITLE: str = "Voice-Based Agricultural Advisory System in Gujarati"
    DEBUG: bool = Field(default=False)

    # Secret Keys (Loaded dynamically)
    HF_API_KEY: str = Field(default="")
    SUPABASE_URL: str = Field(default="")
    SUPABASE_ANON_KEY: str = Field(default="")
    SUPABASE_DB_URL: str = Field(default="")
    DATA_GOV_IN_API_KEY: str = Field(default="")
    ADMIN_PIN: str = Field(default="1234")

    # STT & TTS Engine Flags
    STT_MODE: str = Field(default="hf_api")  # "hf_api" | "local"
    TTS_PRIORITY: list[str] = Field(default_factory=lambda: ["piper", "mms_tts", "gtts"])
    WHISPER_MODEL_ID: str = Field(default="openai/whisper-tiny")
    EMBEDDING_MODEL_ID: str = Field(default="BAAI/bge-m3")
    LLM_MODEL_ID: str = Field(default="Qwen/Qwen2.5-7B-Instruct")
    TRANSLATION_MODEL_ID: str = Field(default="facebook/nllb-200-distilled-600M")
    TTS_MODEL_ID: str = Field(default="Arjun4707/piper-gujarati-male")

    # Ingestion & RAG Settings
    CHUNK_SIZE: int = Field(default=800)
    CHUNK_OVERLAP: int = Field(default=120)
    TOP_K_RETRIEVAL: int = Field(default=5)
    SIMILARITY_THRESHOLD: float = Field(default=0.35)

    # Local Storage Paths
    PDF_DIR: Path = Field(default=BASE_DIR / "data" / "pdfs")
    CACHE_DIR: Path = Field(default=BASE_DIR / "data" / "cache")
    LOCAL_DB_PATH: Path = Field(default=BASE_DIR / "data" / "kisaan_mitra.db")


def load_settings() -> AppSettings:
    """Loads configuration settings prioritizing Streamlit Secrets then OS environment."""
    secrets_dict: Dict[str, Any] = {}

    # Try loading from Streamlit secrets if running inside Streamlit
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets:
            secrets_dict = dict(st.secrets)
    except Exception:
        secrets_dict = {}

    # If secrets_dict is empty (e.g. running outside Streamlit via CLI), load .streamlit/secrets.toml directly
    if not secrets_dict:
        secrets_path = BASE_DIR / ".streamlit" / "secrets.toml"
        if secrets_path.exists():
            try:
                try:
                    import tomllib
                    with open(secrets_path, "rb") as f:
                        secrets_dict = tomllib.load(f)
                except ImportError:
                    import toml
                    with open(secrets_path, "r", encoding="utf-8") as f:
                        secrets_dict = toml.load(f)
            except Exception as e:
                pass

    def get_secret(key: str, default: str = "") -> str:
        return secrets_dict.get(key, os.environ.get(key, default))

    return AppSettings(
        HF_API_KEY=get_secret("HF_API_KEY"),
        SUPABASE_URL=get_secret("SUPABASE_URL"),
        SUPABASE_ANON_KEY=get_secret("SUPABASE_ANON_KEY"),
        SUPABASE_DB_URL=get_secret("SUPABASE_DB_URL"),
        DATA_GOV_IN_API_KEY=get_secret("DATA_GOV_IN_API_KEY"),
        ADMIN_PIN=get_secret("ADMIN_PIN", "1234"),
    )


# Instantiate global settings
settings = load_settings()
