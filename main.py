"""
--------------------------------------------------------------------------------------------
Pruefungsstudienarbeit Programmieren 3 WS 25/26
Gruppenmitglieder: Alexander Hollenrieder, Thilo Fuhrmann, Dominic Schüll, Tobias Zint
Erstellungsdatum: 10.11.2025
--------------------------------------------------------------------------------------------
"""

import functionsbasic as fb
from functionsbasic import *            # Import von allem mit *
import functionsweather as fw
from functionsweather import *          # Alle anderen Packages in functionsbasic.py

##################################### Streamlit ###########################################################

st.set_page_config(layout="wide")
st.title("Fahrradroute 🚲 🗺️")                                                # Titel

col1, col2, col3 = st.columns([1, 1, 1])                                # Reihe 1

with col1:  
    start_input = st.text_input("Startpunkt 📍", value="München")
    if start_input:
        start_name = start_input

with col2:
    zs_input = st.text_input("Zwischenpunkt 🔸", value=None)
    if zs_input:
        zs_name = zs_input
    else:
        zs_name = None

with col3:  
    dest_input = st.text_input("Zielpunkt 🏁", value="Augsburg")
    if dest_input:
        dest_name = dest_input

st.markdown(" ")                                                        # Abstand
                                                                        
col4, col5, col6, col7 = st.columns([1, 1, 2, 1])                       # Reihe 2

with col4:  
    speed_input = st.text_input("Geschwindigkeit", value="20")
    if speed_input:
        avg_speed = float(speed_input)
    
with col5:                                                              # Eingabe des Körpergewichts
    weight_biker_input = st.text_input("Körpergewicht kg", value="75")
    if weight_biker_input:
        weight_biker_kg = float(weight_biker_input)

with col6:                                                              # Ankreuzen des Radtyps
    bike = st.radio(
        "Fahrradtyp 🚴‍♂️ 🚵‍♂️ 🚲",
        ["Rennrad", "Gravelbike", "Citybike", "E-Bike"],
        horizontal=True
    )

with col7:
    calc_route = st.button("Route berechnen")
            

# Autostart Streamlit
app_file = "main.py"
app_path = os.path.join(os.path.dirname(__file__), app_file)


if not os.environ.get("STREAMLIT_RUNNING"):
    os.environ["STREAMLIT_RUNNING"] = "true"
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    subprocess.run(cmd)


st.markdown(                # Hintergrundbild für Streamlit
    """
    <style>
    .stApp {
        background-image: url("https://wallpaperaccess.com/full/1908054.jpg");
        background-size: cover;
        background-position: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

    ######################################### Fahrradtyp berechnen #######################################################

    bike_profile = fb.bike_type(bike)      # Ändert das profile der Berechnung

    ################################### ORS-Route berechnen und Folium Karte erstellen ###################################

    # Route mit dem Fahrrad berechnen
    route_bike = client.directions(coords, elevation = True, profile= bike_profile, format='geojson')

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
        map.save("meine_karte.html")
        
        # HTML laden und einbetten
        with open("meine_karte.html", "r", encoding="utf-8") as f:
            html_data = f.read()

        with st.sidebar.expander("Routeninfos", expanded=True):
            st.write(f"**Distanz:** {Distanz_km:.2f} km")
            st.write(f"**Dauer (ORS):** {Dauer_h_ORS:.2f} h")
            st.write(f"**Geschwindigkeit angenommen:** {avg_speed:.2f} km/h")
            st.write(f"**Dauer (eigene Berechnung):** {Dauer_h_eigen:.2f} h")
            st.write(f"**Höhenmeter↑:** {elevation_up:.1f} m")
            st.write(f"**Höhenmeter↓:** {elevation_down:.1f} m")
            
        with st.sidebar.expander("Wetter", expanded=True):
            st.write(f"**Wetter in {start_name}**")
            st.write(f"Beschreibung: {weather_sidebar["start_weather_text"]}")
            st.write(f"Temperatur: {weather_sidebar["start_temp"]:.2f} °C")
            st.write(f"Windgeschwindigkeit: {weather_sidebar["start_wind_speed"]:.2f} km/h")
            st.write("---")
            if zs_name is not None:
                st.write(f"**Wetter in {zs_name}**")
                st.write(f"Beschreibung: {weather_sidebar["zs_weather_text"]}")
                st.write(f"Temperatur: {weather_sidebar["zs_temp"]:.2f} °C")
                st.write(f"Windgeschwindigkeit: {weather_sidebar["zs_wind_speed"]:.2f} km/h")
                st.write("---")
            st.write(f"**Wetter in {dest_name}**")
            st.write(f"Beschreibung: {weather_sidebar["ziel_weather_text"]}")
            st.write(f"Temperatur: {weather_sidebar["ziel_temp"]:.2f} °C")
            st.write(f"Windgeschwindigkeit: {weather_sidebar["ziel_wind_speed"]:.2f} km/h")

        if sport_data_yes_no and sport_data is not None:
            with st.sidebar.expander("Sportdaten", expanded=True):
                st.write(f"**Leistung:** {sport_data['Gesamtleistung']:.2f} W")
                st.write(f"**Kalorienverbrauch:** {sport_data['Kalorienverbrauch']:.2f} kcal")
                

        st.components.v1.html(html_data, height=900, width=1800)

