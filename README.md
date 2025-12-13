# Readme Prüfungsstudienarbeit

## Produktziel

Für Radfahrer mit dem Wunsch sich automatisch Routen über eine Onlinekarte generieren zu können, entwickeln wir ein Tool, das solche durch Eingabe von Start- und Endpunkt erstellen und anzeigen kann.

----------------------------------------------------------------------------------------
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
## Definition Zeitaufwand Storypoints

ein Storypoint entspricht 10 Minuten

----------------------------------------------------------------------------------------
## Auslagerung der Standartfunktionen

- Die Funktionen welche zu Folium bzw Openrouteservice gehören wurden in functionsbasic ausgelagert
- Alle Packages die in Zukunft noch kommen sollten in functionsbasic eingeführt werden
- Das Marker setzen funktioniert jetzt mit Klassen z.B. place_marker.start(start, route_v["Startpunkt"])
- 
----------------------------------------------------------------------------------------
## Wetterdienst API

- Da die API vom deutschen Wetterdienst nicht funktioniert wie gewünscht habe ich jetzt die API von Open Meteo
eingebunden, welche auch eine Installation in Anaconda

----------------------------------------------------------------------------------------
## Streamlit

- Um Streamlit automatisiert öffnen zu können folgenden Befehl in Anaconda eingeben
"conda init powershell"
- Jetzt kann man Anaconda über das Terminal in VS Code verwenden 
-> "streamlit run main.py" Befehl funktioniert in VS Code

## Streamlit Community Cloud

-Das Projekt ist über folgenden Link erreichbar: https://pruefungsstudienarbeit-d8vq93hhknpasmnijvtvth.streamlit.app/
-Damit es weiterhin läuft müssen alle hinzugefügten Packages in die Textdatei requirements eingetragen werden