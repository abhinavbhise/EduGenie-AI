import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv()

API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()

if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash") if API_KEY else None
_EXECUTOR = ThreadPoolExecutor(max_workers=4)


def _fallback_response(prompt: str, reason: str) -> str:
    cleaned_prompt = " ".join(prompt.split())
    return (
        "# Quick Study Help\n\n"
        f"Gemini could not complete the request ({reason}).\n\n"
        f"**Prompt:** {cleaned_prompt}\n\n"
        "## What to do next\n"
        "- This is a local runtime issue, not a Vercel deployment issue\n"
        "- If the message mentions quota or rate limits, wait and retry or use a less busy API key\n"
        "- Restart the local server after changing environment variables\n"
        "- Make sure `GEMINI_API_KEY` is set and valid in your local `.env` file\n"
    )


def _classify_error(exc: Exception) -> str:
    message = f"{exc!r} {exc}".lower()

    if "quota" in message or "rate limit" in message or "resourceexhausted" in message:
        return "Gemini rate limit/quota exceeded"

    return "Gemini request failed"


def generate(prompt: str) -> str:
    if model is None:
        print("Gemini fallback: GEMINI_API_KEY is missing or empty.", file=sys.stderr)
        return _fallback_response(prompt, "missing GEMINI_API_KEY")

    future = _EXECUTOR.submit(model.generate_content, prompt)

    try:
        response = future.result(timeout=15)
    except FuturesTimeoutError:
        print("Gemini fallback: request timed out after 15s.", file=sys.stderr)
        return _fallback_response(prompt, "request timed out")
    except Exception as exc:
        print(f"Gemini fallback: {exc!r}", file=sys.stderr)
        return _fallback_response(prompt, _classify_error(exc))

    text = getattr(response, "text", "").strip()
    if text:
        return text

    print("Gemini fallback: empty response text returned.", file=sys.stderr)
    return _fallback_response(prompt, "empty response")
