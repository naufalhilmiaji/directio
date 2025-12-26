# backend/providers/openstreetmap.py

from backend.providers.base import MapProvider
from backend.providers.photon import PhotonProvider
from backend.providers.osm import OSMProvider


class OpenStreetMapProvider(MapProvider):
    """
    Composite provider that uses:
    - Photon for geocoding / place search
    - OSRM (via OSMProvider) for routing
    """

    def __init__(self):
        self._geocoder = PhotonProvider()
        self._router = OSMProvider()

    async def search_places(self, query: str, location: str, limit: int):
        return await self._geocoder.search_places(
            query=query,
            location=location,
            limit=limit,
        )

    async def get_directions(self, origin, destination):
        return await self._router.get_directions(
            origin=origin,
            destination=destination,
        )

    async def geocode(self, query: str):
        results = await self.search_places(query=query, location="", limit=1)
        if not results:
            raise ValueError(f"Could not geocode location: {query}")

        coords = results[0]["geometry"]["coordinates"]
        lon, lat = coords
        return lat, lon
