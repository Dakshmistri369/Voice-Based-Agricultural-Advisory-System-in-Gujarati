"""
Streamlit Layout Orchestrator for Gujarati Kisaan Mitra AI.
Handles dynamic theme injection (Green / Dark / Light) across the DOM including Sidebar.
"""

import pathlib
import textwrap
import streamlit as st
from ui.theme import normalize_theme_name, get_theme_dict, THEMES


def inject_theme_styles(theme: str = None):
    """
    Injects Google Fonts, active theme CSS variables, and custom styles.css.
    Guarantees complete coverage across main container, sidebar, and native widgets.
    """
    if theme is None:
        theme = st.session_state.get("theme", "green")

    theme_key = normalize_theme_name(theme)
    tokens = THEMES[theme_key]

    css_path = pathlib.Path(__file__).resolve().parent.parent / "assets" / "styles.css"
    local_css = ""
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            local_css = f.read()

    # Dynamic CSS variable overrides targeting every scope
    dynamic_vars = f"""
    :root,
    html,
    body,
    [data-testid="stAppViewContainer"],
    .stApp,
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    .main {{
        --bg-primary:         {tokens['bg_primary']} !important;
        --bg-surface:         {tokens['bg_surface']} !important;
        --bg-elevated:        {tokens['bg_elevated']} !important;
        --bg-sidebar:         {tokens['bg_sidebar']} !important;
        --bg-sidebar-item:    {tokens['bg_sidebar_item']} !important;
        --border-subtle:      {tokens['border_subtle']} !important;
        --text-primary:       {tokens['text_primary']} !important;
        --text-secondary:     {tokens['text_secondary']} !important;
        --text-muted:         {tokens['text_muted']} !important;
        --text-sidebar:       {tokens['text_sidebar']} !important;
        --text-sidebar-muted: {tokens['text_sidebar_muted']} !important;
        --inverted-surface:   {tokens['inverted_surface']} !important;
        --inverted-text:      {tokens['inverted_text']} !important;
        --accent:             {tokens['accent']} !important;
        --accent-light:       {tokens['accent_light']} !important;
        --accent-pale:        {tokens['accent_pale']} !important;
        --accent-hover:       {tokens['accent_hover']} !important;
        --alert-orange:       {tokens['alert_orange']} !important;
        --alert-bg:           {tokens['alert_bg']} !important;
        --chip-bg:            {tokens['chip_bg']} !important;
        --chip-text:          {tokens['chip_text']} !important;
        --chip-border:        {tokens['chip_border']} !important;
        --chip-active-bg:     {tokens['chip_active_bg']} !important;
        --chip-active-text:   {tokens['chip_active_text']} !important;
        --input-bg:           {tokens['input_bg']} !important;
        --input-border:       {tokens['input_border']} !important;
        --input-text:         {tokens['input_text']} !important;
        --input-placeholder:  {tokens['input_placeholder']} !important;
        --shadow:             {tokens['shadow']} !important;
        --mic-ring-shadow:    {tokens['mic_ring_shadow']} !important;
        --skeleton-start:     {tokens['skeleton_start']} !important;
        --skeleton-mid:       {tokens['skeleton_mid']} !important;
        --price-up:           {tokens['price_up']} !important;
        --price-down:         {tokens['price_down']} !important;
        /* Aliases */
        --bg-base:         {tokens['bg_primary']} !important;
        --border-hairline: {tokens['border_subtle']} !important;
        --bg-inverted:     {tokens['inverted_surface']} !important;
        --text-inverted:   {tokens['inverted_text']} !important;
        --card-shadow:     {tokens['shadow']} !important;
    }}

    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: {tokens['bg_primary']} !important;
        color: {tokens['text_primary']} !important;
    }}

    section[data-testid="stSidebar"],
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {{
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        min-width: 230px !important;
        max-width: 260px !important;
        width: 240px !important;
        transform: none !important;
        margin-left: 0 !important;
        background-color: {tokens['bg_sidebar']} !important;
        color: {tokens['text_sidebar']} !important;
        border-right: none !important;
    }}
    """

    html_code = textwrap.dedent(f"""
<script>
  try {{
    var _t = '{theme_key}';
    document.documentElement.setAttribute('data-theme', _t);
    if (document.body) document.body.setAttribute('data-theme', _t);
    function _applyTheme() {{
      var selectors = ['.stApp', '[data-testid="stAppViewContainer"]',
                       '[data-testid="stSidebar"]', '.main', '.block-container'];
      selectors.forEach(function(s) {{
        var el = document.querySelector(s);
        if (el) el.setAttribute('data-theme', _t);
      }});
    }}
    _applyTheme();
    setTimeout(_applyTheme, 100);
    setTimeout(_applyTheme, 500);
    setTimeout(_applyTheme, 1500);
    window.openStreamlitSidebar = function() {{
      var btn = document.querySelector('[data-testid="collapsedControl"] button') ||
                document.querySelector('[data-testid="collapsedControl"]') ||
                document.querySelector('button[aria-label="Expand sidebar"]');
      if (btn) btn.click();
    }};
    if (window.MutationObserver) {{
      new MutationObserver(_applyTheme).observe(document.body,
        {{childList: true, subtree: true}});
    }}
  }} catch(e) {{}}
</script>
<style>
{local_css}
{dynamic_vars}
</style>
""").strip()

    st.markdown(html_code, unsafe_allow_html=True)
