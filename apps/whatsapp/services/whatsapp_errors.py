"""Helpers for Meta Graph API errors."""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


def normalize_wa_recipient(phone: str) -> str:
    """Meta expects digits only (E.164 without '+')."""
    return "".join(ch for ch in phone if ch.isdigit())


def parse_graph_error(response: httpx.Response) -> dict[str, Any]:
    try:
        data = response.json()
    except (json.JSONDecodeError, ValueError):
        return {"raw": response.text[:500]}
    err = data.get("error", data)
    return {
        "status": response.status_code,
        "message": err.get("message"),
        "type": err.get("type"),
        "code": err.get("code"),
        "error_subcode": err.get("error_subcode"),
        "fbtrace_id": err.get("fbtrace_id"),
    }


def log_graph_error(response: httpx.Response, *, context: str = "") -> dict[str, Any]:
    details = parse_graph_error(response)
    logger.error(
        "WhatsApp Graph API error%s: %s",
        f" ({context})" if context else "",
        details,
    )
    return details


def is_retryable_status(status_code: int) -> bool:
    return status_code in (429, 500, 502, 503, 504)
