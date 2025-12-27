# backend/providers/photon.py

import asyncio
import httpx
import time
from typing import List

from backend.config import PHOTON_BASE_URL, HTTP_REQUEST_TIMEOUT


class PhotonProvider:
    """
    Map provider backed by Photon (OpenStreetMap data).

    Used for:
    - place search
    - geocoding (text -> coordinates)

    This provider applies a regional bias toward Indonesia
    to avoid ambiguous global matches.
    """

    # Jakarta / Indonesia bias (safe defaults)
    _BIAS_LAT = -6.2
    _BIAS_LON = 106.8

    # Indonesia bounding box (west, south, east, north)
    _INDONESIA_BBOX = "95.0,-11.0,141.0,6.0"

    def __init__(self):
        self._last_request = 0.0
        self._min_interval = 1.0  # 1 request / second (Photon-friendly)

    async def _rate_limit(self):
        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request = time.time()

    async def search_places(
        self,
        query: str,
        location: str,
        limit: int,
    ) -> List[dict]:
        if not query:
            raise ValueError("Query must be provided")

        # Combine query + location textually
        search_text = f"{query} {location}".strip()

        params = {
            "q": search_text,
            "limit": limit,
            "lat": self._BIAS_LAT,
            "lon": self._BIAS_LON,
            "bbox": self._INDONESIA_BBOX,
        }

        headers = {
            "User-Agent": ("directio/1.0 " "(local demo; contact: nhilmiaji@gmail.com)"),
            "Accept": "application/json",
        }

        timeout = httpx.Timeout(
            connect=5.0,
            read=HTTP_REQUEST_TIMEOUT,
            write=5.0,
            pool=5.0,
        )

        await self._rate_limit()

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(
                    PHOTON_BASE_URL,
                    params=params,
                    headers=headers,
                )
                resp.raise_for_status()

        except httpx.ReadTimeout:
            raise ValueError("Photon search timed out")

        except httpx.HTTPStatusError as e:
            raise ValueError(f"Photon search failed with status {e.response.status_code}")

        except httpx.RequestError as e:
            raise ValueError(f"Photon request error: {e}")

        data = resp.json()

        if "features" not in data or not isinstance(data["features"], list):
            raise ValueError("Unexpected Photon response format")

        return data["features"]
