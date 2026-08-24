"""
Government Schemes Browser Section for Gujarati Kisaan Mitra AI.
"""

import streamlit as st
from ui.components import clean_html
from data_services.scheme_browser import list_all_schemes

CATEGORY_LABELS = {
    "All":       "બધી (All)",
    "Central":   "કેન્દ્ર સરકાર",
    "Gujarat":   "ગુજરાત સ. ",
    "Insurance": "વીમો (Insurance)",
    "Credit":    "ક્રેડિટ/KCC",
    "Subsidy":   "સહાય/Subsidy",
}


def render_schemes_section():
    """Government scheme browser — semantic search + category filter + cards."""

    # ── Section Header ────────────────────────────────
    st.markdown(clean_html("""
<div class="section-header">
    <h2>📄 સરકારી ખેત-યોજનાઓ</h2>
    <p>PDF Corpus — Re-indexed scheme documents</p>
</div>
"""), unsafe_allow_html=True)

    # ── Semantic Search Bar (BUG 3 Fix) ───────────────
    search_q = st.text_input(
        "🔍  યોજના શોધો (Search Schemes):",
        placeholder="PM-KISAN, PMFBY, ખેડૂત સહાય…",
        key="scheme_search_input"
    )

    # ── Category Filters (BUG 2 Fix) ──────────────────
    if "scheme_cat_filter" not in st.session_state:
        st.session_state["scheme_cat_filter"] = "All"

    cats = list(CATEGORY_LABELS.keys())
    cat_cols = st.columns(len(cats))
    for idx, cat in enumerate(cats):
        is_active = st.session_state["scheme_cat_filter"] == cat
        label = f"✦ {CATEGORY_LABELS[cat]}" if is_active else CATEGORY_LABELS[cat]
        if cat_cols[idx].button(label, key=f"scheme_cat_{idx}", use_container_width=True):
            st.session_state["scheme_cat_filter"] = cat
            st.rerun()

    # ── Fetch Schemes ─────────────────────────────────
    with st.spinner("યોજનાઓ લોડ…"):
        cat_filter = st.session_state.get("scheme_cat_filter", "All")
        schemes = list_all_schemes(category_filter=cat_filter)

    # Apply text search filter
    if search_q:
        sq = search_q.lower()
        schemes = [s for s in schemes if sq in s.get("name", "").lower() or sq in s.get("detail_text", "").lower()]

    # ── Render Scheme Cards (BUG 4 & 5 Fix) ───────────
    if not schemes:
        st.markdown(clean_html("""
<div style="text-align:center;padding:3rem 1rem;color:var(--text-muted);font-family:Noto Sans Gujarati,sans-serif;">
    📂 કોઈ યોજના મળી નહીં. PDF corpus ફરી index કરો (Admin).
</div>
"""), unsafe_allow_html=True)
        return

    for idx, s in enumerate(schemes):
        cat_badge = f'<span style="font-family:JetBrains Mono,monospace;font-size:0.65rem;border:1px solid var(--border-subtle);background-color:var(--bg-elevated);padding:3px 10px;border-radius:9999px;color:var(--text-secondary);font-weight:600;">{s.get("category","")}</span>'
        src_chip = f'<span class="source-chip">📄 {s.get("source_filename","")[:40]}</span>'

        st.markdown(clean_html(f"""
<div class="scheme-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.25rem;">
        <div style="font-family:Space Grotesk,sans-serif;font-size:1.1rem;font-weight:700;color:var(--text-primary);max-width:80%;">{s['name']}</div>
        {cat_badge}
    </div>
    <div class="scheme-benefit-hero">{s['benefit']}</div>
    <div style="font-family:Noto Sans Gujarati,sans-serif;font-size:0.85rem;color:var(--text-secondary);margin-top:0.5rem;line-height:1.65;">
        {s['detail_text'][:280]}…
    </div>
    <div style="margin-top:0.75rem;">{src_chip}</div>
</div>
"""), unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(f"🎤 '{s['name'][:25]}' વિશે પૂછો", key=f"scheme_ask_{idx}", use_container_width=True):
                st.session_state["active_section"] = "home"
                st.session_state["prefill_query"] = f"{s['name']} યોજના ની માહિતી"
                st.rerun()
        with col2:
            with st.expander("📖 વધુ વિગત (Expand)", expanded=False):
                st.markdown(
                    f"<div style='font-family:Noto Sans Gujarati,sans-serif;font-size:0.88rem;color:var(--text-primary);line-height:1.75;'>{s['detail_text']}</div>",
                    unsafe_allow_html=True
                )
