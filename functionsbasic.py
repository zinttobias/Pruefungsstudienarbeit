# Import notwendiger Bibliotheken bzw. Packages

import numpy
import requests as req 
import folium
import openrouteservice
import math
from folium.plugins import MiniMap, MeasureControl
import streamlit as st
import streamlit.components.v1 as components
import subprocess
import sys
import os
import webbrowser

#ORS-Client Zugangsschlüssel
client = openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImRmNzExNzZkYmZhMzQ4Njc5OGE3MDEzM2EwMWFiOWE5IiwiaCI6Im11cm11cjY0In0=")
         

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

    def start(self, coords, popup):
        folium.Marker(
            location=[coords[1], coords[0]],
            tooltip="Start",
            popup=popup,
            icon=folium.Icon(color="green", icon="play")
        ).add_to(self.our_map)

    def zwischenstopp(self, coords, popup):
        folium.Marker(
            location=[coords[1], coords[0]],
            tooltip="Zwischenstopp",
            popup=popup,
            icon=folium.Icon(color="orange", icon="pause")
        ).add_to(self.our_map)

    def ziel(self, coords, popup):
        folium.Marker(
            location=[coords[1], coords[0]],
            tooltip="Ziel",
            popup=popup,
            icon=folium.Icon(color="red", icon="flag")
        ).add_to(self.our_map)

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

#####################################################################################################################################################

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Hier drunter keine Funktionsdefinitionen mehr einfügen !!!!!!!!!!!!!!!
# Ansonsten werden die Informationen im schlimmsten Fall nicht mehr in Headline und Sidebar angezeigt !!!!