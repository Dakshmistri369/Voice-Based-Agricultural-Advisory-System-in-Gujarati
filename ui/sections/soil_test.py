"""
Soil Test Section for Gujarati Kisaan Mitra AI.
Shows pH, N/P/K nutrient values and fertilizer recommendations per district.
Uses static/fallback data (no external soil API).
"""

import streamlit as st
from ui.components import clean_html

# Static district-based soil data (representative values for Gujarat districts)
DISTRICT_SOIL_DATA = {
    "default": {"ph": 7.2, "n": "મધ્યમ", "p": "ઓછું", "k": "સારો",
                "recs": ["યુરિયા 50 કિ./હ.", "DAP 40 કિ./હ.", "MOP 20 કિ./હ."]},
    "રાજકોટ":  {"ph": 7.4, "n": "મધ્યમ", "p": "ઓછું", "k": "સારો",
                "recs": ["યુરિયા 50 કિ./હ.", "DAP 40 કિ./હ.", "MOP 20 કિ./હ."]},
    "અમદાવાદ": {"ph": 7.8, "n": "ઓછું", "p": "ઓછું", "k": "મધ્યમ",
                "recs": ["યુરિયા 60 કિ./હ.", "SSP 60 કિ./હ.", "MOP 25 કિ./હ."]},
    "જૂનાગઢ":  {"ph": 6.9, "n": "સારો", "p": "મધ્યમ", "k": "સારો",
                "recs": ["યુરિયા 30 કિ./હ.", "DAP 20 કિ./હ.", "MOP 15 કિ./હ."]},
    "અમરેલી":  {"ph": 7.1, "n": "મધ્યમ", "p": "ઓછું", "k": "સારો",
                "recs": ["યુરિયા 50 કિ./હ.", "DAP 40 કિ./હ.", "MOP 20 કિ./હ."]},
    "સુરત":    {"ph": 6.5, "n": "સારો", "p": "સારો", "k": "ઓછું",
                "recs": ["MOP 40 કિ./હ.", "Borax 2 કિ./હ.", "Zinc Sulphate 10 કિ./હ."]},
    "ભાવનગર":  {"ph": 7.6, "n": "ઓછું", "p": "ઓછું", "k": "સારો",
                "recs": ["યુરિયા 70 કિ./હ.", "DAP 50 કિ./હ.", "MOP 20 કિ./હ."]},
    "જામનગર":  {"ph": 7.3, "n": "મધ્યમ", "p": "ઓછું", "k": "સારો",
                "recs": ["યુરિયા 50 કિ./હ.", "SSP 50 કિ./હ.", "MOP 20 કિ./હ."]},
    "કચ્છ":    {"ph": 8.1, "n": "ઓછું", "p": "ઓછું", "k": "મધ્યમ",
                "recs": ["FYM 10 ટ./હ.", "DAP 60 કિ./હ.", "Gypsum 400 કિ./હ."]},
    "ગાંધીનગર":{"ph": 7.5, "n": "મધ્યમ", "p": "ઓછું", "k": "સારો",
                "recs": ["યુરિયા 50 કિ./હ.", "DAP 40 કિ./હ.", "MOP 20 કિ./હ."]},
}

LEVEL_COLORS = {
    "સારો":   "#16A34A",
    "મધ્યમ":  "#D97706",
    "ઓછું":   "#DC2626",
}


