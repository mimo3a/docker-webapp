# Todo-App mit Docker Compose

Eine einfache REST-API zur Verwaltung von Todos. Die Anwendung besteht aus zwei Containern, die mit Docker Compose orchestriert werden.

**Autor:** Oleksandr Demianov (GitHub: mimo3a)

**Lehrveranstaltung:** Current Technologies, MCI

## Architektur

Die Anwendung besteht aus zwei Diensten:

- **app:** Python-Backend mit Flask. Es stellt die REST-API auf Port 5000 bereit. Das Image wird über das `Dockerfile` im Ordner `app/` gebaut.
- **db:** PostgreSQL 16 (offizielles Image). Die Daten werden im benannten Volume `postgres_data` gespeichert.

```
Browser / Client  --->  app (Flask, Port 5000)  --->  db (PostgreSQL, Port 5432 intern)
                                                          |
                                                   Volume: postgres_data
```

Beide Container laufen im selben Docker-Netzwerk. Daher erreicht das Backend die Datenbank über den Servicenamen `db`. Der Datenbank-Port wird nicht nach außen freigegeben.

## Projektstruktur

```
docker-webapp/
├── app/
│   ├── app.py              # Flask-Anwendung (REST-API)
│   ├── requirements.txt    # Python-Abhängigkeiten
│   ├── Dockerfile          # Bauanleitung für das Backend-Image
│   └── .dockerignore
├── docker-compose.yml      # Orchestrierung von app und db
├── .env.example            # Vorlage für die Umgebungsvariablen
├── .gitignore
└── README.md
```

## Voraussetzungen

- Docker Desktop (beziehungsweise Docker Engine) mit Docker Compose v2
- Port 5000 muss frei sein

## Starten

1. Repository klonen und in den Ordner wechseln.
2. Datei `.env` aus der Vorlage erstellen und ein eigenes Passwort eintragen:

   ```bash
   cp .env.example .env
   ```

   Unter Windows (PowerShell):

   ```powershell
   Copy-Item .env.example .env
   ```

3. Container bauen und starten:

   ```bash
   docker compose up --build
   ```

4. Die API ist unter `http://localhost:5000/todos` erreichbar.

Stoppen:

```bash
docker compose down
```

## API-Endpunkte

| Methode | Pfad | Beschreibung | Antwort |
|---|---|---|---|
| GET | `/todos` | Alle Todos abrufen | 200 + Liste |
| POST | `/todos` | Neues Todo anlegen, Body: `{"title": "..."}` | 201 + Todo, 400 bei ungültigen Daten |
| DELETE | `/todos/<id>` | Todo löschen | 204, 404 falls nicht vorhanden |

Beispiel für ein Todo:

```json
{ "id": 1, "title": "Docker lernen", "done": false }
```

### Beispiele mit curl

```bash
curl http://localhost:5000/todos
curl -X POST http://localhost:5000/todos -H "Content-Type: application/json" -d '{"title":"Docker lernen"}'
curl -X DELETE http://localhost:5000/todos/1
```

### Beispiele mit PowerShell

```powershell
Invoke-RestMethod -Uri http://localhost:5000/todos
Invoke-RestMethod -Uri http://localhost:5000/todos -Method Post -ContentType "application/json" -Body '{"title":"Docker lernen"}'
Invoke-RestMethod -Uri http://localhost:5000/todos/1 -Method Delete
```

## Umsetzung der Anforderungen

- **Webanwendung:** REST-API mit Lesen, Anlegen und Löschen von Todos sowie Datenbankanbindung.
- **Dockerfile:** Das Backend wird über `app/Dockerfile` gebaut. Die Abhängigkeiten werden vor dem Code kopiert, damit der Layer-Cache bei Codeänderungen erhalten bleibt.
- **Mindestens zwei Container:** `app` und `db` werden über `docker-compose.yml` gemeinsam gestartet.
- **Benanntes Volume:** Die PostgreSQL-Daten liegen im Volume `postgres_data`. Damit bleiben sie auch nach `docker compose down` erhalten.
- **Keine Passwörter im Compose-File:** Zugangsdaten werden als Variablen (`${POSTGRES_PASSWORD}` und so weiter) referenziert. Die Werte stehen in der Datei `.env`, die über `.gitignore` vom Repository ausgeschlossen ist.
- **Startreihenfolge:** Die Datenbank besitzt einen Healthcheck mit `pg_isready`. Das Backend startet erst, wenn die Datenbank bereit ist (`condition: service_healthy`).

## Persistenz testen

1. Einige Todos per POST anlegen.
2. `docker compose down` und anschließend `docker compose up` ausführen.
3. `GET /todos` zeigt weiterhin dieselben Todos, da das Volume erhalten bleibt.
4. Mit `docker compose down -v` wird auch das Volume gelöscht. Danach ist die Liste leer.

**Fazit:** Die Daten werden nicht im Container, sondern im benannten Volume gespeichert. Container lassen sich daher jederzeit löschen und neu erstellen.
