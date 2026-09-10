from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class WeatherData:
    """Structured weather information for display."""
    city: str
    country: str
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int
    wind_speed: float
    condition: str
    description: str
    icon_symbol: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# WMO Weather interpretation codes
WMO_CODES = {
    0: ("Clear", "Clear sky", "☀️"),
    1: ("Mainly Clear", "Mainly clear", "🌤️"),
    2: ("Partly Cloudy", "Partly cloudy", "⛅"),
    3: ("Overcast", "Overcast", "☁️"),
    45: ("Fog", "Foggy", "🌫️"),
    48: ("Fog", "Depositing rime fog", "🌫️"),
    51: ("Drizzle", "Light drizzle", "🌦️"),
    53: ("Drizzle", "Moderate drizzle", "🌦️"),
    55: ("Drizzle", "Dense drizzle", "🌧️"),
    61: ("Rain", "Slight rain", "🌧️"),
    63: ("Rain", "Moderate rain", "🌧️"),
    65: ("Rain", "Heavy rain", "🌧️"),
    71: ("Snow", "Slight snow fall", "❄️"),
    73: ("Snow", "Moderate snow fall", "❄️"),
    75: ("Snow", "Heavy snow fall", "❄️"),
    77: ("Snow", "Snow grains", "❄️"),
    80: ("Rain Showers", "Slight rain showers", "🌦️"),
    81: ("Rain Showers", "Moderate rain showers", "🌧️"),
    82: ("Rain Showers", "Violent rain showers", "⛈️"),
    85: ("Snow Showers", "Slight snow showers", "❄️"),
    86: ("Snow Showers", "Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "Thunderstorm", "⛈️"),
    96: ("Thunderstorm", "Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm", "Thunderstorm with heavy hail", "⛈️"),
}


def get_weather_icon(condition: str, icon_code: str = "") -> str:
    cond_lower = condition.lower()
    is_night = icon_code.endswith("n")

    if "thunderstorm" in cond_lower:
        return "⛈️"
    elif "drizzle" in cond_lower:
        return "🌦️"
    elif "rain" in cond_lower:
        return "🌧️"
    elif "snow" in cond_lower:
        return "❄️"
    elif "clear" in cond_lower:
        return "🌙" if is_night else "☀️"
    elif "cloud" in cond_lower:
        if "few" in cond_lower or "scattered" in cond_lower:
            return "🌤️" if not is_night else "☁️"
        return "☁️"
    elif any(fog_type in cond_lower for fog_type in ["mist", "smoke", "haze", "dust", "fog", "sand"]):
        return "🌫️"
    else:
        return "🌤️"


def parse_weather_data(raw_data: dict) -> WeatherData:
    name = raw_data.get("name", "Unknown City")
    sys_data = raw_data.get("sys", {})
    country = sys_data.get("country", "")

    main_data = raw_data.get("main", {})
    temp = float(main_data.get("temp", 0.0))
    feels_like = float(main_data.get("feels_like", 0.0))
    temp_min = float(main_data.get("temp_min", temp))
    temp_max = float(main_data.get("temp_max", temp))
    humidity = int(main_data.get("humidity", 0))

    wind_data = raw_data.get("wind", {})
    wind_speed = float(wind_data.get("speed", 0.0))

    if raw_data.get("_source") == "open_meteo":
        w_code = raw_data.get("weather_code", 0)
        cond_info = WMO_CODES.get(w_code, ("Clear", "Clear sky", "☀️"))
        condition = cond_info[0]
        description = cond_info[1]
        icon_symbol = cond_info[2]
    else:
        weather_list = raw_data.get("weather", [{}])
        primary_weather = weather_list[0] if weather_list else {}
        condition = primary_weather.get("main", "Clear")
        description = primary_weather.get("description", condition).capitalize()
        icon_code = primary_weather.get("icon", "")
        icon_symbol = get_weather_icon(condition, icon_code)

    return WeatherData(
        city=name,
        country=country,
        temperature=round(temp, 1),
        feels_like=round(feels_like, 1),
        temp_min=round(temp_min, 1),
        temp_max=round(temp_max, 1),
        humidity=humidity,
        wind_speed=round(wind_speed, 1),
        condition=condition,
        description=description,
        icon_symbol=icon_symbol
    )
