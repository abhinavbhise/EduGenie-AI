import asyncio

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path

# Import run_ai from graph module. Try relative import first, then absolute,
# then try importing via importlib and adjusting sys.path to include the
# package directory so linters/IDE can resolve it.
try:
    from .graph import run_ai  # type: ignore
    from .n8n import send_reminder_to_n8n  # type: ignore
except Exception:
    try:
        from graph import run_ai
        from n8n import send_reminder_to_n8n
    except Exception:
        import importlib
        import sys
        from pathlib import Path

        project_root = Path(__file__).resolve().parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        graph_mod = importlib.import_module("graph")
        run_ai = getattr(graph_mod, "run_ai")
        n8n_mod = importlib.import_module("n8n")
        send_reminder_to_n8n = getattr(n8n_mod, "send_reminder_to_n8n")

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="EduGenie AI")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class AIRequest(BaseModel):
    feature: str
    prompt: str
    difficulty: str


class ReminderRequest(BaseModel):
    email: str
    time: str
    reminder: str


def _generation_timeout(feature: str) -> int:
    if feature == "Quiz":
        return 25
    if feature == "Flashcards":
        return 18
    return 15


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.post("/generate")
async def generate(data: AIRequest):
    timeout_seconds = _generation_timeout(data.feature)

    try:
        answer = await asyncio.wait_for(
            asyncio.to_thread(
                run_ai,
                data.feature,
                data.prompt,
                data.difficulty,
            ),
            timeout=timeout_seconds,
        )
    except asyncio.TimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="AI generation took too long. Please try again with a shorter prompt or simpler quiz.",
        ) from exc

    return {
        "response": answer
    }


@app.post("/remind")
async def remind(data: ReminderRequest):
    email = data.email.strip()
    time = data.time.strip()
    reminder = data.reminder.strip()

    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")

    if not reminder:
        raise HTTPException(status_code=400, detail="Reminder text is required.")

    if not time:
        raise HTTPException(status_code=400, detail="Reminder time is required.")

    try:
        delivery = await send_reminder_to_n8n(email=email, time=time, reminder=reminder)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Failed to reach the n8n webhook.") from exc

    return {
        "response": delivery["message"],
        "configured": delivery["configured"],
        "delivered": delivery["delivered"],
        "payload": delivery["payload"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
