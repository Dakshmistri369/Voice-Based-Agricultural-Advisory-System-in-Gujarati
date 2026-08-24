# 🌾 ગુજરાતી કિસાન મિત્ર AI (Gujarati Kisaan Mitra AI)
> **A Voice-First, Document-Grounded Agricultural Advisory System for Gujarati Farmers**

---

## 📌 Project Overview

**ગુજરાતી કિસાન મિત્ર AI** is a complete bilingual, voice-first Retrieval-Augmented Generation (RAG) platform. It allows farmers in Gujarat to speak or type agricultural questions in **Gujarati** (or Gujlish) and receive instant, grounded voice and text guidance on:
- 📄 **Government Schemes** (PM-KISAN, PMFBY, i-Khedut Subsidy, Kisan Credit Card)
- 💰 **Daily APMC Mandi Prices** (Live prices across 33 Gujarat districts)
- ☔ **Weather & AQI Forecasts** (Hyperlocal 5-day forecasts with farming advisories)
- 🌱 **Crop Advisory & Pest Management** (Grounded in verified agricultural textbooks and PDF guides)

---

## 💻 Languages & Tech Stack

### 🎨 Frontend
- **Languages**: Python (Streamlit framework), HTML5, CSS3, JavaScript (DOM & Theme observers)
- **Styling**: Vanilla CSS3 Custom Properties (Centralized Token System) + Tailwind CSS + Custom Responsive Grid
- **Themes**: Dual Monochrome Aesthetic (**Pure Black Theme** & **Pure White Theme**) with professional SVG toggles
- **Typography**: 
  - Gujarati: *Noto Sans Gujarati*, *Hind Vadodara*
  - English Headings: *Space Grotesk*
  - Body: *Inter*
  - Metadata / Code: *JetBrains Mono*

### ⚙️ Backend
- **Core Language**: Python 3.10+ / 3.11+ / 3.12+ / 3.13+
- **Architecture**: 8-Stage Voice & Text Pipeline Orchestrator (`pipeline.py`)
- **Database & Vector Store**: 
  - **Cloud Database**: Supabase (PostgreSQL 15+ with `pgvector` extension)
  - **Offline Fallback Database**: SQLite3 with NumPy cosine vector search
- **Document Processing**: PyMuPDF (PDF parser) + Tesseract OCR (Gujarati & English) + LangChain recursive chunkers

---

## 🤖 AI Models & LLM Architecture

| Component | Model / Engine | Purpose |
|:---|:---|:---|
| **Large Language Model (LLM)** | `Qwen/Qwen2.5-7B-Instruct` / `meta-llama/Llama-3.1-8B-Instruct` | Grounded reasoning, agronomic question answering, and strict safety guidelines |
| **Vector Embedding Model** | `BAAI/bge-m3` (1024-dimensional) | State-of-the-art multilingual dense vector embeddings across Gujarati & English text |
| **Speech-to-Text (STT)** | `openai/whisper-tiny` / `openai/whisper-large-v3` | Transcribing spoken Gujarati voice audio to Gujarati Unicode text |
| **Text-to-Speech (TTS)** | 1. `Arjun4707/piper-gujarati-male` (Piper ONNX)<br>2. `facebook/mms-tts-guj` (Meta MMS)<br>3. `gTTS` (Google Gujarati TTS) | Multi-tier voice synthesis delivering spoken answers in clear Gujarati audio |
| **Translation & Cross-Lingual Pivot** | `deep-translator` (Google Translate Engine) + `facebook/nllb-200-distilled-600M` | Gujarati ↔ English bidirectional translation for semantic search across English PDF corpus |
| **Optical Character Recognition (OCR)** | `Tesseract OCR` (`guj` + `eng` language packs) | Extracting Gujarati text from scanned PDF pages and images |

---

## 🛠️ External Tools & Live APIs

1. **Supabase Cloud**: PostgreSQL vector database hosting PDF embeddings, logs, and mandi price cache.
2. **Open-Meteo Weather API**: Free, live hourly and 5-day weather forecasts across all 33 Gujarat districts.
3. **Open-Meteo Air Quality API**: Live PM2.5, PM10, and US AQI calculations with farming safety advisories.
4. **AGMARKNET / Data.gov.in**: Real-time mandi commodity prices from Gujarat APMCs (with local JSON cache fallback).
5. **Hugging Face Inference API**: Serverless execution for LLM generation, Whisper STT, and MMS-TTS.

---

## 📦 Python Libraries Used

### 1. Web & UI Framework
- `streamlit` (v1.32.0+) — Interactive web app interface and state management
- `audio-recorder-streamlit` (v0.0.8+) — In-browser microphone audio recording widget

### 2. Document Parsing & Text Processing
- `PyMuPDF` / `fitz` (v1.23.0+) — Ultra-fast PDF page extraction and text scraping
- `pytesseract` (v0.3.10+) — Python wrapper for Tesseract OCR engine
- `Pillow` / `PIL` (v10.0.0+) — Image manipulation and OCR preprocessing
- `langchain-text-splitters` (v0.0.1+) — Recursive character text chunking with Gujarati Unicode boundaries

