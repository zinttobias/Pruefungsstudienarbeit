"""
--------------------------------------------------------------------------------------------
Pruefungsstudienarbeit Programmieren 3 WS 25/26
surface.py
Mapping für Untergrund und Gelände
--------------------------------------------------------------------------------------------
"""

# Mapping der ORS-Surface-Codes
SURFACE_TYPES = {
    0: "unbekannt",
    1: "gepflastert",
    2: "ungepflastert",                 #beinhaltet Holzchips, Fels
    3: "Asphalt",
    4: "Beton",
    5: "Kopfsteinpflaster",             #Wert existiert nicht mehr
    6: "verdichtet",
    7: "Holz",
    8: "Schotter",
    9: "feiner Kies",                   #Wert existiert nicht mehr
    10: "natürlicher Boden",
    11: "Erde",
    12: "Matsch",
    13: "Schnee/Eis",
    14: "Kopfsteinpflaster",
    15: "Sand",
    16: "Holzchips",                    #Wert existiert nicht mehr
    17: "Gras",
    18: "Rasengitterstein"
}

# Farbcode für Folium - Routenanzeige, statt rot
SURFACE_COLORS = {
    "unbekannt": "black",
    "gepflastert": "blue",
    "ungepflastert": "brown",
    "Asphalt": "blue",
    "Beton": "lightblue",
    "Kopfsteinpflaster": "gray",
    "verdichtet": "burlywood",
    "Holz": "peru",
    "Schotter": "saddlebrown",
    "feiner Kies": "orange",
    "natürlicher Boden": "dark green",
    "Erde": "green",
    "Matsch": "brown",
    "Schnee/Eis": "cyan",
    "Sand": "yellow",
    "Holzchips": "peru",
    "Gras": "lightgreen",
    "Rasengitterstein": "olive"
}
