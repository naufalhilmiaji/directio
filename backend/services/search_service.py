# backend/services/search_service.py
from backend.schemas import Place


def normalize_osm_places(raw_places):
    places = []

    for p in raw_places:
        name = p.get("display_name", "Unknown")
        lat = float(p["lat"])
        lon = float(p["lon"])

        place = Place(
            name=name,
            lat=lat,
            lon=lon,
            address=name,
            map_url=f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}",
        )
        places.append(place)

    return places


def normalize_photon_places(features):
    places = []

    for feature in features:
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        coords = geometry.get("coordinates", [])
        if len(coords) != 2:
            continue

        lon, lat = coords

        name = props.get("name") or props.get("street") or props.get("city") or "Unknown place"

        address_parts = [
            props.get("street"),
            props.get("city"),
            props.get("country"),
        ]
        address = ", ".join([p for p in address_parts if p])

        places.append(
            Place(
                name=name,
                lat=lat,
                lon=lon,
                address=address or name,
                map_url=f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}",
            )
        )

    return places


async def geocode_first(provider, query: str):
    results = await provider.search_places(query=query, location="", limit=1)
    if not results:
        raise ValueError(f"Could not geocode location: {query}")

    feature = results[0]
    coords = feature["geometry"]["coordinates"]
    lon, lat = coords
    return lat, lon
