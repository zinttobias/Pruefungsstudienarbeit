# Pruefungsstudienarbeit
# Gruppenmitglieder: Alexander Hollenrieder, Thilo Fuhrmann, Dominic Schüll, Tobias Zint

import numpy
import requests as req 
import folium
import openrouteservice

#ORS-Client Zugang
client = openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImRmNzExNzZkYmZhMzQ4Njc5OGE3MDEzM2EwMWFiOWE5IiwiaCI6Im11cm11cjY0In0=")
         
koordinaten = {
    "coordinates": [
        [10.314009, 47.716193],     # Kempten
        [10.642521, 48.061231],      # Türkheim
        [45.5236, -122.6750]        # Portland   
    ]
}
#Eingabe der Durchschnittsgeschwindigkeit in km/h. Abhängig von der eigenen Leistung des Fahrers
Durchschnittsgeschwindigkeit_kmh = 25

#Route Kempten -> Türkkheim
coords = ((10.314009, 47.716193), (10.642521, 48.061231))

# Route mit dem Fahrrad berechnen
route = client.directions(coords, profile='cycling-regular', format='geojson')

# Geometrie extrahieren und decodieren
geometry = route['features'][0]['geometry']
coords_route = geometry['coordinates'] 

#Start und Zielpunkt definieren
point_a = [10.314009, 47.716193]
point_b =  [10.642521, 48.061231]

#Map-Anzeigebereich
m = folium.Map(location=(47.716193, 10.314009), zoom_start=12)

#Marker für Start und Ziel
folium.Marker(
    location = [47.716193, 10.314009],
    tooltip = "Start",
    popup = "Kempten",
    icon = folium.Icon(color = "blue", icon = "remove"),
).add_to(m)

folium.Marker(
    location = [48.061231, 10.642521],
    tooltip = "Ziel",
    popup = "Türkeim",
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
Dauer_h_eigen = Distanz_km / Durchschnittsgeschwindigkeit_kmh               #Dauer in Stunden

# Popup-Text erzeugen
info_text = (
    f"<b>Routeninformationen</b><br>"
    f"Entfernung: {Distanz_km:.2f} km<br>"
    f"Dauer (ORS): {Dauer_h_ORS:.1f} h<br>"
    f"Dauer (eigene Berechnung): {Dauer_h_eigen:.1f} h<br>"
    f"Geschwindigkeit angenommen: {Durchschnittsgeschwindigkeit_kmh} km/h"
)

# Marker in der Mitte der Route setzen
Mitte_Route = len(coords_route) // 2
Mitte1, Mitte2 = coords_route[Mitte_Route]

# Routeninfo-Marker hinzufügen mit Folium
folium.Marker(
    location=[Mitte2, Mitte1],
    tooltip="Routeninfo",
    popup=folium.Popup(info_text, max_width=300),
    icon=folium.Icon(color="yellow", icon="info-sign")
).add_to(m)


#Anzeigen/Speichern der Karte
m
m.save("meine_karte.html")

