import requests

WEATHER_DATA = {
    "name": "weather",
    "description": "Check current weather for a city",
    "type": 1,
    "options": [{
        "name": "city",
        "description": "City name (e.g. Warsaw, London)",
        "type": 3,
        "required": True
    }]
}

def cmd_weather(data):
    city = data["options"][0]["value"]
    
    # 1. Najpierw szukamy współrzędnych miasta
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    
    try:
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"):
            return {"type": 4, "data": {"content": f"❌ City **{city}** not found."}}
            
        location = geo_res["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        name = location["name"]
        country = location.get("country", "")
        
        # 2. Pobieramy pogodę
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&wind_speed_unit=kmh"
        w_res = requests.get(weather_url).json()
        
        current = w_res["current"]
        temp = current["temperature_2m"]
        feel = current["apparent_temperature"]
        humid = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        
        # Ikony pogody (WMO codes)
        code = current["weather_code"]
        icon = "☀️"
        if code in [1, 2, 3]: icon = "⛅"
        elif code in [45, 48]: icon = "🌫️"
        elif code in [51, 53, 55, 61, 63, 65]: icon = "🌧️"
        elif code in [71, 73, 75, 77]: icon = "❄️"
        elif code >= 95: icon = "⛈️"

        return {
            "type": 4,
            "data": {
                "embeds": [{
                    "title": f"{icon} Weather in {name}, {country}",
                    "color": 0x3498db,
                    "fields": [
                        {"name": "Temperature", "value": f"**{temp}°C** (Feels like {feel}°C)", "inline": True},
                        {"name": "Humidity", "value": f"{humid}%", "inline": True},
                        {"name": "Wind", "value": f"{wind} km/h", "inline": True}
                    ],
                    "footer": {"text": "Powered by Open-Meteo"}
                }]
            }
        }
            
    except Exception as e:
        return {"type": 4, "data": {"content": f"❌ Error fetching weather: {str(e)}"}}