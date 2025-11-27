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
import streamlit.components.v1 as components
import subprocess
import sys
import os
import webbrowser

##################################### Streamlit ###########################################################

# Anpassungen
st.title("Fahrradroute")                                                        # Titel
col1, col2, col3, col4, col5, col6 = st.columns(6)                              # Spalten erzeugen

with col1:                                                                      # Spalte 1
    start_input = st.text_input("Startpunkt", value = "München")
    if start_input:
        start_name = start_input

with col2:
    zs_input = st.text_input("Zwischenpunkt", value = None)
    if zs_input:
        zs_name = zs_input
    else:
        zs_name = None

with col3:                                                                      # Spalte 2
    dest_input = st.text_input("Zielpunkt", value = "Augsburg")
    if dest_input:
        dest_name = dest_input

with col4:                                                                      # Spalte 3
    speed_input = st.text_input("Geschwindigkeit", value = "20")
    if speed_input:
        avg_speed = float(speed_input)

with col5:                                                                      # Spalte 4
    weight_biker_input = st.text_input("Körpergewicht kg", value = "75")
    if weight_biker_input:
        weight_biker_kg = float(weight_biker_input)

with col6:
    calc_route = st.button("Route berechnen")

# Autostart Streamlit
app_file = "main.py"
app_path = os.path.join(os.path.dirname(__file__), app_file)


if not os.environ.get("STREAMLIT_RUNNING"):
    os.environ["STREAMLIT_RUNNING"] = "true"
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    subprocess.run(cmd)

if start_input and dest_input and speed_input: 

    ##################################### Eingabe der Route und Verarbeitung ###############################################

    start_coords = fb.get_coords(start_name)                    # Startkoordinaten für die Route abrufen
    dest_coords =  fb.get_coords(dest_name)                     # Zielkoordinaten für die Route abrufen
    zs_coords = None

    coords = [start_coords]                                     # Liste mit start als erstem Element

    if zs_name is not None:                                     # Wenn Zwischenstopp gefragt
        zs_coords = fb.get_coords(zs_name)                      # Zwischenstopp einfügen
        coords.append(zs_coords)

    coords.append(dest_coords)

    ############################### ORS-Route berechnen und Folium Karte erstellen #######################################

    # Route mit dem Fahrrad berechnen
    route_bike = client.directions(coords, elevation = True, profile='cycling-regular', format='geojson')

    # Geometrie extrahieren und decodieren
    geometry = route_bike['features'][0]['geometry']
    coords_route = geometry['coordinates'] 

    #Start und Zielpunkt definieren
    destination = dest_coords                                                         #Zielkoordinaten       

    #Map-Anzeigebereich von our_map 
    map = folium.Map(location=(start_coords[1], start_coords[0]), zoom_start=12)     #[latitude, longitude]


    ############################ Wetterinformationen grafisch auf der Karte einfügen ####################################

    weather_sidebar = fw.include_weather_to_folium(map, start_coords, dest_coords, zs_coords)

    ############################### Platzieren der Folium Marker auf der Karte ##########################################
    place_marker = fb.MarkerPlacingFolium(map)

    place_marker.start(start_coords, start_name)

    if zs_name is not None:
        place_marker.zwischenstopp(zs_coords, zs_name)

    place_marker.ziel(dest_coords, dest_name)


    ############################################### ORS-Route hinzufügen ###############################################

    folium.PolyLine([(lat, lon) for lon, lat, _ in coords_route],
                color="red", weight=5, opacity=0.8).add_to(map)

    ################ Entfernung und Dauer aus der Route extrahieren und Umrechnen der Daten#############################

    Distanz_m = route_bike['features'][0]['properties']['summary']['distance']      # Distanz in Meter
    Dauer_s_ORS  = route_bike['features'][0]['properties']['summary']['duration']   # Zeitdauer in Sekunden
    Dauer_h_ORS = Dauer_s_ORS / 3600                                                # Dauer in Stunden    
    Distanz_km = Distanz_m / 1000                                                   # Distanz in Kilometer
    Dauer_h_eigen = Distanz_km / avg_speed                                          # Dauer in Stunden

    ############################### Höhenmeter aus der Route extrahieren ###############################################

    elevation_up = route_bike['features'][0]['properties']['ascent']                # Höhenmeter Anstieg
    elevation_down = route_bike['features'][0]['properties']['descent']             # Höhenmeter Abstieg

    ############################## Sportrelevante Daten berechnen #######################################################

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
    map.fit_bounds(bounds, padding=(80, 80))                        # Rand von 80 Pixeln hinzufügen (padding)

    #################################### Überschrift und Sidebar ########################################################

    Headline = fb.place_header(start_name, dest_name)   

    Sidebar =  fb.place_sidebar(Distanz_km, Dauer_h_ORS, Dauer_h_eigen, avg_speed,
                                start_name, dest_name, dest_name, ## route_v["Zwischenstopp"],  
                                weather_sidebar["start_temp"], weather_sidebar["start_wind_speed"], weather_sidebar["start_wind_direction"],         
                                weather_sidebar["ziel_temp"], weather_sidebar["ziel_wind_speed"], weather_sidebar["ziel_wind_direction"],
                                weather_sidebar["zs_temp"], weather_sidebar["zs_wind_speed"], weather_sidebar["zs_wind_direction"],
                                weather_sidebar["start_weather_text"], weather_sidebar["ziel_weather_text"], weather_sidebar["zs_weather_text"],
                                elevation_up, elevation_down,
                                sport_data_yes_no, sport_data
                                )             

    map.get_root().html.add_child(folium.Element(Headline))       # Überschrift HTML an Karte anhängen
    map.get_root().html.add_child(folium.Element(Sidebar))        # Sidebar HTML an Karte anhängen

    ############################### Hinzufügen von Features und Abspeichern der Karte ##################################

    MeasureControl().add_to(map)                                  # Hinzufügen eines Messwerkzeugs  

    if calc_route:
        map.save("meine_karte.html")                                  # Anzeigen/Speichern der Karte

        # Karte als HTML rendern
        html_data = map._repr_html_()
        components.html(html_data, height=1200, width=1200)