"""
hf_llm_service.py
-----------------
Wraps HuggingFace Inference API for:
  • LLM → meta-llama/Llama-3.2-3B-Instruct  (HF_TOKEN_LLM)

Generates Gujarati agricultural answers using RAG context.
"""

import logging
import httpx

from config import HF_API_BASE, HF_LLM_MODEL, HF_TOKEN_LLM

log = logging.getLogger(__name__)
_TIMEOUT = 90.0

_SYSTEM_PROMPT = """તમે એક અનુભવી કૃષિ સલાહકાર (Agriculture Advisor) છો જે ગુજરાત ના ખેડૂતોને મદદ કરો છો.

નિયમો:
1. હંમેશા ગુજરાતીમાં જવાબ આપો.
2. સરળ ભાષા વાપરો — ખેડૂત સમજી શકે.
3. જો context આપ્યો હોય, ફક્ત context ના આધારે જ જવાબ આપો.
4. ₹ amount, doses, deadlines clearly mention કરો.
5. જો ખ. ખ. (dosage) ની ભૂળ (mistake) ની ચિંતા હોય: "KVK / ખેત-નિષ્ણાત ની સલાહ લો" ઉમેરો.
6. Context ના જ્ઞ. (knowledge) ઉ. ઉ. (outside) ઉ. ઉ. ઉ. ઉ. (don't guess): "મને ઉ.ઉ. .... KVK (...) ઉ.ઉ." (contact KVK)."""


def generate_answer(question: str, context: str = "") -> str:
    """
    Call Llama-3.2-3B-Instruct on HF and return Gujarati answer text.
    Falls back to a polite Gujarati fallback string on error.
    """
    if not HF_TOKEN_LLM:
        return "API key ઉ.ઉ. (not configured). ikhedut.gujarat.gov.in ઉ.ઉ. (visit) ઉ.ઉ."

    prompt = _build_prompt(question, context)
    url = f"{HF_API_BASE}/{HF_LLM_MODEL}"

    try:
        resp = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {HF_TOKEN_LLM}",
                "Content-Type": "application/json",
            },
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 400,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "return_full_text": False,
                },
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        # HF returns list of dicts OR a dict depending on model
        if isinstance(data, list) and data:
            text = data[0].get("generated_text", "")
        elif isinstance(data, dict):
            text = data.get("generated_text", "")
        else:
            text = ""

        answer = text.strip()
        log.info("LLM answer (%d chars): %s...", len(answer), answer[:80])
        return answer if answer else _fallback()

    except httpx.HTTPStatusError as e:
        log.error("LLM HTTP %s: %s", e.response.status_code, e.response.text[:200])
        return _fallback()
    except Exception as e:
        log.error("LLM error: %s", e)
        return _fallback()


def _build_prompt(question: str, context: str) -> str:
    ctx_block = f"\nContext:\n{context}\n" if context.strip() else ""
    return (
        f"<|system|>\n{_SYSTEM_PROMPT}\n<|end|>\n"
        f"<|user|>\n{ctx_block}\nПрошение (Question): {question}\n<|end|>\n"
        f"<|assistant|>\n"
    )


def _fallback() -> str:
    return (
        "માફ કરશો, હાલ સર્વર ઉ.ઉ. (unavailable). "
        "ikhedut.gujarat.gov.in ઉ.ઉ. (visit) અથવા "
        "Kisan Helpline: 1800-180-1551 ઉ.ઉ. (call) ઉ.ઉ."
    )
