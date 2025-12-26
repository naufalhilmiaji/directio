# backend/providers/osm.py

import asyncio
import httpx
from typing import List

from backend.config import (
    NOMINATIM_BASE_URL,
    OSRM_BASE_URL,
    USER_AGENT,
    HTTP_REQUEST_TIMEOUT,
)
from backend.providers.base import MapProvider


class OSMProvider(MapProvider):
    """
    OpenStreetMap provider using:
    - Nominatim for place search
    - OSRM for routing (later)
    """

    def __init__(self):
        # Simple in-process rate limiting (OSM policy-friendly)
        self._lock = asyncio.Lock()
        self._last_request_ts = 0.0
        self._min_interval = 1.5  # 1 request per second

    async def _rate_limit(self):
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_request_ts
            if elapsed < self._min_interval:
                await asyncio.sleep(self._min_interval - elapsed)
            self._last_request_ts = asyncio.get_event_loop().time()

    async def search_places(
        self,
        query: str,
        location: str,
        limit: int,
    ) -> List[dict]:
        if not query or not location:
            raise ValueError("Query and location must be provided")

        await self._rate_limit()

        params = {
            "q": f"{query} in {location}",
            "format": "json",
            "limit": limit,
            "addressdetails": 1,
        }

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        }

        timeout = httpx.Timeout(
            connect=5.0,
            read=HTTP_REQUEST_TIMEOUT,
            write=5.0,
            pool=5.0,
        )

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(
                    f"{NOMINATIM_BASE_URL}/search",
                    params=params,
                    headers=headers,
                )
                resp.raise_for_status()

        except httpx.ReadTimeout:
            raise ValueError("OSM search timeout")

        except httpx.HTTPStatusError as e:
            raise ValueError(f"OSM search failed with status {e.response.status_code}")

        except httpx.RequestError:
            raise ValueError("OSM search request error")

        data = resp.json()

        if not isinstance(data, list):
            raise ValueError("Unexpected OSM response format")

        return data

    async def get_directions(self, origin: str, destination: str):
        raise NotImplementedError("OSRM directions not implemented yet")
