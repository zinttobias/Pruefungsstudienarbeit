import numpy
import requests as req 
import folium
import openrouteservice
import math

#ORS-Client Zugang
client = openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImRmNzExNzZkYmZhMzQ4Njc5OGE3MDEzM2EwMWFiOWE5IiwiaCI6Im11cm11cjY0In0=")
         

######################################  Allgemeine Funktionsdefinitionen ###########################################

# Funktion zur Abfrage der Routenparameter vom Benutzer

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
####################################################################################################################################################


# Funktion zum Wandeln eines Stadtnamens in Koordinaten
         
def get_coords(city_name):
    response = client.pelias_search(text=city_name, size=1)         # Anfrage Stadtname mit einem Ergebnis
    coords = response['features'][0]['geometry']['coordinates']     # Erstes Ergebnis von features, Übergabe der Koordinaten
    return coords                                                   # [longitude, latitude] in coords

####################################################################################################################################################

# Klasse zum Platzieren der Folium Marker auf der Karte

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

####################################################################################################################################################

# Funktion zum Erstellen einer Überschrift

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

####################################################################################################################################################

# Funtion zum Erstellen eines Seitenbalkens

def place_sidebar(dist_km, dauer_ors, dauer_eigen, speed, start, ziel, temp_start, temp_ziel):
    return f"""
    <div style="position: fixed; 
                top: 180px; left: 10px; width: 260px; height: auto; 
                background-color: white; 
                border:2px solid grey; 
                z-index:9999; 
                padding:10px; 
                overflow:auto;">
        <h4><b>Routeninformationen</b></h4>
        <p><b>Distanz:</b> {dist_km:.2f} km </p>
        <p><b>Dauer (ORS):</b> {dauer_ors:.2f} h </p>
        <p><b>Geschwindigkeit angenommen:</b> {speed:.2f} km/h </p>
        <p><b>Dauer (eigene Berechnung):</b> {dauer_eigen:.2f} h </p>
        <p><b>Temparatur in </b>{start}: {temp_start:.2f} °C </p>
        <p><b>Temparatur in </b>{ziel}: {temp_ziel:.2f} °C </p>
        
    </div>
    """

