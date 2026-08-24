"""
UI Component HTML Builders for Gujarati Kisaan Mitra AI.
Supports dual Monochrome Aesthetic: Black & White Themes via Central Token System.
"""

import re
from typing import Dict, List, Optional, Any


def clean_html(html_str: str) -> str:
    """Removes all leading/trailing line whitespace to prevent Streamlit markdown from creating code blocks."""
    lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    return "".join(lines)


def render_header(
    stt_status: str = "Whisper-API",
    tts_status: str = "Piper-TTS",
    llm_status: str = "Qwen2.5-7B"
) -> str:
    """Renders the top monochrome header with title, Gujarati tagline, and service status indicators."""
    raw_html = f"""
<div class="border-b pb-4 mb-6" style="border-color: var(--border-subtle);">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
            <h1 class="text-3xl font-bold font-['Space_Grotesk'] tracking-tight" style="color: var(--text-primary);">
                ગુજરાતી કિસાન મિત્ર AI
            </h1>
            <p class="text-xs sm:text-sm font-['Noto_Sans_Gujarati'] mt-1" style="color: var(--text-secondary);">
                દસ્તાવેજ-આધારિત અવાજ ખેતી માર્ગદર્શક (Voice-Based PDF Agricultural Advisory)
            </p>
        </div>
        <div class="flex items-center gap-3 text-xs font-mono" style="color: var(--text-secondary);">
            <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full" style="border: 1px solid var(--border-subtle); background-color: var(--bg-surface);">
                <span class="w-1.5 h-1.5 rounded-full animate-pulse" style="background-color: var(--text-primary);"></span>
                <span>STT: {stt_status}</span>
            </div>
            <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full" style="border: 1px solid var(--border-subtle); background-color: var(--bg-surface);">
                <span class="w-1.5 h-1.5 rounded-full" style="background-color: var(--text-primary);"></span>
                <span>TTS: {tts_status}</span>
            </div>
            <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full" style="border: 1px solid var(--border-subtle); background-color: var(--bg-surface);">
                <span class="w-1.5 h-1.5 rounded-full" style="background-color: var(--text-primary);"></span>
                <span>LLM: {llm_status}</span>
            </div>
        </div>
    </div>
</div>
"""
    return clean_html(raw_html)


def render_intent_pill(intent_name: str) -> str:
    """Renders an uppercase monochrome intent classification pill."""
    raw_html = f"""
<div class="intent-pill">
    <span class="w-1.5 h-1.5 rounded-full" style="background-color: var(--text-primary);"></span>
    <span>{intent_name.upper()}</span>
</div>
"""
    return clean_html(raw_html)


def render_source_chip(filename: str, page_number: int) -> str:
    """Renders a PDF source-citation chip for grounded answers."""
    raw_html = f"""
<div class="source-chip">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
    <span>📄 {filename} · p.{page_number}</span>
</div>
"""
    return clean_html(raw_html)


def render_chat_bubble(
    message: str,
    is_user: bool = False,
    intent: Optional[str] = None,
    source_chip: Optional[Dict[str, Any]] = None
) -> str:
    """Renders a chat message bubble using theme variables."""
    clean_msg = message.strip()
    if clean_msg.endswith("</div>"):
        clean_msg = clean_msg[:-6].strip()

    if is_user:
        raw_html = f"""
<div class="flex justify-end mb-4">
    <div class="chat-bubble-user">
        {clean_msg}
    </div>
</div>
"""
        return clean_html(raw_html)
    else:
        intent_html = render_intent_pill(intent) if intent else ""
        chip_html = (
            render_source_chip(source_chip["filename"], source_chip["page_number"])
            if source_chip else ""
        )
        raw_html = f"""
<div class="flex justify-start mb-5">
    <div class="chat-bubble-ai">
        {intent_html}
        <div class="mt-1" style="color: var(--text-primary);">{clean_msg}</div>
        {chip_html}
    </div>
</div>
"""
        return clean_html(raw_html)


