"""
8-Stage Voice & Text Pipeline Orchestrator for Gujarati Kisaan Mitra AI.
Executes Audio -> STT -> Transliterator -> Translation -> Intent/Entities -> RAG/Live Service -> LLM -> TTS.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple

from core.audio_utils import normalize_audio_to_wav
from core.stt_service import stt_service
from core.transliterator import transliterator
from core.translator import translator_service
from core.intent_detector import intent_detector
from core.entity_extractor import entity_extractor
from data_services.rag_service import rag_service
from data_services.weather_service import weather_service
from data_services.price_service import price_service
from core.llm_service import llm_service
from core.tts_service import tts_service

logger = logging.getLogger("PipelineOrchestrator")


class PipelineOrchestrator:
    """Orchestrates end-to-end voice and text queries through the 8 pipeline stages."""

    def process_query(
        self,
        audio_bytes: Optional[bytes] = None,
        text_query: Optional[str] = None,
        selected_district: str = "Rajkot"
    ) -> Dict[str, Any]:
        """
        Executes complete 8-stage pipeline.
        Returns pipeline output payload containing query, response, cards, sources, audio, and trace metrics.
        """
        t_start = time.time()
        stage_latencies: Dict[str, int] = {}

        # STAGE 1 & 2: Audio Capture & Speech-to-Text (STT)
        t_stt_start = time.time()
        stt_engine = "Text Input Direct"
        if audio_bytes:
            wav_bytes = normalize_audio_to_wav(audio_bytes)
            gu_transcript, stt_engine = stt_service.transcribe_audio(wav_bytes)
        else:
            gu_transcript = text_query.strip() if text_query else ""
        stage_latencies["stt_ms"] = int((time.time() - t_stt_start) * 1000)

        if not gu_transcript:
            return {
                "success": False,
                "error": "કોઈ અવાજ કે લખાણ મળ્યું નથી (No speech input detected)."
            }

        # STAGE 3: Script Normalization (Gujlish -> Gujarati script)
        t_norm_start = time.time()
        norm_query = transliterator.normalize_text(gu_transcript)
        stage_latencies["normalization_ms"] = int((time.time() - t_norm_start) * 1000)

        # STAGE 4: Understanding (Intent Detection & Entity Extraction on normalized query)
        t_und_start = time.time()
        intent, confidence, evidence = intent_detector.detect_intent(norm_query)
        entities = entity_extractor.extract_entities(norm_query)
        if selected_district and not entities.get("district"):
            entities["district"] = selected_district
        stage_latencies["understanding_ms"] = int((time.time() - t_und_start) * 1000)

        # STAGE 5: Translation (gu -> en) — only if needed for RAG / general inquiries
        t_trans_start = time.time()
        en_query = norm_query
        if intent in ["CROP_ADVICE", "SCHEME", "UNKNOWN"]:
            en_query = translator_service.translate_gu_to_en(norm_query)
        stage_latencies["translate_gu_en_ms"] = int((time.time() - t_trans_start) * 1000)

        # STAGE 6: Service Routing & Retrieval (PDF RAG or Live Weather / Price Data)
        t_ret_start = time.time()
        context_text = ""
        is_context_found = False
        sources = []
        top_sim = 0.0
        price_card_data = None
        weather_card_data = None

        if intent == "PRICE":
            commodity = entities.get("crop") or "Cotton"
            district = entities.get("district") or selected_district
            price_card_data = price_service.fetch_mandi_price(commodity, district)
            context_text = f"Today's APMC Mandi Price for {price_card_data['commodity_en']} in {price_card_data['district_gu']} is Modal: Rs {price_card_data['modal_price']}/20kg, Min: Rs {price_card_data['min_price']}, Max: Rs {price_card_data['max_price']}."
            is_context_found = True

        elif intent == "WEATHER":
            district = entities.get("district") or selected_district
            weather_card_data = weather_service.fetch_weather(district)
            context_text = f"Live weather forecast for {weather_card_data['district_english']}: Temp {weather_card_data['temp_c']}°C, Condition: {weather_card_data['condition_gujarati']}, Humidity: {weather_card_data['humidity']}%. Advisories: {'. '.join(weather_card_data['advisories'])}"
            is_context_found = True

        elif intent == "GREETING":
            is_context_found = True
            context_text = "Greeting"

        else:
            # RAG Search over document_chunks PDF knowledge base
            doc_category = "scheme" if intent == "SCHEME" else ("crop_advisory" if intent == "CROP_ADVICE" else None)
            # Try searching with query (bge-m3 handles multilingual query directly)
            search_query = en_query if en_query != norm_query else norm_query
            is_context_found, context_text, sources, top_sim = rag_service.retrieve_context(
                query_text=search_query,
                doc_category=doc_category
            )
            # If category-filtered search finds nothing, fallback to searching all PDF chunks
            if not is_context_found and doc_category is not None:
                is_context_found, context_text, sources, top_sim = rag_service.retrieve_context(
                    query_text=search_query,
                    doc_category=None
                )

        stage_latencies["retrieval_ms"] = int((time.time() - t_ret_start) * 1000)

        # STAGE 7: Grounded LLM Generation & en -> gu Translation
        t_llm_start = time.time()
        if intent == "GREETING":
            en_answer = "Hello! I am Gujarati Kisaan Mitra AI. How can I assist you with farming schemes, crop advice, weather, or market prices today?"
            gu_answer = "નમસ્તે ખેડૂત મિત્ર! હું ગુજરાતી કિસાન મિત્ર AI છું. આજે હું તમને સરકારી યોજનાઓ, પાક માર્ગદર્શન, હવામાન અથવા બજાર ભાવ વિશે કેવી રીતે મદદ કરી શકું?"
            val_meta = {"is_gujarati_script": True, "is_grounded": True}

        elif intent == "PRICE" and price_card_data:
            en_answer = f"Today's APMC Mandi Price for {price_card_data['commodity_en']} in {price_card_data['district_gu']} is Rs {price_card_data['modal_price']} per 20kg (Min: Rs {price_card_data['min_price']}, Max: Rs {price_card_data['max_price']})."
            gu_answer = f"{price_card_data['district_gu']} APMC યાર્ડમાં આજે {price_card_data['commodity_gu']} નો બજાર ભાવ ₹{price_card_data['modal_price']} પ્રતિ મણ (20 kg) છે. (ન્યૂનતમ: ₹{price_card_data['min_price']}, મહત્તમ: ₹{price_card_data['max_price']})."
            val_meta = {"is_gujarati_script": True, "is_grounded": True}

        elif intent == "WEATHER" and weather_card_data:
            advisories_str = " ".join(weather_card_data['advisories'])
            en_answer = f"Live weather forecast for {weather_card_data['district_english']}: Temp {weather_card_data['temp_c']}°C, Condition: {weather_card_data['condition_gujarati']}, Humidity: {weather_card_data['humidity']}%. Advisories: {advisories_str}"
            gu_answer = f"{weather_card_data['district_gujarati']} માં આજે તાપમાન {weather_card_data['temp_c']}°C અને {weather_card_data['condition_gujarati']} રહેશે. {advisories_str}"
            val_meta = {"is_gujarati_script": True, "is_grounded": True}

        else:
            en_answer, gu_answer, val_meta = llm_service.generate_grounded_answer(
                query_text=en_query,
                context_text=context_text,
                is_context_found=is_context_found
            )

        stage_latencies["llm_generation_ms"] = int((time.time() - t_llm_start) * 1000)

        # STAGE 8: Text-to-Speech (TTS) Synthesis
        t_tts_start = time.time()
        audio_output_bytes, tts_engine = tts_service.synthesize_speech(gu_answer)
        stage_latencies["tts_ms"] = int((time.time() - t_tts_start) * 1000)

        total_latency_ms = int((time.time() - t_start) * 1000)

        # Construct trace payload
        trace_data = {
            "gu_transcript": gu_transcript,
            "en_query": en_query,
            "intent": intent,
            "confidence": f"{confidence:.2f}",
            "sources": sources,
            "en_answer": en_answer,
            "gu_answer": gu_answer,
            "stt_engine": stt_engine,
            "tts_engine": tts_engine,
            "total_latency_ms": total_latency_ms,
            "latency_ms": stage_latencies
        }

        return {
            "success": True,
            "gu_transcript": gu_transcript,
            "gu_answer": gu_answer,
            "intent": intent,
            "sources": sources,
            "price_card_data": price_card_data,
            "weather_card_data": weather_card_data,
            "audio_bytes": audio_output_bytes,
            "trace_data": trace_data
        }


# Global singleton instance
pipeline = PipelineOrchestrator()
