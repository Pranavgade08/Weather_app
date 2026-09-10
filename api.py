import json
import os
import urllib.error
import urllib.parse
import urllib.request

# =====================================================================
# API CONFIGURATION
# =====================================================================
# If you have an OpenWeatherMap API key, paste it here:
# (Get a free key from: https://home.openweathermap.org/api_keys)
API_KEY = "YOUR_API_KEY_HERE"

# Alternatively, set the environment variable OPENWEATHER_API_KEY
API_KEY = os.environ.get("OPENWEATHER_API_KEY", API_KEY)


def fetch_weather(city_name: str) -> dict:
    """
    Fetches live weather data for a city.
    - If OpenWeatherMap API_KEY is provided, uses OpenWeatherMap.
    - If API_KEY is default/empty, automatically uses free global weather providers (No API key needed).
    """
    cleaned_city = city_name.strip()
    if not cleaned_city:
        raise ValueError("Please enter a city name.")

    # 1. OpenWeatherMap if key is configured
    if API_KEY and API_KEY != "YOUR_API_KEY_HERE":
        return _fetch_openweathermap(cleaned_city, API_KEY)

    # 2. Free Open-Meteo & wttr.in fallback (No key required)
    try:
        return _fetch_open_meteo(cleaned_city)
    except LookupError:
        return _fetch_wttr(cleaned_city)


def _fetch_openweathermap(city_name: str, key: str) -> dict:
    """Fetches weather from OpenWeatherMap API."""
    params = {
        "q": city_name,
        "appid": key.strip(),
        "units": "metric"
    }
    url = f"https://api.openweathermap.org/data/2.5/weather?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "WeatherApp/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as http_err:
        if http_err.code == 404:
            raise LookupError(f"City '{city_name}' was not found. Please check spelling.")
        elif http_err.code == 401:
            raise PermissionError("Invalid OpenWeatherMap API key in api.py.")
        else:
            raise Exception(f"HTTP Error {http_err.code}: {http_err.reason}")
    except urllib.error.URLError:
        raise ConnectionError("Network error. Please check your internet connection.")


def _fetch_open_meteo(city_name: str) -> dict:
    """Fetches weather from Open-Meteo."""
    candidates = [city_name]
    words = city_name.split()
    if len(words) > 1:
        candidates.append(words[-1])  # e.g. "Sambhajinagar" for "Chhatrapati Sambhajinagar"
        candidates.append(words[0])

    location = None
    for cand in candidates:
        geo_params = {"name": cand, "count": 1, "language": "en", "format": "json"}
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?{urllib.parse.urlencode(geo_params)}"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "WeatherApp/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=6) as response:
                geo_data = json.loads(response.read().decode("utf-8"))
                results = geo_data.get("results", [])
                if results:
                    location = results[0]
                    break
        except Exception:
            continue

    if not location:
        raise LookupError(f"City '{city_name}' was not found.")

    lat = location.get("latitude")
    lon = location.get("longitude")
    matched_city = location.get("name", city_name)
    matched_country = location.get("country_code", location.get("country", ""))

    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }
    weather_url = f"https://api.open-meteo.com/v1/forecast?{urllib.parse.urlencode(weather_params)}"
    req_w = urllib.request.Request(weather_url, headers={"User-Agent": "WeatherApp/1.0"})

    with urllib.request.urlopen(req_w, timeout=8) as response:
        w_data = json.loads(response.read().decode("utf-8"))

    current = w_data.get("current", {})
    daily = w_data.get("daily", {})
    temp_max_list = daily.get("temperature_2m_max", [])
    temp_min_list = daily.get("temperature_2m_min", [])
    temp = current.get("temperature_2m", 0.0)
    wind_kmh = current.get("wind_speed_10m", 0.0)

    return {
        "_source": "open_meteo",
        "name": matched_city,
        "sys": {"country": matched_country},
        "main": {
            "temp": temp,
            "feels_like": current.get("apparent_temperature", temp),
            "temp_min": temp_min_list[0] if temp_min_list else temp,
            "temp_max": temp_max_list[0] if temp_max_list else temp,
            "humidity": current.get("relative_humidity_2m", 0),
        },
        "wind": {"speed": round(wind_kmh / 3.6, 1)},
        "weather_code": current.get("weather_code", 0)
    }


def _fetch_wttr(city_name: str) -> dict:
    """Fallback weather provider for global locations."""
    encoded = urllib.parse.quote(city_name)
    url = f"https://wttr.in/{encoded}?format=j1"
    req = urllib.request.Request(url, headers={"User-Agent": "WeatherApp/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        raise LookupError(f"City '{city_name}' was not found.")

    current = data.get("current_condition", [{}])[0]
    weather = data.get("weather", [{}])[0]
    area = data.get("nearest_area", [{}])[0]

    city = area.get("areaName", [{}])[0].get("value", city_name)
    country = area.get("country", [{}])[0].get("value", "")

    temp_c = float(current.get("temp_C", 0.0))
    feels_c = float(current.get("FeelsLikeC", temp_c))
    temp_min = float(weather.get("mintempC", temp_c))
    temp_max = float(weather.get("maxtempC", temp_c))
    humidity = int(current.get("humidity", 0))
    wind_kmh = float(current.get("windspeedKmph", 0.0))
    desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")

    return {
        "_source": "wttr",
        "name": city,
        "sys": {"country": country},
        "main": {
            "temp": temp_c,
            "feels_like": feels_c,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "humidity": humidity,
        },
        "wind": {"speed": round(wind_kmh / 3.6, 1)},
        "weather": [{"main": desc, "description": desc, "icon": ""}]
    }
