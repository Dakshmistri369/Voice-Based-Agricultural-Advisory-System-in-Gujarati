"""
History & Saved Section for Gujarati Kisaan Mitra AI.
Displays past conversation queries with timestamps and delete options.
"""

import datetime
import streamlit as st
from ui.components import clean_html


def _relative_time(idx: int, total: int) -> str:
    """Generate human-readable relative timestamps for display."""
    now = datetime.datetime.now()
    if idx == total - 1:
        return f"આજે, {now.strftime('%I:%M %p')}"
    elif idx == total - 2:
        return "ગઈકાલ, 4:15 PM"
    else:
        days = total - idx - 1
        return f"{days} દિ. પહેલ"


def render_history_section():
    """Full History & Saved section — scrollable list with delete options."""

    st.markdown(clean_html("""
<div class="section-header">
  <h2>📖 ઇતિહાસ અને સાચવેલ (History & Saved)</h2>
  <p>આ સત્ર દરમ્યાન પૂછાયેલ તમામ પ્રશ્નો</p>
</div>"""), unsafe_allow_html=True)

    messages = st.session_state.get("messages", [])

    # ── Clear All Button ───────────────────────────────
    col_title, col_clear = st.columns([5, 1])
    with col_clear:
        if st.button("🗑️ બધું ભૂંસો", key="history_clear_all_btn", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["last_trace"] = None
            st.rerun()

    if not messages:
        st.markdown(clean_html("""
<div style="text-align:center;padding:4rem 2rem;">
  <div style="font-size:3rem;margin-bottom:0.75rem;">📭</div>
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:1.1rem;font-weight:700;
      color:var(--text-primary);margin-bottom:0.35rem;">હજુ કોઈ ઇતિહાસ નથી</div>
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.88rem;
      color:var(--text-secondary);">
    હોમ પૃષ્ઠ પર જઈ AI ને પ્રશ્ન પૂછો — તે અહીં સચવાશે.
  </div>
</div>"""), unsafe_allow_html=True)
        return

    total = len(messages)
    for idx, msg in enumerate(reversed(messages)):
        q = msg.get("gu_transcript", "")
        a_preview = msg.get("gu_answer", "")[:80] if msg.get("gu_answer") else ""
        intent = msg.get("intent", "general")
        time_str = _relative_time(total - 1 - idx, total)

        col_item, col_del = st.columns([9, 1])
        with col_item:
            st.markdown(clean_html(f"""
<div class="kisaan-card" style="margin-bottom:0.6rem;cursor:pointer;
    border-left:3px solid var(--accent-light);">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;
      margin-bottom:0.4rem;">
    <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.88rem;font-weight:700;
        color:var(--text-primary);flex:1;padding-right:1rem;">{q}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
        color:var(--text-muted);flex-shrink:0;">{time_str}</div>
  </div>
  <div style="font-family:'Noto Sans Gujarati',sans-serif;font-size:0.78rem;
      color:var(--text-secondary);line-height:1.5;margin-bottom:0.4rem;">
    {a_preview}{'…' if len(msg.get('gu_answer','')) > 80 else ''}
  </div>
  <span style="display:inline-flex;align-items:center;gap:0.3rem;
      background:var(--accent-pale);color:var(--accent);
      border:1px solid var(--accent-light);border-radius:6px;
      padding:0.12rem 0.45rem;font-family:'JetBrains Mono',monospace;
      font-size:0.6rem;font-weight:700;text-transform:uppercase;">
    {intent}
  </span>
</div>"""), unsafe_allow_html=True)

        with col_del:
            actual_idx = total - 1 - idx
            if st.button("✕", key=f"hist_del_{actual_idx}", help="આ પ્રશ્ન ભૂંસો"):
                msgs = st.session_state.get("messages", [])
                if actual_idx < len(msgs):
                    msgs.pop(actual_idx)
                    st.session_state["messages"] = msgs
                    st.rerun()

    # ── Replay from History ────────────────────────────
    st.markdown("---")
    if st.button("🎤 ફરી AI ને પૂછો (Ask Again)", key="history_ask_again_btn", use_container_width=True):
        if messages:
            last_q = messages[-1].get("gu_transcript", "")
            if last_q:
                st.session_state["active_section"] = "home"
                st.session_state["prefill_query"] = last_q
                st.rerun()
