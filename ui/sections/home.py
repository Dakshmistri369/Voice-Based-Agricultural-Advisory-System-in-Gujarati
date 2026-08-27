"""
Home Dashboard — 9-panel interactive grid layout matching reference PNG.
Panel layout (3 rows × 3 cols):
  Row 1: Home Dashboard | Voice Assistant (Interactive Mic) | Answer with Sources
  Row 2: Crop Advisory  | Weather & Alerts                 | Market Prices
  Row 3: Soil Test      | Govt Schemes                     | History & Saved
Footer: Feature badge bar
"""

import hashlib
import streamlit as st
from config import settings
from pipeline import pipeline
from core.tts_service import detect_audio_mime_type
from ui.theme import normalize_theme_name, get_theme_dict
from ui.components import (
    clean_html,
    panel_badge,
    render_answer_panel,
    render_crop_panel_mini,
    render_weather_panel_mini,
    render_price_table_mini,
    render_soil_panel_mini,
    render_feature_footer,
    render_chat_bubble,
    render_price_card,
    render_weather_card,
    render_pipeline_trace,
)

try:
    from audio_recorder_streamlit import audio_recorder
except ImportError:
    audio_recorder = None


# ── Static/fallback data for panels ─────────────────────────────────
_DEFAULT_SCHEMES = [
    ("🚜", "PM કિસાન સન્માન નિધિ", "વર્ષે ₹6,000 ની સહાય", "PM-KISAN યોજના વિશે માહિતી આપો"),
    ("💳", "કિસાન ક્રેડિટ કાર્ડ (KCC)", "સસ્તા વ્યાજે લોન", "કિસાન ક્રેડિટ કાર્ડ (KCC) યોજના વિશે જણાવો"),
    ("🛡️", "પાક વિમા યોજના", "પાક નુક્સાન પર વીમો", "પ્રધાનમંત્રી પાક વીમા યોજના (PMFBY) ના નિયમો શું છે?"),
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
            "temp_c": 26.3, "humidity": 65, "wind_speed": 12,
            "condition_gujarati": "સૂર્ય, હળવો ઘટાટોપ",
            "forecast_days": [
                {"day_gu": "આજે", "temp_max": 32, "temp_min": 24, "rain_mm": 0},
                {"day_gu": "કાલે", "temp_max": 31, "temp_min": 23, "rain_mm": 2},
                {"day_gu": "પર.", "temp_max": 30, "temp_min": 23, "rain_mm": 5},
            ],
            "advisories": ["પાણી આઠ-આઠ ઘંટે આપો", "તીડનું નિયંત્રણ કરો"],
            "alert_text": "2 દિવસમાં વરસાદની શક્યતા છે. પાકની સુરક્ષા કરો.",
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
    """9-panel interactive grid home dashboard."""

    current_theme = normalize_theme_name(st.session_state.get("theme", "green"))
    tokens = get_theme_dict(current_theme)
    district = st.session_state.get("selected_district", "રાજકોટ")
    messages = st.session_state.get("messages", [])
    selected_crop = st.session_state.get("selected_crop", "groundnut")

    # ── Greeting header ────────────────────────────────
    st.markdown(clean_html(f"""
<div style="padding:0.25rem 0 0.5rem 0;">
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

    query_to_process = None
    is_audio_query = False

    # ─────────────────────────────────────────────────────
    #  ROW 1: Home Dashboard | Voice Assistant | Answer
    # ─────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3, gap="small")

    # --- Panel 1: Home Dashboard ---
    with col1:
        st.markdown(panel_badge("1", "Home Dashboard"), unsafe_allow_html=True)
        with st.container():
            st.markdown(clean_html("""
<div style="background:var(--bg-surface);border:1px solid var(--border-subtle);border-radius:16px;padding:1rem;box-shadow:var(--shadow);">
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:1.15rem;font-weight:700;color:var(--text-primary);margin-bottom:0.15rem;">
    🙏 નમસ્તે ખેડૂતભાઈ!
  </div>
  <div style="font-family:Inter,sans-serif;font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.6rem;">
    આજની મુખ્ય માહિતી (Click to explore)
  </div>
</div>"""), unsafe_allow_html=True)

            # 3 Clickable Stat Buttons in Info Bar
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button(f"🌤️ {weather['temp_c']}°C\nહવામાન", key="btn_info_weather", use_container_width=True, help="હવામાન વિભાગ પર જાઓ"):
                    st.session_state["active_section"] = "weather"
                    st.rerun()
            with c2:
                if st.button(f"💰 ₹{cotton_price.get('modal_price', 1527)}\nબજાર ભાવ", key="btn_info_price", use_container_width=True, help="બજાર ભાવ વિભાગ પર જાઓ"):
                    st.session_state["active_section"] = "prices"
                    st.rerun()
            with c3:
                if st.button("🌱 મગફળી\nપાક સલાહ", key="btn_info_crop", use_container_width=True, help="પાક સલાહ વિભાગ પર જાઓ"):
                    st.session_state["active_section"] = "crop_advisory"
                    st.rerun()

            st.markdown("<div style='height:0.35rem;'></div>", unsafe_allow_html=True)

            # Quick Action Buttons
            st.markdown("<p style='font-family:JetBrains Mono,monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--text-muted);margin:0 0 0.3rem 0;'>ઝડપી સહાય</p>", unsafe_allow_html=True)
            q1, q2 = st.columns(2)
            with q1:
                if st.button("🎤 અવાજથી પૂછો", key="btn_quick_voice", use_container_width=True, help="માઇકથી પ્રશ્ન પૂછો"):
                    query_to_process = f"આજે {district} માં ખેડૂતો માટે મુખ્ય સલાહ શું છે?"
            with q2:
                if st.button("💬 લખીને પૂછો", key="btn_quick_text", use_container_width=True, help="ટેક્સ્ટથી પ્રશ્ન પૂછો"):
                    query_to_process = f"આજે {district} માં કપાસ અને મગફળીનો ભાવ કેટલો છે?"

            # Clickable Alert Suggestions
            st.markdown("<p style='font-family:JetBrains Mono,monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--text-muted);margin:0.4rem 0 0.25rem 0;'>તાજા સૂચનાઓ (Click to ask)</p>", unsafe_allow_html=True)
            if st.button("🐛 મગફળીમાં તીડનું નિયંત્રણ કેવી રીતે કરવું?", key="alert_ask_1", use_container_width=True):
                query_to_process = "મગફળીમાં તીડનું નિયંત્રણ કેવી રીતે કરવું?"
            if st.button("🌧️ વરસાદની શક્યતા 2 દિવસમાં છે (વિગત)", key="alert_ask_2", use_container_width=True):
                query_to_process = f"આગામી 2 દિવસમાં {district} માં વરસાદની શું આગાહી છે?"

    # --- Panel 2: Voice Assistant (Interactive Microphone) ---
    with col2:
        st.markdown(panel_badge("2", "Voice Assistant (Ask)"), unsafe_allow_html=True)
        with st.container():
            waveform_bars = "".join('<div class="waveform-bar"></div>' for _ in range(10))
            st.markdown(clean_html(f"""
<div style="background:var(--bg-surface);border:1px solid var(--border-subtle);border-radius:16px;padding:0.75rem 1rem;box-shadow:var(--shadow);text-align:center;">
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:1rem;font-weight:700;color:var(--text-primary);margin-bottom:0.3rem;">
    કિસાન મિત્ર AI
  </div>
  <div class="waveform" style="justify-content:center;margin:0.2rem auto;">{waveform_bars}</div>
</div>"""), unsafe_allow_html=True)

            # Real interactive microphone widget in Panel 2
            st.markdown("<div style='text-align:center;margin:0.5rem 0 0.2rem 0;'>", unsafe_allow_html=True)
            if audio_recorder is not None:
                panel2_audio = audio_recorder(
                    text="🎙️ માઇક દબાવીને બોલો (Click Mic to Speak)",
                    recording_color="#DC2626",
                    neutral_color="#2D6A4F",
                    icon_name="microphone",
                    icon_size="3x",
                    key="panel2_main_mic"
                )
                if panel2_audio:
                    audio_hash = hashlib.md5(panel2_audio).hexdigest()
                    if audio_hash != st.session_state.get("last_processed_audio_hash"):
                        query_to_process = panel2_audio
                        is_audio_query = True
                        st.session_state["last_processed_audio_hash"] = audio_hash
            else:
                st.info("Audio recorder module loading...")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(clean_html("""
<div style="text-align:center;padding:0.2rem 0;">
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.88rem;font-weight:600;color:var(--text-primary);">
    સાંભળું છું… બોલો
  </div>
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.72rem;color:var(--text-muted);font-style:italic;margin-top:0.2rem;">
    ઉદાહ.: "મગફળીમાં પીળાશ શા માટે આવે છે?"
  </div>
  <div style="display:inline-flex;align-items:center;gap:0.35rem;background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:9999px;padding:0.2rem 0.65rem;font-family:'Noto Sans Gujarati',sans-serif;font-size:0.75rem;color:var(--text-secondary);margin-top:0.4rem;">
    <span>🇮🇳</span><span>ગુજરાતી</span><span style="color:var(--text-muted);">▾</span>
  </div>
</div>"""), unsafe_allow_html=True)

    # --- Panel 3: Answer (with Sources) ---
    with col3:
        st.markdown(panel_badge("3", "Answer (with Sources)"), unsafe_allow_html=True)
        with st.container():
            if messages:
                last = messages[-1]
                bullets = [b.strip("• ").strip() for b in
                           last.get("gu_answer", "").split("।") if b.strip()][:3]
                if not bullets:
                    bullets = ["AI જવાબ ઉપર દર્શાવેલ છે."]
                srcs = [(s.get("filename", "PDF"), "PDF")
                        for s in last.get("sources", [])[:3]]
                answer_html = render_answer_panel(
                    answer_text=last.get("gu_answer", "")[:130] + ("…" if len(last.get("gu_answer", "")) > 130 else ""),
                    bullets=bullets[:3] if bullets else None,
                    sources=srcs if srcs else None
                )
            else:
                answer_html = render_answer_panel(
                    answer_text="મગફળીમાં પીળાશ નાઇટ્રોજનની કમી, વધુ પાણી અથવા રોગને કારણે આવે છે.",
                    bullets=["યોગ્ય ખાતર આપો (યુરિયા)", "પાણીનું નીકળવું સુનિશ્ચિત કરો", "પાંડડાનું ફૂગનાશક છિટકાવ કરો"],
                    sources=[("કૃષિ યુનિ. માર્ગદર્શન PDF", "PDF"), ("ICAR મગફળી પાક માર્ગદર્શન", "PDF"), ("કૃષિ નિષ્ણાત સલાહ", "Web")]
                )
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

        crops_mini = [
            ("cotton", "🌿", "કપાસ"), ("groundnut", "🥜", "મગફળી"),
            ("wheat", "🌾", "ઘઉં"), ("pigeon", "🫘", "તુવેર"), ("sorghum", "🌽", "જ્વાર"),
        ]
        mini_cols = st.columns(len(crops_mini))
        for i, (cid, icon, lbl) in enumerate(crops_mini):
            if mini_cols[i].button(f"{icon}\n{lbl}", key=f"home_crop_{cid}", help=f"{lbl} પસંદ કરો"):
                st.session_state["selected_crop"] = cid
                st.rerun()

        if st.button("🌱 સંપૂર્ણ પાક સલાહ જુઓ →", key="btn_more_crop", use_container_width=True):
            st.session_state["active_section"] = "crop_advisory"
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
        if st.button("🌤️ 5-દિવસ હવામાન અને AQI જુઓ →", key="btn_more_weather", use_container_width=True):
            st.session_state["active_section"] = "weather"
            st.rerun()

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
        if st.button("💰 બધા પાકના બજાર ભાવ જુઓ →", key="btn_more_prices", use_container_width=True):
            st.session_state["active_section"] = "prices"
            st.rerun()

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
        if st.button("🧪 સંપૂર્ણ માટી તપાસ રિપોર્ટ જુઓ →", key="btn_more_soil", use_container_width=True):
            st.session_state["active_section"] = "soil_test"
            st.rerun()

    # --- Panel 8: Government Schemes (Clickable Scheme Buttons) ---
    with col8:
        st.markdown(panel_badge("8", "Government Schemes"), unsafe_allow_html=True)
        with st.container():
            st.markdown(clean_html("""
<div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.88rem;font-weight:700;
    color:var(--text-primary);margin-bottom:0.4rem;">
  સરકારી યોજના
</div>"""), unsafe_allow_html=True)

            # Render 3 interactive scheme rows with buttons
            for idx, (icon, name, sub, query_text) in enumerate(_DEFAULT_SCHEMES):
                sc1, sc2 = st.columns([3.2, 1.8])
                with sc1:
                    st.markdown(clean_html(f"""
<div style="display:flex;align-items:center;gap:0.4rem;padding:0.25rem 0;">
  <span style="font-size:1.1rem;">{icon}</span>
  <div>
    <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.8rem;font-weight:700;color:var(--text-primary);">{name}</div>
    <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.65rem;color:var(--text-muted);">{sub}</div>
  </div>
</div>"""), unsafe_allow_html=True)
                with sc2:
                    if st.button("વધુ જાણો →", key=f"btn_scheme_item_{idx}", use_container_width=True, help=f"{name} ની માહિતી"):
                        query_to_process = query_text

            st.markdown("<div style='height:0.25rem;'></div>", unsafe_allow_html=True)
            if st.button("📄 બધી સરકારી યોજનાઓ જુઓ →", key="btn_more_schemes", use_container_width=True):
                st.session_state["active_section"] = "schemes"
                st.rerun()

    # --- Panel 9: History & Saved ---
    with col9:
        st.markdown(panel_badge("9", "History & Saved"), unsafe_allow_html=True)
        with st.container():
            st.markdown(clean_html("""
<div class="history-panel-header">
  <div class="history-panel-title">મારો ઇતિહાસ</div>
</div>"""), unsafe_allow_html=True)

            if messages:
                for idx, msg in enumerate(reversed(messages[-3:])):
                    q_text = msg.get("gu_transcript", "")[:35]
                    if st.button(f"🔄 {q_text}…", key=f"btn_hist_replay_{idx}", use_container_width=True, help="આ પ્રશ્ન ફરી પૂછો"):
                        query_to_process = msg.get("gu_transcript", "")
            else:
                st.markdown(clean_html("""
<div class="history-empty" style="padding:1rem 0;">
  <div style="font-size:1.2rem;margin-bottom:0.2rem;">📭</div>
  <div>હજુ કોઈ પ્રશ્ન પૂછ્યો નથી</div>
</div>"""), unsafe_allow_html=True)

            if st.button("📖 સંપૂર્ણ ઇતિહાસ જુઓ →", key="btn_more_history", use_container_width=True):
                st.session_state["active_section"] = "history"
                st.rerun()

    st.markdown('<div style="height:0.75rem;"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    #  FEATURE FOOTER
    # ─────────────────────────────────────────────────────
    st.markdown(render_feature_footer(), unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    #  BOTTOM VOICE / TEXT CHAT BAR
    # ─────────────────────────────────────────────────────
    st.markdown(
        '<div style="margin-top:1.25rem;border-top:1px solid var(--border-subtle);'
        'padding-top:1rem;"></div>',
        unsafe_allow_html=True
    )
    st.markdown(clean_html("""
<div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;
    color:var(--text-primary);margin-bottom:0.5rem;">
  🎤 AI ને સીધો પ્રશ્ન પૂછો અથવા ફાઇલ અપલોડ કરો
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
                text="માઇક દબાવો",
                recording_color="#DC2626",
                neutral_color=tokens["accent"],
                icon_name="microphone",
                icon_size="2x",
                key="bottom_voice_mic"
            )

    with col_upload:
        uploaded_file = st.file_uploader(
            "ઓડિયો ફાઇલ (WAV/MP3):",
            type=["wav", "mp3", "m4a"],
            label_visibility="collapsed",
            key="bottom_file_uploader"
        )
        if uploaded_file is not None:
            recorded_bytes = uploaded_file.read()

    user_text_input = st.chat_input("ગુજરાતીમાં પ્રશ્ન ટાઇપ કરો… (Type question in Gujarati)")

    # ── Handle Input Processing ────────────────────────
    if recorded_bytes:
        audio_hash = hashlib.md5(recorded_bytes).hexdigest()
        if audio_hash != st.session_state.get("last_processed_audio_hash"):
            query_to_process = recorded_bytes
            is_audio_query = True
            st.session_state["last_processed_audio_hash"] = audio_hash
    elif user_text_input:
        query_to_process = user_text_input

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

    # ── Conversation History Render ───────────────────
    if messages:
        st.markdown(
            '<div style="font-family:\'Space Grotesk\',sans-serif;font-size:0.9rem;font-weight:700;'
            'color:var(--text-primary);margin:1rem 0 0.5rem 0;">💬 વાર્તાલાપ (Chat History)</div>',
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
