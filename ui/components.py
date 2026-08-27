"""
UI Component HTML Builders for Gujarati Kisaan Mitra AI.
Green Theme + Dark/Light support. All panel builder functions live here.
"""

import re
from typing import Dict, List, Optional, Any


def clean_html(html_str: str) -> str:
    """Removes leading/trailing line whitespace to prevent Streamlit markdown code blocks."""
    lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    return "".join(lines)


# ── Panel Badge ───────────────────────────────────────────────────
def panel_badge(number: str, label: str) -> str:
    return clean_html(f"""
<div style="margin-bottom:0.5rem;">
  <span style="display:inline-flex;align-items:center;gap:0.3rem;
    background:var(--accent);color:#fff;font-family:'Inter',sans-serif;
    font-size:0.68rem;font-weight:700;letter-spacing:0.02em;
    padding:0.18rem 0.55rem;border-radius:6px;">
    {number}. {label}
  </span>
</div>""")


# ── Home Info Bar ─────────────────────────────────────────────────
def render_home_info_bar(temp_c, price_val, crop_label) -> str:
    return clean_html(f"""
<div style="display:flex;gap:0.5rem;margin-bottom:0.7rem;">
  <div style="flex:1;background:var(--bg-elevated);border:1px solid var(--border-subtle);
      border-radius:10px;padding:0.45rem 0.55rem;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;text-transform:uppercase;
        letter-spacing:0.05em;color:var(--text-muted);margin-bottom:0.1rem;">હવામાન</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:800;
        color:var(--text-primary);">☀️ {temp_c}°C</div>
    <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.58rem;color:var(--text-muted);
        margin-top:0.1rem;">સૂર્ય, હળવો ઘટાટોપ</div>
  </div>
  <div style="flex:1;background:var(--bg-elevated);border:1px solid var(--border-subtle);
      border-radius:10px;padding:0.45rem 0.55rem;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;text-transform:uppercase;
        letter-spacing:0.05em;color:var(--text-muted);margin-bottom:0.1rem;">બજાર ભાવ</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:800;
        color:var(--text-primary);">₹ {price_val}</div>
    <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.58rem;color:var(--text-muted);
        margin-top:0.1rem;">ક્વિ./પ્રતિ ક્વિન્ટલ</div>
  </div>
  <div style="flex:1;background:var(--bg-elevated);border:1px solid var(--border-subtle);
      border-radius:10px;padding:0.45rem 0.55rem;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;text-transform:uppercase;
        letter-spacing:0.05em;color:var(--text-muted);margin-bottom:0.1rem;">પાક સલાહ</div>
    <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.9rem;font-weight:800;
        color:var(--text-primary);">{crop_label}</div>
    <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.58rem;color:var(--text-muted);
        margin-top:0.1rem;">પાણી આપવું જરૂરી</div>
  </div>
</div>""")


# ── Voice Assistant Panel ─────────────────────────────────────────
def render_voice_panel() -> str:
    bars = "".join(
        f'<div class="waveform-bar"></div>' for _ in range(10)
    )
    return clean_html(f"""
<div class="voice-panel-center" style="padding:0.3rem 0;">
  <div class="voice-panel-title">કિસાન મિત્ર AI</div>
  <div class="waveform" style="justify-content:center;">{bars}</div>
  <div style="width:68px;height:68px;border-radius:50%;background:var(--accent);
      color:#fff;display:flex;align-items:center;justify-content:center;
      font-size:1.7rem;margin:0.4rem auto;
      box-shadow:0 4px 16px var(--mic-ring-shadow);">🎤</div>
  <div class="voice-hint">સાંભળું છું… બોલો</div>
  <div class="voice-example">ઉદાહ.: "મગફળીમાં પીળાશ શા માટે આવે છે?"</div>
  <div class="lang-pill" style="margin:0.4rem auto;display:inline-flex;">
    <span>🇮🇳</span><span>ગુજરાતી</span><span style="color:var(--text-muted);">▾</span>
  </div>
</div>""")


