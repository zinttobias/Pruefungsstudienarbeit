import folium
import requests

####################################### Open-Meteo Wetterdienst API###############################################

def getWeather(lat, lon):       # Wetterdaten abrufen für lat lon 
    
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

# Funktion zur Bestimmung der Kreisfarbe anhand der Temperatur am jeweiligen Ort

def weather_circle_style(temp):                        

    radius_circle = 600

    if temp is None or temp == "Keine Daten":
        return ("gray", radius_circle)
    if temp < 5:
        return ("blue", radius_circle)     # kalt
    elif temp < 15:
        return ("green", radius_circle)    # mild
    elif temp < 25:
        return ("orange", radius_circle)   # warm
    else:
        return ("red", radius_circle)      # sehr heiß
    
###############################################################################################################

# Funktion zum Hinzufügen eines Kreises um die Wetterinformationen zu visualisieren

def add_weather_circle(map_obj, coords, temperature, popup_text=""):

    color, radius = weather_circle_style(temperature)       # Farbe und Radius anhand Temperatur bestimmen

    folium.Circle(                                          # Kreis hinzufügen
        location = [coords[1], coords[0]],                    # lat, lon für den Kreis
        radius = radius,
        color = color,
        fill = True,
        fill_color = color,
        fill_opacity = 0.25,
        popup = popup_text
    ).add_to(map_obj)

###############################################################################################################

# Funktion zum Einfügen der Gesamten Wetterinformationen in die Folium Karte

def include_weather_to_folium(map_obj, coords_start, coords_ziel, coords_zs):

    zs_coords_weather = None

    start_weather = getWeather(coords_start[1], coords_start[0])      # Wetter am Startpunkt abrufen
    ziel_weather  = getWeather(coords_ziel[1], coords_ziel[0])        # Wetter am Zielpunkt abrufen

    if coords_zs is not None:
        zs_coords_weather = getWeather(coords_zs[1], coords_zs[0])      # Wetter am Zwischenstopp abrufen
        add_weather_circle(                                             # Temperaturkreis am Zwischenstopp   
            map_obj,
            coords_zs,
            zs_coords_weather["temperatur"],
            popup_text=f"Temperatur: {zs_coords_weather['temperatur']} °C"
        )

    add_weather_circle(                                                 # Temperaturkreis am Startpunkt
        map_obj,
        coords_start,
        start_weather["temperatur"],
        popup_text=f"Temperatur: {start_weather['temperatur']} °C"
    )

    add_weather_circle(                                                 # Temperaturkreis am Zielpunkt   
        map_obj,
        coords_ziel,
        ziel_weather["temperatur"],
        popup_text=f"Temperatur: {ziel_weather['temperatur']} °C"
    )
    return {
        "start_temp": start_weather["temperatur"],
        "ziel_temp": ziel_weather["temperatur"],
        "zs_temp": zs_coords_weather["temperatur"] if zs_coords_weather is not None else None,
    }

################################################################################################################