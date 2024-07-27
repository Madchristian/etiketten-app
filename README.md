# Etiketten-App

## Beschreibung

Diese Anwendung generiert aus einer Datei im Format <strong>Termine (TAB).txt</strong> ein PDF-Dokument mit Etiketten, die auf Schlüsselanhänger aufgeklebt werden können. Für diesen Zweck verwenden Sie bitte Avery Zweckform Typ 3657 "49x25". Um die Datei zu erstellen, wählen Sie in unserem TKP Planer die Option "Exportieren - Termine (TAB getrennt)" und laden Sie die heruntergeladene Datei hier hoch.

## Technologie-Stack

### Frontend
- **React**: JavaScript-Bibliothek zur Erstellung von Benutzeroberflächen.
- **Axios**: HTTP-Client zur Kommunikation mit dem Backend.
- **CSS**: Für das Styling der Anwendung.

### Backend
- **Python**: Programmiersprache zur Implementierung der Logik.
- **FastAPI**: Web-Framework für den Aufbau von APIs.
- **Pandas**: Datenanalyse- und Manipulationsbibliothek.
- **ReportLab**: Bibliothek zur Erstellung von PDF-Dokumenten.
- **Uvicorn**: ASGI-Server zum Ausführen der FastAPI-Anwendung.

### Containerization
- **Docker**: Containerplattform zur Bereitstellung der Anwendung.
- **Docker Compose**: Werkzeug zur Definition und Ausführung mehrerer Docker-Container.

### Sicherheit
- **CORS**: Konfiguration, um den Zugriff nur von bestimmten Domains zu erlauben.
- **File Size Limiter**: Begrenzung der Dateigröße auf 300 KB.
- **File Type Validator**: Akzeptiert nur .txt-Dateien.
- **Rate Limiting**: Begrenzung der Anzahl der Uploads, um Missbrauch zu verhindern.

## Setup und Installation

### Voraussetzungen
- Docker
- Docker Compose
- Git

### Installation

1. **Repository klonen**
    ```sh
    git clone https://github.com/Madchristian/etiketten-app.git
    cd etiketten-app
    ```

2. **Umgebungsvariablen konfigurieren**
    Erstelle eine `.env` Datei im Wurzelverzeichnis und füge die benötigten Umgebungsvariablen hinzu (z.B. für Rate Limiting).

3. **Docker Container starten**
    ```sh
    docker-compose up --build
    ```

4. **Zugriff auf die Anwendung**
    - **Frontend**: [http://localhost:3000](http://localhost:3000)
    - **Backend**: [http://localhost:8000](http://localhost:8000)

## Nutzung

1. Navigieren Sie zur Webseite.
2. Laden Sie die Datei im Format <strong>Termine (TAB).txt</strong> hoch.
3. Die generierte PDF-Datei wird automatisch heruntergeladen.

## Sicherheit

Der Backend-Service auf Port 8000 ist durch mehrere Maßnahmen geschützt:
- Akzeptiert nur .txt-Dateien.
- Maximale Dateigröße von 300 KB.
- Rate Limiting, um Missbrauch zu verhindern.

## Lizenz

Diese Anwendung ist unter der Apache 2.0-Lizenz veröffentlicht. Siehe die [LICENSE](./LICENSE) Datei für weitere Details.