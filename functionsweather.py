import folium
import requests

####################################### Wetter-Codes von Open-Meteo ##############################################

WEATHER_DESCRIPTIONS = {                        # Wettercode weist einer Zahl eine Wetterbeschreibung zu
    0: "Klarer Himmel",
    1: "Überwiegend klar",
    2: "Teilweise bewölkt",
    3: "Bedeckt",
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

def turn_code_in_text(dictionary, weather_code, default=None):
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

        weather_description = turn_code_in_text(
            WEATHER_DESCRIPTIONS, weather_code, default="Keine Daten vorhanden"
        )

        return {
            "temperatur": float(temp),
            "zeit": time,
            "Wetterbeschreibung": weather_description,
            "Windgeschwindigkeit_kmh": float(windspeed),
            "Windrichtung_grad": float(winddirection)
        }

    except Exception as e:
        print("Wetter-Fehler:", e)
        return {"temperatur": None, "zeit": None}

######################################## Wettervorhersage Funktion ##############################################

def get_Weather_Prediction_for_duration_hours(lat, lon, start_time_hours, duration_hours):

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,weathercode,windspeed_10m,winddirection_10m"
        "&current_weather=true"
        "&timezone=Europe%2FBerlin"
        "&forecast_days=7"   # Open-Meteo liefert gerne viel -> wir schneiden später hart zu
    )

    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        hourly_times = data["hourly"]["time"]
        temperature_all = data["hourly"]["temperature_2m"]
        weather_code_all = data["hourly"]["weathercode"]
        wind_speed_all = data["hourly"]["windspeed_10m"]
        wind_dir_all = data["hourly"]["winddirection_10m"]

        now_time = data["current_weather"]["time"]

        if now_time in hourly_times:
            now_index = hourly_times.index(now_time)
        else:
            now_hour = str(now_time)[:13] + ":00"
            now_index = hourly_times.index(now_hour) if now_hour in hourly_times else 0

        start_index = now_index + int(start_time_hours)
        end_index = start_index + int(duration_hours)

        temperature_pred = temperature_all[start_index:end_index]
        weather_code_pred = weather_code_all[start_index:end_index]
        wind_speed_pred = wind_speed_all[start_index:end_index]
        wind_direction_pred = wind_dir_all[start_index:end_index]

        weather_description_pred = [
            turn_code_in_text(WEATHER_DESCRIPTIONS, int(code), default="Keine Daten vorhanden")
            for code in weather_code_pred
        ]

        return {
            "temp_pred": [float(temp) for temp in temperature_pred],
            "whather_descr_pred": weather_description_pred,
            "wind_speed_pred": [float(speed) for speed in wind_speed_pred],
            "wind_dir_pred": [float(direction) for direction in wind_direction_pred]
        }

    except Exception as e:
        print("Wettervorhersage-Fehler:", e)
        return {
            "temp_pred": None,
            "whather_descr_pred": None,
            "wind_speed_pred": None,
            "wind_dir_pred": None
        }

######################################### Wetter geeignet fürs Radfahren ############################################

def is_weather_goog_enough_for_biking(start_weather_prediction_directory,
                                      zs_weather_prediction_directory,
                                      ziel_weather_prediction_directory):

    temp_prediction_s = start_weather_prediction_directory["temp_pred"]
    weather_descr_prediction_s = start_weather_prediction_directory["whather_descr_pred"]
    wind_speed_prediction_s = start_weather_prediction_directory["wind_speed_pred"]

    if zs_weather_prediction_directory is not None:
        temp_prediction_zs = zs_weather_prediction_directory["temp_pred"]
        weather_descr_prediction_zs = zs_weather_prediction_directory["whather_descr_pred"]
        wind_speed_prediction_zs = zs_weather_prediction_directory["wind_speed_pred"]

    temp_prediction_z = ziel_weather_prediction_directory["temp_pred"]
    weather_descr_prediction_z = ziel_weather_prediction_directory["whather_descr_pred"]
    wind_speed_prediction_z = ziel_weather_prediction_directory["wind_speed_pred"]

    MIN_TEMP = 5.0
    MAX_WIND = 20.0

    BAD_WEATHER_CRITERIUMS = [
        "Gewitter", "Hagel", "Starker Regen", "Heftiger Regenschauer",
        "Starker Schneefall", "Schneeschauer", "Gefrierender Regen",
        "Eisregen", "Glatteis", "Sturm", "Orkan", "Nebel", "Reifnebel",
        "Schnee", "Schneekörner", "Starker Nieselregen", "Mäßiger Regen"
    ]

    gruende = []

    # Start prüfen (safe länge)
    n_s = min(len(temp_prediction_s), len(weather_descr_prediction_s), len(wind_speed_prediction_s))
    for i in range(n_s):

        if temp_prediction_s[i] < MIN_TEMP:
            gruende.append(f"Start: Stunde {i} zu kalt ({temp_prediction_s[i]}°C)")

        if wind_speed_prediction_s[i] > MAX_WIND:
            gruende.append(f"Start: Stunde {i} zu windig ({wind_speed_prediction_s[i]} km/h)")

        for w in BAD_WEATHER_CRITERIUMS:
            if w.lower() in str(weather_descr_prediction_s[i]).lower():
                gruende.append(f"Start: Stunde {i} {weather_descr_prediction_s[i]}")
                break

    # Zwischenstopp prüfen
    if zs_weather_prediction_directory is not None:
        n_zs = min(len(temp_prediction_zs), len(weather_descr_prediction_zs), len(wind_speed_prediction_zs))
        for i in range(n_zs):

            if temp_prediction_zs[i] < MIN_TEMP:
                gruende.append(f"Zwischenstopp: Stunde {i} zu kalt ({temp_prediction_zs[i]}°C)")

            if wind_speed_prediction_zs[i] > MAX_WIND:
                gruende.append(f"Zwischenstopp: Stunde {i} zu windig ({wind_speed_prediction_zs[i]} km/h)")

            for w in BAD_WEATHER_CRITERIUMS:
                if w.lower() in str(weather_descr_prediction_zs[i]).lower():
                    gruende.append(f"Zwischenstopp: Stunde {i} {weather_descr_prediction_zs[i]}")
                    break

    # Ziel prüfen
    n_z = min(len(temp_prediction_z), len(weather_descr_prediction_z), len(wind_speed_prediction_z))
    for i in range(n_z):

        if temp_prediction_z[i] < MIN_TEMP:
            gruende.append(f"Ziel: Stunde {i} zu kalt ({temp_prediction_z[i]}°C)")

        if wind_speed_prediction_z[i] > MAX_WIND:
            gruende.append(f"Ziel: Stunde {i} zu windig ({wind_speed_prediction_z[i]} km/h)")

        for w in BAD_WEATHER_CRITERIUMS:
            if w.lower() in str(weather_descr_prediction_z[i]).lower():
                gruende.append(f"Ziel: Stunde {i} {weather_descr_prediction_z[i]}")
                break

    if len(gruende) == 0:
        return True, ["Wetter passt über die gesamte Dauer"]
    else:
        return False, gruende