def render_price_card(
    commodity_gu: str,
    commodity_en: str,
    modal_price: int,
    min_price: int,
    max_price: int,
    district_gu: str,
    price_date: str,
    is_live: bool = True
) -> str:
    """Renders a structured monochrome APMC Mandi price result card with theme variables."""
    source_label = "લાઈવ APMC ભાવ" if is_live else "કેશ કરેલ ભાવ (Cache)"
    raw_html = f"""
<div class="kisaan-card mb-5">
    <div class="flex items-center justify-between border-b pb-3 mb-4" style="border-color: var(--border-subtle);">
        <div>
            <span class="text-xs font-mono uppercase tracking-wider" style="color: var(--text-muted);">APMC MANDI PRICE</span>
            <h3 class="text-xl font-bold font-['Noto_Sans_Gujarati']" style="color: var(--text-primary);">
                {commodity_gu} <span class="text-sm font-normal" style="color: var(--text-secondary);">({commodity_en})</span>
            </h3>
            <p class="text-xs font-['Noto_Sans_Gujarati'] mt-0.5" style="color: var(--text-secondary);">
                જિલ્લો: {district_gu} · તારીખ: {price_date}
            </p>
        </div>
        <div class="text-right">
            <span class="inline-block text-[11px] font-mono px-2.5 py-1 rounded-full" style="border: 1px solid var(--border-subtle); background-color: var(--bg-elevated); color: var(--text-secondary);">
                {source_label}
            </span>
        </div>
    </div>
    <div class="grid grid-cols-3 gap-3 text-center">
        <div class="p-3 rounded-xl" style="background-color: var(--bg-elevated); border: 1px solid var(--border-subtle);">
            <div class="text-xs font-mono uppercase" style="color: var(--text-muted);">ન્યૂનતમ (MIN)</div>
            <div class="text-xl font-bold font-mono mt-1" style="color: var(--text-primary);">₹{min_price}</div>
            <div class="text-[10px] font-mono mt-0.5" style="color: var(--text-secondary);">પ્રતિ મણ (20 kg)</div>
        </div>
        <div class="p-3 rounded-xl shadow-lg" style="background-color: var(--bg-primary); border: 2px solid var(--text-primary);">
            <div class="text-xs font-mono uppercase" style="color: var(--text-secondary);">બજાર ભાવ (MODAL)</div>
            <div class="text-2xl font-extrabold font-mono mt-0.5" style="color: var(--text-primary);">₹{modal_price}</div>
            <div class="text-[10px] font-mono mt-0.5" style="color: var(--text-primary);">પ્રતિ મણ (20 kg)</div>
        </div>
        <div class="p-3 rounded-xl" style="background-color: var(--bg-elevated); border: 1px solid var(--border-subtle);">
            <div class="text-xs font-mono uppercase" style="color: var(--text-muted);">મહત્તમ (MAX)</div>
            <div class="text-xl font-bold font-mono mt-1" style="color: var(--text-primary);">₹{max_price}</div>
            <div class="text-[10px] font-mono mt-0.5" style="color: var(--text-secondary);">પ્રતિ મણ (20 kg)</div>
        </div>
    </div>
</div>
"""
    return clean_html(raw_html)


