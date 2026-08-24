"""
Design System Theme Tokens and Generators for Gujarati Kisaan Mitra AI.
Single Source of Truth for Dual Monochrome Aesthetic: Black (Dark) & White (Light) Themes.
"""

from typing import Dict, Any

# ── Dark Theme Tokens (Black) ─────────────────────────────────
DARK_TOKENS = {
    "bg_primary":        "#000000",
    "bg_surface":        "#0D0D0D",
    "bg_elevated":       "#1A1A1A",
    "border_subtle":     "#2E2E2E",
    "text_primary":      "#FFFFFF",
    "text_secondary":    "#A3A3A3",
    "text_muted":        "#6B6B6B",
    "inverted_surface":  "#FFFFFF",
    "inverted_text":     "#000000",
    "chip_bg":           "#1A1A1A",
    "chip_text":         "#FFFFFF",
    "chip_border":       "#2E2E2E",
    "chip_active_bg":    "#FFFFFF",
    "chip_active_text":  "#000000",
    "input_bg":          "#0D0D0D",
    "input_border":      "#2E2E2E",
    "input_text":        "#FFFFFF",
    "input_placeholder": "#6B6B6B",
    "shadow":            "none",
    "mic_ring_shadow":   "rgba(255, 255, 255, 0.4)",
}

# ── Light Theme Tokens (White) ────────────────────────────────
LIGHT_TOKENS = {
    "bg_primary":        "#FFFFFF",
    "bg_surface":        "#F7F7F7",
    "bg_elevated":       "#FFFFFF",
    "border_subtle":     "#E0E0E0",
    "text_primary":      "#000000",
    "text_secondary":    "#4A4A4A",
    "text_muted":        "#7A7A7A",
    "inverted_surface":  "#000000",
    "inverted_text":     "#FFFFFF",
    "chip_bg":           "#F0F0F0",
    "chip_text":         "#000000",
    "chip_border":       "#D8D8D8",
    "chip_active_bg":    "#000000",
    "chip_active_text":  "#FFFFFF",
    "input_bg":          "#FFFFFF",
    "input_border":      "#D0D0D0",
    "input_text":        "#000000",
    "input_placeholder": "#8A8A8A",
    "shadow":            "0 1px 3px rgba(0, 0, 0, 0.08)",
    "mic_ring_shadow":   "rgba(0, 0, 0, 0.25)",
}

# Typography Families
FONT_HEADING = "'Space Grotesk', sans-serif"
FONT_BODY = "'Inter', sans-serif"
FONT_GUJARATI = "'Noto Sans Gujarati', 'Hind Vadodara', sans-serif"
FONT_MONO = "'JetBrains Mono', monospace"

THEMES: Dict[str, Dict[str, Any]] = {
    "dark": {
        "id": "dark",
        "name": "black",
        "label": "બ્લેક થીમ",
        "english_label": "Black Theme",
        "toggle_label": "☀️ વ્હાઇટ થીમ",
        "icon": "🌙",
        "target": "light",
        **DARK_TOKENS,
        # Aliases for backwards compatibility
        "bg_base": DARK_TOKENS["bg_primary"],
        "border_hairline": DARK_TOKENS["border_subtle"],
        "bg_inverted": DARK_TOKENS["inverted_surface"],
        "text_inverted": DARK_TOKENS["inverted_text"],
        "card_shadow": DARK_TOKENS["shadow"],
    },
    "light": {
        "id": "light",
        "name": "white",
        "label": "વ્હાઇટ થીમ",
        "english_label": "White Theme",
        "toggle_label": "🌙 બ્લેક થીમ",
        "icon": "☀️",
        "target": "dark",
        **LIGHT_TOKENS,
        # Aliases for backwards compatibility
        "bg_base": LIGHT_TOKENS["bg_primary"],
        "border_hairline": LIGHT_TOKENS["border_subtle"],
        "bg_inverted": LIGHT_TOKENS["inverted_surface"],
        "text_inverted": LIGHT_TOKENS["inverted_text"],
        "card_shadow": LIGHT_TOKENS["shadow"],
    }
}


def normalize_theme_name(theme: str) -> str:
    """Normalizes theme names: 'white' -> 'light', 'black' -> 'dark'."""
    t = (theme or "dark").lower().strip()
    if t in ("white", "light"):
        return "light"
    return "dark"


def get_theme_dict(theme_name: str = "dark") -> Dict[str, str]:
    """Returns all design system tokens for the specified theme."""
    key = normalize_theme_name(theme_name)
    tokens = THEMES[key]
    return {
        "bg_primary": tokens["bg_primary"],
        "bg_surface": tokens["bg_surface"],
        "bg_elevated": tokens["bg_elevated"],
        "border_subtle": tokens["border_subtle"],
        "text_primary": tokens["text_primary"],
        "text_secondary": tokens["text_secondary"],
        "text_muted": tokens["text_muted"],
        "inverted_surface": tokens["inverted_surface"],
        "inverted_text": tokens["inverted_text"],
        "chip_bg": tokens["chip_bg"],
        "chip_text": tokens["chip_text"],
        "chip_border": tokens["chip_border"],
        "chip_active_bg": tokens["chip_active_bg"],
        "chip_active_text": tokens["chip_active_text"],
        "input_bg": tokens["input_bg"],
        "input_border": tokens["input_border"],
        "input_text": tokens["input_text"],
        "input_placeholder": tokens["input_placeholder"],
        "shadow": tokens["shadow"],
        "mic_ring_shadow": tokens["mic_ring_shadow"],
        # Aliases
        "bg_base": tokens["bg_base"],
        "border_hairline": tokens["border_hairline"],
        "bg_inverted": tokens["bg_inverted"],
        "text_inverted": tokens["text_inverted"],
        "card_shadow": tokens["card_shadow"],
        "font_heading": FONT_HEADING,
        "font_body": FONT_BODY,
        "font_gujarati": FONT_GUJARATI,
        "font_mono": FONT_MONO,
    }
