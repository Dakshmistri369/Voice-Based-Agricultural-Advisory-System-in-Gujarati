"""
Crop Advisory Section for Gujarati Kisaan Mitra AI.
All content is retrieved from the RAG vector store (doc_category='crop_advisory').
"""

import streamlit as st
from ui.components import clean_html
from data_services.rag_service import rag_service
from core.tts_service import tts_service

CROPS = [
    ("cotton",    "🌾 કપાસ"),
    ("groundnut", "🥜 મગફળી"),
    ("cumin",     "🌿 જીરું"),
    ("wheat",     "🌾 ઘઉં"),
    ("bajra",     "🌾 બાજરી"),
    ("castor",    "🌻 એરંડો"),
    ("onion",     "🧅 ડુંગળી"),
    ("sesame",    "🌱 તલ"),
]

SUBSECTIONS = [
    ("sowing",      "🌱 વાવણી"),
    ("fertilizer",  "🧪 ખાતર"),
    ("irrigation",  "💧 સિંચાઈ"),
    ("pests",       "🐛 જીવાત / રોગ"),
    ("varieties",   "🔬 જાતો"),
]


def render_crop_advisory_section():
    """Crop-specific advisory — shows RAG results for selected crop across subsections."""

    # ── Section Header ────────────────────────────────
    st.markdown(clean_html("""
<div class="section-header">
    <h2>🌱 પાક સલાહ (Crop Advisory)</h2>
    <p>PDF Corpus RAG Retrieval — Verified Agricultural Guidance</p>
</div>
"""), unsafe_allow_html=True)

    # ── Crop Selector (radio chips via buttons) ───────
    if "selected_crop" not in st.session_state:
        st.session_state["selected_crop"] = "cotton"

    cols = st.columns(len(CROPS))
    for idx, (crop_id, crop_label) in enumerate(CROPS):
        is_active = st.session_state["selected_crop"] == crop_id
        btn_label = f"✦ {crop_label}" if is_active else crop_label
        if cols[idx].button(btn_label, key=f"crop_sel_{crop_id}", use_container_width=True):
            st.session_state["selected_crop"] = crop_id
            st.rerun()

    selected_id = st.session_state["selected_crop"]
    selected_label = next((lbl for cid, lbl in CROPS if cid == selected_id), selected_id)

    st.markdown(clean_html(f"""
<div style="font-family:Space Grotesk,sans-serif;font-size:1.25rem;font-weight:700;color:var(--text-primary);margin:1rem 0 0.25rem 0;">
    {selected_label} — ખેતી માર્ગદર્શિકા
</div>
"""), unsafe_allow_html=True)

    # ── Fetch RAG Context for Each Subsection ─────────
    district = st.session_state.get("selected_district", "")
    all_text_parts = []

    for sub_id, sub_label in SUBSECTIONS:
        query = f"{selected_id} {sub_id}"
        with st.spinner(f"{sub_label} ખોળાઈ…"):
            try:
                is_found, combined, sources, _ = rag_service.retrieve_context(
                    query, top_k=3, doc_category="crop_advisory"
                )
            except Exception:
                is_found, combined, sources = False, "", []

        if not is_found:
            try:
                is_found, combined, sources, _ = rag_service.retrieve_context(selected_id, top_k=2)
            except Exception:
                is_found, combined, sources = False, "", []

        if not is_found or not combined:
            combined = "ઉપલબ્ધ PDF corpus માં આ વિભાગ માટે ડેટા મળ્યો નહીં."
            source_file, page_no = "", ""
        else:
            combined = combined[:500]
            source_file = sources[0].get("filename", "") if sources else ""
            page_no     = sources[0].get("page", "")     if sources else ""

        all_text_parts.append(f"{sub_label}: {combined}")

        src_chip = f'<span class="source-chip">📄 {source_file} p.{page_no}</span>' if source_file else ""

        st.markdown(clean_html(f"""
<div class="kisaan-card p-4 mb-3">
    <div class="crop-subsection-header">{sub_label}</div>
    <div style="font-family:Noto Sans Gujarati,sans-serif;font-size:0.88rem;color:var(--text-primary);line-height:1.75;">
        {combined}
    </div>
    <div style="margin-top:0.6rem;">{src_chip}</div>
</div>
"""), unsafe_allow_html=True)

    # ── TTS Listen Button ─────────────────────────────
    st.markdown("---")
    if st.button("🔊  સંપૂર્ણ સલાહ સાંભળો (Listen)", key="crop_tts_btn", use_container_width=True):
        full_text = f"{selected_label} ની ખેતી સલાહ. " + ". ".join(all_text_parts)
        with st.spinner("ઓડિઓ…"):
            audio_bytes, engine = tts_service.synthesize_speech(full_text[:1500])
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
        else:
            st.warning("TTS ઉપલબ્ધ નથી.")

    # ── Cross-navigate to Chat ────────────────────────
    if st.button(f"🎤  {selected_label} વિશે AI ને પૂછો", key="crop_chat_btn", use_container_width=True):
        st.session_state["active_section"] = "home"
        st.session_state["prefill_query"] = f"{selected_label} ના પાકની ખાતર, સિંચાઈ, જીવાત નિયંત્રણ?"
        st.rerun()
