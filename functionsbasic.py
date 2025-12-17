"""
--------------------------------------------------------------------------------------------
Pruefungsstudienarbeit Programmieren 3 WS 25/26
functionsbasic.py
Funktionen die das allgemeine Projekt betreffen werden hier eingetragen
--------------------------------------------------------------------------------------------
"""

# Import notwendiger Bibliotheken bzw. Packages

import numpy
import requests as req 
import folium
import openrouteservice
import math
from folium.plugins import MiniMap, MeasureControl
from functionsweather import WEATHER_ICONS
from functionsweather import *
import streamlit as st
import streamlit.components.v1 as components
import subprocess
import sys
import os
import webbrowser
import ipinfo
import matplotlib.pyplot as plt

#ORS-Client Zugangsschlüssel

#client = openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImRmNzExNzZkYmZhMzQ4Njc5OGE3MDEzM2EwMWFiOWE5IiwiaCI6Im11cm11cjY0In0=")
client = openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjZlM2NmMjA2OGY5MjQwMmJhYmY2YzNjM2NlMDYwNjg1IiwiaCI6Im11cm11cjY0In0=")

######################################  Allgemeine Funktionsdefinitionen ###########################################

########################################## Funktion zum Wandeln eines Stadtnamens in Koordinaten #############################
         
def get_coords(city_name):
    response = client.pelias_search(text=city_name, size=1)         # Anfrage Stadtname mit einem Ergebnis
    coords = response['features'][0]['geometry']['coordinates']     # Erstes Ergebnis von features, Übergabe der Koordinaten
    return coords                                                   # [longitude, latitude] in coords

######################################## Klasse zum Platzieren der Folium Marker auf der Karte ###############################

class MarkerPlacingFolium:
    def __init__(self, map_obj):
        self.our_map = map_obj
        self.weather_data = {}

    def start(self, coords, popup):
        code = self.weather_data.get("start_weather_code")
        weather_icon = self._icon_from_weather_code(code)

        folium.Marker(
            location=[coords[1], coords[0]],
            tooltip="Start",
            popup=popup,
            icon=weather_icon
        ).add_to(self.our_map)

    def zwischenstopp(self, coords, popup):
        code = self.weather_data.get("zs_weather_code")
        weather_icon = self._icon_from_weather_code(code)

        folium.Marker(
            location=[coords[1], coords[0]],
            tooltip="Zwischenstopp",
            popup=popup,
            icon=weather_icon
        ).add_to(self.our_map)

    def ziel(self, coords, popup):
        code = self.weather_data.get("ziel_weather_code")
        weather_icon = self._icon_from_weather_code(code)

        folium.Marker(
            location=[coords[1], coords[0]],
            tooltip="Ziel",
            popup=popup,
            icon=weather_icon
        ).add_to(self.our_map)

    def set_weather_data(self, weather_dict):
        self.weather_data = weather_dict

    def _icon_from_weather_code(self, code):
        if code is None:
            return folium.Icon(icon="map-marker", prefix="fa", color="black")

        icon_name, color = WEATHER_ICONS.get(
            code, ("question", "black")
        )

        return folium.Icon(icon=icon_name, prefix="fa", color=color)



################################# Sportrelevante Daten Leistung, Kalorienverbrauch ###########################################

def power_calories(weight_kg, average_speed_kmh, elevation_gain_m, duration_h, sport_data_wanted = True):
    if not sport_data_wanted:
        return None
    
    g = 9.81                                                            # Erdbeschleunigung in m/s²
    average_speed_ms = average_speed_kmh / 3.6                          # Umrechnung km/h in m/s
    elevation_gain_m_per_s = elevation_gain_m / (duration_h * 3600)     # Höhengewinn pro Sekunde

    P_roll = 0.005 * weight_kg * g * average_speed_ms                   # Rollwiderstandsleistung
    P_aero = 0.5 * 1.225 * 0.9 * 0.3 * (average_speed_ms ** 3)          # Luftwiderstandsleistung
    P_pot = weight_kg * g * elevation_gain_m_per_s                      # Steigungsleistung

    P_complete = P_roll + P_aero + P_pot  
    calories_mechanical = P_complete * duration_h * 60 * 0.01433        # nur die Leistung die aufs Rad geht

    n = 0.25                                                            # Wirkungsgrad des menschlichen Körpers

    calories_burned = calories_mechanical / n

    return {                                           
        "Gesamtleistung": P_complete,                                   # Gesamtleistung in Watt
        "Kalorienverbrauch": calories_burned                            # Kalorienverbrauch in kcal  
    }

########################################## Verarbeiten des Fahrradtyps ######################################################

def bike_type(bike):
    if bike == "Rennrad":
        type_of_bike = "cycling-road"

    elif bike == "Gravelbike":
        type_of_bike = "cycling-mountain"
    
    elif bike == "Citybike":
        type_of_bike = "cycling-regular"
    
    elif bike == "E-Bike":
        type_of_bike = "cycling-electric"

    return type_of_bike

########################################## Funktion zum Erstellen einer Überschrift #########################################

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

########################################### Standortabfrage ###############################################################

access_token = 'a8e2f4c99a642d'
handler = ipinfo.getHandler(access_token)

def update_ipinfo(location_button):
    try:
        location = handler.getDetails()
        found_city = location.city
        if location_button == "Startpunkt":
            st.session_state.start = found_city
        if location_button == "Zwischenpunkt":
            st.session_state.zs = found_city
        if location_button == "Zielpunkt":
            st.session_state.dest = found_city
            
    except Exception as e:  
        st.error(f"Fehler bei der API-Abfrage: {e}")

#####################################################################################################################################################
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Hier drunter keine Funktionsdefinitionen mehr einfügen !!!!!!!!!!!!!!!
# Ansonsten werden die Informationen im schlimmsten Fall nicht mehr in Headline und Sidebar angezeigt !!!!