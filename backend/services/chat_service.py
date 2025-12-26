# backend/services/chat_service.py
from backend.llm.client import extract_intent
from backend.providers.osm import OSMProvider
from backend.providers.photon import PhotonProvider
from backend.schemas import Place, PlacesResponse
from backend.services.search_service import normalize_osm_places, normalize_photon_places
from backend.utils.cache import TTLCache


provider = PhotonProvider()
cache = TTLCache(ttl_seconds=60)


def build_places_cache_key(intent) -> str:
    return f"find_places|{intent.query}|{intent.location}|{intent.limit}"


async def handle_chat(message: str):
    intent = await extract_intent(message)

    if intent.intent == "find_places":
        if not intent.query or not intent.location:
            raise ValueError("Missing query or location")

        cache_key = build_places_cache_key(intent)

        cached = cache.get(cache_key)
        if cached:
            print("Cache hit:", cache_key)

            return cached

        raw_places = await provider.search_places(
            query=intent.query,
            location=intent.location,
            limit=intent.limit,
        )

        places = normalize_photon_places(raw_places)

        response = PlacesResponse(
            intent="find_places",
            summary=f"{intent.query.title()} places near {intent.location}",
            places=places,
        )

        cache.set(cache_key, response)
        return response

    raise ValueError(f"Unsupported intent: {intent.intent}")