# ── Answer Panel ─────────────────────────────────────────────────
def render_answer_panel(answer_text: str = "", bullets: list = None, sources: list = None) -> str:
    if not answer_text:
        answer_text = "અહીં AI નો જવાબ દેખાશે. ઉપર માઇક દબાવીને બોલો."
    if bullets is None:
        bullets = ["યોગ્ય ખાતર આપો (યુરિયા)", "પાણીનું નીકળવું સુનિશ્ચિત કરો", "પાંડડાનું ફૂગનાશક છિટકાવ કરો"]
    if sources is None:
        sources = [
            ("કૃષિ યુનિ. માર્ગદર્શન PDF", "PDF"),
            ("ICAR મગફળી પાક માર્ગદર્શન", "PDF"),
            ("કૃષિ નિષ્ણાત સલાહ", "Web"),
        ]
    bullets_html = "".join(
        f'<div class="answer-bullet">{b}</div>' for b in bullets
    )
    sources_html = "".join(
        f"""<div class="source-row">
          <span style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.7rem;color:var(--text-secondary);">{i+1}. {name}</span>
          <span class="source-badge {'source-badge-web' if t=='Web' else ''}">{t}</span>
        </div>""" for i, (name, t) in enumerate(sources)
    )
    return clean_html(f"""
<div>
  <div class="answer-section-title">જવાબ</div>
  <div class="answer-text">{answer_text}</div>
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.72rem;
      color:var(--text-muted);text-transform:uppercase;letter-spacing:0.04em;
      margin-bottom:0.3rem;">સૂચનો:</div>
  {bullets_html}
  <div class="sources-section">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;text-transform:uppercase;
        letter-spacing:0.05em;color:var(--text-muted);margin-bottom:0.25rem;">
      સંદર્ભ સ્ત્રોત (Sources)
    </div>
    {sources_html}
  </div>
</div>""")


# ── Crop Advisory Panel ───────────────────────────────────────────
def render_crop_panel_mini(selected_crop: str = "groundnut") -> str:
    crops = [
        ("cotton",    "🌿", "કપાસ"),
        ("groundnut", "🥜", "મગફળી"),
        ("wheat",     "🌾", "ઘઉં"),
        ("pigeon",    "🫘", "તુવેર"),
        ("sorghum",   "🌽", "જ્વાર"),
    ]
    tabs_html = ""
    for cid, icon, lbl in crops:
        active_cls = "crop-tab-active" if cid == selected_crop else ""
        tabs_html += f"""<div class="crop-tab {active_cls}">
          <span class="crop-tab-icon">{icon}</span>
          <span class="crop-tab-label">{lbl}</span>
        </div>"""

    # advisory per crop
    advisories = {
        "cotton":    ["પાણી આપવાનો ચાલુ રાખો", "તીડનું નિયંત્રણ કરો", "20:20:00 ખાતર 40 કિ./હ. આપો"],
        "groundnut": ["પાણી આપવાનો ચાલુ રાખો", "ફૂગ નિયંત્રણ", "DAP 50 કિ./હ. આપો"],
        "wheat":     ["ઠંડા હવામાનમાં સિંચાઈ", "રસ્ટ નિયંત્રણ", "યુરિયા 40 કિ./હ."],
        "pigeon":    ["સૂકો ચોમાસો", "AFB નિયંત્રણ", "SSP 30 કિ./હ."],
        "sorghum":   ["ઓછું પાણી", "ઈયળ નિયંત્રણ", "NPK 20:20:0"],
    }
    adv = advisories.get(selected_crop, advisories["groundnut"])
    checks = "".join(
        f'<div class="crop-check-row"><span class="crop-check-icon">✓</span><span>{a}</span></div>'
        for a in adv
    )
    crop_name = next((lbl for cid, _, lbl in crops if cid == selected_crop), "મગફળી")
    return clean_html(f"""
<div>
  <div class="crop-tab-strip">{tabs_html}</div>
  <div class="crop-advisory-title">{crop_name} માટે સલાહ</div>
  {checks}
</div>""")


