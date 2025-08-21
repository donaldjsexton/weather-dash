from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

from app.services.weather import fetch_current
from app.services.geocode import geocode_city

app = FastAPI(title="WeatherDash", version="0.2.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

def _f(s: str | None) -> float | None:
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None

@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    city: str | None = None,
    lat: str | None = None,
    lon: str | None = None,
    units: str = "imperial",
):
    data, error = None, None
    try:
        flat, flon = _f(lat), _f(lon)
        if flat is not None and flon is not None:
            data = await fetch_current(flat, flon, units)
        elif city:
            geo = await geocode_city(city)
            if not geo:
                error = f"Could not geocode '{city}'."
            else:
                glat, glon, gcity, country = geo
                data = await fetch_current(glat, glon, units)
                data["city"], data["country"] = gcity, country
    except Exception as e:
        error = str(e)
    return templates.TemplateResponse("index.html", {"request": request, "data": data, "error": error})

@app.get("/api/weather")
async def api_weather(
    city: str | None = None,
    lat: str | None = None,
    lon: str | None = None,
    units: str = "imperial",
):
    flat, flon = _f(lat), _f(lon)
    try:
        if flat is not None and flon is not None:
            return JSONResponse(await fetch_current(flat, flon, units))
        if city:
            geo = await geocode_city(city)
            if not geo:
                raise HTTPException(status_code=404, detail="City not found")
            glat, glon, gcity, country = geo
            data = await fetch_current(glat, glon, units)
            data["city"], data["country"] = gcity, country
            return JSONResponse(data)
        raise HTTPException(status_code=400, detail="Provide city or lat/lon")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.get("/healthz")
async def healthz():
    return {"ok": True, "version": app.version}

