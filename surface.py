# ============================================
# surface.py
# Mapping für Untergund und Legende
# ============================================

# Mapping der ORS-Surface-Codes
SURFACE_TYPES = {
    0: "unbekannt",
    1: "befestigt",
    2: "unbefestigt",
    3: "Asphalt",
    4: "Beton",
    5: "Kopfsteinpflaster",
    6: "verdichtet",
    7: "Feinschotter",
    8: "Schotter",
    9: "Erde",
    10: "natürlicher Boden",
    11: "Eis",
    12: "Pflastersteine",
    13: "Sand",
    14: "Holz",
    15: "Natursteinplatten",
    16: "Gras",
    17: "Rasengittersteine"
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
