import os
from datetime import datetime, timedelta, timezone

import httpx

DEFAULT_N8N_REMINDER_WEBHOOK_URL = "https://edugenie.app.n8n.cloud/webhook/edugenie-remind"


def _build_reminder_payload(email: str, time: str, reminder: str) -> dict:
    now = datetime.now().astimezone()
    hour, minute = (int(part) for part in time.split(":", 1))

    scheduled_for = now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0,
    )

    if scheduled_for <= now:
        scheduled_for += timedelta(days=1)

    delay_seconds = max(0, int((scheduled_for - now).total_seconds()))

    return {
        "email": email,
        "time": time,
        "reminder": reminder,
        "scheduled_for": scheduled_for.isoformat(),
        "delay_seconds": delay_seconds,
        "timezone": now.tzinfo.tzname(now) if now.tzinfo else "local",
        "source": "EduGenie AI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def send_reminder_to_n8n(email: str, time: str, reminder: str) -> dict:
    webhook_url = os.getenv("N8N_REMINDER_WEBHOOK_URL", "").strip() or DEFAULT_N8N_REMINDER_WEBHOOK_URL

    payload = _build_reminder_payload(email, time, reminder)

    if not webhook_url:
        return {
            "configured": False,
            "delivered": False,
            "message": "N8N_REMINDER_WEBHOOK_URL is not set yet. The reminder payload was captured locally.",
            "payload": payload,
        }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(webhook_url, json=payload)
        response.raise_for_status()

    return {
        "configured": True,
        "delivered": True,
        "message": "Reminder scheduled in n8n successfully.",
        "payload": payload,
    }
