"""
--------------------------------------------------------------------------------------------
Pruefungsstudienarbeit Programmieren 3 WS 25/26
Gruppenmitglieder: Alexander Hollenrieder, Thilo Fuhrmann, Dominic Schüll, Tobias Zint
Erstellungsdatum der Projektdatei: 10.11.2025
Abgabedatum: 17.12.2025 (Tag der Abschlusspräsentation)
main.py
Hauptprogramm zur Berechnung und Darstellung der Fahrradroute mit Streamlit und Folium
--------------------------------------------------------------------------------------------
"""

import functionsbasic as fb
from functionsbasic import *                        # Import von allem mit *
import functionsweather as fw
from functionsweather import *
from surface import SURFACE_TYPES, SURFACE_COLORS   # Import der Untergrundcodes und Farben

##################################### Streamlit ###########################################################

st.set_page_config(layout="wide")
st.title("Fahrradroute 🚲 🗺️")                              # Titel

if 'start' not in st.session_state:
    st.session_state.start = "München"

if 'zs' not in st.session_state:
    st.session_state.zs = ""

if 'dest' not in st.session_state:
    st.session_state.dest = "Augsburg"

col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 3, 1, 3, 1], vertical_alignment="bottom")            # Reihe 1

with col1:  
    start_input = st.text_input("Startpunkt 📍", key = "start")
    if start_input:
        start_name = start_input

with col2:
    st.button("📍", key = "button_start", help = "Standort als Startpunkt festlegen", on_click=fb.update_ipinfo, args=("Startpunkt",))
    

with col3:
    zs_input = st.text_input("Zwischenpunkt 🔸", key = "zs")
    if zs_input:
        zs_name = zs_input
    else:
        zs_name = None

with col4:
    location_zs = st.button("📍", key = "button_zs", help = "Standort als Zwischenpunkt festlegen", on_click=fb.update_ipinfo, args=("Zwischenpunkt",))

with col5:  
    dest_input = st.text_input("Zielpunkt 🏁", key = "dest")
    if dest_input:
        dest_name = dest_input

with col6:
    location_dest = st.button("📍", key = "button_dest", help = "Standort als Zielpunkt festlegen", on_click=fb.update_ipinfo, args=("Zielpunkt",))

st.markdown(" ")                                                        # Abstand
                                                                        
col7, col8, col9, col10, col11 = st.columns([1, 1, 1, 1, 1], vertical_alignment="bottom")              # Reihe 2

with col7:  
    speed_input = st.text_input("Geschwindigkeit", value="20")
    if speed_input:
        avg_speed = float(speed_input)
    
with col8:                                                              # Eingabe des Körpergewichts
    weight_biker_input = st.text_input("Körpergewicht kg", value="75")
    if weight_biker_input:
        weight_biker_kg = float(weight_biker_input)

with col9:                                                              # Ankreuzen des Radtyps
    bike = st.radio(
        "Fahrradtyp 🚴‍♂️ 🚵‍♂️ 🚲",
        ["Rennrad", "Gravelbike", "Citybike", "E-Bike"],
        horizontal=True
    )
with col10:
    start_time_hours = st.number_input("Start in h ab jetzt", min_value=0, max_value=168, value=0, step=1)

