# Pruefungsstudienarbeit Programmieren 3 WS 25/26
# Gruppenmitglieder: Alexander Hollenrieder, Thilo Fuhrmann, Dominic Schüll, Tobias Zint

import functionsbasic as fb
from functionsbasic import *
import functionsweather as fw
from functionsweather import *
from folium.plugins import MiniMap, MeasureControl


######################################################################################################################

route_v = fb.routen_abfrage()                                   # Schreiben der Routenabfrage in route_v Dictionary

start = fb.get_coords(route_v["Startpunkt"])                    # Startkoordinaten für die Route abrufen
ziel =  fb.get_coords(route_v["Zielpunkt"])                     # Zielkoordinaten für die Route abrufen
zs_coords = None

coords = [start]                                                # Liste mit start als erstem Element

if route_v["Zwischenstopp"] is not None:                        # Wenn Zwischenstopp gefragt
    zs_coords = fb.get_coords(route_v["Zwischenstopp"])         # Zwischenstopp einfügen
    coords.append(zs_coords)

coords.append(ziel)

# Route mit dem Fahrrad berechnen
route_bike = client.directions(coords, elevation = True, profile='cycling-regular', format='geojson')

# Geometrie extrahieren und decodieren
geometry = route_bike['features'][0]['geometry']
coords_route = geometry['coordinates'] 

#Start und Zielpunkt definieren
destination = ziel                            #Zielkoordinaten       

#Map-Anzeigebereich
our_map = folium.Map(location=(start[1], start[0]), zoom_start=12)     #[latitude, longitude]

############################################### Wetter ##############################################################

start_weather = fw.getWeather(start[1], start[0])      # Wetter am Startpunkt abrufen
ziel_weather  = fw.getWeather(ziel[1], ziel[0])        # Wetter am Zielpunkt abrufen

add_weather_circle(                                     # Temperaturkreis am Startpunkt
    our_map,
    start,
    start_weather["temperatur"],
    popup_text=f"Temperatur: {start_weather['temperatur']} °C"
)

add_weather_circle(                                     # Temperaturkreis am Zielpunkt   
    our_map,
    ziel,
    ziel_weather["temperatur"],
    popup_text=f"Temperatur: {ziel_weather['temperatur']} °C"
)

# Platzieren der Folium Marker auf der Karte
place_marker = fb.MarkerPlacingFolium(our_map)

place_marker.start(start, route_v["Startpunkt"])

if zs_coords is not None:
    place_marker.zwischenstopp(zs_coords, route_v["Zwischenstopp"])

place_marker.ziel(ziel, route_v["Zielpunkt"])


# ORS-Route hinzufügen
folium.PolyLine([(lat, lon) for lon, lat, _ in coords_route],
               color="red", weight=5, opacity=0.8).add_to(our_map)

# Entfernung und Dauer aus der Route extrahieren und Umrechnen der Daten
Distanz_m = route_bike['features'][0]['properties']['summary']['distance']      # Distanz in Meter
Dauer_s_ORS  = route_bike['features'][0]['properties']['summary']['duration']   # Zeitdauer in Sekunden
Dauer_h_ORS = Dauer_s_ORS / 3600                                                # Dauer in Stunden    
Distanz_km = Distanz_m / 1000                                                   # Distanz in Kilometer
Dauer_h_eigen = Distanz_km / route_v["Durchschnittsgeschwindigkeit"]            # Dauer in Stunden


# Kartenzoom auf die Route anpassen
# Bounding Box Minimal- und Maximalwerte aus der Route berechnen
lats = [lat for lon, lat, _ in coords_route]
lons = [lon for lon, lat, _ in coords_route]                           

bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]

# Map auf die Bounds zoomen
our_map.fit_bounds(bounds, padding=(80, 80))                        # Rand von 80 Pixeln hinzufügen (padding)

#################################### Überschrift und Sidebar #########################################################

Headline = fb.place_header(route_v["Startpunkt"], route_v["Zielpunkt"])              
Sidebar =  fb.place_sidebar(Distanz_km, 
                            Dauer_h_ORS, 
                            Dauer_h_eigen, 
                            route_v["Durchschnittsgeschwindigkeit"],
                            route_v["Startpunkt"],
                            route_v["Zielpunkt"],
                            start_weather["temperatur"],
                            ziel_weather["temperatur"])             

our_map.get_root().html.add_child(folium.Element(Headline))       # Überschrift HTML an Karte anhängen
our_map.get_root().html.add_child(folium.Element(Sidebar))        # Sidebar HTML an Karte anhängen

#######################################################################################################################

MiniMap().add_to(our_map)                                         # Hinzufügen einer MiniMap
MeasureControl().add_to(our_map)                                  # Hinzufügen eines Messwerkzeugs  



our_map.save("meine_karte.html")                                  # Anzeigen/Speichern der Karte