# ── Weather Panel ─────────────────────────────────────────────────
def render_weather_panel_mini(district: str, temp_c, humidity, wind_speed,
                               condition_gu: str, forecast_days: list,
                               alert_text: str = "") -> str:
    forecast_html = ""
    for day in forecast_days[:3]:
        rain_mm = day.get("rain_mm", 0)
        rain_str = f"🌧️{rain_mm}mm" if rain_mm > 0.5 else "☀️"
        forecast_html += f"""<div class="forecast-mini-item">
          <div class="forecast-mini-day">{day.get('day_gu','')}</div>
          <div class="forecast-mini-temp">{day.get('temp_max','--')}°/{day.get('temp_min','--')}°</div>
          <div class="forecast-mini-rain">{rain_str}</div>
        </div>"""

    alert_html = ""
    if alert_text:
        alert_html = f"""<div class="weather-alert-banner">
          <span class="weather-alert-icon">⚠️</span>
          <span>{alert_text}</span>
        </div>"""

    return clean_html(f"""
<div>
  <div class="weather-location">📍 {district}, ગુજરાત</div>
  <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.2rem;">
    <div class="weather-temp-hero">☀️ {temp_c}°C</div>
  </div>
  <div class="weather-condition">{condition_gu}</div>
  <div class="weather-stats">
    <div class="weather-stat-item">💧 {humidity}%</div>
    <div class="weather-stat-item">🌬️ {wind_speed} km/h</div>
    <div class="weather-stat-item">🌧️ 0%</div>
  </div>
  <div class="forecast-mini">{forecast_html}</div>
  {alert_html}
</div>""")


# ── Market Prices Panel ───────────────────────────────────────────
def render_price_table_mini(rows: list) -> str:
    """rows = list of (crop_gu, market, price, change_pct, up: bool)"""
    rows_html = ""
    for crop_gu, market, price, change, up in rows:
        arrow = "▲" if up else "▼"
        cls   = "price-change-up" if up else "price-change-down"
        rows_html += f"""<tr>
          <td style="font-family:'Noto Sans Gujarati',sans-serif;">{crop_gu}</td>
          <td style="font-family:'Noto Sans Gujarati',sans-serif;color:var(--text-secondary);">{market}</td>
          <td style="font-family:'JetBrains Mono',monospace;font-weight:700;">{price}</td>
          <td class="{cls}">{arrow} {change}</td>
        </tr>"""
    return clean_html(f"""
<div>
  <table class="price-table" style="width:100%;">
    <thead>
      <tr>
        <th>પાક</th>
        <th>બજાર</th>
        <th>ભાવ (₹/ક્વિ.)</th>
        <th>પરિવર્તન</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>""")


# ── Soil Test Panel ───────────────────────────────────────────────
def render_soil_panel_mini(ph: float, n_level: str, p_level: str, k_level: str,
                            recs: list) -> str:
    p_cls = "soil-stat-warning" if p_level == "ઓછું" else ""
    recs_html = "".join(
        f'<div class="soil-rec-bullet">{r}</div>' for r in recs
    )
    return clean_html(f"""
<div>
  <div class="soil-panel-title">માટી તપાસ</div>
  <div class="soil-stats-row">
    <div class="soil-stat">
      <div class="soil-stat-label">pH</div>
      <div class="soil-stat-value">{ph}</div>
      <div class="soil-stat-sub">સારો</div>
    </div>
    <div class="soil-stat">
      <div class="soil-stat-label">નાઇટ્રોજન (N)</div>
      <div class="soil-stat-value">{n_level}</div>
      <div class="soil-stat-sub">મધ્યમ</div>
    </div>
    <div class="soil-stat">
      <div class="soil-stat-label">ફોસ્ફરસ (P)</div>
      <div class="soil-stat-value {p_cls}">{p_level}</div>
      <div class="soil-stat-sub" style="{'color:var(--price-down);' if p_level=='ઓછું' else ''}">{'ઓછું' if p_level=='ઓછું' else 'ઠીક'}</div>
    </div>
    <div class="soil-stat">
      <div class="soil-stat-label">પોટાસ (K)</div>
      <div class="soil-stat-value">{k_level}</div>
      <div class="soil-stat-sub">સારો</div>
    </div>
  </div>
  <div class="soil-rec-title">સૂચન</div>
  {recs_html}
</div>""")


