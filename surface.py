# ============================================
# surface.py
# Mapping für Untergund und Legende
# ============================================

# Mapping der ORS-Surface-Codes
SURFACE_TYPES = {
    0: "unbekannt",
    1: "gepflastert",
    2: "ungepflastert",
    3: "Asphalt",
    4: "Beton",
    5: "Kopfsteinpflaster",
    6: "verdichtet",
    7: "Holz",
    8: "Schotter",
    9: "feiner Kies",
    10: "natürlicher Boden",
    11: "Erde",
    12: "Matsch",
    13: "Schnee/Eis",
    14: "Kopfsteinpflaster",
    15: "Sand",
    16: "Holzchips",
    17: "Gras",
    18: "Rasengitterstein"
}

# Farbcode für Folium - Routenanzeige, statt rot
SURFACE_COLORS = {
    "Asphalt": "blue",
    "Beton": "lightblue",
    "befestigt": "blue",
    "Pflastersteine": "gray",
    "Kopfsteinpflaster": "darkgray",
    "Feinschotter": "orange",
    "Schotter": "saddlebrown",
    "Erde": "green",
    "natürlicher Boden": "darkgreen",
    "Gras": "lightgreen",
    "Sand": "yellow",
    "Holz": "peru",
    "verdichtet": "burlywood",
    "Rasengittersteine": "olive",
    "Natursteinplatten": "dimgray",
    "Eis": "cyan",
    "unbefestigt": "brown",
    "unbekannt": "black"
}
