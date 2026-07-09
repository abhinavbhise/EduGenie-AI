import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv()

API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()

if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash") if API_KEY else None
_EXECUTOR = ThreadPoolExecutor(max_workers=4)


def _fallback_response(prompt: str) -> str:
    cleaned_prompt = " ".join(prompt.split())
    return (
        "# Quick Study Help\n\n"
        "I could not reach Gemini fast enough, so here is a short fallback answer.\n\n"
        f"**Prompt:** {cleaned_prompt}\n\n"
        "## What to do next\n"
        "- Try again in a moment\n"
        "- Shorten the prompt if it is very long\n"
        "- Check whether your Gemini API key is valid\n"
    )


def generate(prompt: str) -> str:
    if model is None:
        return _fallback_response(prompt)

    future = _EXECUTOR.submit(model.generate_content, prompt)

    try:
        response = future.result(timeout=15)
    except FuturesTimeoutError:
        return _fallback_response(prompt)
    except Exception:
        return _fallback_response(prompt)

    text = getattr(response, "text", "").strip()
    if text:
        return text

    return _fallback_response(prompt)
