# Import notwendiger Bibliotheken bzw. Packages

import numpy
import requests as req 
import folium
import openrouteservice
import math

#ORS-Client Zugangsschlüssel
client = openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImRmNzExNzZkYmZhMzQ4Njc5OGE3MDEzM2EwMWFiOWE5IiwiaCI6Im11cm11cjY0In0=")
         

######################################  Allgemeine Funktionsdefinitionen ###########################################
###################################### Funktion zur Abfrage der Routenparameter vom Benutzer #######################

def routen_abfrage():
    startpunkt = input("Geben Sie den Startpunkt der Route ein:")                               # Eingabe Startpunkt
    while not startpunkt.strip():
        startpunkt = input("Eingabe darf nicht leer sein. Bitte erneut versuchen: ")

    zielpunkt = input("Geben Sie den Zielpunkt der Route ein:")                                 # Eingabe Zielpunkt
    while not zielpunkt.strip():
        zielpunkt = input("Eingabe darf nicht leer sein. Bitte erneut versuchen: ")

    zwischenstopp = None                                                                        # Abfrage auf Zwischenstopp                   
    auswahl_zs = input("Möchten Sie einen Zwischenstopp hinzufügen? (ja/nein): ").lower()

    if auswahl_zs == "ja":
        zwischenstopp = input("Geben Sie den Zwischenstopp der Route ein:")
        while not zwischenstopp.strip():
            zwischenstopp = input("Eingabe darf nicht leer sein. Bitte erneut versuchen: ")

    v_avg = input("Vorraussichtliche Durchschnittsgeschwindigkeit in km/h: ")                  # Eingabe Durchschnittsgeschwindigkeit
    while not v_avg.strip():
        v_avg = input("Eingabe darf nicht leer sein. Bitte erneut versuchen: ")

    return {                                            # Rückgabe als Dictionary(Benutzen: route_v["Startpunkt"])
        "Startpunkt": startpunkt,
        "Zielpunkt": zielpunkt,
        "Zwischenstopp": zwischenstopp,
        "Durchschnittsgeschwindigkeit": float(v_avg)    # Umwandeln in einen float Typ
    }
########################################## Funktion zum Wandeln eines Stadtnamens in Koordinaten #############################
         
def get_coords(city_name):
    response = client.pelias_search(text=city_name, size=1)         # Anfrage Stadtname mit einem Ergebnis
    coords = response['features'][0]['geometry']['coordinates']     # Erstes Ergebnis von features, Übergabe der Koordinaten
    return coords                                                   # [longitude, latitude] in coords

######################################## Klasse zum Platzieren der Folium Marker auf der Karte ###############################

class MarkerPlacingFolium:
    def __init__(self, map_obj):
        self.our_map = map_obj

    def start(self, coords, popup):
        folium.Marker(
            location=[coords[1], coords[0]],
            tooltip="Start",
            popup=popup,
            icon=folium.Icon(color="green", icon="play")
        ).add_to(self.our_map)

    def zwischenstopp(self, coords, popup):
        folium.Marker(
            location=[coords[1], coords[0]],
            tooltip="Zwischenstopp",
            popup=popup,
            icon=folium.Icon(color="orange", icon="pause")
        ).add_to(self.our_map)

    def ziel(self, coords, popup):
        folium.Marker(
            location=[coords[1], coords[0]],
            tooltip="Ziel",
            popup=popup,
            icon=folium.Icon(color="red", icon="flag")
        ).add_to(self.our_map)


################################# Sportrelevante Daten Leistung, Kalorienverbrauch ###########################################

def power_calories(weight_kg, average_speed_kmh, elevation_gain_m, duration_h, sport_data_wanted = True):
    if not sport_data_wanted:
        return None
    
    g = 9.81                                                            # Erdbeschleunigung in m/s²
    average_speed_ms = average_speed_kmh / 3.6                          # Umrechnung km/h in m/s
    elevation_gain_m_per_s = elevation_gain_m / (duration_h * 3600)     # Höhengewinn pro Sekunde

    P_roll = 0.005 * weight_kg * g * average_speed_ms                   # Rollwiderstandsleistung
    P_aero = 0.5 * 1.225 * 0.9 * 0.3 * (average_speed_ms ** 3)          # Luftwiderstandsleistung
    P_pot = weight_kg * g * elevation_gain_m_per_s                      # Steigungsleistung

    P_complete = P_roll + P_aero + P_pot  
    calories_mechanical = P_complete * duration_h * 60 * 0.01433        # nur die Leistung die aufs Rad geht

    n = 0.25                                                            # Wirkungsgrad des menschlichen Körpers

    calories_burned = calories_mechanical / n

    return {                                           
        "Gesamtleistung": P_complete,                                   # Gesamtleistung in Watt
        "Kalorienverbrauch": calories_burned                            # Kalorienverbrauch in kcal  
    }

########################################## Funktion zum Erstellen einer Überschrift #########################################

