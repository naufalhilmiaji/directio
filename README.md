# directio

**directio** is an API that turns natural-language requests into **places and directions** using open map data.

You send a sentence like:

> “Where can I eat ramen near Sudirman Jakarta?”

And get back structured, map-ready results.

directio uses a **local LLM** for intent understanding and **OpenStreetMap-based services** for maps and routing.
No hosted LLM APIs. No paid map services.

---

## What can I do with directio?

* Find places by natural language
  *“Find coffee shops near my office”*
* Get directions between locations
  *“How do I get from Monas to Sudirman?”*
* Build map-based apps without writing search or routing logic
* Use your **own API key** with per-user rate limits

directio is a **backend API**, designed to be consumed by web or mobile apps.

---

## Quick start

### 1️⃣ Run the server

```bash
pip install -r requirements.txt
uvicorn backend.main:app
```

The API will be available at:

```
http://127.0.0.1:8000
```

---

### 2️⃣ Create an API key (one time)

directio uses API-key authentication.
Each user has **one API key**.

```bash
curl -X POST http://127.0.0.1:8000/keys \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com"}'
```

Response:

```json
{
  "message": "API key created. Store it securely; it will not be shown again.",
  "api_key": "directio_xxxxxxxxxxxxxxxxxxxxx"
}
```

⚠️ Save this key. It cannot be recovered later.

---

### 3️⃣ Make a request

Use your API key in the `X-API-Key` header.

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: directio_xxxxxxxxxxxxxxxxxxxxx" \
  -d '{"message":"Where can I eat ramen near Sudirman Jakarta?"}'
```

---

## Example responses

### Place search

```json
{
  "intent": "find_places",
  "summary": "Ramen places near Sudirman Jakarta",
  "places": [
    {
      "name": "Ramen 38",
      "lat": -6.2275566,
      "lon": 106.809542,
      "address": "Jakarta, Indonesia",
      "map_url": "https://www.openstreetmap.org/?mlat=-6.2275566&mlon=106.809542"
    }
  ]
}
```

---

### Directions

```json
{
  "intent": "get_directions",
  "summary": "Directions from Monas Jakarta to Sudirman Jakarta",
  "route": {
    "distance_meters": 5200,
    "duration_seconds": 900,
    "geometry": {
      "type": "LineString",
      "coordinates": [...]
    }
  }
}
```

The route geometry can be rendered directly in map libraries like **Leaflet**.

---

## Authentication & rate limits

* Authentication is done via **API keys**
* One API key per email
* API keys are required for `/chat`
* Requests are rate-limited **per API key**
* Key creation (`/keys`) is IP-rate-limited to prevent abuse

If a limit is exceeded, the API returns:

```json
{
  "detail": "Too many requests"
}
```

---

## Why local LLMs?

directio uses a **local LLM only for intent extraction**.

* No user data sent to third-party LLM APIs
* Predictable behavior
* Full control over failures and latency

The LLM does **not** call map services directly — all external access is handled by deterministic backend code.

---

## Project status

directio is currently focused on:

* Stable intent extraction
* Place search
* Directions & routing
* Clean API contracts
* Safe usage limits

Planned improvements:

* Persistent API key storage
* Usage metrics per key
* Frontend examples
* Additional map providers

---

## License

MIT License.
