import httpx
from typing import Any, Dict
from app.services.cache import cache_get, cache_set

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL = 300

WX = {
    0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Drizzle (light)", 53: "Drizzle (mod)", 55: "Drizzle (dense)",
    56: "Freezing drizzle (light)", 57: "Freezing drizzle (dense)",
    61: "Rain (light)", 63: "Rain (mod)", 65: "Rain (heavy)",
    66: "Freezing rain (light)", 67: "Freezing rain (heavy)",
    71: "Snow (light)", 73: "Snow (mod)", 75: "Snow (heavy)",
    77: "Snow grains",
    80: "Rain showers (light)", 81: "Rain showers (mod)", 82: "Rain showers (violent)",
    85: "Snow showers (light)", 86: "Snow showers (heavy)",
    95: "Thunderstorm", 96: "Thunderstorm (hail)", 99: "Thunderstorm (hail heavy)",
}

def _units(units: str) -> Dict[str, str]:
    if units == "imperial":
        return {"temperature_unit": "fahrenheit", "wind_speed_unit": "mph"}
    return {"temperature_unit": "celsius", "wind_speed_unit": "ms"}

async def fetch_current(lat: float, lon: float, units: str = "imperial") -> Dict[str, Any]:
    cache_key = f"wx2:{lat:.4f}:{lon:.4f}:{units}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m,weather_code",
        "timezone": "auto",
        **_units(units),
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(FORECAST_URL, params=params)
        r.raise_for_status()
        data = r.json()

    cur = (data or {}).get("current") or {}
    code = cur.get("weather_code")
    normalized = {
        "city": None,
        "country": None,
        "temp": cur.get("temperature_2m"),
        "feels_like": cur.get("apparent_temperature"),
        "temp_min": None,
        "temp_max": None,
        "humidity": cur.get("relative_humidity_2m"),
        "pressure": cur.get("pressure_msl"),
        "wind_speed": cur.get("wind_speed_10m"),
        "wind_deg": cur.get("wind_direction_10m"),
        "weather": WX.get(code, f"Code {code}"),
        "icon": None,
        "timezone": data.get("timezone"),
        "dt": cur.get("time"),
        "units": units,
        "lat": lat,
        "lon": lon,
    }
    cache_set(cache_key, normalized, ttl=CACHE_TTL)
    return normalized

