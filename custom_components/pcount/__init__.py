"""The p-count parking occupation integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import PCountApiClient
from .const import CONF_CARPARK_ID, DOMAIN
from .coordinator import PCountCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Served under /pcount/pcount-card.js regardless of how many carparks are
# configured - registered once in async_setup, not per config entry.
CARD_URL_PATH = f"/{DOMAIN}/pcount-card.js"
CARD_VERSION = "2"  # bump to bust the frontend cache whenever the card changes


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the pcount-card Lovelace card as a frontend resource."""
    js_path = Path(__file__).parent / "www" / "pcount-card.js"

    try:
        # Home Assistant >= 2024.7 (async, avoids executor hop).
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(CARD_URL_PATH, str(js_path), True)]
        )
    except ImportError:
        # Home Assistant < 2024.7 fallback (sync, deprecated in newer core
        # but still functional).
        hass.http.register_static_path(CARD_URL_PATH, str(js_path), True)

    add_extra_js_url(hass, f"{CARD_URL_PATH}?v={CARD_VERSION}")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up p-count from a config entry."""
    session = async_get_clientsession(hass)
    client = PCountApiClient(
        session,
        entry.data[CONF_HOST],
        entry.data[CONF_CARPARK_ID],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )
    coordinator = PCountCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload the entry when options (currently: the poll interval) change,
    # so a new PCountCoordinator picks up the updated value immediately.
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
