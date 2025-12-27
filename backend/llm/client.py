import json
import re
import httpx
import time
from backend.config import LLM_ENDPOINT, LLM_MODEL, LLM_REQUEST_TIMEOUT
from backend.schemas import LLMIntent


SYSTEM_PROMPT = """
You are an API planner.

Convert the user request into JSON ONLY.
Your response MUST be valid JSON.
Double-check commas, quotes, and braces before responding.
Do not explain.
Do not include markdown.
Do not include text outside JSON.

Supported intents:
- find_places
- get_directions

Intent selection rules:
- Use "get_directions" when the user expresses movement, travel, or navigation
  between two locations (e.g. "go to", "from ... to ...", "how do I get",
  "directions", "navigate").
- If the user expresses movement between two named places,
  you MUST choose "get_directions" even if the fields are ambiguous.
- Use "find_places" ONLY when the user is searching for places near a location,
  not when they want to travel between two locations.

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

Examples:

User: Where can I eat ramen near Sudirman Jakarta?

Response:
{
  "intent": "find_places",
  "query": "ramen",
  "location": "Sudirman Jakarta",
  "limit": 5
}

User: How do I get from Monas to Sudirman?

Response:
{
  "intent": "get_directions",
  "origin": "Monas Jakarta",
  "destination": "Sudirman Jakarta"
}

User: I want to go to Monumen Nasional Jakarta from Margo City Depok

Response:
{
  "intent": "get_directions",
  "origin": "Margo City Depok",
  "destination": "Monumen Nasional Jakarta"
}
"""


timeout = httpx.Timeout(
    connect=5.0,
    read=LLM_REQUEST_TIMEOUT,
    write=5.0,
    pool=5.0,
)


def parse_json_strict(text: str) -> dict:
    # Extract first JSON object from text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM output")

    json_text = match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}")


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
        data = parse_json_strict(raw)
    except httpx.ReadTimeout:
        raise ValueError("LLM timeout: model took too long to respond")

    except httpx.ConnectTimeout:
        raise ValueError("LLM connection timeout")

    except Exception as e:
        raise ValueError(f"LLM intent extraction failed: {e}") from e

    return LLMIntent.model_validate(data)
