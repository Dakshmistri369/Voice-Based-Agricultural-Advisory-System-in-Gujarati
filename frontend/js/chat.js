// chat.js — Message rendering and card rendering

const chatWindow = document.getElementById('chat-window');
const typingIndicator = document.getElementById('typing-indicator');
const cardsSection = document.getElementById('cards-section');

// ── Welcome message ──────────────────────────────────────
function showWelcome() {
  appendBotMessage(
    '🙏 નમસ્તે! હું <b>કિસાન સહાયક</b> છું.\n\n' +
    'ખેડૂત ભાઈ-બહેનો, અહીં પૂછો:\n' +
    '• 💰 <b>ભાવ</b> — "આજે કપાસ ભાવ?"\n' +
    '• ☔ <b>વ.</b> — "વ. (Weather) કેવું?"\n' +
    '• 📋 <b>યોજના</b> — "PM-KISAN ₹?"\n' +
    '• 🌱 <b>ખ.</b> — "કપ. ખ. (fertilizer)?"\n\n' +
    'માઇક 🎤 દ. (press) ≡ ≡ ≡ ≡ (Gujarati) ≡ ≡ !'
  );
}

// ── Append messages ──────────────────────────────────────
function appendUserMessage(text) {
  const el = createMsg('user', '👤', text);
  chatWindow.appendChild(el);
  scrollToBottom();
}

function appendBotMessage(html) {
  const el = createMsg('bot', '🌾', html, true);
  chatWindow.appendChild(el);
  scrollToBottom();
}

function createMsg(type, avatarEmoji, content, isHtml = false) {
  const wrap = document.createElement('div');
  wrap.className = `msg ${type}`;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = avatarEmoji;

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  if (isHtml) {
    bubble.innerHTML = content.replace(/\n/g, '<br>');
  } else {
    bubble.textContent = content;
  }

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  return wrap;
}

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ── Typing indicator ─────────────────────────────────────
function showTyping() {
  typingIndicator.classList.remove('hidden');
  scrollToBottom();
}
function hideTyping() {
  typingIndicator.classList.add('hidden');
}

// ── Cards ─────────────────────────────────────────────────
function clearCards() {
  cardsSection.innerHTML = '';
}

function renderExtraData(extra) {
  clearCards();
  if (!extra) return;

  if (extra.type === 'price_card' && extra.data) {
    renderPriceCard(extra.data);
  } else if (extra.type === 'weather_card' && extra.data) {
    renderWeatherCard(extra.data);
  } else if (extra.type === 'scheme_cards' && extra.data) {
    extra.data.slice(0, 3).forEach(renderSchemeCard);
  } else if (extra.type === 'crop_info' && extra.data) {
    extra.data.slice(0, 2).forEach(renderCropCard);
  }
}

function renderPriceCard(d) {
  const card = document.createElement('div');
  card.className = 'price-card';
  card.innerHTML = `
    <h3>${d.gu_name || d.commodity}</h3>
    <div class="price-big">₹${d.modal_price.toLocaleString()}</div>
    <div class="price-range">Range: ₹${d.min_price.toLocaleString()} – ₹${d.max_price.toLocaleString()} / ${d.unit}</div>
    <div class="price-market">📍 ${d.market}, ${d.district}</div>
    ${d.note_guj ? `<div class="price-market" style="margin-top:6px;font-style:italic">${d.note_guj}</div>` : ''}
  `;
  cardsSection.appendChild(card);
}

function renderWeatherCard(d) {
  const advisoriesHtml = (d.advisories || []).map(a =>
    `<div class="advisory-item"><span>${a.icon || '📌'}</span><span>${a.msg_guj}</span></div>`
  ).join('');

  const forecastHtml = (d.forecast_days || []).map(f => `
    <div class="forecast-day">
      <div>${_shortDate(f.date)}</div>
      <div>${f.condition}</div>
      <div class="rain">💧 ${f.rain_mm}mm</div>
      <div>${f.max_temp}° / ${f.min_temp}°</div>
    </div>
  `).join('');

  const card = document.createElement('div');
  card.className = 'weather-card';
  card.innerHTML = `
    <h3>🌤️ ${d.city || 'Gujarat'} — Weather</h3>
    <div class="weather-top">
      <div class="weather-temp">${d.current_temp}</div>
      <div class="weather-meta">
        💧 Humidity: ${d.humidity}<br>
        🌧️ Rain Today: ${d.rain_today}<br>
        💨 Wind: ${d.wind_kmh || '—'}<br>
        📅 ${d.fetched_at || ''} (${d.source || ''})
      </div>
    </div>
    <div class="weather-advisory">${advisoriesHtml}</div>
    ${forecastHtml ? `<div class="weather-forecast">${forecastHtml}</div>` : ''}
  `;
  cardsSection.appendChild(card);
}

function renderSchemeCard(s) {
  const card = document.createElement('div');
  card.className = 'scheme-card';
  card.innerHTML = `
    <div class="scheme-badge">${s.category || 'Scheme'}</div>
    <h3>${s.name_gujarati || s.name_english}</h3>
    <p class="benefit">${s.benefit_gujarati || ''}</p>
    ${s.helpline ? `<div class="helpline">📞 ${s.helpline}</div>` : ''}
    ${s.website ? `<a class="apply-link" href="${s.website}" target="_blank" rel="noopener">Apply ↗</a>` : ''}
  `;
  cardsSection.appendChild(card);
}

function renderCropCard(c) {
  const card = document.createElement('div');
  card.className = 'scheme-card';
  card.style.borderColor = 'rgba(34,197,94,.3)';
  const fert = c.fertilizer || {};
  card.innerHTML = `
    <div class="scheme-badge" style="background:rgba(34,197,94,.15);color:#86efac">🌱 Crop Info</div>
    <h3>${c.gu_name || ''}</h3>
    <p class="benefit">Season: ${c.season || ''} | Sowing: ${c.sowing_guj || ''}</p>
    <p class="benefit" style="font-size:13px">${fert.basal ? '🌿 Basal: ' + fert.basal : ''}</p>
    ${fert.top_dress ? `<p class="benefit" style="font-size:13px">⬆️ Top-dress: ${fert.top_dress}</p>` : ''}
  `;
  cardsSection.appendChild(card);
}

function _shortDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return `${d.getDate()}/${d.getMonth() + 1}`;
}
