"""
Design System Theme Tokens and Generators for Gujarati Kisaan Mitra AI.
Single Source of Truth for Three Themes: Green (default), Black (Dark), White (Light).
"""

from typing import Dict, Any

# ── Green Theme Tokens (default — matches reference PNG) ──────────
GREEN_TOKENS = {
    "bg_primary":        "#F0F4F0",
    "bg_surface":        "#FFFFFF",
    "bg_elevated":       "#F7FAF7",
    "bg_sidebar":        "#1B4332",
    "bg_sidebar_item":   "#2D6A4F",
    "border_subtle":     "#C8DDD0",
    "text_primary":      "#1A1A1A",
    "text_secondary":    "#4A5568",
    "text_muted":        "#718096",
    "text_sidebar":      "#FFFFFF",
    "text_sidebar_muted":"#B7D5C4",
    "inverted_surface":  "#1B4332",
    "inverted_text":     "#FFFFFF",
    "accent":            "#2D6A4F",
    "accent_light":      "#52B788",
    "accent_pale":       "#D8F3DC",
    "accent_hover":      "#1B4332",
    "alert_orange":      "#F97316",
    "alert_bg":          "#FFF7ED",
    "chip_bg":           "#D8F3DC",
    "chip_text":         "#1B4332",
    "chip_border":       "#95D5B2",
    "chip_active_bg":    "#1B4332",
    "chip_active_text":  "#FFFFFF",
    "input_bg":          "#FFFFFF",
    "input_border":      "#C8DDD0",
    "input_text":        "#1A1A1A",
    "input_placeholder": "#9CA3AF",
    "shadow":            "0 2px 8px rgba(27,67,50,0.10)",
    "mic_ring_shadow":   "rgba(27, 67, 50, 0.35)",
    "skeleton_start":    "#E8F0EA",
    "skeleton_mid":      "#D1E3D6",
    "price_up":          "#16A34A",
    "price_down":        "#DC2626",
}

# ── Dark Theme Tokens (Black) ─────────────────────────────────
DARK_TOKENS = {
    "bg_primary":        "#000000",
    "bg_surface":        "#0D0D0D",
    "bg_elevated":       "#1A1A1A",
    "bg_sidebar":        "#0D0D0D",
    "bg_sidebar_item":   "#1A1A1A",
    "border_subtle":     "#2E2E2E",
    "text_primary":      "#FFFFFF",
    "text_secondary":    "#A3A3A3",
    "text_muted":        "#6B6B6B",
    "text_sidebar":      "#FFFFFF",
    "text_sidebar_muted":"#6B6B6B",
    "inverted_surface":  "#FFFFFF",
    "inverted_text":     "#000000",
    "accent":            "#FFFFFF",
    "accent_light":      "#A3A3A3",
    "accent_pale":       "#1A1A1A",
    "accent_hover":      "#FFFFFF",
    "alert_orange":      "#F97316",
    "alert_bg":          "#1A0F00",
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
    "skeleton_start":    "#0D0D0D",
    "skeleton_mid":      "#1A1A1A",
    "price_up":          "#4ADE80",
    "price_down":        "#F87171",
}

# ── Light Theme Tokens (White) ────────────────────────────────
LIGHT_TOKENS = {
    "bg_primary":        "#FFFFFF",
    "bg_surface":        "#F7F7F7",
    "bg_elevated":       "#FFFFFF",
    "bg_sidebar":        "#F7F7F7",
    "bg_sidebar_item":   "#EFEFEF",
    "border_subtle":     "#E0E0E0",
    "text_primary":      "#000000",
    "text_secondary":    "#4A4A4A",
    "text_muted":        "#7A7A7A",
    "text_sidebar":      "#000000",
    "text_sidebar_muted":"#7A7A7A",
    "inverted_surface":  "#000000",
    "inverted_text":     "#FFFFFF",
    "accent":            "#000000",
    "accent_light":      "#4A4A4A",
    "accent_pale":       "#F0F0F0",
    "accent_hover":      "#000000",
    "alert_orange":      "#F97316",
    "alert_bg":          "#FFF7ED",
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
    "skeleton_start":    "#F0F0F0",
    "skeleton_mid":      "#E0E0E0",
    "price_up":          "#16A34A",
    "price_down":        "#DC2626",
}

# Typography Families
FONT_HEADING  = "'Space Grotesk', sans-serif"
FONT_BODY     = "'Inter', sans-serif"
FONT_GUJARATI = "'Noto Sans Gujarati', 'Hind Vadodara', sans-serif"
FONT_MONO     = "'JetBrains Mono', monospace"

