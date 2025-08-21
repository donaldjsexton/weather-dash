import httpx
from typing import Optional, Tuple

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

async def geocode_city(city: str) -> Optional[Tuple[float, float, str, str]]:
    # returns (lat, lon, city_name, country_code) or None
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(GEOCODE_URL, params=params)
        r.raise_for_status()
        data = r.json()
    results = (data or {}).get("results") or []
    if not results:
        return None
    first = results[0]
    return (
        float(first["latitude"]),
        float(first["longitude"]),
        first.get("name", city),
        first.get("country_code", ""),
    )

