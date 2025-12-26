# backend/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import List, Literal, Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class LLMIntent(BaseModel):
    intent: Literal["find_places", "get_directions"]
    query: Optional[str] = None
    location: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=10)


class Place(BaseModel):
    name: str
    lat: float
    lon: float
    address: str
    map_url: str


class PlacesResponse(BaseModel):
    intent: Literal["find_places"]
    summary: str
    places: List[Place]


class ErrorResponse(BaseModel):
    error: str


class Route(BaseModel):
    distance_meters: float
    duration_seconds: float
    geometry: dict  # GeoJSON LineString


class DirectionsResponse(BaseModel):
    intent: Literal["get_directions"]
    summary: str
    route: Route


class CreateKeyRequest(BaseModel):
    email: EmailStr
