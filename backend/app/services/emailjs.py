from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Optional

import httpx

from app.core.config import settings

EMAILJS_API_URL = "https://api.emailjs.com/api/v1.0/email/send"
REQUEST_TIMEOUT_SECONDS = 10.0

logger = logging.getLogger(__name__)


def is_emailjs_configured() -> bool:
    return bool(
        settings.emailjs_service_id
        and settings.emailjs_public_key
        and settings.emailjs_template_account_change
    )


def send_account_change_email(
    *,
    to_email: str,
    to_name: Optional[str],
    change_type: str,
    changed_at: Optional[datetime] = None,
) -> bool:
    if not is_emailjs_configured():
        return False

    when = changed_at or datetime.now(timezone.utc)
    template_params = {
        "to_email": to_email,
        "to_name": to_name or to_email,
        "change_type": change_type,
        "changed_at": when.isoformat(),
        "app_name": "Corpo Padel",
    }

    payload = {
        "service_id": settings.emailjs_service_id,
        "template_id": settings.emailjs_template_account_change,
        "user_id": settings.emailjs_public_key,
        "template_params": template_params,
    }

    headers = {"Content-Type": "application/json"}
    if settings.emailjs_private_key:
        payload["accessToken"] = settings.emailjs_private_key

    try:
        response = httpx.post(
            EMAILJS_API_URL,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        resp = exc.response
        body = None
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        logger.error(
            "EmailJS send failed: status=%s body=%s",
            resp.status_code,
            body,
        )
        return False
    except Exception:
        logger.exception("EmailJS send failed (unexpected)")
        return False

    return True