def place_header(start, ziel):
    return f"""
    <div style="position: fixed; 
                top: 10px; 
                left: 50%; 
                transform: translateX(-50%);
                z-index: 9999; 
                background-color: white; 
                padding: 5px 10px; 
                border-radius: 5px;
                font-size: 22px;">
        <b>Fahrradroute: {start} -> {ziel}</b>
    </div>
    """

########################################### Funtion zum Erstellen eines Seitenbalkens ########################################

def place_sidebar(dist_km, dauer_ors, dauer_eigen, speed, start, ziel, zs,
                    temp_start, windspeed_start, winddirection_start, 
                        temp_ziel, windspeed_ziel, winddirection_ziel, 
                            temp_zs, windspeed_zs, winddirection_zs,
                                weather_desc_start, weather_desc_ziel, weather_desc_zs,
                                elevation_up, elevation_down, sport_data_yes_no, sport_data):
     
    zs_sidebar = ""
    if temp_zs is not None and zs is not None:
        zs_sidebar = (
        f"<p><b>Wetter in {zs}</b></p>"
        f"<p>Beschreibung: {weather_desc_zs}</p>"
        f"<p>Temperatur: {temp_zs:.2f} °C</p>"
        f"<p>Windgeschwindigkeit: {windspeed_zs:.2f} km/h</p>"
        f"<p>-------------------------------<p>"
        )

    sport_data_sidebar = ""
    if sport_data_yes_no and sport_data is not None:
        sport_data_sidebar = (
            f"<p><b>Leistung:</b> {sport_data['Gesamtleistung']:.2f} W</p>"
            f"<p><b>Kalorienverbrauch:</b> {sport_data['Kalorienverbrauch']:.2f} kcal</p>"
        )
    
    return f"""
    <div style="position: fixed; 
                top: 180px; left: 10px; width: 260px; height: auto; 
                background-color: white; 
                border:2px solid grey; 
                z-index:9999; 
                padding:10px; 
                overflow:auto;">
                                            
        <style>
        .accordion-item {{                         
            margin-bottom: 8px;
            border-bottom: 1px solid #ccc;
        }}
        .accordion-label {{
            display: block;
            padding: 8px;
            background: #eee;
            cursor: pointer;
            font-weight: bold;
        }}
        .accordion-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.25s ease-out;
            padding-left: 5px;
        }}
        .accordion-item input[type="checkbox"] {{
            display: none;
        }}
        .accordion-item input:checked ~ .accordion-content {{
            max-height: 500px;
            padding: 8px 5px;
        }}
        </style>

        <h4><b>Routeninformationen</b></h4>

        <div class="accordion">

            <!-- Routeninfo -->
            <div class="accordion-item">
                <input type="checkbox" id="acc-route" checked>
                <label class="accordion-label" for="acc-route">Routeninfo</label>
                <div class="accordion-content">
                    <p><b>Distanz:</b> {dist_km:.2f} km </p>
                    <p><b>Dauer (ORS):</b> {dauer_ors:.2f} h </p>
                    <p><b>Geschwindigkeit angenommen:</b> {speed:.2f} km/h </p>
                    <p><b>Dauer (eigene Berechnung):</b> {dauer_eigen:.2f} h </p>
                    <p><b>Höhenmeter↑:</b> {elevation_up:.1f} m </p>
                    <p><b>Höhenmeter↓:</b> {elevation_down:.1f} m </p>
                </div>
            </div>

            <!-- Wetter -->
            <div class="accordion-item">
                <input type="checkbox" id="acc-weather" checked>
                <label class="accordion-label" for="acc-weather">Wetter</label>
                <div class="accordion-content">
                    <p><b>Wetter in {start} </b></p>
                    <p>Beschreibung: {weather_desc_start} </p>
                    <p>Temperatur: {temp_start:.2f} °C </p>
                    <p>Windgeschwindigkeit: {windspeed_start:.2f} km/h </p>
                    <p>-------------------------------</p>

                    {zs_sidebar}

                    <p><b>Wetter in {ziel} </b></p>
                    <p>Beschreibung: {weather_desc_ziel} </p>
                    <p>Temperatur: {temp_ziel:.2f} °C </p>
                    <p>Windgeschwindigkeit: {windspeed_ziel:.2f} km/h </p>
                    
                </div>
            </div>

            <!-- Sportdaten -->
            <div class="accordion-item">
                <input type="checkbox" id="acc-sport">
                <label class="accordion-label" for="acc-sport">Sportdaten</label>
                <div class="accordion-content">
                    {sport_data_sidebar}
                </div>
            </div>

        </div>
    </div>
    """

#####################################################################################################################################################

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Hier drunter keine Funktionsdefinitionen mehr einfügen !!!!!!!!!!!!!!!
# Ansonsten werden die Informationen im schlimmsten Fall nicht mehr in Headline und Sidebar angezeigt !!!!