def render_soil_test_section():
    """Full Soil Test section with district selector and NPK cards."""
    district = st.session_state.get("selected_district", "રાજકોટ")

    # ── Section Header ─────────────────────────────────
    st.markdown(clean_html(f"""
<div class="section-header">
  <h2>🧪 માટી તપાસ (Soil Test)</h2>
  <p>ગુજરાત જિલ્લા મુજબ NPK અને pH ના આધારિત ખાતર સૂચન</p>
</div>"""), unsafe_allow_html=True)

    # ── District Override ──────────────────────────────
    from ui.navigation import DISTRICTS
    override = st.selectbox(
        "જિલ્લો પસંદ કરો:",
        DISTRICTS,
        index=DISTRICTS.index(district) if district in DISTRICTS else 0,
        key="soil_district_override"
    )
    if override != district:
        st.session_state["selected_district"] = override
        district = override

    soil = DISTRICT_SOIL_DATA.get(district, DISTRICT_SOIL_DATA["default"])

    # ── Hero Stats Row ──────────────────────────────────
    col_ph, col_n, col_p, col_k = st.columns(4)

    def _stat_card(col, label_top, label_small, value, sub, color=None):
        col.markdown(clean_html(f"""
<div class="stat-card" style="text-align:center;">
  <div class="stat-card-label">{label_top}</div>
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.6rem;
      color:var(--text-muted);margin-bottom:0.2rem;">{label_small}</div>
  <div class="stat-card-value" style="font-size:1.6rem;
      {'color:'+color+';' if color else ''}">
    {value}
  </div>
  <div class="stat-card-unit">{sub}</div>
</div>"""), unsafe_allow_html=True)

    ph_color = "#16A34A" if 6.5 <= soil["ph"] <= 7.5 else ("#D97706" if soil["ph"] <= 8.0 else "#DC2626")
    _stat_card(col_ph, "pH", "ઍસિડ/બેઝ", soil["ph"], "સ્તર", ph_color)
    _stat_card(col_n, "નાઇટ્રોજન (N)", "", soil["n"], "સ્તર", LEVEL_COLORS.get(soil["n"]))
    _stat_card(col_p, "ફોસ્ફરસ (P)", "", soil["p"], "સ્તર", LEVEL_COLORS.get(soil["p"]))
    _stat_card(col_k, "પોટાસ (K)", "", soil["k"], "સ્તર", LEVEL_COLORS.get(soil["k"]))

    st.markdown('<div style="height:0.75rem;"></div>', unsafe_allow_html=True)

    # ── Two columns: recommendations + image ───────────
    col_rec, col_img = st.columns([3, 2])

    with col_rec:
        recs_html = "".join(
            f'<div class="soil-rec-bullet">{r}</div>' for r in soil["recs"]
        )
        st.markdown(clean_html(f"""
<div class="kisaan-card">
  <div class="crop-subsection-header">🌿 ખાતર સૂચન (Fertilizer Recommendations)</div>
  {recs_html}
  <div style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid var(--border-subtle);">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;text-transform:uppercase;
        letter-spacing:0.05em;color:var(--text-muted);margin-bottom:0.4rem;">⚠️ સૂચના</div>
    <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.8rem;
        color:var(--text-secondary);line-height:1.65;">
      ઉપરોક્ત સૂચન અંદાજિત છે. ચોક્કસ ખાતર માટે કૃષિ અધિકારી પાસે
      વ્યક્તિગત માટી પ્રયોગશાળા (Soil Testing Laboratory) નો ઉપયોગ કરો.
    </div>
  </div>
</div>"""), unsafe_allow_html=True)

    with col_img:
        st.markdown(clean_html(f"""
<div class="kisaan-card" style="text-align:center;">
  <div style="font-size:4rem;margin-bottom:0.5rem;">🌍</div>
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.88rem;font-weight:700;
      color:var(--text-primary);margin-bottom:0.25rem;">{district} જિલ્લો</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;text-transform:uppercase;
      letter-spacing:0.05em;color:var(--text-muted);">Gujarat Black/Alluvial Soil</div>
  <div style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid var(--border-subtle);">
    <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.78rem;
        color:var(--text-secondary);">
      માટી ઉઠાવ: 0-30 સે.મી. ઊંડાઈ
    </div>
  </div>
</div>"""), unsafe_allow_html=True)

    # ── Interpretation Guide ───────────────────────────
    st.markdown(clean_html("""
<div class="kisaan-card" style="margin-top:0.5rem;">
  <div class="crop-subsection-header">📊 સ્તર અર્થઘટન (Level Interpretation)</div>
  <div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-top:0.4rem;">
    <div style="display:flex;align-items:center;gap:0.4rem;">
      <span style="width:10px;height:10px;border-radius:50%;background:#16A34A;display:inline-block;"></span>
      <span style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.8rem;color:var(--text-primary);">
        <strong>સારો</strong> — ઉચ્ચ સ્તર, ઓછા ખાતરની જરૂર
      </span>
    </div>
    <div style="display:flex;align-items:center;gap:0.4rem;">
      <span style="width:10px;height:10px;border-radius:50%;background:#D97706;display:inline-block;"></span>
      <span style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.8rem;color:var(--text-primary);">
        <strong>મધ્યમ</strong> — સામાન્ય ખાતરની જરૂર
      </span>
    </div>
    <div style="display:flex;align-items:center;gap:0.4rem;">
      <span style="width:10px;height:10px;border-radius:50%;background:#DC2626;display:inline-block;"></span>
      <span style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.8rem;color:var(--text-primary);">
        <strong>ઓછું</strong> — ખાતર ઉમેરવું ફરજિયાત
      </span>
    </div>
  </div>
</div>"""), unsafe_allow_html=True)

    # ── CTA ────────────────────────────────────────────
    if st.button("🎤 માટી સુધારણા વિશે AI ને પૂછો", key="soil_ask_ai_btn", use_container_width=True):
        st.session_state["active_section"] = "home"
        st.session_state["prefill_query"] = f"{district} માં {soil['n']} નાઇટ્રોજન માટે ખાતર સૂચન?"
        st.rerun()
