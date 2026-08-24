"""
Sidebar Navigation Builder for Gujarati Kisaan Mitra AI.
Renders wordmark, styled nav-item buttons, theme toggle, and collapsible Settings expander.
"""

import streamlit as st
from typing import Callable
from ui.components import clean_html
from ingest_pdfs import run_pdf_ingestion
from config import settings
from ui.theme import normalize_theme_name


NAV_ITEMS = [
    ("home",         "🏠", "હોમ / વોઇસ ચેટ"),
    ("schemes",      "📄", "સરકારી યોજનાઓ"),
    ("weather",      "☔", "હવામાન અને AQI"),
    ("prices",       "💰", "બજાર ભાવ (મંડી)"),
    ("crop_advisory","🌱", "પાક સલાહ"),
    ("disease",      "🐛", "રોગ ઓળખ (Beta)"),
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
    """Renders complete sidebar: wordmark + nav items + settings expander."""

    current_theme = normalize_theme_name(st.session_state.get("theme", "dark"))
    is_dark = current_theme == "dark"

    # ── Wordmark ──────────────────────────────────────
    st.markdown(clean_html("""
<div style="padding:0.25rem 0.25rem 0.75rem 0.25rem; margin-bottom:0.25rem;">
    <div style="font-family:'Space Grotesk',sans-serif; font-size:1rem; font-weight:700; color:var(--text-primary); letter-spacing:-0.01em;">
        ગુજરાતી કિસાન મિત્ર AI
    </div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em; margin-top:2px;">
        Voice-Based PDF Advisory
    </div>
</div>
<div style="height:1px; background:var(--border-subtle); margin:0 0 0.75rem 0;"></div>
"""), unsafe_allow_html=True)

    # ── Nav Item Buttons ───────────────────────────────
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

    # ── Hairline Divider ──────────────────────────────
    st.markdown('<div style="height:1px;background:var(--border-subtle);margin:0.75rem 0;"></div>', unsafe_allow_html=True)

    # ── Settings Expander ─────────────────────────────
    with st.expander("⚙️  સેટિંગ્સ (Settings)", expanded=False):

        # Theme selector in settings as well
        theme_options = ["🌙 ડાર્ક / બ્લેક (Black)", "☀️ લાઇટ / વ્હાઇટ (White)"]
        current_theme_idx = 0 if is_dark else 1
        selected_theme_label = st.selectbox(
            "થીમ પસંદ કરો (Theme):",
            options=theme_options,
            index=current_theme_idx,
            key="settings_theme_selector"
        )
        new_theme_mode = "dark" if "ડાર્ક" in selected_theme_label or "Black" in selected_theme_label else "light"
        if new_theme_mode != current_theme:
            st.session_state["theme"] = new_theme_mode
            st.rerun()

        # Global district selector (single source of truth)
        current_district = st.session_state.get("selected_district", "રાજકોટ")
        district_idx = DISTRICTS.index(current_district) if current_district in DISTRICTS else 0
        new_district = st.selectbox(
            "જિલ્લો પસંદ કરો",
            options=DISTRICTS,
            index=district_idx,
            key="district_selector"
        )
        if new_district != current_district:
            st.session_state["selected_district"] = new_district
            st.rerun()

        # Pipeline trace toggle
        st.session_state["show_trace"] = st.checkbox(
            "🔍 Pipeline Trace",
            value=st.session_state.get("show_trace", True),
            key="trace_toggle"
        )

        # Clear chat
        if st.button("🗑️  ચેટ સાફ કરો", use_container_width=True, key="clear_chat_btn"):
            st.session_state["messages"] = []
            st.session_state["last_trace"] = None
            st.rerun()

        st.markdown('<div style="height:1px;background:var(--border-subtle);margin:0.5rem 0;"></div>', unsafe_allow_html=True)
        st.markdown("<p style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin:0 0 0.5rem 0;'>Admin Actions</p>", unsafe_allow_html=True)

        admin_pin = st.text_input("અધિકૃત PIN", type="password", key="admin_pin_input")
        if st.button("🔄  Re-index Documents", use_container_width=True, key="reindex_btn"):
            if admin_pin == settings.ADMIN_PIN:
                with st.spinner("ઇન્ડેક્સ થઈ રહ્યું છે…"):
                    summary = run_pdf_ingestion()
                    st.success(f"✅ {summary.get('total_chunks', 0)} chunks ingested.")
            else:
                st.error("ખોટો PIN")

    # ── Footer Caption ────────────────────────────────
    st.markdown(
        '<p style="font-family:Inter,sans-serif;font-size:0.65rem;color:var(--text-muted);margin-top:1.5rem;text-align:center;">Phase 8 Integrated Voice Application</p>',
        unsafe_allow_html=True
    )
