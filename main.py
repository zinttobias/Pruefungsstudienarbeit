# Pruefungsstudienarbeit
# Gruppenmitglieder: Alexander Hollenrieder, Thilo Fuhrmann, Dominic Schüll, Tobias Zint

import numpy
import requests as req 
import folium
import openrouteservice

#ORS-Client Zugang
client = openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImRmNzExNzZkYmZhMzQ4Njc5OGE3MDEzM2EwMWFiOWE5IiwiaCI6Im11cm11cjY0In0=")
         
# Eingabe der Wunschstrecke und Durchschnittsgeschwindigkeit

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

route_v = routen_abfrage()                              # Aufruf der Funktion und Speichern der Werte in route_v

#Funktion Stadtname zu Koordinaten

def get_coords(city_name):
    response = client.pelias_search(text=city_name, size=1)         # Anfrage Stadtname mit einem Ergebnis
    coords = response['features'][0]['geometry']['coordinates']     # Erstes Ergebnis von features, Übergabe der Koordinaten
    return coords                                                   # [longitude, latitude] in coords

coords = (get_coords(route_v["Startpunkt"]), get_coords(route_v["Zielpunkt"]))            # Koordinaten abrufen


# Route mit dem Fahrrad berechnen
route = client.directions(coords, profile='cycling-regular', format='geojson')

# Geometrie extrahieren und decodieren
geometry = route['features'][0]['geometry']
coords_route = geometry['coordinates'] 

#Start und Zielpunkt definieren
start = coords[0]                                                   #Startkoordinaten
destination = coords[1]                                             #Zielkoordinaten       

#Map-Anzeigebereich
m = folium.Map(location=(start[1], start[0]), zoom_start=12)        #[latitude, longitude]

#Marker für Start und Ziel
folium.Marker(
    location = [start[1], start[0]],
    tooltip = "Start",
    popup = route_v["Startpunkt"],
    icon = folium.Icon(color = "green", icon = "remove"),
).add_to(m)

folium.Marker(
    location = [destination[1], destination[0]],
    tooltip = "Ziel",
    popup = route_v["Zielpunkt"],
    icon = folium.Icon(color="red", icon = "flag"),
).add_to(m)

# ORS-Route hinzufügen
folium.PolyLine([(lat, lon) for lon, lat in coords_route],
                color="red", weight=5, opacity=0.8).add_to(m)


# Anzeigen der Routen-Informationen:

# Entfernung und Dauer aus der Route extrahieren 
Distanz_m = route['features'][0]['properties']['summary']['distance']       # Distanz in Meter
Dauer_s_ORS  = route['features'][0]['properties']['summary']['duration']    # Zeitdauer in Sekunden

Dauer_h_ORS = Dauer_s_ORS / 3600                                            # Dauer in Stunden    

Distanz_km = Distanz_m / 1000                                               #Distanz in Kilometer
Dauer_h_eigen = Distanz_km / route_v["Durchschnittsgeschwindigkeit"]        #Dauer in Stunden

# Popup-Text erzeugen
info_text = (
    f"<b>Routeninformationen</b><br>"
    f"Entfernung: {Distanz_km:.2f} km<br>"
    f"Dauer (ORS): {Dauer_h_ORS:.1f} h<br>"
    f"Dauer (eigene Berechnung): {Dauer_h_eigen:.1f} h<br>"
    f"Geschwindigkeit angenommen: {route_v["Durchschnittsgeschwindigkeit"]} km/h"
)

# Marker in der Mitte der Route setzen
Mitte_Route = len(coords_route) // 2
Mitte1, Mitte2 = coords_route[Mitte_Route]

# Routeninfo-Marker hinzufügen mit Folium
folium.Marker(
    location=[Mitte2, Mitte1],
    tooltip="Routeninfo",
    popup=folium.Popup(info_text, max_width=300),
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(m)


# Kartenanpassungen unter dieser Zeile:

# Kartenzoom auf die Route anpassen
# Bounding Box Minimal- und Maximalwerte aus der Route berechnen
lats = [lat for lon, lat in coords_route]
lons = [lon for lon, lat in coords_route]

bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]

# Map auf die Bounds zoomen
m.fit_bounds(bounds, padding=(80, 80))  # Rand von 80 Pixeln hinzufügen (padding)

# Überschrift auf der Karte 
title_html = f'''                                                   
     <h3 align="center" style="font-size:22px; margin-top:10px;">
         <b>Fahrradroute: {route_v["Startpunkt"]} -> {route_v["Zielpunkt"]}</b>
     </h3>
'''
m.get_root().html.add_child(folium.Element(title_html))

#Anzeigen/Speichern der Karte
m.save("meine_karte.html")

