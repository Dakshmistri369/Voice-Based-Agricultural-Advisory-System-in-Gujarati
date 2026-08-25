"""
Weather & AQI Dashboard Section for Gujarati Kisaan Mitra AI.
"""

import streamlit as st
from ui.components import clean_html
from data_services.weather_service import weather_service
from data_services.aqi_service import fetch_aqi
from core.tts_service import tts_service

GUJARATI_DAYS = ["સોમ", "મંગળ", "બુધ", "ગુરુ", "શુક્ર", "શનિ", "રવિ"]


def render_weather_section():
    """Full weather + AQI dashboard with farming advisory and TTS listen button."""
    district = st.session_state.get("selected_district", "રાજકોટ")

    # ── Section Header with Back Navigation ───────────
    col_back, col_title = st.columns([1.3, 5])
    with col_back:
        if st.button("← પાછા ફરો", key="weather_section_back_btn", help="હોમ / મુખ્ય પેજ પર પાછા જાઓ", use_container_width=True):
            st.session_state["active_section"] = "home"
            st.rerun()

    st.markdown(clean_html(f"""
<div class="section-header">
    <h2>☔ હવામાન અને હવાની ગુણવત્તા (AQI)</h2>
    <p>Open-Meteo Live Forecast & CPCB Air Quality · {district} જિલ્લો</p>
</div>
"""), unsafe_allow_html=True)

    # Local district override
    from ui.navigation import DISTRICTS
    override = st.selectbox("જિલ્લો બદલો:", DISTRICTS,
                            index=DISTRICTS.index(district) if district in DISTRICTS else 0,
                            key="weather_district_override")
    if override != district:
        st.session_state["selected_district"] = override
        st.rerun()

    # ── Fetch Data ────────────────────────────────────
    with st.spinner("હવામાન ડેટા લોડ…"):
        weather = weather_service.fetch_weather(district)
        aqi = fetch_aqi(district)

    # ── Hero Stat Cards Row ───────────────────────────
    aqi_class = aqi.get("bucket_class", "aqi-good")
    aqi_border = {"aqi-good": "1px solid var(--border-subtle)",
                  "aqi-moderate": "2px solid var(--text-primary)",
                  "aqi-unhealthy": "3px solid var(--text-primary)",
                  "aqi-hazardous": "3px dashed var(--text-primary)"}.get(aqi_class, "1px solid var(--border-subtle)")
    aqi_icon = {"aqi-good": "●", "aqi-moderate": "◐", "aqi-unhealthy": "⚠", "aqi-hazardous": "⚠"}.get(aqi_class, "●")

    st.markdown(clean_html(f"""
<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
    <div class="stat-card">
        <div class="stat-card-label">🌡️ તાપમાન</div>
        <div class="stat-card-value">{weather['temp_c']}</div>
        <div class="stat-card-unit">°C</div>
    </div>
    <div class="stat-card">
        <div class="stat-card-label">💧 ભેજ</div>
        <div class="stat-card-value">{weather['humidity']}</div>
        <div class="stat-card-unit">%</div>
    </div>
    <div class="stat-card" style="border:{aqi_border};">
        <div class="stat-card-label">{aqi_icon} AQI (US)</div>
        <div class="stat-card-value">{aqi['us_aqi']}</div>
        <div class="stat-card-unit">{aqi['bucket_label']}</div>
    </div>
    <div class="stat-card">
        <div class="stat-card-label">🌬️ પવન</div>
        <div class="stat-card-value">{weather['wind_speed']}</div>
        <div class="stat-card-unit">km/h</div>
    </div>
</div>
"""), unsafe_allow_html=True)

    # ── 5-Day Forecast Strip ──────────────────────────
    forecast_days = weather.get("forecast_days", [])
    if forecast_days:
        forecast_html_parts = []
        for day in forecast_days[:5]:
            rain_mm = day.get("rain_mm", 0)
            rain_str = f"🌧️ {rain_mm}mm" if rain_mm > 0.5 else "☀️"
            forecast_html_parts.append(f"""
<div class="forecast-day-card">
    <div class="forecast-day-name">{day.get('day_gu', '')}</div>
    <div class="forecast-temp">{day.get('temp_max', '--')}°</div>
    <div style="font-size:0.7rem;color:var(--text-muted);font-family:JetBrains Mono,monospace;">{day.get('temp_min', '--')}°</div>
    <div class="forecast-rain">{rain_str}</div>
</div>""")
        forecast_inner = "".join(forecast_html_parts)
        st.markdown(clean_html(f"""
<div style="margin-bottom:1.25rem;">
    <div class="crop-subsection-header">5 દિવસ આગાહી (5-Day Forecast)</div>
    <div class="forecast-strip">{forecast_inner}</div>
</div>
"""), unsafe_allow_html=True)

    # ── Farming Advisory ──────────────────────────────
    advisories = weather.get("advisories", [])
    aqi_advisory = aqi.get("farming_advice", "")
    all_advisories = list(advisories)
    if aqi_advisory:
        all_advisories.append(aqi_advisory)

    advisory_bullets = "".join(
        f"<li style='font-family:Noto Sans Gujarati,sans-serif;font-size:0.9rem;color:var(--text-primary);margin-bottom:0.5rem;'>{b}</li>"
        for b in all_advisories
    )

    st.markdown(clean_html(f"""
<div class="kisaan-card p-5 mb-4">
    <div class="crop-subsection-header">🌾 ખેતી માટે સલાહ (Farming Advisory)</div>
    <ul style="list-style:none;padding:0;margin:0.5rem 0 0 0;">{advisory_bullets}</ul>
</div>
"""), unsafe_allow_html=True)

    # AQI detailed info card
    st.markdown(clean_html(f"""
<div class="kisaan-card p-4 mb-4">
    <div class="crop-subsection-header">💨 હવાની ગુણવત્તા વિગત (Air Quality Detail)</div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.75rem;margin-top:0.5rem;text-align:center;">
        <div>
            <div style="font-family:JetBrains Mono,monospace;font-size:0.6rem;color:var(--text-muted);text-transform:uppercase;">PM2.5</div>
            <div style="font-family:JetBrains Mono,monospace;font-size:1.2rem;font-weight:700;color:var(--text-primary);">{aqi['pm25']}</div>
            <div style="font-size:0.65rem;color:var(--text-secondary);">μg/m³</div>
        </div>
        <div>
            <div style="font-family:JetBrains Mono,monospace;font-size:0.6rem;color:var(--text-muted);text-transform:uppercase;">PM10</div>
            <div style="font-family:JetBrains Mono,monospace;font-size:1.2rem;font-weight:700;color:var(--text-primary);">{aqi['pm10']}</div>
            <div style="font-size:0.65rem;color:var(--text-secondary);">μg/m³</div>
        </div>
        <div>
            <div style="font-family:JetBrains Mono,monospace;font-size:0.6rem;color:var(--text-muted);text-transform:uppercase;">ગ્રેડ</div>
            <div style="font-family:Noto Sans Gujarati,sans-serif;font-size:0.8rem;font-weight:700;color:var(--text-primary);margin-top:0.2rem;">{aqi['bucket_label']}</div>
            <div style="font-size:0.65rem;color:var(--text-secondary);">{'Live' if aqi['is_live'] else 'Cached'}</div>
        </div>
    </div>
    <div style="margin-top:0.75rem;font-family:Noto Sans Gujarati,sans-serif;font-size:0.8rem;color:var(--text-secondary);">{aqi['bucket_advice']}</div>
</div>
"""), unsafe_allow_html=True)

    # ── TTS Listen Button ─────────────────────────────
    st.markdown("---")
    if st.button("🔊  સંપૂર્ણ સલાહ સાંભળો (Listen to Advisory)", key="weather_tts_btn", use_container_width=True):
        full_advisory = f"{district} માં હાલ તાપમાન {weather['temp_c']} ° C, ભેજ {weather['humidity']} %. AQI {aqi['us_aqi']}, {aqi['bucket_label']}. " + ". ".join(all_advisories)
        with st.spinner("ઓડિઓ તૈયાર…"):
            audio_bytes, engine = tts_service.synthesize_speech(full_advisory)
        if audio_bytes:
            from core.tts_service import detect_audio_mime_type
            st.audio(audio_bytes, format=detect_audio_mime_type(audio_bytes))
        else:
            st.warning("TTS ઉપલબ્ધ નથી.")
