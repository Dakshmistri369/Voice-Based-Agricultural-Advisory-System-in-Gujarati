"""
Streamlit Layout Orchestrator for Gujarati Kisaan Mitra AI.
Handles dynamic dual-theme injection (Black & White) across the entire DOM including Sidebar.
"""

import pathlib
import textwrap
import streamlit as st
from ui.theme import normalize_theme_name, get_theme_dict, THEMES


def inject_theme_styles(theme: str = None):
    """
    Injects Tailwind CDN script, active theme CSS variables, and custom styles.css.
    Guarantees complete coverage across main container, sidebar, and native widgets.
    """
    if theme is None:
        theme = st.session_state.get("theme", "dark")

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
        --bg-primary: {tokens['bg_primary']} !important;
        --bg-surface: {tokens['bg_surface']} !important;
        --bg-elevated: {tokens['bg_elevated']} !important;
        --border-subtle: {tokens['border_subtle']} !important;
        --text-primary: {tokens['text_primary']} !important;
        --text-secondary: {tokens['text_secondary']} !important;
        --text-muted: {tokens['text_muted']} !important;
        --inverted-surface: {tokens['inverted_surface']} !important;
        --inverted-text: {tokens['inverted_text']} !important;
        --chip-bg: {tokens['chip_bg']} !important;
        --chip-text: {tokens['chip_text']} !important;
        --chip-border: {tokens['chip_border']} !important;
        --chip-active-bg: {tokens['chip_active_bg']} !important;
        --chip-active-text: {tokens['chip_active_text']} !important;
        --input-bg: {tokens['input_bg']} !important;
        --input-border: {tokens['input_border']} !important;
        --input-text: {tokens['input_text']} !important;
        --input-placeholder: {tokens['input_placeholder']} !important;
        --shadow: {tokens['shadow']} !important;
        --mic-ring-shadow: {tokens['mic_ring_shadow']} !important;
        --skeleton-start: {tokens.get('skeleton_start', tokens['bg_surface'])} !important;
        --skeleton-mid: {tokens.get('skeleton_mid', tokens['bg_elevated'])} !important;

        /* Backwards-compatible Aliases */
        --bg-base: {tokens['bg_primary']} !important;
        --border-hairline: {tokens['border_subtle']} !important;
        --bg-inverted: {tokens['inverted_surface']} !important;
        --text-inverted: {tokens['inverted_text']} !important;
        --card-shadow: {tokens['shadow']} !important;
    }}

    /* Global element background and color enforcement */
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
        min-width: 280px !important;
        max-width: 320px !important;
        width: 280px !important;
        transform: none !important;
        margin-left: 0 !important;
        background-color: {tokens['bg_surface']} !important;
        color: {tokens['text_primary']} !important;
        border-right: 1px solid {tokens['border_subtle']} !important;
    }}
    """

    html_code = textwrap.dedent(f"""
<script src="https://cdn.tailwindcss.com"></script>
<script>
  try {{
    /* Set data-theme on every major scope immediately */
    var _t = '{theme_key}';
    document.documentElement.setAttribute('data-theme', _t);
    if (document.body) document.body.setAttribute('data-theme', _t);
    /* Poll for Streamlit elements to set attribute once they mount */
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
    /* Helper to toggle Streamlit sidebar */
    window.openStreamlitSidebar = function() {{
      var btn = document.querySelector('[data-testid="collapsedControl"] button') ||
                document.querySelector('[data-testid="collapsedControl"]') ||
                document.querySelector('button[aria-label="Expand sidebar"]') ||
                document.querySelector('button[data-testid="stSidebarCollapseButton"]');
      if (btn) {{
        btn.click();
      }}
    }};
    /* MutationObserver keeps newly injected elements themed */
    if (window.MutationObserver) {{
      new MutationObserver(_applyTheme).observe(document.body,
        {{childList: true, subtree: true}});
    }}
  }} catch(e) {{}}
  tailwind.config = {{
    theme: {{
      extend: {{
        colors: {{
          'kisaan-bg': '{tokens['bg_primary']}',
          'kisaan-surface': '{tokens['bg_surface']}',
          'kisaan-elevated': '{tokens['bg_elevated']}',
          'kisaan-border': '{tokens['border_subtle']}',
          'kisaan-primary': '{tokens['text_primary']}',
          'kisaan-secondary': '{tokens['text_secondary']}',
          'kisaan-muted': '{tokens['text_muted']}'
        }},
        fontFamily: {{
          'heading': ['Space Grotesk', 'sans-serif'],
          'body': ['Inter', 'sans-serif'],
          'gujarati': ['Noto Sans Gujarati', 'Hind Vadodara', 'sans-serif'],
          'mono': ['JetBrains Mono', 'monospace']
        }}
      }}
    }}
  }}
</script>
<style>
{local_css}
{dynamic_vars}
</style>
""").strip()

    st.markdown(html_code, unsafe_allow_html=True)
