from fastapi import Header, HTTPException
from backend.security.api_keys import API_KEYS


async def get_current_user(x_api_key: str | None = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    user = API_KEYS.get(x_api_key)
    if not user or not user.get("active"):
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user
