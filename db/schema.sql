-- PostgreSQL / Supabase Schema for Gujarati Kisaan Mitra AI

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Document Chunks Table (Primary PDF Knowledge Base Vector Store)
CREATE TABLE IF NOT EXISTS document_chunks (
    id BIGSERIAL PRIMARY KEY,
    source_filename TEXT NOT NULL,
    doc_category VARCHAR(50) NOT NULL CHECK (doc_category IN ('scheme', 'crop_advisory', 'general')),
    page_number INT NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    detected_language VARCHAR(10) NOT NULL CHECK (detected_language IN ('gu', 'en', 'mixed')),
    char_count INT NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    embedding vector(1024)
);

-- IVFFlat Cosine Index for fast vector similarity search
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Filtering Composite Index
CREATE INDEX IF NOT EXISTS idx_document_chunks_cat_lang 
ON document_chunks (doc_category, detected_language);

CREATE INDEX IF NOT EXISTS idx_document_chunks_source 
ON document_chunks (source_filename);

-- 2. Mandi Prices Table (APMC Live Data Cache)
CREATE TABLE IF NOT EXISTS mandi_prices (
    id SERIAL PRIMARY KEY,
    commodity_name_english VARCHAR(100) NOT NULL,
    commodity_name_gujarati VARCHAR(100) NOT NULL,
    market_name VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    modal_price INT NOT NULL,
    min_price INT NOT NULL,
    max_price INT NOT NULL,
    unit VARCHAR(20) DEFAULT '20 kg',
    price_date DATE NOT NULL,
    source VARCHAR(20) DEFAULT 'live',
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mandi_prices_commodity_date 
ON mandi_prices (commodity_name_english, price_date DESC);

-- 3. Conversation Logs Table (Audit & Debug Trace Store)
CREATE TABLE IF NOT EXISTS conversation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) NOT NULL,
    gujarati_query TEXT,
    english_query TEXT,
    detected_intent VARCHAR(50),
    intent_confidence NUMERIC(4,2),
    retrieved_sources JSONB,
    english_answer TEXT,
    gujarati_answer TEXT,
    stt_engine VARCHAR(50),
    tts_engine VARCHAR(50),
    latency_ms_by_stage JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversation_logs_session 
ON conversation_logs (session_id, created_at DESC);

-- 4. Districts Reference Table (33 Gujarat Districts)
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    district_name_gujarati VARCHAR(100) NOT NULL UNIQUE,
    district_name_english VARCHAR(100) NOT NULL UNIQUE,
    latitude NUMERIC(8,5),
    longitude NUMERIC(8,5)
);
