from typing import Dict
import secrets

# In-memory key store (replace with DB later)
API_KEYS: Dict[str, dict] = {}


def generate_api_key() -> str:
    return "directio_" + secrets.token_urlsafe(32)


def register_api_key(email: str, rate_limit: int = 10) -> str:
    api_key = generate_api_key()
    API_KEYS[api_key] = {
        "owner": email,
        "rate_limit": rate_limit,
        "active": True,
    }
    return api_key
