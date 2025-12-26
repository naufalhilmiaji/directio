# backend/main.py
from fastapi import FastAPI, HTTPException
from backend.schemas import ChatRequest, ErrorResponse
from backend.services.chat_service import handle_chat

app = FastAPI(title="Local LLM Maps API")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        return await handle_chat(req.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        message = str(e) or "Internal error occurred"
        raise HTTPException(status_code=400, detail=message)
