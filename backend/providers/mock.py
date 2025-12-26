from backend.providers.base import MapProvider


class MockProvider(MapProvider):
    async def search_places(self, query, location, limit):
        return [
            {
                "name": "Mock Ramen Place",
                "lat": -6.2146,
                "lon": 106.8451,
                "address": "Sudirman Jakarta",
            }
        ]