# ── Government Schemes Panel ──────────────────────────────────────
def render_schemes_panel_mini(schemes: list) -> str:
    """schemes = list of (icon, name, sub, section_key)"""
    cards_html = ""
    for icon, name, sub, _ in schemes:
        cards_html += f"""<div class="scheme-mini-card">
          <div class="scheme-mini-icon">{icon}</div>
          <div>
            <div class="scheme-mini-name">{name}</div>
            <div class="scheme-mini-sub">{sub}</div>
          </div>
          <div class="scheme-mini-btn">વધુ જાણો →</div>
        </div>"""
    return clean_html(f"<div>{cards_html}</div>")


# ── History Panel ─────────────────────────────────────────────────
def render_history_panel_mini(messages: list) -> str:
    if not messages:
        return clean_html("""
<div class="history-empty">
  <div style="font-size:1.5rem;margin-bottom:0.4rem;">📭</div>
  <div>હજુ કોઈ પ્રશ્ન પૂછ્યો નથી</div>
</div>""")

    import datetime
    items_html = ""
    for i, msg in enumerate(reversed(messages[-5:])):
        q = msg.get("gu_transcript", "")[:40]
        if not q:
            continue
        t = f"આજે, {datetime.datetime.now().strftime('%I:%M %p')}" if i == 0 else (
            "ગઈકાલ, 4:15 PM" if i == 1 else f"{i+1} દિ. પહેલ"
        )
        items_html += f"""<div class="history-item">
          <div class="history-item-q">{q}{'…' if len(msg.get('gu_transcript','')) > 40 else ''}</div>
          <div class="history-item-time">{t}</div>
          <div class="history-arrow">›</div>
        </div>"""
    return clean_html(f"<div>{items_html}</div>")


# ── Feature Footer ────────────────────────────────────────────────
def render_feature_footer() -> str:
    features = [
        ("➕", "Large Buttons"),
        ("🎤", "Voice First"),
        ("🇮🇳", "Local Language (Gujarati)"),
        ("📶", "Offline Support"),
        ("📱", "Mobile Responsive"),
        ("🌙", "Dark/Light Mode"),
        ("✨", "Simple Icons"),
    ]
    badges = "".join(
        f'<div class="feature-badge"><span class="feature-badge-icon">{i}</span><span>{l}</span></div>'
        for i, l in features
    )
    return clean_html(f'<div class="feature-footer">{badges}</div>')


# ── Legacy components (kept for full-page sections) ───────────────

