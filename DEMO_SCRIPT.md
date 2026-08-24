# 🎬 Gujarati Kisaan Mitra AI — 3-Minute Judge Demonstration Script

> **Goal:** Demonstrate an end-to-end voice-in / voice-out agricultural AI system in Gujarati grounded strictly in real PDF documents, with live mandi pricing, weather advisories, side-by-side PDF citation proof, and resilient fallback handling.

---

## 00:00 – 00:30 | Introduction & Visual Aesthetic
- **Show App Header:** Open the web application running at `http://localhost:8501`.
- **Key Talking Point:**
  > "Welcome to **ગુજરાતી કિસાન મિત્ર AI** (Gujarati Kisaan Mitra AI) — a voice-first agricultural advisory system designed for Gujarati farmers. Low literacy should never stand between a farmer and official agricultural advice. Notice the pure black, high-contrast editorial UI built specifically for outdoor field visibility."
- **Point out Status Indicators:** Highlight the monochrome STT, TTS, and LLM status pills at top right.

---

## 00:30 – 01:15 | Core Differentiation: PDF-Grounded Scheme Query
- **Action:** Click the microphone button or type the Gujlish query:
  `"PM-KISAN ma kitla paisa male che?"`
- **System Behavior:**
  1. Voice/Text transcribed into Gujarati script: `"PM-KISAN યોજનામાં વાર્ષિક કેટલા રૂપિયા મળે છે?"`.
  2. PDF RAG engine retrieves exact passage from `_એગ્રીકલ્ચર બુક.pdf`.
  3. Spoken answer played automatically in Gujarati:
     `"પીએમ-કિસાન યોજના હેઠળ તમામ પાત્ર ખેડૂતોને વાર્ષિક ₹6,000 ત્રણ સમાન હપ્તામાં સીધા બેંક ખાતામાં જમા કરવામાં આવે છે."`
- **Groundedness Proof Moment (Side-by-Side Verification):**
  - Point to the `📄 _એગ્રીકલ્ચર બુક.pdf · p.4` source chip.
  - Expand the `🔍 Pipeline Trace` debug panel to reveal the exact PDF page text retrieved from vector search.
  - **Key Talking Point:**
    > "The AI is not hallucinating from general internet knowledge — here is the exact official PDF document page it read to generate this answer."

---

## 01:15 – 02:00 | Agronomy Advisory & Safety Guardrails
- **Action:** Click the quick recommendation chip: `"🌱 ખાતરની માત્રા"` or ask:
  `"કપાસ માટે કેટલું ખાતર નાખવું?"`
- **System Behavior:**
  - AI bubble renders with uppercase intent pill `CROP_ADVICE`.
  - Notice the mandatory agronomic caution sentence prepended automatically:
    `"સ્થાનિક કૃષિ વૈજ્ઞાનિક અથવા KVK ના નિષ્ણાતની સલાહ લીધા બાદ જ ખાતર કે દવાનો ઉપયોગ કરવો."`
- **Key Talking Point:**
  > "Notice our safety guardrails. Before any chemical dosage is recommended, the system automatically prepends a mandatory caution instructing the farmer to verify with their local KVK agronomist."

---

## 02:00 – 02:30 | Real-Time Weather & APMC Mandi Price Cards
- **Action 1 (Mandi Price):** Click `"💰 કપાસનો ભાવ"` or ask `"આજે રાજકોટ માં કપાસનો ભાવ કેટલો?"`.
  - System renders high-contrast APMC price card: **Modal ₹1,550 / 20 kg** (Min ₹1,480, Max ₹1,620).
- **Action 2 (Weather):** Select `"જૂનાગઢ"` from the sidebar district selector and click `"☔ વાતાવરણ"`.
  - System renders live Open-Meteo weather advisory card for Junagadh (24.8°C, Humidity 97%) with Gujarati farming advice:
    `"હવામાં ભેજનું પ્રમાણ વધુ હોવાથી ફૂગજન્ય રોગ થવાની શક્યતા છે."`

---

## 02:30 – 03:00 | Out-of-Domain Strict Fallback & Resilience Demo
- **Action:** Ask an out-of-domain question:
  `"અંતરિક્ષ રોકેટ સાયન્સ વિશે માહિતી આપો"`
- **System Behavior:**
  - Vector similarity returns below threshold (0.40).
  - System outputs exact KVK fallback sentence:
    `"મને આ વિષય પર પૂરતી માહિતી નથી. કૃપા કરી તમારા નજીકના કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) નો સંપર્ક કરો."`
- **Final Talking Point:**
  > "If information is not present in our ingested PDF knowledge base, the AI refuses to guess or make up facts — it directs the farmer straight to their nearest Krishi Vigyan Kendra. Grounded, safe, and voice-enabled."
