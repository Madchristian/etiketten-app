# etiketten-app
# Etiketten-App

Diese Anwendung generiert PDF-Dateien mit Etiketten aus einer hochgeladenen `.txt` Datei. Die Etiketten sind für Avery Zweckform "49x25" geeignet. Benutzer können die `.txt` Datei hochladen, und die App erstellt ein PDF mit den Etiketten zum Ausdrucken und Aufkleben auf Schlüsselanhänger.

## Funktionen

- Hochladen einer `.txt` Datei mit Termindaten.
- Generierung eines PDF mit Etiketten basierend auf den hochgeladenen Daten.
- Unterstützung für Avery Zweckform 3657 "49x25" Etiketten.
- Automatische Beschriftung mit Kundendaten, Auftragsnummern und Notizen.
- Begrenzung der Notizen auf maximal 200 Zeichen und maximal 5 Zeilen.
- QR-Code-Erzeugung für Auftragsnummern (deaktiviert)
- Sicherstellung, dass nur .txt Dateien hochgeladen werden können und dass die Dateigröße 300 KB nicht überschreitet.
- Löschen der hochgeladenen Datei nach der Verarbeitung.

## Sicherheitsdetails

- Die Anwendung akzeptiert nur `.txt` Dateien mit einer maximalen Größe von 300 KB.
- Der Upload und die Verarbeitung der Dateien sind durch einen Try-Finally-Block gesichert, um sicherzustellen, dass temporäre Dateien immer gelöscht werden.
- Cross-Origin Resource Sharing (CORS) ist konfiguriert, um den Zugriff nur von bestimmten Origins zuzulassen.
- Die PDF-Datei wird nur an den Benutzer zurückgegeben, der sie hochgeladen hat.

## Anforderungen

- Node.js und Yarn für das Frontend
- Python 3.12 und pip für das Backend
- Docker und Docker Compose zum Hosten der Anwendung

## Installation und Ausführung

### 1. Klonen des Repositories

```sh
git clone https://github.com/DeinBenutzername/etiketten-app.git
cd etiketten-app

docker-compose up --build
```

Anpassen der CORS-Einstellungen in `backend/app/main.py`:
```python
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://etiketten.cstrube.de",
    # Füge weitere erlaubte Origins hier hinzu
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```


Deployment Beispiel mit traefik:
```yaml
version: '3.7'

services:
  frontend:
    image: etiketten-app-frontend
    build:
      context: ./frontend
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`etiketten.cstrube.de`)"
      - "traefik.http.services.frontend.loadbalancer.server.port=3000"
    ports:
      - "3000:3000"

  backend:
    image: etiketten-app-backend
    build:
      context: ./backend
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`etiketten.cstrube.de`) && PathPrefix(`/upload`)"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
    ports:
      - "8000:8000"

  traefik:
    image: traefik:v2.4
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    ```