def render_header(stt_status="Whisper-API", tts_status="Piper-TTS", llm_status="Qwen2.5-7B") -> str:
    return clean_html(f"""
<div style="border-bottom:1px solid var(--border-subtle);padding-bottom:0.75rem;margin-bottom:1rem;">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
    <div>
      <h1 style="font-family:'Space Grotesk',sans-serif;font-size:1.5rem;font-weight:700;
          color:var(--text-primary);margin:0 0 0.2rem 0;">ગુજરાતી કિસાન મિત્ર AI</h1>
      <p style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.78rem;
          color:var(--text-secondary);margin:0;">
        દસ્તાવેજ-આધારિત અવાજ ખેતી માર્ગદર્શક (Voice-Based PDF Agricultural Advisory)
      </p>
    </div>
    <div style="display:flex;align-items:center;gap:0.5rem;font-size:0.7rem;
        font-family:'JetBrains Mono',monospace;color:var(--text-secondary);">
      <span style="border:1px solid var(--border-subtle);background:var(--bg-surface);
          padding:0.2rem 0.55rem;border-radius:9999px;">● STT: {stt_status}</span>
      <span style="border:1px solid var(--border-subtle);background:var(--bg-surface);
          padding:0.2rem 0.55rem;border-radius:9999px;">● TTS: {tts_status}</span>
      <span style="border:1px solid var(--border-subtle);background:var(--bg-surface);
          padding:0.2rem 0.55rem;border-radius:9999px;">● LLM: {llm_status}</span>
    </div>
  </div>
</div>""")


def render_intent_pill(intent_name: str) -> str:
    return clean_html(f"""
<div style="display:inline-flex;align-items:center;gap:0.35rem;font-family:'JetBrains Mono',monospace;
    font-size:0.7rem;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;
    color:var(--accent);background:var(--accent-pale);border:1px solid var(--accent-light);
    padding:0.2rem 0.55rem;border-radius:9999px;margin-bottom:0.5rem;">
  {intent_name.upper()}
</div>""")


def render_source_chip(filename: str, page_number: int) -> str:
    return clean_html(f"""
<div style="display:inline-flex;align-items:center;gap:0.4rem;font-family:'JetBrains Mono',monospace;
    font-size:0.72rem;color:var(--text-secondary);background:var(--bg-primary);
    border:1px dashed var(--border-subtle);padding:0.3rem 0.65rem;border-radius:8px;margin-top:0.75rem;">
  📄 {filename} · p.{page_number}
</div>""")


def render_chat_bubble(message: str, is_user: bool = False,
                       intent: Optional[str] = None,
                       source_chip: Optional[Dict[str, Any]] = None) -> str:
    clean_msg = message.strip()
    if clean_msg.endswith("</div>"):
        clean_msg = clean_msg[:-6].strip()
    if is_user:
        return clean_html(f"""
<div style="display:flex;justify-content:flex-end;margin-bottom:1rem;">
  <div class="chat-bubble-user">{clean_msg}</div>
</div>""")
    else:
        intent_html = render_intent_pill(intent) if intent else ""
        chip_html   = render_source_chip(source_chip["filename"], source_chip["page_number"]) if source_chip else ""
        return clean_html(f"""
<div style="display:flex;justify-content:flex-start;margin-bottom:1.25rem;">
  <div class="chat-bubble-ai">
    {intent_html}
    <div style="margin-top:0.25rem;color:var(--text-primary);">{clean_msg}</div>
    {chip_html}
  </div>
</div>""")


