🇩🇪 [Deutsche Version](README.de.md)

# p-count Parking Occupancy for Home Assistant

Custom integration for Home Assistant that exposes parking occupancy data
from [p-count.de](https://p-count.de) as sensors – one "free spots" entity
per parking section.

Not officially affiliated with or endorsed by p-count.de. Use at your own
risk.

## Requirements

- A p-count.de parking instance with credentials (carpark ID, username,
  password) – get these from your parking operator, not from this
  integration.
- Home Assistant ≥ 2024.1.0

## Installation

### Via HACS (recommended, once listed in the store)

Until it's accepted into the official HACS store, add it as a custom
repository:

1. HACS → Integrations → Menu (⋮) → Custom repositories
2. URL: `https://github.com/HalmSascha/ha-pcount-integration`, category:
   Integration
3. Install "p-count Parking Occupancy" and restart Home Assistant

### Manual

Copy `custom_components/pcount` into your Home Assistant
`config/custom_components/` directory and restart Home Assistant.

## Setup

Settings → Devices & Services → Add Integration → search for "p-count
Parking Occupancy". The setup dialog asks for:

| Field | Description |
|---|---|
| Host | Domain of your p-count instance, defaults to `p-count.de` |
| Carpark ID | Carpark slug from your p-count URL (e.g. `musterfirma1`) |
| Username | Basic auth username for your instance |
| Password | Basic auth password for your instance |

These credentials stay entirely local in your Home Assistant configuration
and are never shared or bundled – this integration ships without any
preset credentials for a specific parking operator.

## Provided Entities

For each parking section reported by the API (e.g. `P1+2`, `P3`), a sensor
entity is created with the current free-spot count. Additional attributes:
`short_name`, `long_name`, `occupied_spots`, `measured_at`.

Note: the sensor's friendly name is currently generated in German ("Freie
Plätze \<section\>"), regardless of your Home Assistant UI language, so the
auto-assigned entity ID looks like `sensor.freie_plaetze_p1_2` rather than an
English equivalent. Full localization of entity names is tracked in the
roadmap below.

## Poll Interval

Defaults to 30 seconds. Changeable under Settings → Devices & Services →
p-count → Configure. The interval cannot be set below 30 seconds (lower
values are rejected in the form with an error message) – a safeguard against
accidentally overloading the API. Changes take effect immediately, no Home
Assistant restart required.

## Lovelace Card

The integration ships its own custom card (`pcount-card`), visually modeled
after the official p-count Mobile/WebApp: a header with the carpark name and
"last updated" timestamp, an optional company logo banner, and one row per
section with a red/green occupied-vs-free bar.

The card registers itself as a frontend resource automatically (no manual
entry needed under Settings → Dashboards → Resources).

### Visual Editor

When adding the card via the dashboard UI ("Add Card" → "p-count Parking
Occupancy"), a visual editor (built on `ha-form`) opens with an entity
picker for the sensors plus text fields for title and company logo URL – no
manual YAML needed. The YAML/UI code editor keeps working in parallel.

### YAML Example

```yaml
type: custom:pcount-card
title: Musterfirma 1
logo_url: https://example.com/logo.png
entities:
  - sensor.freie_plaetze_p1_2
  - sensor.freie_plaetze_p3
```

| Option | Required | Description |
|---|---|---|
| `entities` | yes | List of free-spots sensor entity IDs, in display order |
| `title` | no | Card heading, defaults to "Parking Occupancy" |
| `logo_url` | no | URL of a company logo, shown as a banner below the header (mirrors the logo banner in the p-count app) |

Colors can be customized per dashboard/theme via CSS variables:
`--pcount-card-occupied-color`, `--pcount-card-free-color`,
`--pcount-card-label-color`.

## Roadmap

- [x] Foundation: config flow, coordinator, sensor entities
- [x] Lovelace card (`pcount-card`), modeled after the p-count app
- [x] Visual card editor (`getConfigElement`)
- [x] Bilingual README (DE/EN)
- [ ] Localize sensor entity names (currently hardcoded German)
- [ ] Tests (pytest-homeassistant-custom-component)
- [ ] Submission to the official HACS default store
- [ ] iOS app with CarPlay integration as a separate follow-up project

## License

[MIT](LICENSE)
