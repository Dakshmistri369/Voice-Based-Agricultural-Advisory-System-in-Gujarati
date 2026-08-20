"""
main.py — FastAPI application for the Voice-Based Agricultural Advisory System
"""

import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import config
from models import TextAskRequest, AskResponse
from intent_detector import classify_intent, extract_commodity, extract_crop
from rag_service import search_schemes, search_crops, format_scheme_context, format_crop_context
from hf_llm_service import generate_answer
from hf_voice_service import transcribe_gujarati, speak_gujarati
from weather_service import get_weather_advisory
from price_service import get_price, get_all_prices

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
log = logging.getLogger("main")

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="કિસાન સહાયક — Gujarati Agricultural Advisory API",
    description="Voice-based Gujarati farming assistant powered by Llama 3.2 + HF APIs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated audio files
config.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/audio", StaticFiles(directory=str(config.AUDIO_DIR)), name="audio")

# Serve frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


# ── Health check ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_model": config.HF_LLM_MODEL,
        "stt_model": config.HF_STT_MODEL,
        "tts_model": config.HF_TTS_MODEL,
        "hf_voice_configured": bool(config.HF_TOKEN_VOICE),
        "hf_llm_configured": bool(config.HF_TOKEN_LLM),
    }


# ── Text Ask ─────────────────────────────────────────────────
@app.post("/text-ask", response_model=AskResponse)
def text_ask(body: TextAskRequest):
    query = body.text.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Empty query")

    intent, conf = classify_intent(query)
    log.info("Intent: %s (%.2f) | Query: %s", intent, conf, query[:60])

    context, extra_data = _resolve_context(intent, query, body.district or "Rajkot",
                                           body.lat, body.lon)

    answer = generate_answer(query, context)

    return AskResponse(
        question=query,
        answer_text=answer,
        intent=intent,
        extra_data=extra_data,
        audio_url=None,
    )


# ── Voice Ask ────────────────────────────────────────────────
@app.post("/voice-ask")
async def voice_ask(
    audio: UploadFile = File(...),
    district: str = Form("Rajkot"),
    lat: float = Form(config.DEFAULT_LAT),
    lon: float = Form(config.DEFAULT_LON),
):
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio")

    # STT
    stt = transcribe_gujarati(audio_bytes, audio.filename or "audio.webm")
    query = stt.get("text", "").strip()
    if not query:
        return JSONResponse(status_code=422, content={
            "error": "Audio recognized but no text found. Please speak clearly in Gujarati.",
            "stt_error": stt.get("error"),
        })

    intent, _ = classify_intent(query)
    context, extra_data = _resolve_context(intent, query, district, lat, lon)

    answer = generate_answer(query, context)

    # TTS
    audio_filename = speak_gujarati(answer)
    audio_url = f"/static/audio/{audio_filename}" if audio_filename else None

    return {
        "question": query,
        "answer_text": answer,
        "intent": intent,
        "extra_data": extra_data,
        "audio_url": audio_url,
        "tts_available": audio_url is not None,
    }


# ── Weather ──────────────────────────────────────────────────
@app.get("/weather")
def weather(
    lat: float = Query(config.DEFAULT_LAT),
    lon: float = Query(config.DEFAULT_LON),
    city: str = Query(config.DEFAULT_CITY),
):
    return get_weather_advisory(lat, lon, city)


# ── Price ────────────────────────────────────────────────────
@app.get("/price")
def price(
    commodity: str = Query(..., description="Commodity name e.g. cotton, mungfali, jeera"),
    district: str = Query("Rajkot"),
):
    result = get_price(commodity, district)
    if not result:
        raise HTTPException(status_code=404, detail=f"Price not found for '{commodity}' in {district}")
    return result


@app.get("/prices/all")
def all_prices():
    return get_all_prices()


# ── Schemes ──────────────────────────────────────────────────
@app.get("/schemes")
def schemes(query: str = Query(..., description="Gujarati / English scheme keyword")):
    results = search_schemes(query, top_k=5)
    return [
        {
            "id": r["scheme"].get("id"),
            "name_gujarati": r["scheme"].get("name_gujarati"),
            "benefit_gujarati": r["scheme"].get("benefit_gujarati"),
            "eligibility_gujarati": r["scheme"].get("eligibility_gujarati"),
            "how_to_apply_gujarati": r["scheme"].get("how_to_apply_gujarati"),
            "helpline": r["scheme"].get("helpline"),
            "website": r["scheme"].get("website"),
            "similarity": r["score"],
        }
        for r in results
    ]


# ── Root redirect ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Kisaan Sahayak API running. Visit /docs for API reference or /app for UI."}


# ── Internal helper ───────────────────────────────────────────
def _resolve_context(intent: str, query: str, district: str, lat, lon) -> tuple[str, dict]:
    """Build context string + extra_data dict based on detected intent."""
    context = ""
    extra_data: dict = {"intent": intent}

    if intent == "PRICE":
        commodity = extract_commodity(query)
        price_info = get_price(commodity, district)
        if price_info:
            context = (
                f"Commodity: {price_info['gu_name']} ({price_info['commodity']})\n"
                f"Market: {price_info['market']}, {price_info['district']}\n"
                f"Modal Price: ₹{price_info['modal_price']}/quintal\n"
                f"Range: ₹{price_info['min_price']} – ₹{price_info['max_price']}"
            )
            extra_data["type"] = "price_card"
            extra_data["data"] = price_info
        else:
            context = "આ commodity ≡ ≡ ≡ price ≡ ≡. AGMARKNET.gov.in ≡ ≡."

    elif intent == "WEATHER":
        weather_info = get_weather_advisory(
            lat or config.DEFAULT_LAT,
            lon or config.DEFAULT_LON,
            district,
        )
        advisories_text = " | ".join(a["msg_guj"] for a in weather_info.get("advisories", []))
        context = (
            f"Temperature: {weather_info['current_temp']}, "
            f"Humidity: {weather_info['humidity']}, "
            f"Rain today: {weather_info['rain_today']}\n"
            f"Advisories: {advisories_text}"
        )
        extra_data["type"] = "weather_card"
        extra_data["data"] = weather_info

    elif intent == "SCHEME":
        results = search_schemes(query, top_k=3)
        context = format_scheme_context(results)
        extra_data["type"] = "scheme_cards"
        extra_data["data"] = [r["scheme"] for r in results]

    elif intent in ("CROP_ADVICE", "DISEASE"):
        crop_key = extract_crop(query)
        results = search_crops(query if not crop_key else crop_key, top_k=2)
        context = format_crop_context(results)
        extra_data["type"] = "crop_info"
        extra_data["data"] = [r["crop"] for r in results]

    return context, extra_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.APP_HOST, port=config.APP_PORT, reload=True)
