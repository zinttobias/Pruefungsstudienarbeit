import folium
from wetterdienst.provider.dwd.observation import DwdObservationRequest
from wetterdienst import Settings

#############################################################################################################

# Open Meteo API kein Deutscher Wetterdienst die API ist einfach bodenlos



# Performance verbessern:
import requests

def getWeather(lat, lon):
    """
    Holt aktuelle Temperatur für lat/lon von Open-Meteo.
    Gibt Temperatur in °C zurück oder None, falls Fehler.
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
    )

    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        temp = data["current_weather"]["temperature"]
        time = data["current_weather"]["time"]

        return {"temperatur": float(temp), "zeit": time}

    except Exception as e:
        print("Wetter-Fehler:", e)
        return {"temperatur": None, "zeit": None}


##############################################################################################################

def weather_circle_style(temp):                         # Farbe und Radius bestimmen

    if temp is None or temp == "Keine Daten":
        return ("gray", 300)

    if temp < 5:
        return ("blue", 400)     # kalt
    elif temp < 15:
        return ("green", 500)    # mild
    elif temp < 25:
        return ("orange", 600)   # warm
    else:
        return ("red", 700)      # sehr heiß
    
###############################################################################################################

def add_weather_circle(map_obj, coords, temperature, popup_text=""):

    color, radius = weather_circle_style(temperature)       # Farbe & Radius anhand Temperatur bestimmen

    folium.Circle(                                          # Kreis hinzufügen
        location=[coords[1], coords[0]],                    # lat, lon
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.25,
        popup=popup_text
    ).add_to(map_obj)