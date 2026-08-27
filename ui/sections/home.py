"""
Home Dashboard — 9-panel grid layout matching reference PNG exactly.
Panel layout (3 rows × 3 cols):
  Row 1: Home Dashboard | Voice Assistant | Answer with Sources
  Row 2: Crop Advisory  | Weather & Alerts| Market Prices
  Row 3: Soil Test      | Govt Schemes    | History & Saved
Footer: Feature badge bar
"""

import streamlit as st
from config import settings
from pipeline import pipeline
from core.tts_service import detect_audio_mime_type
from ui.theme import normalize_theme_name, get_theme_dict
from ui.components import (
    clean_html,
    panel_badge,
    render_home_info_bar,
    render_voice_panel,
    render_answer_panel,
    render_crop_panel_mini,
    render_weather_panel_mini,
    render_price_table_mini,
    render_soil_panel_mini,
    render_schemes_panel_mini,
    render_history_panel_mini,
    render_feature_footer,
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


# ── Static/fallback data for panels (live data is fetched in full sections) ──
_DEFAULT_SCHEMES = [
    ("🚜", "PM કિસાન સન્માન નિધિ", "વર્ષે ₹6,000 ની સહાય", "schemes"),
    ("💳", "કિસાન ક્રેડિટ કાર્ડ (KCC)", "સસ્તા વ્યાજે લોન", "schemes"),
    ("🛡️", "પાક વિમા યોજના", "પાક નુક્સાન પર વીમો", "schemes"),
]

_DEFAULT_PRICE_ROWS = [
    ("કપાસ",   "રાજકોટ",  "1,527", "2.3%", True),
    ("મગફળી",  "જામનગર", "1,183", "1.8%", True),
    ("ઘઉં",    "અમદાવાદ", "2,125", "0.5%", False),
    ("તુવેર",  "ભાવનગર", "5,680", "1.2%", True),
]

_DEFAULT_SOIL = {
    "ph": 7.2, "n": "મધ્યમ", "p": "ઓછું", "k": "સારો",
    "recs": ["યુરિયા 50 કિ./હ.", "DAP 40 કિ./હ.", "MOP 20 કિ./હ."]
}


def _try_fetch_weather(district: str) -> dict:
    """Fetch live weather or return safe fallback."""
    try:
        from data_services.weather_service import weather_service
        return weather_service.fetch_weather(district)
    except Exception:
        return {
            "temp_c": 32, "humidity": 65, "wind_speed": 12,
            "condition_gujarati": "સૂર્ય, હળવો ઘટાટોપ",
            "forecast_days": [
                {"day_gu": "આજે", "temp_max": 32, "temp_min": 24, "rain_mm": 0},
                {"day_gu": "કાલે", "temp_max": 31, "temp_min": 23, "rain_mm": 2},
                {"day_gu": "પર.", "temp_max": 30, "temp_min": 23, "rain_mm": 5},
            ],
            "advisories": ["પાણી આઠ-આઠ ઘંટે આપો", "ઠંડા કલ્ટ ઉગ્યા ટાળો"],
            "alert_text": "2 દિવસમાં વરસાદ થઈ શકે. ફ્લડ ઝ ઘ ઝ.",
        }


def _try_fetch_price(commodity: str, district: str) -> dict:
    """Fetch live price or return safe fallback."""
    try:
        from data_services.price_service import price_service
        return price_service.fetch_mandi_price(commodity, district)
    except Exception:
        return {"modal_price": 1527, "is_live": False}


def _get_soil(district: str) -> dict:
    try:
        from ui.sections.soil_test import DISTRICT_SOIL_DATA
        return DISTRICT_SOIL_DATA.get(district, DISTRICT_SOIL_DATA["default"])
    except Exception:
        return _DEFAULT_SOIL


def render_home_section():
    """9-panel grid home dashboard."""

    current_theme = normalize_theme_name(st.session_state.get("theme", "green"))
    tokens = get_theme_dict(current_theme)
    district = st.session_state.get("selected_district", "રાજકોટ")
    messages = st.session_state.get("messages", [])
    selected_crop = st.session_state.get("selected_crop", "groundnut")

    # ── Greeting header ────────────────────────────────
    st.markdown(clean_html(f"""
<div style="padding:0.25rem 0 0.75rem 0;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.35rem;font-weight:700;
      color:var(--text-primary);margin-bottom:0.1rem;">
    🌾 ગુજરાતી કિસાન મિત્ર AI
  </div>
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.78rem;
      color:var(--text-secondary);">
    Farmer Friendly · Voice Based · Local Language (Gujarati) · Easy to Use
  </div>
</div>"""), unsafe_allow_html=True)

    # ── Fetch live data (weather once for dashboard) ───
    with st.spinner("ડેટા લોડ…"):
        weather = _try_fetch_weather(district)
        cotton_price = _try_fetch_price("Cotton", district)
        soil = _get_soil(district)

    # ─────────────────────────────────────────────────────
    #  ROW 1: Home Dashboard | Voice Assistant | Answer
    # ─────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3, gap="small")

    # --- Panel 1: Home Dashboard ---
    with col1:
        st.markdown(panel_badge("1", "Home Dashboard"), unsafe_allow_html=True)
        with st.container():
            st.markdown(clean_html(f"""
<div class="panel-card">
  <div class="greeting-title">🙏 નમસ્તે ખેડૂતભાઈ!</div>
  <div class="greeting-sub">આજની મુખ્ય માહિતી</div>
  {render_home_info_bar(weather['temp_c'], cotton_price.get('modal_price', 1527), 'મગફળી')}
  <div style="margin-bottom:0.5rem;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;text-transform:uppercase;
        letter-spacing:0.05em;color:var(--text-muted);margin-bottom:0.35rem;">ઝડપી સહાય</div>
    <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
      <div class="voice-btn-large" style="flex:1;font-size:0.75rem;padding:0.5rem 0.5rem;">🎤 અવાજથી પૂછો</div>
      <div class="text-btn-large" style="flex:1;font-size:0.75rem;padding:0.5rem 0.5rem;">💬 લખીને પૂછો</div>
    </div>
  </div>
  <div style="margin-top:0.4rem;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;text-transform:uppercase;
        letter-spacing:0.05em;color:var(--text-muted);margin-bottom:0.25rem;">તાઝ સૂચનાઓ</div>
    <div class="alert-row"><div class="alert-dot"></div><div>મગફળીમાં તીડનું નિયંત્રણ કરો.</div></div>
    <div class="alert-row"><div class="alert-dot"></div><div>વરસાદની શક્યતા 2 દિવસમાં છે.</div></div>
  </div>
</div>"""), unsafe_allow_html=True)

    # --- Panel 2: Voice Assistant ---
    with col2:
        st.markdown(panel_badge("2", "Voice Assistant (Ask)"), unsafe_allow_html=True)
        with st.container():
            st.markdown(f'<div class="panel-card">{render_voice_panel()}</div>',
                        unsafe_allow_html=True)

    # --- Panel 3: Answer (with Sources) ---
    with col3:
        st.markdown(panel_badge("3", "Answer (with Sources)"), unsafe_allow_html=True)
        with st.container():
            if messages:
                last = messages[-1]
                bullets = [b.strip("• ").strip() for b in
                           last.get("gu_answer", "").split("।") if b.strip()][:3]
                if not bullets:
                    bullets = ["AI જવાબ ઉપર દ્રષ્ટ કરો"]
                srcs = [(s.get("filename", "PDF"), "PDF")
                        for s in last.get("sources", [])[:3]]
                answer_html = render_answer_panel(
                    answer_text=last.get("gu_answer", "")[:120] + "…",
                    bullets=bullets[:3] if bullets else None,
                    sources=srcs if srcs else None
                )
            else:
                answer_html = render_answer_panel()
            st.markdown(f'<div class="panel-card">{answer_html}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    #  ROW 2: Crop Advisory | Weather | Market Prices
    # ─────────────────────────────────────────────────────
    col4, col5, col6 = st.columns(3, gap="small")

    # --- Panel 4: Crop Advisory ---
    with col4:
        st.markdown(panel_badge("4", "Crop Advisory"), unsafe_allow_html=True)
        crop_html = render_crop_panel_mini(selected_crop)
        st.markdown(f'<div class="panel-card">{crop_html}</div>', unsafe_allow_html=True)

        # Crop selector buttons below
        crops_mini = [
            ("cotton", "🌿", "કપાસ"), ("groundnut", "🥜", "મગફળી"),
            ("wheat", "🌾", "ઘઉં"), ("pigeon", "🫘", "તુવેર"), ("sorghum", "🌽", "જ્વાર"),
        ]
        mini_cols = st.columns(len(crops_mini))
        for i, (cid, icon, lbl) in enumerate(crops_mini):
            if mini_cols[i].button(f"{icon}", key=f"home_crop_{cid}", help=lbl):
                st.session_state["selected_crop"] = cid
                st.rerun()

    # --- Panel 5: Weather & Alerts ---
    with col5:
        st.markdown(panel_badge("5", "Weather & Alerts"), unsafe_allow_html=True)
        forecast = weather.get("forecast_days", [])
        alert = weather.get("alert_text", "")
        weather_html = render_weather_panel_mini(
            district=district,
            temp_c=weather["temp_c"],
            humidity=weather["humidity"],
            wind_speed=weather["wind_speed"],
            condition_gu=weather.get("condition_gujarati", ""),
            forecast_days=forecast,
            alert_text=alert
        )
        st.markdown(f'<div class="panel-card">{weather_html}</div>', unsafe_allow_html=True)

    # --- Panel 6: Market Prices ---
    with col6:
        st.markdown(panel_badge("6", "Market Prices"), unsafe_allow_html=True)
        price_html = render_price_table_mini(_DEFAULT_PRICE_ROWS)
        st.markdown(clean_html(f"""
<div class="panel-card">
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.82rem;font-weight:700;
      color:var(--text-primary);margin-bottom:0.4rem;">બજાર ભાવ (આજના)</div>
  {price_html}
</div>"""), unsafe_allow_html=True)

    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    #  ROW 3: Soil Test | Govt Schemes | History & Saved
    # ─────────────────────────────────────────────────────
    col7, col8, col9 = st.columns(3, gap="small")

    # --- Panel 7: Soil Test ---
    with col7:
        st.markdown(panel_badge("7", "Soil Test"), unsafe_allow_html=True)
        soil_html = render_soil_panel_mini(
            ph=soil["ph"], n_level=soil["n"], p_level=soil["p"], k_level=soil["k"],
            recs=soil["recs"]
        )
        st.markdown(f'<div class="panel-card">{soil_html}</div>', unsafe_allow_html=True)

    # --- Panel 8: Government Schemes ---
    with col8:
        st.markdown(panel_badge("8", "Government Schemes"), unsafe_allow_html=True)
        schemes_html = render_schemes_panel_mini(_DEFAULT_SCHEMES)
        st.markdown(clean_html(f"""
<div class="panel-card">
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.82rem;font-weight:700;
      color:var(--text-primary);margin-bottom:0.4rem;">સરકારી યોજના</div>
  {schemes_html}
</div>"""), unsafe_allow_html=True)

    # --- Panel 9: History & Saved ---
    with col9:
        st.markdown(panel_badge("9", "History & Saved"), unsafe_allow_html=True)
        history_html = render_history_panel_mini(messages)
        st.markdown(clean_html(f"""
<div class="panel-card">
  <div class="history-panel-header">
    <div class="history-panel-title">મારો ઇતિહાસ</div>
  </div>
  {history_html}
</div>"""), unsafe_allow_html=True)

    st.markdown('<div style="height:0.75rem;"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    #  FEATURE FOOTER
    # ─────────────────────────────────────────────────────
    st.markdown(render_feature_footer(), unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    #  VOICE / TEXT INPUT (below the grid)
    # ─────────────────────────────────────────────────────
    st.markdown(
        '<div style="margin-top:1.25rem;border-top:1px solid var(--border-subtle);'
        'padding-top:1rem;"></div>',
        unsafe_allow_html=True
    )
    st.markdown(clean_html("""
<div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;
    color:var(--text-primary);margin-bottom:0.5rem;">
  🎤 AI ને સીધો પ્રશ્ન પૂછો
</div>"""), unsafe_allow_html=True)

    col_mic, col_upload = st.columns([1, 2])
    recorded_bytes = None

    with col_mic:
        st.markdown(
            '<p style="font-size:0.75rem;color:var(--text-secondary);'
            'font-family:Noto Sans Gujarati,sans-serif;margin-bottom:4px;font-weight:600;">'
            'અવાજ રેકોર્ડ કરો:</p>',
            unsafe_allow_html=True
        )
        if audio_recorder is not None:
            recorded_bytes = audio_recorder(
                text="",
                recording_color=tokens["accent"],
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

    user_text_input = st.chat_input("ગુજરાતીમાં પ્રશ્ન ટાઇપ કરો… (Type question in Gujarati)")

    # ── Quick Chips ───────────────────────────────────
    quick_chip_selected = None
    if not messages:
        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button("💰 ભાવ", use_container_width=True, key="chip_price"):
            quick_chip_selected = f"આજે {district} માં કપાસનો ભાવ કેટલો?"
        if c2.button("☔ હવામાન", use_container_width=True, key="chip_weather"):
            quick_chip_selected = f"આવતીકાલે {district} માં વરસાદ પડશે?"
        if c3.button("📄 PM-KISAN", use_container_width=True, key="chip_scheme"):
            quick_chip_selected = "PM-KISAN યોજનામાં વાર્ષિક કેટલા રૂપિયા મળે છે?"
        if c4.button("🌱 ખાતર", use_container_width=True, key="chip_fertilizer"):
            quick_chip_selected = "કપાસ માટે કેટલું ખાતર નાખવું?"
        if c5.button("🐛 રોગ", use_container_width=True, key="chip_disease"):
            quick_chip_selected = "કપાસના પાકમાં ગેરુ રોગ નું નિયંત્રણ?"

    # ── Process Query ──────────────────────────────────
    query_to_process = None
    is_audio_query = False

    import hashlib
    if recorded_bytes:
        audio_hash = hashlib.md5(recorded_bytes).hexdigest()
        if audio_hash != st.session_state.get("last_processed_audio_hash"):
            query_to_process = recorded_bytes
            is_audio_query = True
            st.session_state["last_processed_audio_hash"] = audio_hash
    elif user_text_input:
        query_to_process = user_text_input
    elif quick_chip_selected:
        query_to_process = quick_chip_selected

    if query_to_process:
        with st.spinner("જવાબ તૈયાર થઈ રહ્યો છે…"):
            if is_audio_query:
                result = pipeline.process_query(audio_bytes=query_to_process,
                                                selected_district=district)
            else:
                result = pipeline.process_query(text_query=query_to_process,
                                                selected_district=district)
            if result.get("success"):
                st.session_state["messages"].append({
                    "gu_transcript": result["gu_transcript"],
                    "gu_answer":     result["gu_answer"],
                    "intent":        result["intent"],
                    "sources":       result["sources"],
                    "price_card_data":   result.get("price_card_data"),
                    "weather_card_data": result.get("weather_card_data"),
                    "audio_bytes":   result.get("audio_bytes"),
                    "trace_data":    result.get("trace_data"),
                })
                st.session_state["last_trace"] = result.get("trace_data")
                st.rerun()
            else:
                st.warning(result.get("error",
                    "કોઈ અવાજ કે લખાણ ઓળખાયું નથી. ફરીથી બોલો અથવા ટાઇપ કરો."))

    # ── Conversation History ───────────────────────────
    if messages:
        st.markdown(
            '<div style="font-family:\'Space Grotesk\',sans-serif;font-size:0.9rem;font-weight:700;'
            'color:var(--text-primary);margin:1rem 0 0.5rem 0;">💬 વાર્તાલાપ</div>',
            unsafe_allow_html=True
        )
        for msg in messages:
            st.markdown(render_chat_bubble(msg["gu_transcript"], is_user=True),
                        unsafe_allow_html=True)

            if msg.get("price_card_data"):
                p = msg["price_card_data"]
                st.markdown(render_price_card(
                    commodity_gu=p["commodity_gu"], commodity_en=p["commodity_en"],
                    modal_price=p["modal_price"], min_price=p["min_price"],
                    max_price=p["max_price"], district_gu=p["district_gu"],
                    price_date=p["price_date"], is_live=p["is_live"]
                ), unsafe_allow_html=True)

            if msg.get("weather_card_data"):
                w = msg["weather_card_data"]
                st.markdown(render_weather_card(
                    district_gu=w["district_gujarati"], temp_c=w["temp_c"],
                    condition_gu=w["condition_gujarati"], humidity=w["humidity"],
                    wind_speed=w["wind_speed"], advisory_bullets=w["advisories"],
                    is_live=w["is_live"]
                ), unsafe_allow_html=True)

            src_chip = None
            if msg.get("sources"):
                top = msg["sources"][0]
                src_chip = {"filename": top["filename"], "page_number": top["page"]}
            st.markdown(render_chat_bubble(
                msg["gu_answer"], is_user=False,
                intent=msg.get("intent"), source_chip=src_chip
            ), unsafe_allow_html=True)

            if msg.get("audio_bytes"):
                st.audio(msg["audio_bytes"], format=detect_audio_mime_type(msg["audio_bytes"]))

    # ── Pipeline Trace ─────────────────────────────────
    if st.session_state.get("show_trace") and st.session_state.get("last_trace"):
        st.markdown(render_pipeline_trace(st.session_state["last_trace"]),
                    unsafe_allow_html=True)
