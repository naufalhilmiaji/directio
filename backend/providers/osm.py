# backend/providers/osm.py

import asyncio
import httpx
from typing import List

from backend.config import (
    OSRM_BASE_URL,
    HTTP_REQUEST_TIMEOUT,
)


class OSMProvider:
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

    async def get_directions(self, origin: tuple, destination: tuple):
        """
        origin, destination: (lat, lon)
        """
        lat1, lon1 = origin
        lat2, lon2 = destination

        url = f"{OSRM_BASE_URL}/route/v1/driving/" f"{lon1},{lat1};{lon2},{lat2}"

        params = {
            "overview": "full",
            "geometries": "geojson",
        }

        timeout = httpx.Timeout(
            connect=5.0,
            read=HTTP_REQUEST_TIMEOUT,
            write=5.0,
            pool=5.0,
        )

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()

        except httpx.ReadTimeout:
            raise ValueError("OSRM routing timeout")

        except httpx.HTTPStatusError as e:
            raise ValueError(f"OSRM routing failed with status {e.response.status_code}")

        data = resp.json()

        if "routes" not in data or not data["routes"]:
            raise ValueError("No route found")

        route = data["routes"][0]

        return {
            "distance": route["distance"],
            "duration": route["duration"],
            "geometry": route["geometry"],
        }
