# backend/providers/base.py
from abc import ABC, abstractmethod


class MapProvider(ABC):
    @abstractmethod
    async def search_places(self, query: str, location: str, limit: int):
        raise NotImplementedError

    @abstractmethod
    async def get_directions(self, origin: str, destination: str):
        raise NotImplementedError
