# backend/security/api_keys.py

from typing import Dict
import secrets


API_KEYS: Dict[str, dict] = {}
EMAIL_INDEX: Dict[str, str] = {}


def generate_api_key() -> str:
    return "dir_live_" + secrets.token_urlsafe(32)


def register_api_key(email: str, rate_limit: int = 10) -> str:
    # Prevent duplicate keys per email
    if email in EMAIL_INDEX:
        raise ValueError("An API key already exists for this email")

    api_key = generate_api_key()

    API_KEYS[api_key] = {
        "owner": email,
        "rate_limit": rate_limit,
        "active": True,
    }

    EMAIL_INDEX[email] = api_key

    return api_key
