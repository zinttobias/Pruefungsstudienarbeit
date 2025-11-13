# Pruefungsstudienarbeit
# PSA Alexander Hollenrieder, Thilo Fuhrmann, Dominic Schüll, Tobias Zint
import numpy
import requests as req     
         
koordinaten = {
    "coordinates": [
        [10.314009, 47.716193],     # Kempten
        [10.642521, 48.061231]      # Türkheim
        [45.5236, -122.6750]        # Portland   
    ]

}

Zugangsdaten = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjZlM2NmMjA2OGY5MjQwMmJhYmY2YzNjM2NlMDYwNjg1IiwiaCI6Im11cm11cjY0In0=',
    'Content-Type': 'application/json; charset=utf-8'
}


