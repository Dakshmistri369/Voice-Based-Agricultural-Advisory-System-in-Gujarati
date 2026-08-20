# 🌾 કિસાન સહાયક — Voice-Based Agricultural Advisory System in Gujarati

A voice-first web app for Gujarat farmers. Speak or type in Gujarati to get instant answers about:
- 💰 **Mandi prices** — Cotton, Groundnut, Jeera, Castor and more (Gujarat APMCs)
- ☔ **Weather** — 5-day forecast + Gujarati farming advisories
- 📋 **Government schemes** — PM-KISAN, PMFBY, KCC, KUSUM, iKhedut (25 schemes)
- 🌱 **Crop advice** — Fertilizer doses, varieties, diseases, irrigation for 12 Gujarat crops

---

## 🛠️ Stack

| Layer | Tech |
|---|---|
| **Frontend** | HTML + Vanilla CSS + Vanilla JS |
| **Backend** | Python FastAPI |
| **STT** | `openai/whisper-large-v3` via HuggingFace Inference API (Token 1) |
| **TTS** | `facebook/mms-tts-guj` via HuggingFace Inference API (Token 1) |
| **LLM** | `meta-llama/Llama-3.2-3B-Instruct` via HuggingFace Inference API (Token 2) |
| **RAG** | TF-IDF cosine similarity over local JSON (no cloud DB needed) |
| **Weather** | Open-Meteo API (free, no key) |
| **Prices** | Static Gujarat APMC JSON + AGMARKNET attempt |

---

## ⚙️ Setup

### 1. Clone and create environment

```bash
cd "d:\Voice-Based Agricultural Advisory System in Gujarati"
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 2. Configure environment variables

```bash
copy .env.example .env
# Edit .env and fill in your HuggingFace tokens:
# HF_TOKEN_VOICE=hf_xxx   ← Token 1 (STT + TTS)
# HF_TOKEN_LLM=hf_xxx     ← Token 2 (LLM)
```

### 3. Start the backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open the frontend

Open `frontend/index.html` directly in Chrome, or serve it:

```bash
# Simple Python file server (from project root)
python -m http.server 3000 --directory frontend
# Then visit http://localhost:3000
```

---

## 🧪 API Test Commands

```bash
# Health check
curl http://localhost:8000/health

# Text ask in Gujarati
curl -X POST http://localhost:8000/text-ask \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"PM-KISAN ₹ 6000 ≡ ≡?\"}"

# Weather
curl "http://localhost:8000/weather?lat=22.3039&lon=70.8022&city=Rajkot"

# Price
curl "http://localhost:8000/price?commodity=cotton&district=Rajkot"

# Schemes
curl "http://localhost:8000/schemes?query=PM-KISAN"
```

---

## 📁 Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app + all endpoints
│   ├── config.py            # Environment config
│   ├── intent_detector.py   # Gujarati keyword intent classifier
│   ├── rag_service.py       # TF-IDF retrieval from JSON
│   ├── hf_voice_service.py  # Whisper STT + MMS TTS (HF Token 1)
│   ├── hf_llm_service.py    # Llama 3.2 3B (HF Token 2)
│   ├── weather_service.py   # Open-Meteo + Gujarati advisories
│   ├── price_service.py     # APMC price lookup
│   └── sql/setup.sql        # Supabase schema (optional)
├── data/
│   ├── schemes/             # 25 Gujarat government schemes (JSON)
│   ├── crops/               # 12 Gujarat crops (JSON)
│   └── prices/              # Static APMC price data (JSON)
├── frontend/
│   ├── index.html
│   ├── css/                 # variables.css, main.css
│   └── js/                  # config, chat, voice, quickActions, app
├── .env.example
└── README.md
```

---

## 🎯 SIH Demo Checklist

- [ ] Backend running on port 8000
- [ ] HF tokens set in `.env`
- [ ] Open `frontend/index.html` in Chrome
- [ ] Test mic: speak "આજે કપાસ ભાવ?" → gets price card + Gujarati audio response
- [ ] Test quick tabs: ભ./Weather/Scheme/Crop
- [ ] Show offline: static prices + cached weather still work without internet
