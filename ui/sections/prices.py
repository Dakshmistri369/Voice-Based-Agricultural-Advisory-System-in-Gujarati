"""
Mandi Price Dashboard Section for Gujarati Kisaan Mitra AI.
"""

import streamlit as st
from ui.components import clean_html
from data_services.price_service import price_service

COMMODITIES = [
    ("Cotton",      "કપાસ"),
    ("Groundnut",   "મગફળી"),
    ("Castor",      "એરંડી"),
    ("Cumin",       "જીરું"),
    ("Wheat",       "ઘઉં"),
    ("Onion",       "ડુંગળી"),
    ("Potato",      "બટાટા"),
    ("Bajra",       "બાજરી"),
    ("Sesame",      "તલ"),
    ("Mustard",     "રાઈ"),
]


def render_prices_section():
    """Full mandi price dashboard with commodity filters, sort toggle, and live/cache badges."""
    district = st.session_state.get("selected_district", "રાજકોટ")

    # ── Section Header with Back Navigation ───────────
    col_back, col_title = st.columns([1.3, 5])
    with col_back:
        if st.button("← પાછા ફરો", key="prices_section_back_btn", help="હોમ / મુખ્ય પેજ પર પાછા જાઓ", use_container_width=True):
            st.session_state["active_section"] = "home"
            st.rerun()

    st.markdown(clean_html(f"""
<div class="section-header">
    <h2>💰 આજના બજાર ભાવ (Mandi Prices)</h2>
    <p>AGMARKNET APMC Prices · {district} APMC · Gujarat</p>
</div>
"""), unsafe_allow_html=True)

    # ── District Override ─────────────────────────────
    from ui.navigation import DISTRICTS
    override = st.selectbox("APMC બજાર બદલો:", DISTRICTS,
                            index=DISTRICTS.index(district) if district in DISTRICTS else 0,
                            key="prices_district_override")
    if override != district:
        st.session_state["selected_district"] = override
        district = override

    # ── Commodity Filter ──────────────────────────────
    if "prices_filter" not in st.session_state:
        st.session_state["prices_filter"] = "All"

    filter_options = ["બધા"] + [gu for _, gu in COMMODITIES]
    filter_cols = st.columns(len(filter_options))
    for idx, label in enumerate(filter_options):
        eng = "All" if label == "બધા" else next((e for e, g in COMMODITIES if g == label), label)
        is_active = st.session_state["prices_filter"] == eng
        btn_label = f"✦ {label}" if is_active else label
        if filter_cols[idx].button(btn_label, key=f"price_filter_{idx}", use_container_width=True):
            st.session_state["prices_filter"] = eng
            st.rerun()

    # ── Sort toggle ───────────────────────────────────
    sort_by = st.radio(
        "ક્રમ:",
        ["ભાવ પ્રમાણે (Price)", "પાક પ્રમાણે (Crop)"],
        horizontal=True,
        index=0,
        key="prices_sort"
    )

    # ── Fetch Prices ──────────────────────────────────
    selected_filter = st.session_state.get("prices_filter", "All")
    commodities_to_show = (
        [(e, g) for e, g in COMMODITIES if e == selected_filter]
        if selected_filter != "All"
        else COMMODITIES
    )

    with st.spinner("ભાવ લોડ…"):
        price_results = []
        for eng, gu in commodities_to_show:
            try:
                p = price_service.fetch_mandi_price(eng, district)
                p["commodity_gu_label"] = gu
                p["commodity_en_label"] = eng
                price_results.append(p)
            except Exception:
                pass

    # Sort
    if "ભાવ" in sort_by:
        price_results.sort(key=lambda x: x.get("modal_price", 0), reverse=True)
    else:
        price_results.sort(key=lambda x: x.get("commodity_gu_label", ""))

    # ── Stale Data Banner ─────────────────────────────
    all_cached = all(not r.get("is_live", False) for r in price_results)
    if all_cached and price_results:
        st.markdown(clean_html("""
<div style="border:1px dashed var(--border-subtle);border-radius:10px;padding:0.75rem 1rem;margin-bottom:1rem;font-family:Inter,sans-serif;font-size:0.8rem;color:var(--text-secondary);">
    ⚠️ હાલમાં લાઇવ ભાવ ઉપલબ્ધ નથી. છેલ્લે અપડેટ થયેલ ભાવ બતાવવામાં આવે છે.
</div>
"""), unsafe_allow_html=True)

    # ── Price Cards Grid ──────────────────────────────
    if not price_results:
        st.markdown(clean_html("""
<div style="text-align:center;padding:3rem;color:var(--text-muted);font-family:Noto Sans Gujarati,sans-serif;">
    કોઈ ભાવ ઉપલબ્ધ નથી.
</div>
"""), unsafe_allow_html=True)
        return

    cols = st.columns(2)
    for idx, p in enumerate(price_results):
        live_badge = (
            '<span style="font-family:JetBrains Mono,monospace;font-size:0.65rem;border:1px solid var(--border-subtle);background-color:var(--bg-elevated);padding:3px 10px;border-radius:9999px;color:var(--text-secondary);font-weight:600;">● લાઇવ</span>'
            if p.get("is_live")
            else f'<span style="font-family:JetBrains Mono,monospace;font-size:0.65rem;border:1px solid var(--border-subtle);background-color:var(--bg-elevated);padding:3px 10px;border-radius:9999px;color:var(--text-muted);font-weight:600;">○ {p.get("price_date","")}</span>'
        )
        with cols[idx % 2]:
            st.markdown(clean_html(f"""
<div class="scheme-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;">
        <div>
            <div style="font-family:Noto Sans Gujarati,sans-serif;font-size:1.1rem;font-weight:700;color:var(--text-primary);">{p['commodity_gu_label']}</div>
            <div style="font-family:Inter,sans-serif;font-size:0.78rem;color:var(--text-muted);">{p.get('market_name',district)} · Gujarat</div>
        </div>
        {live_badge}
    </div>
    <div class="scheme-benefit-hero">₹{p['modal_price']}</div>
    <div style="font-family:JetBrains Mono,monospace;font-size:0.7rem;color:var(--text-secondary);">/ ક્વિન્ટલ (100 kg)</div>
    <div style="font-family:JetBrains Mono,monospace;font-size:0.78rem;color:var(--text-muted);margin-top:0.5rem;">
        ન્યૂનતમ ₹{p['min_price']} · મહત્તમ ₹{p['max_price']}
    </div>
</div>
"""), unsafe_allow_html=True)

            if st.button(f"🎤 {p['commodity_gu_label']} વિશે પૂછો", key=f"ask_price_{idx}", use_container_width=True):
                st.session_state["active_section"] = "home"
                st.session_state["prefill_query"] = f"આજે {district} માં {p['commodity_gu_label']} નો ભાવ કેટલો?"
                st.rerun()
