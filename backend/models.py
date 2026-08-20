"""
models.py — Pydantic request / response models
"""
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Optional, Any


class TextAskRequest(BaseModel):
    text: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    district: Optional[str] = "Rajkot"


class AskResponse(BaseModel):
    question: str
    answer_text: str
    intent: str
    extra_data: Optional[dict] = None
    audio_url: Optional[str] = None   # populated only for /voice-ask


class PriceResponse(BaseModel):
    commodity: str
    gu_name: str
    market: str
    district: str
    modal_price: float
    min_price: float
    max_price: float
    unit: str
    source: str   # "live" | "cache"


class WeatherResponse(BaseModel):
    city: str
    current_temp: str
    humidity: str
    rain_today: str
    forecast_days: list
    advisories: list
    source: str


class SchemeResult(BaseModel):
    id: str
    name_gujarati: str
    benefit_gujarati: str
    eligibility_gujarati: Optional[str] = None
    how_to_apply_gujarati: Optional[str] = None
    helpline: Optional[str] = None
    website: Optional[str] = None
    similarity: Optional[float] = None