THEMES: Dict[str, Dict[str, Any]] = {
    "green": {
        "id": "green",
        "name": "green",
        "label": "ગ્રીન થીમ",
        "english_label": "Green Theme",
        "toggle_label": "🌙 ડાર્ક થીમ",
        "icon": "🌿",
        "target": "dark",
        **GREEN_TOKENS,
        # Backwards-compatible aliases
        "bg_base":        GREEN_TOKENS["bg_primary"],
        "border_hairline":GREEN_TOKENS["border_subtle"],
        "bg_inverted":    GREEN_TOKENS["inverted_surface"],
        "text_inverted":  GREEN_TOKENS["inverted_text"],
        "card_shadow":    GREEN_TOKENS["shadow"],
    },
    "dark": {
        "id": "dark",
        "name": "black",
        "label": "બ્લેક થીમ",
        "english_label": "Black Theme",
        "toggle_label": "☀️ વ્હાઇટ થીમ",
        "icon": "🌙",
        "target": "light",
        **DARK_TOKENS,
        "bg_base":        DARK_TOKENS["bg_primary"],
        "border_hairline":DARK_TOKENS["border_subtle"],
        "bg_inverted":    DARK_TOKENS["inverted_surface"],
        "text_inverted":  DARK_TOKENS["inverted_text"],
        "card_shadow":    DARK_TOKENS["shadow"],
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
        "bg_base":        LIGHT_TOKENS["bg_primary"],
        "border_hairline":LIGHT_TOKENS["border_subtle"],
        "bg_inverted":    LIGHT_TOKENS["inverted_surface"],
        "text_inverted":  LIGHT_TOKENS["inverted_text"],
        "card_shadow":    LIGHT_TOKENS["shadow"],
    },
}


def normalize_theme_name(theme: str) -> str:
    """Normalizes theme names to canonical keys."""
    t = (theme or "green").lower().strip()
    if t in ("white", "light"):
        return "light"
    if t == "dark" or t == "black":
        return "dark"
    return "green"


def get_theme_dict(theme_name: str = "green") -> Dict[str, str]:
    """Returns all design system tokens for the specified theme."""
    key = normalize_theme_name(theme_name)
    tokens = THEMES[key]
    return {
        "bg_primary":         tokens["bg_primary"],
        "bg_surface":         tokens["bg_surface"],
        "bg_elevated":        tokens["bg_elevated"],
        "bg_sidebar":         tokens["bg_sidebar"],
        "bg_sidebar_item":    tokens["bg_sidebar_item"],
        "border_subtle":      tokens["border_subtle"],
        "text_primary":       tokens["text_primary"],
        "text_secondary":     tokens["text_secondary"],
        "text_muted":         tokens["text_muted"],
        "text_sidebar":       tokens["text_sidebar"],
        "text_sidebar_muted": tokens["text_sidebar_muted"],
        "inverted_surface":   tokens["inverted_surface"],
        "inverted_text":      tokens["inverted_text"],
        "accent":             tokens["accent"],
        "accent_light":       tokens["accent_light"],
        "accent_pale":        tokens["accent_pale"],
        "accent_hover":       tokens["accent_hover"],
        "alert_orange":       tokens["alert_orange"],
        "alert_bg":           tokens["alert_bg"],
        "chip_bg":            tokens["chip_bg"],
        "chip_text":          tokens["chip_text"],
        "chip_border":        tokens["chip_border"],
        "chip_active_bg":     tokens["chip_active_bg"],
        "chip_active_text":   tokens["chip_active_text"],
        "input_bg":           tokens["input_bg"],
        "input_border":       tokens["input_border"],
        "input_text":         tokens["input_text"],
        "input_placeholder":  tokens["input_placeholder"],
        "shadow":             tokens["shadow"],
        "mic_ring_shadow":    tokens["mic_ring_shadow"],
        "skeleton_start":     tokens["skeleton_start"],
        "skeleton_mid":       tokens["skeleton_mid"],
        "price_up":           tokens["price_up"],
        "price_down":         tokens["price_down"],
        # Aliases
        "bg_base":           tokens["bg_base"],
        "border_hairline":   tokens["border_hairline"],
        "bg_inverted":       tokens["bg_inverted"],
        "text_inverted":     tokens["text_inverted"],
        "card_shadow":       tokens["card_shadow"],
        "font_heading":      FONT_HEADING,
        "font_body":         FONT_BODY,
        "font_gujarati":     FONT_GUJARATI,
        "font_mono":         FONT_MONO,
    }