#####################################################################################################################

def weather_circle_style(temp):

    radius_circle = 600

    if temp is None or temp == "Keine Daten":
        return ("gray", radius_circle)
    if temp < 5:
        return ("blue", radius_circle)
    elif temp < 15:
        return ("green", radius_circle)
    elif temp < 25:
        return ("orange", radius_circle)
    else:
        return ("red", radius_circle)

###############################################################################################################

def add_weather_circle(map_obj, coords, temperature, popup_text=""):

    color, radius = weather_circle_style(temperature)

    folium.Circle(
        location=[coords[1], coords[0]],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.25,
        popup=popup_text
    ).add_to(map_obj)

###############################################################################################################

def include_weather_to_folium(map_obj, coords_start, coords_ziel, coords_zs, start_time_hours, duration_hours):

    zs_coords_weather = None

    start_weather = getWeather(coords_start[1], coords_start[0])
    ziel_weather = getWeather(coords_ziel[1], coords_ziel[0])

    if coords_zs is not None:
        zs_coords_weather = getWeather(coords_zs[1], coords_zs[0])
        add_weather_circle(
            map_obj,
            coords_zs,
            zs_coords_weather["temperatur"],
            popup_text=f"Temperatur: {zs_coords_weather['temperatur']} °C"
        )

    start_weather_prediction = get_Weather_Prediction_for_duration_hours(
        coords_start[1], coords_start[0], start_time_hours, duration_hours
    )
    ziel_weather_prediction = get_Weather_Prediction_for_duration_hours(
        coords_ziel[1], coords_ziel[0], start_time_hours, duration_hours
    )

    if coords_zs is not None:
        zs_weather_prediction = get_Weather_Prediction_for_duration_hours(
            coords_zs[1], coords_zs[0], start_time_hours, duration_hours
        )
    else:
        zs_weather_prediction = None

    # Dauer von 167h auf Dauer der Fahrt kürzen
    def cut_pred(d, dur):
        if d is None:
            return
        if d.get("temp_pred") is not None:
            d["temp_pred"] = d["temp_pred"][:dur]
        if d.get("whather_descr_pred") is not None:
            d["whather_descr_pred"] = d["whather_descr_pred"][:dur]
        if d.get("wind_speed_pred") is not None:
            d["wind_speed_pred"] = d["wind_speed_pred"][:dur]
        if d.get("wind_dir_pred") is not None:
            d["wind_dir_pred"] = d["wind_dir_pred"][:dur]

    cut_pred(start_weather_prediction, duration_hours)
    cut_pred(ziel_weather_prediction, duration_hours)
    if zs_weather_prediction is not None:
        cut_pred(zs_weather_prediction, duration_hours)
    

    biking_yes_or_no = is_weather_goog_enough_for_biking(
        start_weather_prediction, zs_weather_prediction, ziel_weather_prediction
    )

    can_I_go_biking, no_biking_reasons = biking_yes_or_no

    add_weather_circle(
        map_obj,
        coords_start,
        start_weather["temperatur"],
        popup_text=f"Temperatur: {start_weather['temperatur']} °C"
    )

    add_weather_circle(
        map_obj,
        coords_ziel,
        ziel_weather["temperatur"],
        popup_text=f"Temperatur: {ziel_weather['temperatur']} °C"
    )

    return {
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
        "zs_wind_direction": zs_coords_weather["Windrichtung_grad"] if zs_coords_weather is not None else None,

        "fahrradfahren_empfohlen": can_I_go_biking,
        "gruende_gegen_fahrradfahren": None if can_I_go_biking else no_biking_reasons
    }
