# Pruefungsstudienarbeit
# PSA Alexander Hollenrieder, Thilo Fuhrmann, Dominic Schüll, Tobias Zint

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
    icon = folium.Icon(icon="cloud"),
).add_to(m)

folium.Marker(
    location = [48.061231, 10.642521],
    tooltip = "Ziel",
    popup = "Türkeim",
    icon = folium.Icon(color="green"),
).add_to(m)

# ORS-Route hinzufügen
folium.PolyLine([(lat, lon) for lon, lat in coords_route],
                color="red", weight=5, opacity=0.8).add_to(m)

#Anzeigen/Speichern der Karte
m
m.save("meine_karte.html")

