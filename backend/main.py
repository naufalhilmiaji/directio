# backend/main.py

import logging
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Depends,
)
from pydantic import BaseModel, EmailStr

from backend.schemas import ChatRequest, CreateKeyRequest
from backend.services.chat_service import handle_chat
from backend.utils.rate_limit import SimpleRateLimiter
from backend.security.api_keys import register_api_key
from backend.security.auth import get_current_user


logger = logging.getLogger(__name__)

app = FastAPI(title="directio API")

# Rate limiters
chat_rate_limiter = SimpleRateLimiter(
    max_requests=10,
    window_seconds=60,
)

key_creation_limiter = SimpleRateLimiter(
    max_requests=3,
    window_seconds=3600,  # very strict
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/keys")
async def create_api_key(request: Request, payload: CreateKeyRequest):
    client_ip = request.client.host

    if not key_creation_limiter.allow(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many key creation requests",
        )

    api_key = register_api_key(payload.email)

    return {
        "message": "API key created. Store it securely; it will not be shown again.",
        "api_key": api_key,
    }


@app.post("/chat")
async def chat(
    request: Request,
    req: ChatRequest,
    user=Depends(get_current_user),
):
    """
    Main intent-driven endpoint.
    Authorization is done via API key.
    Rate limiting is enforced per user.
    """
    owner = user["owner"]

    if not chat_rate_limiter.allow(owner):
        raise HTTPException(status_code=429, detail="Too many requests")

    try:
        return await handle_chat(req.message)

    except ValueError as e:
        # Expected client-side errors
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        # Unexpected server-side errors
        logger.exception("Unhandled error in /chat")
        raise HTTPException(status_code=500, detail="Internal server error")
