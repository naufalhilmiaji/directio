# backend/providers/photon.py

import asyncio
import httpx
import time
from typing import List

from backend.config import PHOTON_BASE_URL, HTTP_REQUEST_TIMEOUT


class PhotonProvider:
    """
    Map provider backed by Photon (OpenStreetMap data).
    Suitable for backend and LLM-driven usage.
    """

    def __init__(self):
        self._last_request = 0.0
        self._min_interval = 0.5  # seconds

    async def search_places(self, query: str, location: str, limit: int) -> List[dict]:
        if not query:
            raise ValueError("Query must be provided")

        search_text = f"{query} {location}" if location else query

        params = {
            "q": search_text,
            "limit": limit,
        }

        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request = time.time()

        timeout = httpx.Timeout(
            connect=5.0,
            read=HTTP_REQUEST_TIMEOUT,
            write=5.0,
            pool=5.0,
        )

        headers = {
            "User-Agent": "LocalLLM-Maps/1.0 (learning project; contact: nhilmiaji@gmail.com)",
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(
                    PHOTON_BASE_URL,
                    params=params,
                    headers=headers,
                )
                resp.raise_for_status()

        except httpx.ReadTimeout:
            raise ValueError("Photon search timeout")

        except httpx.HTTPStatusError as e:
            raise ValueError(f"Photon search failed with status {e.response.status_code}")

        except httpx.RequestError:
            raise ValueError("Photon search request error")

        data = resp.json()

        if "features" not in data or not isinstance(data["features"], list):
            raise ValueError("Unexpected Photon response format")

        return data["features"]
