// voice.js — MediaRecorder + HF Whisper STT + MMS TTS playback

let mediaRecorder = null;
let audioChunks = [];
let autoStopTimer = null;

const micBtn    = document.getElementById('mic-btn');
const micIcon   = document.getElementById('mic-icon');
const recStatus = document.getElementById('rec-status');

// ── Mic button handler ───────────────────────────────────
micBtn.addEventListener('click', async () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    stopRecording();
  } else {
    await startRecording();
  }
});

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];

    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : 'audio/webm';

    mediaRecorder = new MediaRecorder(stream, { mimeType });
    mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      const blob = new Blob(audioChunks, { type: mimeType });
      await sendVoiceToBackend(blob);
    };

    mediaRecorder.start(250);   // collect chunks every 250ms

    // UI → recording state
    micBtn.classList.add('recording');
    micIcon.textContent = '⏹️';
    recStatus.classList.remove('hidden');

    // Auto-stop after CONFIG.MAX_RECORD_MS
    autoStopTimer = setTimeout(stopRecording, CONFIG.MAX_RECORD_MS);

  } catch (err) {
    console.error('Mic error:', err);
    appendBotMessage('⚠️ Microphone access denied. Please allow mic permissions and try again.');
  }
}

function stopRecording() {
  if (autoStopTimer) { clearTimeout(autoStopTimer); autoStopTimer = null; }
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }
  micBtn.classList.remove('recording');
  micIcon.textContent = '🎤';
  recStatus.classList.add('hidden');
}

// ── Send audio to /voice-ask ─────────────────────────────
async function sendVoiceToBackend(blob) {
  const district = document.getElementById('district-sel').value;
  const formData = new FormData();
  formData.append('audio', blob, 'query.webm');
  formData.append('district', district);
  formData.append('lat', CONFIG.DEFAULT_LAT);
  formData.append('lon', CONFIG.DEFAULT_LON);

  appendUserMessage('🎤 [Voice query sent]');
  showTyping();

  try {
    const resp = await fetch(`${CONFIG.API_BASE}/voice-ask`, {
      method: 'POST',
      body: formData,
    });

    if (!resp.ok) {
      const err = await resp.json();
      hideTyping();
      appendBotMessage(`⚠️ ${err.error || 'Voice recognition failed. Please try again.'}`);
      return;
    }

    const data = await resp.json();
    hideTyping();

    // Show recognised text
    if (data.question && data.question !== '[Voice query sent]') {
      appendUserMessage(`🎤 "${data.question}"`);
    }

    appendBotMessage(data.answer_text || '—');
    renderExtraData(data.extra_data);

    // Auto-play TTS response
    if (data.audio_url && CONFIG.TTS_AUTOPLAY) {
      playTTS(CONFIG.API_BASE + data.audio_url);
    } else if (!data.tts_available) {
      // Browser TTS fallback
      speakFallback(data.answer_text);
    }

  } catch (err) {
    hideTyping();
    console.error('Voice ask error:', err);
    appendBotMessage('⚠️ Server unavailable. Please check backend is running.');
  }
}

// ── TTS audio playback ───────────────────────────────────
function playTTS(url) {
  const player = document.getElementById('tts-player');
  player.src = url;
  player.play().catch(e => console.warn('Audio play blocked:', e));
}

// ── Browser SpeechSynthesis fallback ────────────────────
function speakFallback(text) {
  if (!('speechSynthesis' in window) || !text) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'gu-IN';
  utter.rate = 0.9;
  // Pick Gujarati voice if available
  const voices = window.speechSynthesis.getVoices();
  const guVoice = voices.find(v => v.lang.startsWith('gu'));
  if (guVoice) utter.voice = guVoice;
  window.speechSynthesis.speak(utter);
}
