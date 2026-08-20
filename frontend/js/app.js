// app.js — Main application: health check, text query, init

// ── DOM refs ─────────────────────────────────────────────
const textInput   = document.getElementById('text-input');
const sendBtn     = document.getElementById('send-btn');
const statusDot   = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');

// ── Init ─────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  showWelcome();
  checkBackendHealth();
});

// ── Health check ─────────────────────────────────────────
async function checkBackendHealth() {
  try {
    const resp = await fetch(`${CONFIG.API_BASE}/health`, { signal: AbortSignal.timeout(5000) });
    if (resp.ok) {
      const data = await resp.json();
      setStatus('online', `✅ Connected (${data.llm_model.split('/').pop()})`);
    } else {
      setStatus('offline', '⚠️ Backend error');
    }
  } catch {
    setStatus('offline', '❌ Backend offline — start backend');
  }
}

function setStatus(state, label) {
  statusDot.className = `status-dot ${state}`;
  statusLabel.textContent = label;
}

// ── Text query ────────────────────────────────────────────
sendBtn.addEventListener('click', submitText);
textInput.addEventListener('keydown', e => { if (e.key === 'Enter') submitText(); });

function submitText() {
  const q = textInput.value.trim();
  if (!q) return;
  textInput.value = '';
  sendTextQuery(q);
}

async function sendTextQuery(query) {
  appendUserMessage(query);
  showTyping();
  clearCards();

  const district = document.getElementById('district-sel').value;

  try {
    const resp = await fetch(`${CONFIG.API_BASE}/text-ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: query,
        district: district,
        lat: CONFIG.DEFAULT_LAT,
        lon: CONFIG.DEFAULT_LON,
      }),
    });

    hideTyping();

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      appendBotMessage(`⚠️ Error: ${err.detail || resp.statusText}`);
      return;
    }

    const data = await resp.json();
    appendBotMessage(data.answer_text || '—');
    renderExtraData(data.extra_data);

    // Browser TTS fallback (server TTS only on voice-ask)
    speakFallback(data.answer_text);

  } catch (err) {
    hideTyping();
    appendBotMessage('⚠️ Cannot reach backend. Make sure `uvicorn main:app` is running on port 8000.');
    console.error(err);
  }
}
