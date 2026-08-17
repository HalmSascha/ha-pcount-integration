"""DataUpdateCoordinator for the p-count integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PCountApiClient, PCountApiError, PCountAuthError, PCountData
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, MIN_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PCountCoordinator(DataUpdateCoordinator[PCountData]):
    """Coordinator that polls the p-count occupation endpoint.

    The poll interval is user-configurable via the options flow (default
    DEFAULT_SCAN_INTERVAL), but is always clamped to MIN_SCAN_INTERVAL as a
    hard floor - the options flow already rejects lower values in the UI,
    this is just a defensive second line in case options ever get set some
    other way (e.g. directly in storage).
    """

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: PCountApiClient
    ) -> None:
        self.client = client
        scan_interval = max(
            entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            MIN_SCAN_INTERVAL,
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"pcount_{entry.entry_id}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> PCountData:
        try:
            return await self.client.async_get_data()
        except PCountAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except PCountApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
