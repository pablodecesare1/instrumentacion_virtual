import requests

def fetch_weather_caba():
    """
    Clima actual en CABA (aprox. Obelisco).
    Devuelve dict con temperatura, humedad, presión, viento, nubosidad, etc.
    """
    lat, lon = -34.6037, -58.3816  # CABA
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "America/Argentina/Buenos_Aires",
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "cloud_cover",
            "precipitation",
        ]),
    }

    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    cur = data.get("current", {})
    units = data.get("current_units", {})

    def pick(k, label):
        v = cur.get(k, None)
        u = units.get(k, "")
        if v is None:
            return [label, "N/D"]
        return [label, f"{v} {u}".strip()]

    return {
        "time": cur.get("time", "N/D"),
        "rows": [
            ["Ubicación", "CABA (Buenos Aires)"],
            ["Timestamp", cur.get("time", "N/D")],
            pick("temperature_2m", "Temperatura"),
            pick("relative_humidity_2m", "Humedad"),
            pick("surface_pressure", "Presión"),
            pick("wind_speed_10m", "Viento (vel)"),
            pick("wind_direction_10m", "Viento (dir)"),
            pick("cloud_cover", "Nubosidad"),
            pick("precipitation", "Precipitación"),
        ]
    }
