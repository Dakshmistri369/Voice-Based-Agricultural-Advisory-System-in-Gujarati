"""
Home / Voice Chat Section — renders the pipeline chat interface.
"""

import streamlit as st
from config import settings
from pipeline import pipeline
from ui.theme import normalize_theme_name, get_theme_dict
from ui.components import (
    clean_html,
    render_header,
    render_chat_bubble,
    render_price_card,
    render_weather_card,
    render_pipeline_trace,
    render_empty_state,
)

try:
    from audio_recorder_streamlit import audio_recorder
except ImportError:
    audio_recorder = None


def render_home_section():
    """Full voice-chat pipeline view — dual theme compatible."""

    current_theme = normalize_theme_name(st.session_state.get("theme", "dark"))
    tokens = get_theme_dict(current_theme)

    # Header
    st.markdown(
        render_header(
            stt_status=settings.STT_MODE,
            tts_status="Piper / gTTS",
            llm_status="Qwen2.5-7B"
        ),
        unsafe_allow_html=True
    )

    selected_district = st.session_state.get("selected_district", "રાજકોટ")

    # ── Audio & Text Input ────────────────────────────
    col_mic, col_upload = st.columns([1, 2])
    recorded_bytes = None

    with col_mic:
        st.markdown(
            clean_html("<p style='font-size:0.75rem;color:var(--text-secondary);font-family:Noto Sans Gujarati,sans-serif;margin-bottom:4px;font-weight:600;'>અવાજ રેકોર્ડ કરો:</p>"),
            unsafe_allow_html=True
        )
        if audio_recorder is not None:
            recorded_bytes = audio_recorder(
                text="",
                recording_color=tokens["text_primary"],
                neutral_color=tokens["border_subtle"],
                icon_name="microphone",
                icon_size="2x"
            )

    with col_upload:
        uploaded_file = st.file_uploader(
            "ઓડિયો ફાઇલ (WAV/MP3):",
            type=["wav", "mp3", "m4a"],
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            recorded_bytes = uploaded_file.read()

    # Text input
    user_text_input = st.chat_input("ગુજરાતીમાં પ્રશ્ન ટાઇપ કરો… (Type question in Gujarati)")

    # ── Quick Chips ───────────────────────────────────
    quick_chip_selected = None
    if not st.session_state.get("messages"):
        st.markdown(render_empty_state(), unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button("💰 ભાવ", use_container_width=True, key="chip_price"):
            quick_chip_selected = f"આજે {selected_district} માં કપાસનો ભાવ કેટલો?"
        if c2.button("☔ હવામાન", use_container_width=True, key="chip_weather"):
            quick_chip_selected = f"આવતીકાલે {selected_district} માં વરસાદ પડશે?"
        if c3.button("📄 PM-KISAN", use_container_width=True, key="chip_scheme"):
            quick_chip_selected = "PM-KISAN યોજનામાં વાર્ષિક કેટલા રૂપિયા મળે છે?"
        if c4.button("🌱 ખાતર", use_container_width=True, key="chip_fertilizer"):
            quick_chip_selected = "કપાસ માટે કેટલું ખાતર નાખવું?"
        if c5.button("🐛 રોગ", use_container_width=True, key="chip_disease"):
            quick_chip_selected = "કપાસના પાકમાં ગેરુ રોગ નું નિયંત્રણ?"

    # ── Process Query ─────────────────────────────────
    query_to_process = None
    is_audio_query = False

    if recorded_bytes:
        query_to_process = recorded_bytes
        is_audio_query = True
    elif user_text_input:
        query_to_process = user_text_input
    elif quick_chip_selected:
        query_to_process = quick_chip_selected

    if query_to_process:
        with st.spinner("જવાબ તૈયાર થઈ રહ્યો છે…"):
            if is_audio_query:
                result = pipeline.process_query(audio_bytes=query_to_process, selected_district=selected_district)
            else:
                result = pipeline.process_query(text_query=query_to_process, selected_district=selected_district)

            if result.get("success"):
                st.session_state["messages"].append({
                    "gu_transcript": result["gu_transcript"],
                    "gu_answer": result["gu_answer"],
                    "intent": result["intent"],
                    "sources": result["sources"],
                    "price_card_data": result.get("price_card_data"),
                    "weather_card_data": result.get("weather_card_data"),
                    "audio_bytes": result.get("audio_bytes"),
                    "trace_data": result.get("trace_data")
                })
                st.session_state["last_trace"] = result.get("trace_data")
                st.rerun()
            else:
                st.error(result.get("error", "ભૂલ આવી છે."))

    # ── Conversation History ──────────────────────────
    for msg in st.session_state.get("messages", []):
        st.markdown(render_chat_bubble(message=msg["gu_transcript"], is_user=True), unsafe_allow_html=True)

        if msg.get("price_card_data"):
            p = msg["price_card_data"]
            st.markdown(render_price_card(
                commodity_gu=p["commodity_gu"],
                commodity_en=p["commodity_en"],
                modal_price=p["modal_price"],
                min_price=p["min_price"],
                max_price=p["max_price"],
                district_gu=p["district_gu"],
                price_date=p["price_date"],
                is_live=p["is_live"]
            ), unsafe_allow_html=True)

        if msg.get("weather_card_data"):
            w = msg["weather_card_data"]
            st.markdown(render_weather_card(
                district_gu=w["district_gujarati"],
                temp_c=w["temp_c"],
                condition_gu=w["condition_gujarati"],
                humidity=w["humidity"],
                wind_speed=w["wind_speed"],
                advisory_bullets=w["advisories"],
                is_live=w["is_live"]
            ), unsafe_allow_html=True)

        source_chip = None
        if msg.get("sources") and len(msg["sources"]) > 0:
            top_src = msg["sources"][0]
            source_chip = {"filename": top_src["filename"], "page_number": top_src["page"]}

        st.markdown(render_chat_bubble(
            message=msg["gu_answer"],
            is_user=False,
            intent=msg.get("intent"),
            source_chip=source_chip
        ), unsafe_allow_html=True)

        if msg.get("audio_bytes"):
            st.audio(msg["audio_bytes"], format="audio/wav")

    # ── Pipeline Trace ────────────────────────────────
    if st.session_state.get("show_trace") and st.session_state.get("last_trace"):
        st.markdown(render_pipeline_trace(st.session_state["last_trace"]), unsafe_allow_html=True)
