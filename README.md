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
`sensor.freie_plaetze_<sektion>` mit dem aktuellen Wert für freie Plätze
angelegt. Zusätzliche Attribute: `long_name`, `occupied_spots`, `measured_at`.

Das Abfrageintervall startet bei 30 Sekunden und übernimmt danach den von
der API empfohlenen Wert (`polling_seconds` in der Antwort).

## Roadmap

- [x] Grundgerüst: Config Flow, Coordinator, Sensor-Entities
- [ ] Tests (pytest-homeassistant-custom-component)
- [ ] Aufnahme in den offiziellen HACS-Default-Store
- [ ] iOS-App mit CarPlay-Integration als eigenständiges Folgeprojekt

## Lizenz

[MIT](LICENSE)
