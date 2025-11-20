# Readme Prüfungsstudienarbeit

## Produktziel

Für Radfahrer mit dem Wunsch sich automatisch Routen über eine Onlinekarte generieren zu können, entwickeln wir ein Tool, das solche durch Eingabe von Start- und Endpunkt erstellen und anzeigen kann.

## Eingabeform Start-/ Endpunkt:

Rückgabewerte sind einem Directory angelegt, daher Startpunkt usw. nur noch so aufrufen:

    route_v["Startpunkt"]
    route_v["Zielpunkt"]
    route_v["Zwischenstopp"]
    route_v["Durchschnittsgeschwindigkeit"]
----------------------------------------------------------------------------------------
## Definition von "Done" für abgeschlossene Tasks

- Die Funktion wurde getestet und für funktionsfähig befunden
- Der gesamte Code der erstellen Funktion wurde in den Main-branch überführt
----------------------------------------------------------------------------------------
## Auslagerung der Standartfunktionen

- Die Funktionen welche zu Folium bzw Openrouteservice gehören wurden in functionsbasic ausgelagert
- Alle Packages die in Zukunft noch kommen sollten in functionsbasic eingeführt werden
- Das Marker setzen funktioniert jetzt mit Klassen z.B. place_marker.start(start, route_v["Startpunkt"]) 
