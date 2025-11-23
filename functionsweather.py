import folium
import requests

####################################### Wetter-Codes von Open-Meteo ##############################################

WEATHER_DESCRIPTIONS = {                        # Wettercode weist einer Zahl eine Wetterbeschreibung zu  
    0: "Klarer Himmel",
    1: "Überwiegend klar",
    2: "Teilweise bewölkt",
    3: "Bedeckt",                               # Diese Codes stammen direkt von Open-Meteo
    45: "Nebel",
    48: "Reifnebel",
    51: "Leichter Nieselregen",
    53: "Mäßiger Nieselregen",
    55: "Starker Nieselregen",
    56: "Leichter gefrierender Nieselregen",
    57: "Starker gefrierender Nieselregen",
    61: "Leichter Regen",
    63: "Mäßiger Regen",
    65: "Starker Regen",
    66: "Leichter gefrierender Regen",
    67: "Starker gefrierender Regen",
    71: "Leichter Schneefall",
    73: "Mäßiger Schneefall",
    75: "Starker Schneefall",
    77: "Schneekörner",
    80: "Leichter Regenschauer",
    81: "Mäßiger Regenschauer",
    82: "Heftiger Regenschauer",
    85: "Leichter Schneeschauer",
    86: "Starker Schneeschauer",
    95: "Gewitter",
    96: "Gewitter mit leichtem Hagel",
    99: "Gewitter mit starkem Hagel"
}

####################################### Wettercode in Text umwandeln #############################################

def turn_code_in_text(dictionary, weather_code, default = None):
    if weather_code in dictionary:
        return dictionary[weather_code]
    else:
        return default
    
####################################### Open-Meteo Wetterdienst API ##############################################

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

        temp = data["current_weather"]["temperature"]                   # Temperatur in °C 
        time = data["current_weather"]["time"]                          # Zeit der Wetterabfrage
        weather_code = int(data["current_weather"]["weathercode"])      # Wettercode 
        windspeed = data["current_weather"]["windspeed"]                # Windstärke in km/h
        winddirection = data["current_weather"]["winddirection"]        # Windrichtung in Grad

        weather_description = turn_code_in_text(WEATHER_DESCRIPTIONS, weather_code, default = "Keine Daten vorhanden")

        return {"temperatur": float(temp),                              # Rückgabe der Wetterdaten als Dictionary
                "zeit": time,
                "Wetterbeschreibung": weather_description,
                "Windgeschwindigkeit_kmh": float(windspeed),
                "Windrichtung_grad": float(winddirection)
                }
    
    except Exception as e:                                              # Falls ein Fehler auftritt
        print("Wetter-Fehler:", e)
        return {"temperatur": None,
                "zeit": None
                }

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
        location = [coords[1], coords[0]],                  # lat, lon für den Kreis
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

    start_weather = getWeather(coords_start[1], coords_start[0])        # Wetter am Startpunkt abrufen
    ziel_weather  = getWeather(coords_ziel[1], coords_ziel[0])          # Wetter am Zielpunkt abrufen

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
    return {                                                            # Rückgabe der Wetterdaten als Dictionary    
        "start_temp": start_weather["temperatur"],
        "start_weather_text": start_weather["Wetterbeschreibung"],
        "start_wind_speed": start_weather["Windgeschwindigkeit_kmh"],
        "start_wind_direction": start_weather["Windrichtung_grad"],
        
        "ziel_temp": ziel_weather["temperatur"],
        "ziel_weather_text": ziel_weather["Wetterbeschreibung"],
        "ziel_wind_speed": ziel_weather["Windgeschwindigkeit_kmh"],
        "ziel_wind_direction": ziel_weather["Windrichtung_grad"],

        "zs_temp": zs_coords_weather["temperatur"] if zs_coords_weather is not None else None,
        "zs_weather_text": zs_coords_weather["Wetterbeschreibung"] if zs_coords_weather is not None else None,
        "zs_wind_speed": zs_coords_weather["Windgeschwindigkeit_kmh"] if zs_coords_weather is not None else None,
        "zs_wind_direction": zs_coords_weather["Windrichtung_grad"] if zs_coords_weather is not None else None
    }

################################################################################################################