def render_price_card(commodity_gu, commodity_en, modal_price, min_price, max_price,
                      district_gu, price_date, is_live=True) -> str:
    source_label = "લાઈવ APMC" if is_live else f"છેલ્લો ભાવ ({price_date})"
    return clean_html(f"""
<div class="kisaan-card" style="margin-bottom:1rem;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;
      border-bottom:1px solid var(--border-subtle);padding-bottom:0.75rem;margin-bottom:0.75rem;">
    <div>
      <div style="font-size:0.65rem;font-family:'JetBrains Mono',monospace;text-transform:uppercase;
          letter-spacing:0.06em;color:var(--text-muted);">APMC MANDI PRICE</div>
      <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:1.1rem;font-weight:700;
          color:var(--text-primary);">{commodity_gu} <span style="font-size:0.8rem;font-weight:400;
          color:var(--text-secondary);">({commodity_en})</span></div>
      <div style="font-size:0.75rem;color:var(--text-secondary);">{district_gu} · {price_date}</div>
    </div>
    <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;border:1px solid var(--border-subtle);
        background:var(--bg-elevated);padding:0.2rem 0.6rem;border-radius:9999px;
        color:var(--text-secondary);">{source_label}</span>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.5rem;text-align:center;">
    <div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:10px;padding:0.65rem;">
      <div style="font-size:0.6rem;font-family:'JetBrains Mono',monospace;text-transform:uppercase;
          color:var(--text-muted);">MIN</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;font-weight:700;
          color:var(--text-primary);">₹{min_price}</div>
    </div>
    <div style="background:var(--accent-pale);border:2px solid var(--accent);border-radius:10px;padding:0.65rem;">
      <div style="font-size:0.6rem;font-family:'JetBrains Mono',monospace;text-transform:uppercase;
          color:var(--accent);">MODAL</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.3rem;font-weight:800;
          color:var(--accent);">₹{modal_price}</div>
    </div>
    <div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:10px;padding:0.65rem;">
      <div style="font-size:0.6rem;font-family:'JetBrains Mono',monospace;text-transform:uppercase;
          color:var(--text-muted);">MAX</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;font-weight:700;
          color:var(--text-primary);">₹{max_price}</div>
    </div>
  </div>
</div>""")


def render_weather_card(district_gu, temp_c, condition_gu, humidity, wind_speed,
                        advisory_bullets, is_live=True) -> str:
    bullets_html = "".join(
        f"<li style='font-family:\"Noto Sans Gujarati\",sans-serif;font-size:0.88rem;"
        f"color:var(--text-primary);margin-bottom:0.4rem;'>• {b}</li>"
        for b in advisory_bullets
    )
    return clean_html(f"""
<div class="kisaan-card" style="margin-bottom:1rem;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;
      border-bottom:1px solid var(--border-subtle);padding-bottom:0.75rem;margin-bottom:0.75rem;">
    <div>
      <div style="font-size:0.65rem;font-family:'JetBrains Mono',monospace;text-transform:uppercase;
          letter-spacing:0.06em;color:var(--text-muted);">LIVE WEATHER ADVISORY</div>
      <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:1.1rem;font-weight:700;
          color:var(--text-primary);">{district_gu} જિલ્લો</div>
    </div>
    <div style="text-align:right;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:800;
          color:var(--text-primary);">{temp_c}°C</div>
      <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.72rem;
          color:var(--text-secondary);">{condition_gu}</div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-bottom:0.75rem;">
    <div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);
        border-radius:10px;padding:0.5rem;display:flex;justify-content:space-between;
        font-size:0.78rem;font-family:'JetBrains Mono',monospace;color:var(--text-secondary);">
      <span>ભેજ:</span><span style="font-weight:700;color:var(--text-primary);">{humidity}%</span>
    </div>
    <div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);
        border-radius:10px;padding:0.5rem;display:flex;justify-content:space-between;
        font-size:0.78rem;font-family:'JetBrains Mono',monospace;color:var(--text-secondary);">
      <span>પવન:</span><span style="font-weight:700;color:var(--text-primary);">{wind_speed} km/h</span>
    </div>
  </div>
  <div style="border-top:1px solid var(--border-subtle);padding-top:0.6rem;">
    <div style="font-size:0.62rem;font-family:'JetBrains Mono',monospace;text-transform:uppercase;
        letter-spacing:0.05em;color:var(--text-muted);margin-bottom:0.4rem;">ખેતી સલાહ</div>
    <ul style="list-style:none;padding:0;margin:0;">{bullets_html}</ul>
  </div>
</div>""")


def render_mic_button(is_recording: bool = False, elapsed_seconds: int = 0) -> str:
    label = f"રેકોર્ડ ({elapsed_seconds}s)…" if is_recording else "માઇક દબાવીને બોલો"
    status_class = "mic-button-recording" if is_recording else ""
    return clean_html(f"""
<div class="mic-container">
  <div class="mic-button-ring {status_class}">
    <svg xmlns="http://www.w3.org/2000/svg" style="height:2.2rem;width:2.2rem;" fill="none"
        viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
        d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
    </svg>
  </div>
  <p style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.9rem;font-weight:600;
      color:var(--text-primary);margin-top:0.6rem;">{label}</p>
</div>""")


