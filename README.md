# Studien-Dashboard

Interaktives Dashboard zur Verfolgung des persönlichen Studienfortschritts, entwickelt als prototypische Webanwendung mit Python und Streamlit.

## Voraussetzungen

Für die Ausführung des Dashboards werden Python 3.11 oder höher sowie Git benötigt.

## Installation

PowerShell öffnen und das Repository klonen:

```
git clone https://github.com/GinaBilinski/studium-dashboard.git
cd studium-dashboard
```

Virtuelle Python-Umgebung erstellen und aktivieren:

```
python -m venv .venv
.venv\Scripts\activate
```

Alle benötigten Bibliotheken installieren:

```
pip install -r requirements.txt
```

## Starten

```
streamlit run app.py
```

Nach dem Start öffnet sich das Dashboard automatisch im Standardbrowser unter der Adresse http://localhost:8501. Beim ersten Aufruf wird die Datenbank automatisch angelegt. Anschließend können über den Button "Ziele einstellen" Studienbeginn, geplante Studiendauer und Zielnote festgelegt werden, woraufhin alle Funktionen des Dashboards vollständig nutzbar sind.

## Datenbank zurücksetzen

Falls die Datenbank zurückgesetzt werden soll, kann die Datei studium.db gelöscht werden. Beim nächsten Start wird sie automatisch neu angelegt:

```
rm studium.db
```
