# directio

**directio** is a backend service that converts natural-language intent into
map-based place search and directions.

It uses a **local large language model (LLM)** to understand what the user wants,
then resolves that intent into concrete geographic results using
**OpenStreetMap-based data**.

The system is designed to be deterministic, provider-agnostic, and suitable for
applications that need structured map responses without relying on hosted LLM
APIs or paid map services.

---

## What directio does

- Accepts natural-language queries such as:
  - “Where can I eat ramen near Sudirman?”
  - “Find coffee shops around my office”
- Extracts structured intent using a **locally running LLM**
- Resolves that intent into real places or routes via map providers
- Returns clean, predictable JSON responses ready for frontend consumption

directio is intentionally scoped as a **backend service**, not a UI.

---

## Architecture

directio is designed as a small, composable backend with clear separation of
responsibilities.

At a high level, the system follows a simple pipeline:

```

User input → Intent extraction → Map resolution → Structured response

````

### Core components

- **API layer (FastAPI)**  
  Exposes a minimal JSON API and handles request validation and error mapping.

- **Intent engine (Local LLM)**  
  A locally running LLM is used exclusively to extract structured intent
  (e.g. place search or directions) from natural-language input.  
  The model does not access external services directly.

- **Service layer**  
  Orchestrates intent handling, caching, and provider selection.
  This layer contains the application logic.

- **Map providers**  
  Pluggable provider implementations resolve geographic intent into real-world
  data.  
  The current implementation uses OpenStreetMap-based services, with the design
  allowing additional providers to be added without changing core logic.

- **Caching layer**  
  A lightweight, in-memory TTL cache reduces repeated external requests and
  improves response latency.

### Design principles

- **Provider-agnostic**  
  Map services are abstracted behind a common interface to avoid vendor lock-in.

- **LLM isolation**  
  The LLM is responsible only for intent extraction. All side effects and
  external calls are handled by deterministic code.

- **Rate-limit aware**  
  External map services are accessed conservatively, with caching and throttling
  to respect usage policies.

- **Structured outputs**  
  All responses are returned as predictable JSON objects suitable for frontend
  consumption.

---

## Example API usage

### Request

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Where can I eat ramen near Sudirman Jakarta?"}'
````

### Response

```json
{
  "intent": "find_places",
  "summary": "Ramen places near Sudirman Jakarta",
  "places": [
    {
      "name": "Ramen 38",
      "lat": -6.2275566,
      "lon": 106.809542,
      "address": "Sudirman Central Business District Northway, Jakarta, Indonesia",
      "map_url": "https://www.openstreetmap.org/?mlat=-6.2275566&mlon=106.809542#map=18/-6.2275566/106.809542"
    }
  ]
}
```

---

## Requirements

* Python 3.10+
* A local LLM runtime (e.g. Ollama)
* Internet access for map data

No API keys or billing setup are required.

---

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
uvicorn backend.main:app
```

The API will be available at:

```
http://127.0.0.1:8000
```

---

## Project status

directio is currently focused on:

* Intent-driven place search
* Stable backend architecture
* Clean API contracts

Future work may include:

* Route and direction handling
* Additional map providers
* Persistent caching (e.g. Redis)
* Frontend integration examples

---

## Why local LLMs

directio intentionally uses a **local LLM** to:

* Avoid external LLM dependencies
* Keep intent extraction deterministic and inspectable
* Maintain full control over data flow and failure modes

The LLM is treated as a pure intent parser, not a decision-maker.

---

## License

MIT License.
