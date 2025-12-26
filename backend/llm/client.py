# backend/llm/client.py
import json
import httpx
import time
from backend.config import LLM_ENDPOINT, LLM_MODEL, LLM_REQUEST_TIMEOUT
from backend.schemas import LLMIntent


SYSTEM_PROMPT = """
You are an API planner.

Convert the user request into JSON ONLY.
Do not explain.
Do not include markdown.
Do not include text outside JSON.

Supported intents:
- find_places
- get_directions

Rules:
- For intent "find_places", you MUST include:
  - query (string)
  - location (string)
- For intent "get_directions", you MUST include:
  - origin (string)
  - destination (string)

If the user does not specify a location explicitly,
infer a reasonable city or area from the message.

Always return ALL required fields.

Example:

User: Where can I eat ramen near Sudirman Jakarta?

Response:
{
  "intent": "find_places",
  "query": "ramen",
  "location": "Sudirman Jakarta",
  "limit": 5
}
"""


timeout = httpx.Timeout(
    connect=5.0,
    read=LLM_REQUEST_TIMEOUT,
    write=5.0,
    pool=5.0,
)


async def extract_intent(message: str) -> LLMIntent:
    payload = {
        "model": LLM_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\nUser: {message}",
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        start = time.time()
        resp = await client.post(LLM_ENDPOINT, json=payload)
        resp.raise_for_status()
        elapsed = time.time() - start
        print(f"LLM request took {elapsed:.2f}s")

    resp_json = resp.json()

    if "response" not in resp_json:
        raise ValueError(f"LLM response missing 'response' field: {resp_json}")

    raw = resp_json["response"]

    if not raw.strip():
        raise ValueError("LLM returned empty response")

    try:
        data = json.loads(raw)
    except httpx.ReadTimeout:
        raise ValueError("LLM timeout: model took too long to respond")

    except httpx.ConnectTimeout:
        raise ValueError("LLM connection timeout")

    except Exception as e:
        raise ValueError(f"LLM intent extraction failed: {e}") from e

    return LLMIntent.model_validate(data)