def render_weather_card(
    district_gu: str,
    temp_c: float,
    condition_gu: str,
    humidity: int,
    wind_speed: float,
    advisory_bullets: List[str],
    is_live: bool = True
) -> str:
    """Renders a structured monochrome weather condition + Gujarati farming advisory card."""
    advisory_items = "".join(
        f"<li class='text-sm font-['Noto_Sans_Gujarati'] mb-1.5 flex items-start gap-2' style='color: var(--text-primary);'><span class='font-bold' style='color: var(--text-primary);'>•</span> {bullet}</li>"
        for bullet in advisory_bullets
    )
    raw_html = f"""
<div class="kisaan-card mb-5">
    <div class="flex items-center justify-between border-b pb-3 mb-4" style="border-color: var(--border-subtle);">
        <div>
            <span class="text-xs font-mono uppercase tracking-wider" style="color: var(--text-muted);">LIVE WEATHER ADVISORY</span>
            <h3 class="text-xl font-bold font-['Noto_Sans_Gujarati']" style="color: var(--text-primary);">
                {district_gu} જિલ્લો
            </h3>
        </div>
        <div class="text-right">
            <div class="text-3xl font-extrabold font-mono" style="color: var(--text-primary);">{temp_c}°C</div>
            <div class="text-xs font-['Noto_Sans_Gujarati']" style="color: var(--text-secondary);">{condition_gu}</div>
        </div>
    </div>
    <div class="grid grid-cols-2 gap-3 mb-4 text-xs font-mono" style="color: var(--text-secondary);">
        <div class="p-2.5 rounded-xl flex justify-between" style="background-color: var(--bg-elevated); border: 1px solid var(--border-subtle);">
            <span>ભેજ (HUMIDITY):</span>
            <span class="font-bold" style="color: var(--text-primary);">{humidity}%</span>
        </div>
        <div class="p-2.5 rounded-xl flex justify-between" style="background-color: var(--bg-elevated); border: 1px solid var(--border-subtle);">
            <span>પવન (WIND):</span>
            <span class="font-bold" style="color: var(--text-primary);">{wind_speed} km/h</span>
        </div>
    </div>
    <div class="border-t pt-3" style="border-color: var(--border-subtle);">
        <div class="text-xs font-mono uppercase mb-2" style="color: var(--text-muted);">ખેતી ઉપયોગી સલાહ (FARMING ADVISORY)</div>
        <ul class="space-y-1">
            {advisory_items}
        </ul>
    </div>
</div>
"""
    return clean_html(raw_html)


def render_mic_button(is_recording: bool = False, elapsed_seconds: int = 0) -> str:
    """Renders the primary circular microphone trigger button with optional pulse animation."""
    status_class = "mic-button-recording" if is_recording else ""
    status_label = f"રેકોર્ડિંગ ચાલુ છે ({elapsed_seconds}s)…" if is_recording else "માઇક દબાવીને બોલો"
    raw_html = f"""
<div class="mic-container">
    <div class="mic-button-ring {status_class}">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-9 w-9" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
    </div>
    <p class="text-sm font-semibold font-['Noto_Sans_Gujarati'] mt-3" style="color: var(--text-primary);">
        {status_label}
    </p>
    <p class="text-xs font-['Inter'] mt-0.5" style="color: var(--text-muted);">
        Click to start recording your voice in Gujarati
    </p>
</div>
"""
    return clean_html(raw_html)


def render_quick_chips(chips: Optional[List[str]] = None) -> str:
    """Renders quick recommendation prompt pills."""
    default_chips = [
        "💰 કપાસનો ભાવ",
        "☔ વાતાવરણ",
        "📄 PM-KISAN યોજના",
        "🌱 ખાતરની માત્રા",
        "🐛 પાક રોગ"
    ]
    target_chips = chips or default_chips
    chip_elements = "".join(
        f'<button class="quick-chip">{chip}</button>'
        for chip in target_chips
    )
    raw_html = f"""
<div class="flex flex-wrap gap-2 justify-center my-4">
    {chip_elements}
</div>
"""
    return clean_html(raw_html)


def render_empty_state() -> str:
    """Renders the default empty state prompt."""
    raw_html = f"""
<div class="kisaan-card p-8 text-center my-6">
    <div class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" style="background-color: var(--bg-elevated); border: 1px solid var(--border-subtle); color: var(--text-primary);">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
    </div>
    <h3 class="text-xl font-bold font-['Space_Grotesk']" style="color: var(--text-primary);">માઇક દબાવીને તમારો પ્રશ્ન પૂછો</h3>
    <p class="text-sm font-['Noto_Sans_Gujarati'] max-w-md mx-auto mt-2 leading-relaxed" style="color: var(--text-secondary);">
        તમે સરકારી યોજનાઓ, ખાતરનું પ્રમાણ, હવામાન અથવા આજના બજાર ભાવ વિશે ગુજરાતીમાં પૂછી શકો છો.
    </p>
</div>
"""
    return clean_html(raw_html)