### 3. Machine Learning, NLP & Vectors
- `sentence-transformers` (v2.5.0+) — Neural vector embedding generation using `BAAI/bge-m3`
- `torch` & `torchvision` (v2.0.0+) — Deep learning backend for PyTorch models
- `numpy` (v1.24.0+) — High-performance vector math and Cosine Similarity computations
- `huggingface-hub` (v0.20.0+) — Hugging Face model hub interaction and Inference Client

### 4. Language Translation & Speech Audio
- `deep-translator` (v1.11.4+) — Robust, unlimited Gujarati ↔ English translation
- `gTTS` (v2.5.0+) — Google Text-to-Speech engine for Gujarati audio synthesis
- `beautifulsoup4` (v4.12.0+) — HTML and text scraping utilities

### 5. Database & Cloud Storage
- `supabase` (v2.3.0+) — Supabase Python SDK for authentication and Postgres queries
- `psycopg2-binary` (v2.9.9+) — PostgreSQL database adapter for `pgvector`
- `sqlite3` (Built-in Python standard library) — Local zero-dependency vector fallback store

### 6. Config, Utilities & Data Structures
- `pydantic` (v2.6.0+) — Strict data validation and settings schemas
- `python-dotenv` (v1.0.0+) — Environment variable management
- `requests` (v2.31.0+) — HTTP client for external APIs (Weather, AQI, Hugging Face)
- `pandas` (v2.0.0+) — Data manipulation for Mandi prices and tabular statistics

---

## 🚀 Step-by-Step Setup Guide

### 1. Clone & Setup Environment
```bash
git clone <repository-url>
cd "Voice-Based Agricultural Advisory System in Gujarati"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install all Python libraries
pip install -r requirements.txt
pip install deep-translator
```

### 2. Configure Credentials
Create `.streamlit/secrets.toml`:
```toml
HF_API_KEY = "hf_your_huggingface_api_token"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOi..."
SUPABASE_DB_URL = "postgresql://postgres:password@db.your-project.supabase.co:5432/postgres"
DATA_GOV_IN_API_KEY = "your_data_gov_api_key"
ADMIN_PIN = "1234"
```

### 3. Ingest Agricultural PDF Documents
Place PDF files into `data/pdfs/` and run the vector ingestion script:
```bash
python ingest_pdfs.py
```

### 4. Start the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📂 Project Directory Structure

```
├── app.py                      # Main Streamlit application orchestrator
├── config.py                   # Configuration and secret management
├── pipeline.py                 # 8-Stage Voice & Text Pipeline
├── ingest_pdfs.py              # PDF vector ingestion CLI
├── requirements.txt            # Python dependencies
├── core/                       # Core AI & Service Modules
│   ├── chunker.py              # Recursive text splitter with Gujarati boundary support
│   ├── embeddings.py           # BAAI/bge-m3 vector embedding generator
│   ├── entity_extractor.py     # Crop, district, and commodity entity extraction
│   ├── intent_detector.py      # Multi-class intent classifier
│   ├── llm_service.py          # Grounded LLM reasoning & safety validator
│   ├── pdf_loader.py           # PyMuPDF + Tesseract OCR extraction
│   ├── stt_service.py          # Whisper speech-to-text service
│   ├── translator.py           # deep-translator Gujarati ↔ English pivot
│   ├── transliterator.py       # Gujlish to Gujarati script converter
│   └── tts_service.py          # Multi-engine Gujarati TTS synthesizer
├── data_services/              # Domain & Service Layer
│   ├── aqi_service.py          # Air Quality API integration
│   ├── crop_service.py         # Crop advisories & farming calendars
│   ├── price_service.py        # APMC Mandi prices & cache management
│   ├── rag_service.py          # Semantic similarity search & reranker
│   ├── scheme_browser.py       # Government scheme document browser
│   └── weather_service.py      # Open-Meteo weather integration
├── db/                         # Database Management
│   ├── database.py             # Dual-path Supabase / SQLite vector store
│   └── schema.sql              # Supabase PostgreSQL schema with pgvector
├── ui/                         # User Interface Layer
│   ├── components.py           # Reusable HTML/CSS component renderers
│   ├── layout.py               # Theme injection and Tailwind setup
│   ├── navigation.py           # Sidebar navigation & settings expander
│   ├── theme.py                # Dual Monochrome Design Token System
│   └── sections/               # Page Section Views (Home, Schemes, Weather, Prices, Crop, Disease)
└── assets/                     # Stylesheets and Static Assets
    ├── styles.css              # Main design system & Streamlit overrides
    └── tailwind.min.css        # Fallback Tailwind styles
```

---

## 📜 License
Developed as an Open Agricultural AI Advisory System under the **MIT License**.
