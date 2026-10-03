# Frau Holle – Produktionssteuerungssystem für eine Halbleiterfertigung

Teamprojekt im Rahmen der Module *Software Engineering I & II* (HTW Dresden). Entwickelt nach dem **Unified Process (OpenUP)** mit echten Anforderungsworkshops, iterativer Entwicklung und einem simulierten Auftraggeber (gespielt vom betreuenden Professor) für die fiktive Halbleiterfabrik "Frau Holle".

> Dies ist mein persönlicher Fork des Team-Repositories zu Portfolio-Zwecken. Original: [leni04/i04-projekt-frau-holle](https://github.com/leni04/i04-projekt-frau-holle)

## Über das Projekt

Die Fertigung von Halbleitern ist ein komplexer, 30–80 Tage dauernder Prozess: Silizium-Scheiben werden zu **Losen** zusammengefasst und durchlaufen wiederholt Produktionsschritte (Fotolack auftragen, belichten, ätzen, beschichten) bis zur fertigen Verdrahtung. Bisher gab es dafür keine Software — die Fabrik hatte keine Transparenz über den Fertigungsfortschritt.

**Ziel des Projekts:** Eine Datenbankanwendung, die die Fertigungsabläufe, Anlagen-Ressourcen und Materialverwaltung digital abbildet und den Mitarbeitern/Fertigungsleitern einen Echtzeit-Überblick über den Produktionsstatus gibt.

## Umgesetzte Funktionen (Use Cases)

| UC | Funktion | Status |
|----|----------|--------|
| UC01 | Los starten | ✅ implementiert & vom Auftraggeber abgenommen |
| UC02 | Los zwischen Produktionsschritten bewegen | ✅ implementiert & abgenommen |
| UC03 | Los bearbeiten | ✅ implementiert & abgenommen |
| UC04 | Stammdaten anzeigen | ✅ implementiert & abgenommen *(mein Beitrag)* |
| UC05 | Stammdaten bearbeiten | ✅ implementiert & abgenommen *(mein Beitrag)* |
| UC06 | Daten exportieren (CSV) | ✅ implementiert & abgenommen |
| UC07 | Daten importieren (CSV) | ✅ implementiert & abgenommen |
| UC08 | Backup erstellen | 🧩 nur Konzept (zeitlich nicht mehr umgesetzt) |
| UC09 | Report erstellen | 📝 Anforderungen analysiert, nicht implementiert |
| UC10 | Maschine bearbeiten | 📝 Anforderungen analysiert, nicht implementiert |
| UC11 | Daten visualisieren | 📝 Anforderungen analysiert, nicht implementiert |

Zwei Nutzerrollen mit unterschiedlichen Rechten: **Mitarbeiter** (nur Einsicht) und **Fertigungsleiter** (Einsicht + Bearbeitung).

## Mein Beitrag

Ich war verantwortlich für **UC04 (Stammdaten anzeigen)** und **UC05 (Stammdaten bearbeiten)**:

- Konzeption und Umsetzung der Stammdaten-Übersicht (Analyse, Entwurf und Implementierung eigenständig, da zu Projektbeginn kaum Vorarbeit existierte)
- Wireframes erstellt und nach Kundenfeedback mehrfach iteriert — von einer überladenen Einzelseite zu einer übersichtlichen Navigationsstruktur mit fokussierter Lot-Stammdatenseite als Vorlage für nachfolgende Teams
- Bearbeitungsfunktion für alle Attribute inkl. rollenbasierter Ausblendung der Bearbeitungsfelder für die Rolle "Mitarbeiter"
- Spaltensortierung per Klick auf den Tabellenkopf per JavaScript umgesetzt (dafür JS im Projekt neu angeeignet)
- Vier Entwicklungsiterationen mit regelmäßigem Pull-Request-Workflow gegen den `main`-Branch

(Ausführliche Reflexion inkl. Lessons Learned: [`docs/belegabgabe_se2/Projektreflextion/eigenleistung_Richard.adoc`](docs/belegabgabe_se2/Projektreflextion/eigenleistung_Richard.adoc))

## Tech-Stack

- **Backend:** Python 3.12, Flask (modular über Blueprints), SQLAlchemy (ORM)
- **Datenbank:** PostgreSQL
- **Frontend:** Serverseitig gerenderte HTML-Templates (Jinja2), CSS, JavaScript
- **Zielplattform:** Raspberry Pi (Raspbian/Linux)
- **Vorgehensmodell:** Unified Process / OpenUP, iterativ-inkrementell mit regelmäßigen Kundenmeetings

## Architektur

Die Anwendung ist in Flask-Blueprints je Funktionsbereich strukturiert (`login`, `los_starten`, `los_bewegen`, `los_bearbeiten`, `Stammdaten`, `import_data`, `export_data`, `entities`). Vollständige Architekturdokumentation (C4-Modell, ER-Modell, Klassendiagramme) liegt unter [`docs/architecture`](docs/architecture).

## Setup / Lokale Ausführung

```bash
# 1. Repository klonen
git clone https://github.com/RichardSchultz-gh/semiconductor-logistics-automation.git
cd semiconductor-logistics-automation/src

# 2. Abhängigkeiten installieren
pip install flask sqlalchemy psycopg2-binary

# 3. PostgreSQL-Datenbank anlegen
# Tabellen + Testdaten via docs/development/DB_Tabellen_erstellen/DBanlegen.sql
# (CSV-Testdaten liegen im gleichen Ordner)

# 4. Datenbankzugang ggf. in src/config.py anpassen (Standard: localhost:5432)

# 5. Anwendung starten
python app.py
```

Die Anwendung ist anschließend über die in der Konsole ausgegebene IP erreichbar (Flask-Testserver). Test-Logins: `user1`/`pass1` (Fertigungsleiter), `user2`/`pass2` (Mitarbeiter) — reine Entwicklungs-Zugangsdaten, keine echten Secrets.

## Tests

Test-Fälle je Use Case liegen in [`src/testing`](src/testing), ausführliche Testdokumentation (inkl. Bugtracker) unter [`docs/test`](docs/test).

## Projektdokumentation

Das Projekt wurde vollständig nach OpenUP dokumentiert — Anforderungen, Architektur, Testkonzept, Iterationspläne und Kundenmeeting-Protokolle liegen unter [`docs/`](docs). Das zeigt den kompletten Software-Engineering-Prozess, nicht nur den Code.

## Team (I04)

| Name | GitHub |
|------|--------|
| Richard Schultz | [@RichardSchult-gh](https://github.com/RichardSchult-gh) |
| Marlene Winter | [@leni04](https://github.com/leni04) |
| Nils Generlich | [@nilsgnh](https://github.com/nilsgnh) |
| Yannik-Joel Herrchen | [@yjh-4](https://github.com/yjh-4) |
| Nico Kroll | [@s85210](https://github.com/s85210) |
| Paul Marx | [@pmx1994-dev](https://github.com/pmx1994-dev) |
| Enrico Kersten | [@EnricoKersten](https://github.com/EnricoKersten) |
| Hoang Nguyen Sy | [@Hoang84222](https://github.com/Hoang84222) |

## Lizenz

MIT
