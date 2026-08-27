"""
Sidebar Navigation Builder for Gujarati Kisaan Mitra AI.
Renders forest-green branded sidebar matching reference dashboard PNG.
Nav items: Home, Crop Advisory, Weather, Market Prices, Govt Schemes,
           Soil Test, Local Expert, History, Settings.
"""

import streamlit as st
from ui.components import clean_html
from ingest_pdfs import run_pdf_ingestion
from config import settings
from ui.theme import normalize_theme_name


NAV_ITEMS = [
    ("home",          "🏠", "હોમ"),
    ("crop_advisory", "🌱", "પાક સલાહ"),
    ("weather",       "🌤️", "હવામાન"),
    ("prices",        "💰", "બજાર ભાવ"),
    ("schemes",       "📄", "સરકારી યોજના"),
    ("soil_test",     "🧪", "માટી તપાસ"),
    ("disease",       "🔬", "સ્થાનિક નિષ્ણાત"),
    ("history",       "📖", "ઇતિહાસ"),
]

DISTRICTS = [
    "રાજકોટ", "અમદાવાદ", "જૂનાગઢ", "અમરેલી", "સુરત", "વડોદરા",
    "જામનગર", "ભાવનગર", "કચ્છ", "મહેસાણા", "ગાંધીનગર", "બનાસકાંઠા",
    "સાબરકાંઠા", "આણંદ", "ખેડા", "મોરબી", "પોરબંદર", "સુરેન્દ્રનગર",
    "પાટણ", "ભરૂચ", "નવસારી", "વલસાડ", "તાપી", "દાહોદ", "પંચમહાલ",
    "ડાંગ", "બોટાદ", "ગીર સોમનાથ", "દેવભૂમિ દ્વારકા", "મહિસાગર",
    "અરવલ્લી", "છોટા ઉદેપુર", "નર્મદા"
]


def render_sidebar_nav():
    """Renders complete sidebar: logo/wordmark + nav items + settings expander."""

    current_theme = normalize_theme_name(st.session_state.get("theme", "green"))

    # ── Logo / Wordmark ───────────────────────────────
    st.markdown(clean_html("""
<div style="padding:0.35rem 0.15rem 0.85rem 0.15rem; margin-bottom:0.1rem;">
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
        <div style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.15);display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;">🌾</div>
        <div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:0.88rem;font-weight:700;color:#FFFFFF;letter-spacing:-0.01em;line-height:1.1;">
                કિસાન મિત્ર AI
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:rgba(183,213,196,0.85);text-transform:uppercase;letter-spacing:0.06em;margin-top:1px;">
                Voice · PDF · Gujarati
            </div>
        </div>
    </div>
</div>
<div style="height:1px;background:rgba(255,255,255,0.12);margin:0 0 0.5rem 0;"></div>
"""), unsafe_allow_html=True)

    # ── Nav Item Buttons ──────────────────────────────
    active = st.session_state.get("active_section", "home")
    for section_id, icon, label in NAV_ITEMS:
        is_active = active == section_id
        wrapper_class = "nav-item-active" if is_active else "nav-item-idle"
        st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{section_id}",
            use_container_width=True
        ):
            st.session_state["active_section"] = section_id
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Divider ───────────────────────────────────────
    st.markdown(
        '<div style="height:1px;background:rgba(255,255,255,0.12);margin:0.6rem 0;"></div>',
        unsafe_allow_html=True
    )

    # ── Settings Expander ─────────────────────────────
    with st.expander("⚙️  સેટિંગ્સ", expanded=False):

        # Theme selector
        theme_options = ["🌿 ગ્રીન (Green)", "🌙 ડાર્ક (Dark)", "☀️ લાઇટ (Light)"]
        theme_map = {"🌿 ગ્રીન (Green)": "green", "🌙 ડાર્ક (Dark)": "dark", "☀️ લાઇટ (Light)": "light"}
        rev_map   = {"green": 0, "dark": 1, "light": 2}
        current_theme_idx = rev_map.get(current_theme, 0)
        selected_theme_label = st.selectbox(
            "થીમ:", options=theme_options, index=current_theme_idx, key="settings_theme_selector"
        )
        new_theme_mode = theme_map.get(selected_theme_label, "green")
        if new_theme_mode != current_theme:
            st.session_state["theme"] = new_theme_mode
            st.rerun()

        # District selector
        current_district = st.session_state.get("selected_district", "રાજકોટ")
        district_idx = DISTRICTS.index(current_district) if current_district in DISTRICTS else 0
        new_district = st.selectbox(
            "જિલ્લો:", options=DISTRICTS, index=district_idx, key="district_selector"
        )
        if new_district != current_district:
            st.session_state["selected_district"] = new_district
            st.rerun()

        # Pipeline trace toggle
        st.session_state["show_trace"] = st.checkbox(
            "🔍 Pipeline Trace",
            value=st.session_state.get("show_trace", False),
            key="trace_toggle"
        )

        # Clear chat
        if st.button("🗑️  ચેટ સાફ કરો", use_container_width=True, key="clear_chat_btn"):
            st.session_state["messages"] = []
            st.session_state["last_trace"] = None
            st.rerun()

        st.markdown(
            '<div style="height:1px;background:rgba(255,255,255,0.12);margin:0.5rem 0;"></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:rgba(183,213,196,0.7);"
            "text-transform:uppercase;letter-spacing:0.05em;margin:0 0 0.4rem 0;'>Admin</p>",
            unsafe_allow_html=True
        )
        admin_pin = st.text_input("PIN", type="password", key="admin_pin_input")
        if st.button("🔄  Re-index PDFs", use_container_width=True, key="reindex_btn"):
            if admin_pin == settings.ADMIN_PIN:
                with st.spinner("Indexing…"):
                    summary = run_pdf_ingestion()
                    st.success(f"✅ {summary.get('total_chunks', 0)} chunks indexed.")
            else:
                st.error("ખોટો PIN")

    # ── Footer ────────────────────────────────────────
    st.markdown(
        '<p style="font-family:JetBrains Mono,monospace;font-size:0.58rem;color:rgba(183,213,196,0.55);'
        'margin-top:1.2rem;text-align:center;text-transform:uppercase;letter-spacing:0.05em;">'
        'RAG · Voice · Phase 10.5</p>',
        unsafe_allow_html=True
    )
