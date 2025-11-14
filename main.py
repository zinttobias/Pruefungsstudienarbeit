# Pruefungsstudienarbeit
# PSA Alexander Hollenrieder, Thilo Fuhrmann, Dominic Schüll, Tobias Zint

import numpy
import requests as req 
import folium
         
koordinaten = {
    "coordinates": [
        [10.314009, 47.716193],     # Kempten
        [10.642521, 48.061231],      # Türkheim
        [45.5236, -122.6750]        # Portland   
    ]

}

Zugangsdaten = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjZlM2NmMjA2OGY5MjQwMmJhYmY2YzNjM2NlMDYwNjg1IiwiaCI6Im11cm11cjY0In0=',
    'Content-Type': 'application/json; charset=utf-8'
}

#Start und Zielpunkt definieren
point_a = [10.314009, 47.716193]
point_b =  [10.642521, 48.061231]

#Map-Anzeigebereich
m = folium.Map(location=(10.314009, 47.716193), zoom_start=12)

#Marker für Start und Ziel
folium.Marker(
    location = [10.314009, 47.716193],
    tooltip = "Start",
    popup = "Kempten",
    icon = folium.Icon(icon="cloud"),
).add_to(m)

folium.Marker(
    location = [10.642521, 48.061231],
    tooltip = "Click me!",
    popup = "Ziel",
    icon = folium.Icon(color="green"),
).add_to(m)

#Verbinden der beiden Punkte
folium.PolyLine(
    locations=[point_a, point_b],
    color="blue",
    weight=4,
    opacity=0.8
).add_to(m)


#Anzeigen/Speichern der Karte
m
m.save("meine_karte.html")

