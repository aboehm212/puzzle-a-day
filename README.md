# Puzzle-A-Day – das Punktespiel

Kalenderrätsel nach dem „A-Puzzle-A-Day“ von DragonFjord: Lege alle Teile so, dass nur Monat und Tag frei bleiben.
Modi: Freies Spiel (einstellbare Schwierigkeit, Zeitbonus, Countdown), Sammeln und Tagesaufgabe mit Serie und gemeinsamer Bestenliste.

## Online spielen (GitHub Pages)

Nach jedem Push auf `main` wird das Spiel automatisch veröffentlicht unter
`https://<dein-github-name>.github.io/<repo-name>/`

Auf GitHub Pages läuft das Spiel ohne Server: Punkte, Serie und gesammelte Lösungen werden im Browser gespeichert.
Die gemeinsame Bestenliste gibt es nur mit dem Docker-Server.

## Mit Bestenliste selbst betreiben (Docker)

Fertiges Image (wird bei jedem Push gebaut):

    docker run -d -p 8080:8080 -v puzzle-data:/data --name puzzle-a-day ghcr.io/<dein-github-name>/<repo-name>:latest

Oder lokal bauen:

    docker compose up -d --build

Danach: http://localhost:8080

Gespeichert werden Name und Ergebnis der Tagesaufgabe pro Spieler und Tag in `/data/scores.json` (Tage älter als `KEEP_DAYS`, Standard 60, werden gelöscht).
Es gibt keine Anmeldung, die Bestenliste ist für Familie und Freunde gedacht. Für den Zugriff aus dem Internet einen Reverse-Proxy mit HTTPS davorschalten.
