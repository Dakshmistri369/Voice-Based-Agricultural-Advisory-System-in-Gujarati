"""Disease Detection Section — Beta Coming Soon shell."""
import streamlit as st
from ui.components import clean_html


def render_disease_section():
    col_back, _ = st.columns([1.3, 5])
    with col_back:
        if st.button("← પાછા ફરો", key="disease_section_back_btn", help="હોમ / મુખ્ય પેજ પર પાછા જાઓ", use_container_width=True):
            st.session_state["active_section"] = "home"
            st.rerun()

    st.markdown(clean_html("""
<div class="coming-soon-shell">
    <div style="font-size:3rem;margin-bottom:1rem;">🐛</div>
    <div style="font-family:Space Grotesk,sans-serif;font-size:1.5rem;font-weight:700;color:var(--text-primary);margin-bottom:0.5rem;">
        રોગ ઓળખ — ટૂંક સમયમાં (Beta)
    </div>
    <div style="font-family:Noto Sans Gujarati,sans-serif;font-size:0.9rem;color:var(--text-secondary);max-width:400px;margin:0 auto;line-height:1.7;">
        પાકના ફોટો ઉપલોડ કરી AI-આધારિત રોગ ઓળખ, Phase 11 માં ઉમેરાશે.
    </div>
    <div style="margin-top:1.5rem;font-family:JetBrains Mono,monospace;font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;">
        Plant Disease CNN · Phase 11
    </div>
</div>
"""), unsafe_allow_html=True)
