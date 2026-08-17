🇬🇧 [English version](README.md)

# p-count Parkplatz-Belegung für Home Assistant

Custom Integration für Home Assistant, die Parkplatz-Belegungsdaten von
[p-count.de](https://p-count.de) als Sensoren bereitstellt – eine „Freie
Plätze"-Entity pro Parkplatz-Sektion.

Nicht offiziell mit p-count.de verbunden oder von p-count.de unterstützt.
Nutzung auf eigenes Risiko.

## Voraussetzungen

- Eine p-count.de Parkplatz-Instanz mit Zugangsdaten (Carpark-ID, Benutzername,
  Passwort) – diese bekommst du von deinem Parkplatzbetreiber, nicht von
  dieser Integration.
- Home Assistant ≥ 2024.1.0

## Installation

### Über HACS (empfohlen, sobald im Store gelistet)

Bis zur Aufnahme in den offiziellen HACS-Store als benutzerdefiniertes
Repository hinzufügen:

1. HACS → Integrationen → Menü (⋮) → Benutzerdefinierte Repositories
2. URL: `https://github.com/HalmSascha/ha-pcount-integration`, Kategorie:
   Integration
3. „p-count Parkplatz-Belegung" installieren und Home Assistant neu starten

### Manuell

`custom_components/pcount` in dein Home-Assistant-`config/custom_components/`
Verzeichnis kopieren und Home Assistant neu starten.

## Einrichtung

Einstellungen → Geräte & Dienste → Integration hinzufügen → „p-count
Parkplatz-Belegung" suchen. Im Dialog werden folgende Werte abgefragt:

| Feld | Beschreibung |
|---|---|
| Host | Domain der p-count-Instanz, Standard `p-count.de` |
| Parkplatz-ID | Carpark-Slug aus deiner p-count-URL (z.B. `musterfirma1`) |
| Benutzername | Basic-Auth-Benutzername deiner Instanz |
| Passwort | Basic-Auth-Passwort deiner Instanz |

Diese Zugangsdaten bleiben ausschließlich lokal in deiner Home-Assistant-
Konfiguration gespeichert und werden nirgendwo geteilt oder mitgeliefert –
diese Integration enthält keine voreingestellten Zugangsdaten für einen
bestimmten Parkplatzbetreiber.

## Bereitgestellte Entities

Pro Parkplatz-Sektion (laut API-Antwort, z.B. `P1+2`, `P3`) wird ein Sensor
mit dem aktuellen Wert für freie Plätze angelegt. Zusätzliche Attribute:
`short_name`, `long_name`, `occupied_spots`, `measured_at`.

Der Sensor-Name folgt deiner Home-Assistant-UI-Sprache (Entity-Übersetzungen,
Englisch und Deutsch vorhanden) statt hart codiert zu sein – z.B. „Freie
Plätze P1+2" auf Deutsch, „Free spots P1+2" auf Englisch. Die automatisch
vergebene Entity-ID wird einmalig bei der Erstellung festgelegt und bleibt
danach stabil, auch wenn du später deine Sprache änderst.

## Abfrageintervall

Standardmäßig 30 Sekunden. Änderbar unter Einstellungen → Geräte & Dienste →
p-count → Konfigurieren. Das Intervall lässt sich nicht unter 30 Sekunden
setzen (Eingaben darunter werden im Formular mit einer Fehlermeldung
abgelehnt) – Schutz vor versehentlicher Überlastung der API. Eine Änderung
wirkt sofort, ohne Neustart von Home Assistant.

## Lovelace Card

Die Integration bringt eine eigene Custom Card (`pcount-card`) mit, die
optisch an die offizielle p-count Mobile/WebApp angelehnt ist: Kopfzeile mit
Carpark-Name und „Datenstand"-Zeitstempel, optionalem Firmenlogo-Banner und
einer Zeile pro Sektion mit rot/grün-Balken für belegte/freie Plätze.

Die Card wird automatisch als Frontend-Ressource registriert (kein manueller
Eintrag unter Einstellungen → Dashboards → Ressourcen nötig).

### Grafischer Editor

Beim Hinzufügen der Card über die Dashboard-UI („Karte hinzufügen" → „p-count
Parkplatz-Belegung") öffnet sich ein grafischer Editor (`ha-form`-basiert) mit
einem Entity-Picker für die Sensoren sowie Textfeldern für Titel und
Firmenlogo-URL – kein manuelles YAML nötig. Der YAML/UI-Code-Editor
funktioniert weiterhin parallel.

### YAML-Beispiel

```yaml
type: custom:pcount-card
title: Musterfirma 1
logo_url: https://example.com/logo.png
entities:
  - sensor.freie_plaetze_p1_2   # durch deine echten Entity-IDs ersetzen
  - sensor.freie_plaetze_p3
```

Entity-IDs werden bei der Einrichtung automatisch aus deinem Geräte-/
Parkplatznamen und dem übersetzten Sensor-Namen generiert – die genauen
Werte hängen also von deiner Sprache und Parkplatz-ID ab. Nachschauen unter
Einstellungen → Geräte & Dienste → p-count → dein Parkplatz → Entitäten.

| Option | Pflicht | Beschreibung |
|---|---|---|
| `entities` | ja | Liste der Freie-Plätze-Sensor-Entity-IDs, in Anzeigereihenfolge |
| `title` | nein | Überschrift der Card, Standard „Parkplatz-Belegung" |
| `logo_url` | nein | URL zu einem Firmenlogo, wird als Banner unter der Kopfzeile angezeigt (analog zum Logo-Banner der p-count App) |

Farben lassen sich per CSS-Variablen auf Dashboard-/Theme-Ebene anpassen:
`--pcount-card-occupied-color`, `--pcount-card-free-color`,
`--pcount-card-label-color`.

## Roadmap

- [x] Grundgerüst: Config Flow, Coordinator, Sensor-Entities
- [x] Lovelace Card (`pcount-card`), angelehnt an die p-count App
- [x] Grafischer Card-Editor (`getConfigElement`)
- [x] Zweisprachige README (DE/EN)
- [x] Sensor-Entity-Namen lokalisieren (Entity-Übersetzungen)
- [ ] Tests (pytest-homeassistant-custom-component)
- [ ] Aufnahme in den offiziellen HACS-Default-Store
- [ ] iOS-App mit CarPlay-Integration als eigenständiges Folgeprojekt

## Lizenz

[MIT](LICENSE)
