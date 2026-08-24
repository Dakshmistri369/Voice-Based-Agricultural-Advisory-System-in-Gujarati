"""
ગુજરાતી કિસાન મિત્ર AI — Main Streamlit Orchestrator (Phase 10.5 Refactor)
Multi-section navigation shell. All section logic lives in ui/sections/*.
Supports dynamic Black & White theme switching via corner button.
"""

import sys
from pathlib import Path
import streamlit as st

# Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ui.layout import inject_theme_styles
from ui.navigation import render_sidebar_nav
from ui.sections.home import render_home_section
from ui.sections.schemes import render_schemes_section
from ui.sections.weather import render_weather_section
from ui.sections.prices import render_prices_section
from ui.sections.crop_advisory import render_crop_advisory_section
from ui.sections.disease import render_disease_section

# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="ગુજરાતી કિસાન મિત્ર AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State Initialisation ─────────────────────────
defaults = {
    "theme":            "dark",
    "active_section":   "home",
    "selected_district":"રાજકોટ",
    "messages":         [],
    "last_trace":       None,
    "show_trace":       True,
    "prefill_query":    None,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Global CSS / Theme ────────────────────────────────────
inject_theme_styles(st.session_state.get("theme", "dark"))

# ── Top Corner Bar: Theme Switcher ────────────────────────
current_theme = st.session_state.get("theme", "dark")
is_dark = current_theme == "dark"
# Use unique labels so CSS ::before can inject proper SVG icons
theme_label = "theme-to-white" if is_dark else "theme-to-black"
theme_help = "વ્હાઇટ (લાઇટ) થીમ પસંદ કરો" if is_dark else "બ્લેક (ડાર્ક) થીમ પસંદ કરો"
theme_display = "White Mode" if is_dark else "Black Mode"

top_spacer, top_theme_col = st.columns([5, 1.4])
with top_theme_col:
    if st.button(theme_display, key="corner_theme_toggle_btn", help=theme_help, use_container_width=True):
        st.session_state["theme"] = "light" if is_dark else "dark"
        st.rerun()

# ── Sidebar Navigation ────────────────────────────────────
with st.sidebar:
    render_sidebar_nav()

# ── Section Router ────────────────────────────────────────
section = st.session_state.get("active_section", "home")

if section == "home":
    # Handle cross-section prefill_query (from Prices / Schemes / Crop)
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

else:
    render_home_section()
