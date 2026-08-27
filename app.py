"""
ગુજરાતી કિસાન મિત્ર AI — Main Streamlit Orchestrator
Green-themed 9-panel dashboard. All section logic lives in ui/sections/*.
"""

import sys
from pathlib import Path
import streamlit as st

# Force UTF-8 on Windows and add root to sys.path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ui.layout import inject_theme_styles
from ui.navigation import render_sidebar_nav
from ui.sections.home import render_home_section
from ui.sections.schemes import render_schemes_section
from ui.sections.weather import render_weather_section
from ui.sections.prices import render_prices_section
from ui.sections.crop_advisory import render_crop_advisory_section
from ui.sections.disease import render_disease_section
from ui.sections.soil_test import render_soil_test_section
from ui.sections.history import render_history_section

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="ગુજરાતી કિસાન મિત્ર AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State Initialisation ──────────────────────────────────
defaults = {
    "theme":             "green",
    "active_section":    "home",
    "selected_district": "રાજકોટ",
    "messages":          [],
    "last_trace":        None,
    "show_trace":        False,
    "prefill_query":     None,
    "selected_crop":     "groundnut",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Global CSS / Theme ────────────────────────────────────────────
inject_theme_styles(st.session_state.get("theme", "green"))

# ── Sidebar Navigation ────────────────────────────────────────────
with st.sidebar:
    render_sidebar_nav()

# ── Section Titles ────────────────────────────────────────────────
SECTION_TITLES = {
    "home":          "🏠 હોમ",
    "schemes":       "📄 સરકારી યોજના",
    "weather":       "🌤️ હવામાન",
    "prices":        "💰 બજાર ભાવ",
    "crop_advisory": "🌱 પાક સલાહ",
    "disease":       "🔬 સ્થાનિક નિષ્ણાત",
    "soil_test":     "🧪 માટી તપાસ",
    "history":       "📖 ઇતિહાસ",
}

# ── Top Bar (breadcrumb + theme toggle) ───────────────────────────
current_section = st.session_state.get("active_section", "home")
from ui.theme import normalize_theme_name
current_theme = normalize_theme_name(st.session_state.get("theme", "green"))
theme_labels = {"green": "🌙 Dark", "dark": "☀️ White", "light": "🌿 Green"}
next_themes  = {"green": "dark",    "dark": "light",     "light": "green"}
theme_btn_lbl = theme_labels.get(current_theme, "🌿 Green")
next_theme    = next_themes.get(current_theme, "green")

if current_section != "home":
    top_back_col, top_bread_col, top_theme_col = st.columns([1.8, 3.5, 1.2])
    with top_back_col:
        if st.button("← હોમ પર પાછા ફરો", key="top_back_home_btn",
                     help="મુખ્ય પૃષ્ઠ પર પાછા", use_container_width=True):
            st.session_state["active_section"] = "home"
            st.rerun()
    with top_bread_col:
        curr_title = SECTION_TITLES.get(current_section, current_section)
        st.markdown(
            f'<div style="display:flex;align-items:center;height:100%;padding:0.4rem 0.6rem;'
            f'font-family:Inter,sans-serif;font-size:0.85rem;color:var(--text-secondary);">'
            f'<span>🏠 હોમ</span>'
            f'<span style="margin:0 0.5rem;color:var(--text-muted);">›</span>'
            f'<span style="font-weight:600;color:var(--text-primary);">{curr_title}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with top_theme_col:
        if st.button(theme_btn_lbl, key="corner_theme_toggle_btn",
                     help="થીમ બદલો", use_container_width=True):
            st.session_state["theme"] = next_theme
            st.rerun()
else:
    top_spacer, top_theme_col = st.columns([5, 1.2])
    with top_theme_col:
        if st.button(theme_btn_lbl, key="corner_theme_toggle_btn",
                     help="થીમ બદલો", use_container_width=True):
            st.session_state["theme"] = next_theme
            st.rerun()

st.markdown(
    '<div style="height:1px;background:var(--border-subtle);margin:0.2rem 0 0.6rem 0;"></div>',
    unsafe_allow_html=True
)

# ── Section Router ────────────────────────────────────────────────
section = st.session_state.get("active_section", "home")

if section == "home":
    # Handle cross-section prefill_query
    if st.session_state.get("prefill_query"):
        pq = st.session_state.pop("prefill_query")
        from pipeline import pipeline
        with st.spinner("જવાબ તૈયાર…"):
            result = pipeline.process_query(
                text_query=pq,
                selected_district=st.session_state["selected_district"]
            )
            if result.get("success"):
                st.session_state["messages"].append({
                    "gu_transcript":      result["gu_transcript"],
                    "gu_answer":          result["gu_answer"],
                    "intent":             result["intent"],
                    "sources":            result["sources"],
                    "price_card_data":    result.get("price_card_data"),
                    "weather_card_data":  result.get("weather_card_data"),
                    "audio_bytes":        result.get("audio_bytes"),
                    "trace_data":         result.get("trace_data"),
                })
                st.session_state["last_trace"] = result.get("trace_data")
    render_home_section()

elif section == "schemes":
    render_schemes_section()

elif section == "weather":
    render_weather_section()

elif section == "prices":
    render_prices_section()

elif section == "crop_advisory":
    render_crop_advisory_section()

elif section == "disease":
    render_disease_section()

elif section == "soil_test":
    render_soil_test_section()

elif section == "history":
    render_history_section()

else:
    render_home_section()
