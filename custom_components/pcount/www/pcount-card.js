/**
 * pcount-card - Lovelace custom card for the p-count integration.
 *
 * Visually mirrors the layout of the official p-count Mobile/WebApp
 * (https://p-count.de/#/<carpark_id>): a header with the carpark name and
 * last-updated timestamp, an optional logo banner, and one row per parking
 * section with a red/green occupied-vs-free bar.
 *
 * Plain custom element, no build step / no external dependencies, so it
 * ships as-is inside custom_components/pcount/www/ and works on any
 * Home Assistant frontend without a bundler.
 *
 * Example card config:
 *
 *   type: custom:pcount-card
 *   title: Musterfirma 1
 *   logo_url: https://example.com/logo.png
 *   entities:
 *     - sensor.freie_platze_p1_2
 *     - sensor.freie_platze_p3
 */

class PCountCard extends HTMLElement {
  static getStubConfig(hass) {
    const entities = Object.keys(hass.states).filter((entityId) => {
      const stateObj = hass.states[entityId];
      return (
        entityId.startsWith("sensor.") &&
        stateObj.attributes &&
        "occupied_spots" in stateObj.attributes
      );
    });
    return { type: "custom:pcount-card", entities, logo_url: "" };
  }

  setConfig(config) {
    if (
      !config.entities ||
      !Array.isArray(config.entities) ||
      config.entities.length === 0
    ) {
      throw new Error(
        'pcount-card: "entities" muss eine nicht-leere Liste von Sensor-Entity-IDs sein.'
      );
    }
    this._config = config;
    this._buildDom();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 1 + (this._config?.entities?.length || 1);
  }

  connectedCallback() {
    this._render();
  }

  _buildDom() {
    if (this._root) {
      // Config changed after initial build (e.g. editor preview) - just
      // update the logo and re-render on next hass update.
      this._applyLogo();
      return;
    }

    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `
      <style>
        :host { display: block; }
        ha-card {
          overflow: hidden;
          --pcount-occupied-color: var(--pcount-card-occupied-color, #b71c1c);
          --pcount-free-color: var(--pcount-card-free-color, #2e7d32);
          --pcount-label-bg: var(--pcount-card-label-color, #5c7cb5);
        }
        .header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 16px 8px;
        }
        .header .titles { display: flex; flex-direction: column; min-width: 0; }
        .header .title {
          font-size: 1.15em;
          font-weight: 500;
          color: var(--primary-text-color);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .header .subtitle { font-size: 0.8em; color: var(--secondary-text-color); }
        .header ha-icon-button { --mdc-icon-size: 20px; color: var(--secondary-text-color); }
        .logo-banner {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px;
          background: var(--secondary-background-color, #eceff1);
        }
        .logo-banner img { max-height: 48px; max-width: 80%; }
        .rows { display: flex; flex-direction: column; }
        .row {
          display: flex;
          align-items: stretch;
          min-height: 56px;
          border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
        }
        .row:first-child { border-top: none; }
        .label {
          flex: 0 0 34%;
          background: var(--pcount-label-bg);
          color: #fff;
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding: 6px 12px;
          min-width: 0;
        }
        .label .short {
          font-size: 1.3em;
          font-weight: 700;
          line-height: 1.15;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .label .long {
          font-size: 0.75em;
          opacity: 0.85;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .bar { position: relative; flex: 1 1 auto; overflow: hidden; }
        .segment-bg { position: absolute; top: 0; bottom: 0; }
        .segment-bg.occupied { left: 0; background: var(--pcount-occupied-color); }
        .segment-bg.free { right: 0; background: var(--pcount-free-color); }
        .segment-label {
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          color: #fff;
          font-weight: 700;
          font-size: 0.95em;
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
        }
        .segment-label.occupied-label { left: 10px; }
        .segment-label.free-label { right: 10px; }
        .row.unavailable .bar {
          display: flex;
          align-items: center;
          padding: 0 12px;
          color: var(--secondary-text-color);
          font-style: italic;
        }
      </style>
      <ha-card>
        <div class="header">
          <div class="titles">
            <span class="title"></span>
            <span class="subtitle"></span>
          </div>
          <ha-icon-button label="Aktualisieren">
            <ha-icon icon="mdi:refresh"></ha-icon>
          </ha-icon-button>
        </div>
        <div class="logo-banner" hidden><img alt="Firmenlogo" /></div>
        <div class="rows"></div>
      </ha-card>
    `;
    this._root = root;
    root
      .querySelector("ha-icon-button")
      .addEventListener("click", () => this._refresh());

    this._applyLogo();
  }