with col11:
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
    
    if 'selected_route_index' not in st.session_state:
        st.session_state.selected_route_index = 0
        
    if zs_name == None:
        route_bike = client.directions(         #Route mit dem Fahrrad berechnen
        coords,
        elevation = True,
        profile = bike_profile,
        alternative_routes={
                "target_count": 3,     # Versuche 3 Routen zu finden
                "weight_factor": 1.4,  # Wie viel länger darf die Alternative sein? (1.4 = 40% länger erlaubt)
                "share_factor": 0.7    # Wie viel darf sie sich mit der Hauptroute überschneiden?
            },
        format = 'geojson',
        extra_info=["surface"]                  #Untergründe von ORS abrufen
        )

        # Prüfen, ob Alternative Routen vorhanden sind
        if route_bike and 'features' in route_bike:
            route_list = route_bike['features']      #route_bike['features'] ist die Liste für die Routen
            route_count = len(route_list)

            if route_count > 1:
                # Liste mit Namen für Buttons
                route_name = []
                
                for i, route in enumerate(route_list):
                    # Kurze Infos für die Auswahloptionen
                    props = route['properties']['summary']
                    km = round(props['distance'] / 1000, 1)
                    minutes = round(props['duration'] / 60)
                    
                    label = f"Route {i+1} ({km} km, {minutes} Min.)"
                    route_name.append(label)

                # Auswahlfenster erstellen
                route_select = st.radio("Wähle deine Route:", route_name, horizontal = True)
                st.session_state.selected_route_index = route_name.index(route_select)

    #Bei Zwischenstopp sind keine Alternativrouten möglich
    else: 
        st.session_state.selected_route_index = 0
        route_bike = client.directions(         #Route mit dem Fahrrad berechnen
        coords,
        elevation = True,
        profile = bike_profile,
        format = 'geojson',
        extra_info=["surface"]                  #Untergründe von ORS abrufen
        )

    # Geometrie extrahieren und decodieren
    current_route = route_bike['features'][st.session_state.selected_route_index]['geometry']
    coords_route = current_route['coordinates']


    # Surface-Daten (Abschnittsweise Untergründe)
    # Format: [start_index, end_index, surface_code]

    surface_list = route_bike["features"][st.session_state.selected_route_index]["properties"]["extras"]["surface"]["values"]


    #Start und Zielpunkt definieren
    destination = dest_coords                                                         #Zielkoordinaten       

    #Map-Anzeigebereich von our_map 
    our_map = folium.Map(location=(start_coords[1], start_coords[0]), zoom_start=12)     #[latitude, longitude]

    ############################### Platzieren der Folium Marker auf der Karte ##########################################

    weather_info = fw.include_weather_to_folium(
    our_map,
    start_coords,
    dest_coords,
    zs_coords,
    start_time_hours,
    1
    )
    
    place_marker = fb.MarkerPlacingFolium(our_map)
    place_marker.set_weather_data(weather_info)

    place_marker.start(start_coords, start_name)

    if zs_name is not None:
        place_marker.zwischenstopp(zs_coords, zs_name)

    place_marker.ziel(dest_coords, dest_name)


    ############################################### ORS-Route hinzufügen ###############################################


    # Set erstellen, um nur Oberflächen zu speichern, die auf der Route vorkommen
    used_surfaces = set()                                               #Zur Speicherung der in der Route vorkommenden Untergründe

    # Alternativerouten zeichnen
    if route_bike and 'features' in route_bike and zs_name == None:
        route_list = route_bike['features']      #route_bike['features'] ist die Liste für die Routen
        route_count = len(route_list)

        for i, route in enumerate(route_list):
                if st.session_state.selected_route_index != i and route_count > 1:
                    alternative_route = route_bike['features'][i]['geometry']
                    coords_alternative_route = alternative_route['coordinates']
                    folium.PolyLine(
                        [(coord[1], coord[0]) for coord in coords_alternative_route],
                        color="gray",
                        weight=5,
                        opacity=0.8,
                        tooltip=f"Route {i + 1}"
                   ).add_to(our_map)

    #Ausgewählte Route zeichnen
    for seg_start, seg_end, surface_code in surface_list:

        segment_coords = coords_route[seg_start : seg_end + 1]          #Koordinaten für Wegabschnitte mit gleichem Untergrund

        surface_name = SURFACE_TYPES.get(surface_code, "unbekannt")     #Abruf Oberflächentyp

        color = SURFACE_COLORS.get(surface_name, "black")               #Abruf Untergrundfarbe

        # Abschnitt auf Karte zeichnen
        folium.PolyLine(
            [(coord[1], coord[0]) for coord in segment_coords],             # lat, lon
            color=color,
            weight=5,
            opacity=0.8,
            tooltip=f"Route {st.session_state.selected_route_index + 1}"
        ).add_to(our_map)

        used_surfaces.add(surface_name)                                 #Abspeichern der Untergründe

    ################ Entfernung und Dauer aus der Route extrahieren und Umrechnen der Daten#############################

    Distanz_m = route_bike['features'][st.session_state.selected_route_index]['properties']['summary']['distance']      # Distanz in Meter
    Dauer_s_ORS  = route_bike['features'][st.session_state.selected_route_index]['properties']['summary']['duration']   # Zeitdauer in Sekunden
    Dauer_h_ORS = Dauer_s_ORS / 3600                                                # Dauer in Stunden    
    Distanz_km = Distanz_m / 1000                                                   # Distanz in Kilometer
    Dauer_h_eigen = Distanz_km / avg_speed                                          # Dauer in Stunden

    ############################### Höhenmeter aus der Route extrahieren ###############################################

    elevation_up = route_bike['features'][st.session_state.selected_route_index]['properties']['ascent']                # Höhenmeter Anstieg
    elevation_down = route_bike['features'][st.session_state.selected_route_index]['properties']['descent']             # Höhenmeter Abstieg

    ############################## Sportrelevante Daten berechnen #######################################################

    sport_data_yes_no = True                                # ob sportrelevante Daten gewünscht sind
    sport_data = fb.power_calories(weight_biker_kg,
                                    avg_speed,
                                    elevation_up,
                                    Dauer_h_eigen,
                                    sport_data_yes_no
                                    )
    
    ############################ Wetterinformationen grafisch auf der Karte einfügen ####################################

    duration_eigen_hours = int(Dauer_h_eigen + 1)             # Dauer auf die nächste volle Stunde aufrunden

    weather_sidebar = fw.include_weather_to_folium(our_map, start_coords, dest_coords, zs_coords, 
                                                   int(start_time_hours), duration_eigen_hours)


    ####################################### Kartenanpassungen ##########################################################

    # Kartenzoom auf die Route anpassen
    # Bounding Box Minimal- und Maximalwerte aus der Route berechnen
    lats = [lat for lon, lat, _ in coords_route]
    lons = [lon for lon, lat, _ in coords_route]                           

    bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]

    # Map auf die Bounds zoomen
    our_map.fit_bounds(bounds, padding=(80, 80))                        # Rand von 80 Pixeln hinzufügen (padding)

    #################################### Überschrift und Sidebar ########################################################

    Headline = fb.place_header(start_name, dest_name)   

    our_map.get_root().html.add_child(folium.Element(Headline))       # Überschrift HTML an Karte anhängen

    #################################### Erstellen des Höhenmeterdiagramms #############################################
    
    height_meters = []
    distance_meters = []

    anzahl_punkte = len(coords_route)                           # Berechnung der Anzahl der Routenpunkte
    distanz_pro_punkt = Distanz_m / anzahl_punkte               # Aufteilung der Distanz auf die Routenpunkte

    for i in range(anzahl_punkte):
        distance_meters.append(i * distanz_pro_punkt)           # Jedem Routenpunkt eine Distanz zuweisen

    for punkt in coords_route:                                  # Jedem Routenpunkt eine Höhe zuweisen
        height_at_point = punkt[2]                              # Dritter Wert entspricht der Höhe
        height_meters.append(height_at_point)

    high_meters_plot, axis = plt.subplots()                     # Erstellen des Diagramms 
    axis.plot( distance_meters, height_meters,
               color = "darkgreen", linewidth = 2 )
    
    axis.set_xlabel("Streckenlänge (m)")                        # Beschriftung der Achsen und Titel
    axis.set_ylabel("Höhe (m)")
    axis.set_title("Höhenprofil der Fahrradroute")

    axis.grid(True)                                             # Raster anzeigen lassen
    axis.set_facecolor("#e6e3e3")                             # Diagramm Hintergrund
    high_meters_plot.patch.set_facecolor("white")               # Außenbereich

    ############################### Hinzufügen von Features und Abspeichern der Karte ##################################

    MeasureControl().add_to(our_map)                       # Hinzufügen eines Messwerkzeugs  

    if calc_route:
        our_map.save("meine_karte.html")
        
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
            
        with st.sidebar.expander("Aktuelles Wetter", expanded=True):
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

        with st.sidebar.expander("Wettervorhersage", expanded=True):

            if weather_sidebar.get("fahrradfahren_empfohlen", None) is not None:
                if weather_sidebar["fahrradfahren_empfohlen"]:
                    st.success("✅ Fahrradfahren empfohlen")        # success macht grünen Hintergrund
                else:
                    st.error("❌ Fahrradfahren nicht empfohlen. Wählen einer anderen Abfahrtszeit!")    # error macht roten Hintergrund
                    gruende = weather_sidebar.get("gruende_gegen_fahrradfahren", [])
                    if gruende is not None:
                        for g in gruende:
                            st.write("-", g)
                
        with st.sidebar.expander("Legende – Wegoberflächen", expanded=True):
            st.write("**Farbcodierung der Oberflächen:**")
            for surface in used_surfaces:  # nur die Oberflächen anzeigen, die wirklich auf der Route vorkommen
                color = SURFACE_COLORS.get(surface, "black")
                st.markdown(
                    f"<span style='color:{color}; font-weight:bold;'>█</span> {surface}",
                    unsafe_allow_html=True
                )

########################################### Hinzufügen der Grafiken ########################################################
        
        st.components.v1.html(html_data, height=900, width=1800)    # Hinzufügen der Karte zu Streamlit

        st.pyplot(high_meters_plot)                                 # Hinzufügen des Höhenmeterdiagramms zu Streamlit

