"""
--------------------------------------------------------------------------------------------
Pruefungsstudienarbeit Programmieren 3 WS 25/26
Gruppenmitglieder: Alexander Hollenrieder, Thilo Fuhrmann, Dominic Schüll, Tobias Zint
Erstellungsdatum: 10.11.2025
--------------------------------------------------------------------------------------------
"""

import functionsbasic as fb
from functionsbasic import *
import functionsweather as fw
from functionsweather import *
from folium.plugins import MiniMap, MeasureControl
import streamlit as st
import webbrowser
import subprocess

st.title("Fahrradroute")
# Spalten erzeugen
col1, col2, col3, col4 = st.columns(4)

# Spalte 1
with col1:
    start_name = st.text_input("Startpunkt")

# Spalte 2
with col2:
    ziel_name = st.text_input("Zielpunkt")

# Spalte 3
with col3:
    avg_speed = float(st.text_input("Geschwindigkeit"))

# Spalte 4
with col4:
    calc_route = st.button("Route berechnen")



##################################### Eingabe der Route und Verarbeitung ###############################################

start_coords = fb.get_coords(start_name)                    # Startkoordinaten für die Route abrufen
ziel_coords =  fb.get_coords(ziel_name)                     # Zielkoordinaten für die Route abrufen
zs_coords = None

coords = [start_coords]                                                # Liste mit start als erstem Element

## route_v["Zwischenstopp"] is not None:                        # Wenn Zwischenstopp gefragt
##    zs_coords = fb.get_coords(route_v["Zwischenstopp"])         # Zwischenstopp einfügen
##    coords.append(zs_coords)

coords.append(ziel_coords)

############################### ORS-Route berechnen und Folium Karte erstellen #######################################

st.title("Fahrradroute")

# Route mit dem Fahrrad berechnen
route_bike = client.directions(coords, elevation = True, profile='cycling-regular', format='geojson')

# Geometrie extrahieren und decodieren
geometry = route_bike['features'][0]['geometry']
coords_route = geometry['coordinates'] 

#Start und Zielpunkt definieren
destination = ziel_coords                                                    #Zielkoordinaten       

#Map-Anzeigebereich von our_map 
our_map = folium.Map(location=(start_coords[1], start_coords[0]), zoom_start=12)     #[latitude, longitude]


############################ Wetterinformationen grafisch auf der Karte einfügen ####################################

weather_sidebar = fw.include_weather_to_folium(our_map, start_coords, ziel_coords, zs_coords)

############################### Platzieren der Folium Marker auf der Karte ##########################################
place_marker = fb.MarkerPlacingFolium(our_map)

place_marker.start(start_coords, start_name)

##if zs_coords is not None:
##    place_marker.zwischenstopp(zs_coords, route_v["Zwischenstopp"])

place_marker.ziel(ziel_coords, ziel_name)


############################################### ORS-Route hinzufügen ###############################################

folium.PolyLine([(lat, lon) for lon, lat, _ in coords_route],
               color="red", weight=5, opacity=0.8).add_to(our_map)

################ Entfernung und Dauer aus der Route extrahieren und Umrechnen der Daten#############################

Distanz_m = route_bike['features'][0]['properties']['summary']['distance']      # Distanz in Meter
Dauer_s_ORS  = route_bike['features'][0]['properties']['summary']['duration']   # Zeitdauer in Sekunden
Dauer_h_ORS = Dauer_s_ORS / 3600                                                # Dauer in Stunden    
Distanz_km = Distanz_m / 1000                                                   # Distanz in Kilometer
Dauer_h_eigen = Distanz_km / 3 ##route_v["Durchschnittsgeschwindigkeit"]            # Dauer in Stunden

############################### Höhenmeter aus der Route extrahieren ###############################################

elevation_up = route_bike['features'][0]['properties']['ascent']                # Höhenmeter Anstieg
elevation_down = route_bike['features'][0]['properties']['descent']             # Höhenmeter Abstieg

############################## Sportrelevante Daten berechnen #######################################################

weight_biker_kg = 75                                    # Diese zwei Werte später als Eingabe abfragen   
sport_data_yes_no = True                                # ob sportrelevante Daten gewünscht sind
sport_data = fb.power_calories(weight_biker_kg,
                                avg_speed,
                                elevation_up,
                                Dauer_h_eigen,
                                sport_data_yes_no
                                )

####################################### Kartenanpassungen ##########################################################

# Kartenzoom auf die Route anpassen
# Bounding Box Minimal- und Maximalwerte aus der Route berechnen
lats = [lat for lon, lat, _ in coords_route]
lons = [lon for lon, lat, _ in coords_route]                           

bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]

# Map auf die Bounds zoomen
our_map.fit_bounds(bounds, padding=(80, 80))                        # Rand von 80 Pixeln hinzufügen (padding)

#################################### Überschrift und Sidebar ########################################################

Headline = fb.place_header(start_name, ziel_name)   

Sidebar =  fb.place_sidebar(Distanz_km, Dauer_h_ORS, Dauer_h_eigen, avg_speed,
                            start_name, ziel_name, ziel_name, ## route_v["Zwischenstopp"],  
                            weather_sidebar["start_temp"], weather_sidebar["start_wind_speed"], weather_sidebar["start_wind_direction"],         
                            weather_sidebar["ziel_temp"], weather_sidebar["ziel_wind_speed"], weather_sidebar["ziel_wind_direction"],
                            weather_sidebar["zs_temp"], weather_sidebar["zs_wind_speed"], weather_sidebar["zs_wind_direction"],
                            weather_sidebar["start_weather_text"], weather_sidebar["ziel_weather_text"], weather_sidebar["zs_weather_text"],
                            elevation_up, elevation_down,
                            sport_data_yes_no, sport_data
                            )             

our_map.get_root().html.add_child(folium.Element(Headline))       # Überschrift HTML an Karte anhängen
our_map.get_root().html.add_child(folium.Element(Sidebar))        # Sidebar HTML an Karte anhängen

############################### Hinzufügen von Features und Abspeichern der Karte ##################################

MiniMap().add_to(our_map)                                         # Hinzufügen einer MiniMap
MeasureControl().add_to(our_map)                                  # Hinzufügen eines Messwerkzeugs  

if calc_route:
    our_map.save("meine_karte.html")                                  # Anzeigen/Speichern der Karte