  _applyLogo() {
    if (!this._root) return;
    const logoUrl = this._config.logo_url || this._config.logo || "";
    const banner = this._root.querySelector(".logo-banner");
    if (logoUrl) {
      banner.hidden = false;
      banner.querySelector("img").src = logoUrl;
    } else {
      banner.hidden = true;
    }
  }

  _refresh() {
    if (!this._hass || !this._config) return;
    this._hass.callService("homeassistant", "update_entity", {
      entity_id: this._config.entities,
    });
  }

  _render() {
    if (!this._root || !this._hass || !this._config) return;

    const root = this._root;
    const entities = this._config.entities;
    let latestMeasuredAt = null;
    const rowsHtml = [];

    entities.forEach((entityId) => {
      const stateObj = this._hass.states[entityId];

      if (!stateObj) {
        rowsHtml.push(`
          <div class="row unavailable">
            <div class="label"><span class="short">?</span></div>
            <div class="bar">${entityId} nicht gefunden</div>
          </div>
        `);
        return;
      }

      const shortName =
        stateObj.attributes.short_name ||
        stateObj.attributes.friendly_name ||
        entityId;
      const longName = stateObj.attributes.long_name || "";
      const measuredAt = stateObj.attributes.measured_at;
      if (measuredAt && (!latestMeasuredAt || measuredAt > latestMeasuredAt)) {
        latestMeasuredAt = measuredAt;
      }

      const free = Number(stateObj.state);
      const occupied = Number(stateObj.attributes.occupied_spots);
      const isValid =
        stateObj.state !== "unavailable" &&
        stateObj.state !== "unknown" &&
        !Number.isNaN(free) &&
        !Number.isNaN(occupied);

      if (!isValid) {
        rowsHtml.push(`
          <div class="row unavailable">
            <div class="label">
              <span class="short">${shortName}</span>
              <span class="long">${longName}</span>
            </div>
            <div class="bar">nicht verfügbar</div>
          </div>
        `);
        return;
      }

      const total = occupied + free;
      const occupiedPct = total > 0 ? (occupied / total) * 100 : 50;
      const freePct = total > 0 ? (free / total) * 100 : 50;

      rowsHtml.push(`
        <div class="row">
          <div class="label">
            <span class="short">${shortName}</span>
            <span class="long">${longName}</span>
          </div>
          <div class="bar">
            <div class="segment-bg occupied" style="width:${occupiedPct}%"></div>
            <div class="segment-bg free" style="width:${freePct}%"></div>
            <span class="segment-label occupied-label">${occupied}</span>
            <span class="segment-label free-label">${free}</span>
          </div>
        </div>
      `);
    });

    root.querySelector(".rows").innerHTML = rowsHtml.join("");
    root.querySelector(".title").textContent =
      this._config.title || this._config.name || "Parkplatz-Belegung";

    const subtitleEl = root.querySelector(".subtitle");
    if (latestMeasuredAt) {
      const d = new Date(latestMeasuredAt);
      subtitleEl.textContent = `Datenstand: ${d.toLocaleDateString(
        "de-DE"
      )} ${d.toLocaleTimeString("de-DE", {
        hour: "2-digit",
        minute: "2-digit",
      })} Uhr`;
    } else {
      subtitleEl.textContent = "";
    }
  }
}

customElements.define("pcount-card", PCountCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "pcount-card",
  name: "p-count Parkplatz-Belegung",
  description:
    "Zeigt die p-count Parkplatz-Belegung optisch angelehnt an die offizielle p-count App an.",
  preview: false,
});
