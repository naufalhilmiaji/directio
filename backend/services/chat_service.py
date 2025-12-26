# backend/services/chat_service.py

import logging

from fastapi import HTTPException

from backend.llm.client import extract_intent
from backend.providers.openstreetmap import OpenStreetMapProvider
from backend.schemas import DirectionsResponse, PlacesResponse, Route
from backend.services.search_service import normalize_photon_places
from backend.utils.cache import TTLCache


logger = logging.getLogger(__name__)

provider = OpenStreetMapProvider()
cache = TTLCache(ttl_seconds=60)


def _normalize(value: str) -> str:
    return value.strip().lower()


def build_places_cache_key(intent) -> str:
    return f"find_places|{_normalize(intent.query)}|{_normalize(intent.location)}|{intent.limit}"


def build_directions_cache_key(intent) -> str:
    return f"get_directions|{_normalize(intent.origin)}|{_normalize(intent.destination)}"


async def handle_chat(message: str):
    MAX_MESSAGE_LENGTH = 500

    if len(message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=400, detail="Message too long")

    intent = await extract_intent(message)

    if intent.intent == "find_places":
        if not intent.query or not intent.location:
            raise ValueError("Missing query or location")

        cache_key = build_places_cache_key(intent)
        cached = cache.get(cache_key)
        if cached:
            logger.debug("Cache hit (places): %s", cache_key)
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

    if intent.intent == "get_directions":
        if not intent.origin or not intent.destination:
            raise ValueError("Missing origin or destination")

        cache_key = build_directions_cache_key(intent)
        cached = cache.get(cache_key)
        if cached:
            logger.debug("Cache hit (directions): %s", cache_key)
            return cached

        origin_coords = await provider.geocode(intent.origin)
        destination_coords = await provider.geocode(intent.destination)

        route_data = await provider.get_directions(
            origin=origin_coords,
            destination=destination_coords,
        )

        response = DirectionsResponse(
            intent="get_directions",
            summary=f"Directions from {intent.origin} to {intent.destination}",
            route=Route(
                distance_meters=route_data["distance"],
                duration_seconds=route_data["duration"],
                geometry=route_data["geometry"],
            ),
        )

        cache.set(cache_key, response)
        return response

    raise ValueError(f"Unsupported intent: {intent.intent}")