def render_loading_skeleton(current_stage: str = "સાંભળી રહ્યું છે…") -> str:
    """Renders the monochrome loading skeleton screen with active stage label."""
    raw_html = f"""
<div class="kisaan-card p-5 my-4">
    <div class="flex items-center gap-3 mb-4">
        <span class="w-3 h-3 rounded-full animate-ping" style="background-color: var(--text-primary);"></span>
        <span class="text-sm font-semibold font-['Noto_Sans_Gujarati']" style="color: var(--text-primary);">
            {current_stage}
        </span>
    </div>
    <div class="space-y-3">
        <div class="h-4 skeleton-box w-3/4"></div>
        <div class="h-4 skeleton-box w-full"></div>
        <div class="h-4 skeleton-box w-5/6"></div>
    </div>
</div>
"""
    return clean_html(raw_html)


def render_pipeline_trace(trace_data: Dict[str, Any]) -> str:
    """Renders the collapsible debug pipeline trace panel."""
    sources_str = ", ".join(
        f"{src.get('filename')} (p.{src.get('page')})" for src in trace_data.get("sources", [])
    ) if trace_data.get("sources") else "N/A"

    raw_html = f"""
<div class="trace-panel mt-6">
    <div class="flex items-center justify-between border-b pb-2 mb-3" style="border-color: var(--border-subtle);">
        <span class="text-xs font-mono font-bold uppercase tracking-wider" style="color: var(--text-primary);">🔍 PIPELINE TRACE DEBUG</span>
        <span class="text-[10px] font-mono" style="color: var(--text-secondary);">TOTAL LATENCY: {trace_data.get('total_latency_ms', 0)}ms</span>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div>
            <div class="trace-label">1. GUJARATI TRANSCRIPT (STT)</div>
            <div class="font-['Noto_Sans_Gujarati']" style="color: var(--text-primary);">{trace_data.get('gu_transcript', 'N/A')}</div>
        </div>
        <div>
            <div class="trace-label">2. ENGLISH TRANSLATION</div>
            <div class="font-mono" style="color: var(--text-primary);">{trace_data.get('en_query', 'N/A')}</div>
        </div>
        <div>
            <div class="trace-label">3. DETECTED INTENT & CONFIDENCE</div>
            <div class="font-mono" style="color: var(--text-primary);">{trace_data.get('intent', 'N/A')} ({trace_data.get('confidence', '0.00')})</div>
        </div>
        <div>
            <div class="trace-label">4. RETRIEVED PDF SOURCES</div>
            <div class="font-mono" style="color: var(--text-primary);">{sources_str}</div>
        </div>
        <div class="md:col-span-2">
            <div class="trace-label">5. GROUNDED ENGLISH LLM ANSWER</div>
            <div class="font-mono" style="color: var(--text-primary);">{trace_data.get('en_answer', 'N/A')}</div>
        </div>
        <div class="md:col-span-2">
            <div class="trace-label">6. FINAL GUJARATI SPOKEN ANSWER</div>
            <div class="font-['Noto_Sans_Gujarati']" style="color: var(--text-primary);">{trace_data.get('gu_answer', 'N/A')}</div>
        </div>
        <div>
            <div class="trace-label">7. TTS ENGINE</div>
            <div class="font-mono" style="color: var(--text-primary);">{trace_data.get('tts_engine', 'N/A')}</div>
        </div>
        <div>
            <div class="trace-label">8. STAGE LATENCY BREAKDOWN (MS)</div>
            <div class="font-mono" style="color: var(--text-primary);">{trace_data.get('latency_ms', {})}</div>
        </div>
    </div>
</div>
"""
    return clean_html(raw_html)
