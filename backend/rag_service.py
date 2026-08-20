"""
rag_service.py
--------------
Retrieves relevant context from JSON data files using simple
cosine-similarity over TF-IDF vectors (no cloud DB required).
Optionally uses Supabase pgvector when USE_SUPABASE=true.
"""

import json
import logging
import math
import re
from pathlib import Path
from typing import Callable

from config import SCHEMES_FILE, CROPS_FILE, USE_SUPABASE

log = logging.getLogger(__name__)

# ── In-memory index ──────────────────────────────────────────
_schemes_index: list[dict] = []
_crops_index: list[dict] = []


def _tokenise(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _tf(tokens: list[str]) -> dict[str, float]:
    freq: dict[str, float] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    total = len(tokens) or 1
    return {t: c / total for t, c in freq.items()}


def _cosine(a: dict, b: dict) -> float:
    dot = sum(a.get(t, 0) * b.get(t, 0) for t in b)
    mag_a = math.sqrt(sum(v ** 2 for v in a.values())) or 1
    mag_b = math.sqrt(sum(v ** 2 for v in b.values())) or 1
    return dot / (mag_a * mag_b)


def _build_scheme_text(s: dict) -> str:
    return " ".join([
        s.get("name_gujarati", ""),
        s.get("name_english", ""),
        s.get("short_name", ""),
        s.get("benefit_gujarati", ""),
        s.get("eligibility_gujarati", ""),
        " ".join(s.get("tags", [])),
    ])


def _build_crop_text(c: dict) -> str:
    return " ".join([
        c.get("gu_name", ""),
        c.get("english_name", ""),
        c.get("season", ""),
        c.get("sowing_guj", ""),
        str(c.get("fertilizer", "")),
    ])


def _load_index():
    global _schemes_index, _crops_index
    if _schemes_index:
        return  # already loaded

    schemes_raw = json.loads(SCHEMES_FILE.read_text(encoding="utf-8"))
    for s in schemes_raw:
        text = _build_scheme_text(s)
        _schemes_index.append({"data": s, "vec": _tf(_tokenise(text))})

    crops_raw = json.loads(CROPS_FILE.read_text(encoding="utf-8"))
    for key, c in crops_raw.items():
        text = _build_crop_text(c)
        _crops_index.append({"key": key, "data": c, "vec": _tf(_tokenise(text))})

    log.info("RAG index: %d schemes, %d crops", len(_schemes_index), len(_crops_index))


def search_schemes(query: str, top_k: int = 3) -> list[dict]:
    _load_index()
    qvec = _tf(_tokenise(query))
    scored = sorted(_schemes_index, key=lambda x: _cosine(qvec, x["vec"]), reverse=True)
    return [{"scheme": s["data"], "score": round(_cosine(qvec, s["vec"]), 3)} for s in scored[:top_k]]


def search_crops(query: str, top_k: int = 2) -> list[dict]:
    _load_index()
    qvec = _tf(_tokenise(query))
    scored = sorted(_crops_index, key=lambda x: _cosine(qvec, x["vec"]), reverse=True)
    return [{"key": c["key"], "crop": c["data"], "score": round(_cosine(qvec, c["vec"]), 3)} for c in scored[:top_k]]


def format_scheme_context(results: list[dict]) -> str:
    parts = []
    for r in results:
        s = r["scheme"]
        parts.append(
            f"યોજના: {s.get('name_gujarati','')}\n"
            f"લાભ: {s.get('benefit_gujarati','')}\n"
            f"Eligibility: {s.get('eligibility_gujarati','')}\n"
            f"Apply: {s.get('how_to_apply_gujarati','')}\n"
            f"Helpline: {s.get('helpline','')}\n"
        )
    return "\n---\n".join(parts)


def format_crop_context(results: list[dict]) -> str:
    parts = []
    for r in results:
        c = r["crop"]
        fert = c.get("fertilizer", {})
        parts.append(
            f"પાક: {c.get('gu_name','')}\n"
            f"Season: {c.get('season','')} | Sowing: {c.get('sowing_guj','')}\n"
            f"Fertilizer: {fert.get('basal','')} | Top-dress: {fert.get('top_dress','')}\n"
            f"Irrigation: {c.get('irrigation_guj','')}\n"
            f"Varieties: {', '.join(c.get('varieties_guj', []))}\n"
        )
    return "\n---\n".join(parts)