def render_empty_state() -> str:
    return clean_html("""
<div class="kisaan-card" style="padding:2rem;text-align:center;margin:1rem 0;">
  <div style="width:60px;height:60px;margin:0 auto 0.75rem;border-radius:50%;
      background:var(--accent-pale);border:2px solid var(--accent-light);
      display:flex;align-items:center;justify-content:center;font-size:1.5rem;">🎤</div>
  <h3 style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;
      color:var(--text-primary);margin:0 0 0.4rem 0;">માઇક દબાવીને તમારો પ્રશ્ન પૂછો</h3>
  <p style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.85rem;
      color:var(--text-secondary);max-width:380px;margin:0 auto;line-height:1.65;">
    સરકારી યોજનાઓ, ખાતરનું પ્રમાણ, હવામાન અથવા આજના બજાર ભાવ વિશે ગુજરાતીમાં પૂછો.
  </p>
</div>""")


def render_loading_skeleton(current_stage: str = "સાંભળી રહ્યું છે…") -> str:
    return clean_html(f"""
<div class="kisaan-card" style="padding:1.25rem;margin:0.75rem 0;">
  <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
    <span style="width:10px;height:10px;border-radius:50%;background:var(--accent);
        display:inline-block;animation:pulse-ring 1s infinite;"></span>
    <span style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.88rem;font-weight:600;
        color:var(--text-primary);">{current_stage}</span>
  </div>
  <div style="margin-bottom:0.5rem;"><div class="skeleton-box" style="height:14px;width:75%;"></div></div>
  <div style="margin-bottom:0.5rem;"><div class="skeleton-box" style="height:14px;width:100%;"></div></div>
  <div><div class="skeleton-box" style="height:14px;width:85%;"></div></div>
</div>""")


def render_pipeline_trace(trace_data: Dict[str, Any]) -> str:
    sources_str = ", ".join(
        f"{s.get('filename')} (p.{s.get('page')})" for s in trace_data.get("sources", [])
    ) if trace_data.get("sources") else "N/A"
    return clean_html(f"""
<div class="trace-panel" style="margin-top:1.5rem;">
  <div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border-subtle);
      padding-bottom:0.5rem;margin-bottom:0.75rem;">
    <span style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
        letter-spacing:0.05em;color:var(--accent);">🔍 PIPELINE TRACE</span>
    <span style="font-size:0.65rem;color:var(--text-secondary);">
      LATENCY: {trace_data.get('total_latency_ms',0)}ms</span>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;font-size:0.78rem;">
    <div><div class="trace-label">1. GUJARATI (STT)</div>
      <div style="color:var(--text-primary);font-family:'Noto Sans Gujarati',sans-serif;">
        {trace_data.get('gu_transcript','N/A')}</div></div>
    <div><div class="trace-label">2. ENGLISH</div>
      <div style="color:var(--text-primary);">{trace_data.get('en_query','N/A')}</div></div>
    <div><div class="trace-label">3. INTENT</div>
      <div style="color:var(--text-primary);">{trace_data.get('intent','N/A')} ({trace_data.get('confidence','0.00')})</div></div>
    <div><div class="trace-label">4. SOURCES</div>
      <div style="color:var(--text-primary);">{sources_str}</div></div>
    <div style="grid-column:1/-1;"><div class="trace-label">5. FINAL GUJARATI ANSWER</div>
      <div style="color:var(--text-primary);font-family:'Noto Sans Gujarati',sans-serif;">
        {trace_data.get('gu_answer','N/A')}</div></div>
  </div>
</div>""")
