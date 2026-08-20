-- ============================================================
-- Supabase / PostgreSQL schema for the Gujarati Kisaan system
-- Run this once in Supabase SQL Editor
-- ============================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Schemes table (25 Gujarat farming schemes)
CREATE TABLE IF NOT EXISTS schemes (
    id TEXT PRIMARY KEY,
    name_gujarati TEXT NOT NULL,
    name_english TEXT,
    short_name TEXT,
    category VARCHAR(60),
    benefit_gujarati TEXT,
    eligibility_gujarati TEXT,
    how_to_apply_gujarati TEXT,
    documents_gujarati TEXT[],
    helpline TEXT,
    website TEXT,
    tags TEXT[],
    embedding VECTOR(384)   -- all-MiniLM-L6-v2 produces 384-dim
);

-- Crops table
CREATE TABLE IF NOT EXISTS crops (
    id SERIAL PRIMARY KEY,
    crop_key TEXT UNIQUE,
    gu_name TEXT,
    english_name TEXT,
    season TEXT,
    districts TEXT[],
    sowing_guj TEXT,
    harvest_guj TEXT,
    fertilizer_info JSONB,
    diseases_info JSONB,
    varieties TEXT[],
    price_range JSONB,
    embedding VECTOR(384)
);

-- Mandi prices cache
CREATE TABLE IF NOT EXISTS mandi_prices (
    id SERIAL PRIMARY KEY,
    commodity TEXT NOT NULL,
    gu_name TEXT,
    market TEXT,
    district TEXT,
    modal_price DECIMAL,
    min_price DECIMAL,
    max_price DECIMAL,
    unit TEXT DEFAULT '₹/quintal',
    price_date DATE DEFAULT CURRENT_DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversation logs
CREATE TABLE IF NOT EXISTS conversation_logs (
    id SERIAL PRIMARY KEY,
    session_id TEXT,
    query_text TEXT,
    detected_intent VARCHAR(30),
    response_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector similarity indexes
CREATE INDEX IF NOT EXISTS idx_schemes_embedding ON schemes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
CREATE INDEX IF NOT EXISTS idx_crops_embedding   ON crops   USING ivfflat (embedding vector_cosine_ops) WITH (lists = 5);
