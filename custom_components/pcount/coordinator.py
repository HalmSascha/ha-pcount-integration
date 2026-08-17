"""DataUpdateCoordinator for the p-count integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PCountApiClient, PCountApiError, PCountAuthError, PCountData
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PCountCoordinator(DataUpdateCoordinator[PCountData]):
    """Coordinator that polls the p-count occupation endpoint.

    Starts with DEFAULT_SCAN_INTERVAL and then adopts the server-provided
    `polling_seconds` from the first successful response, so we neither
    hammer the API nor poll needlessly slowly.
    """

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: PCountApiClient
    ) -> None:
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name=f"pcount_{entry.entry_id}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> PCountData:
        try:
            data = await self.client.async_get_data()
        except PCountAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except PCountApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        if data.polling_seconds > 0:
            recommended = timedelta(seconds=data.polling_seconds)
            if recommended != self.update_interval:
                self.update_interval = recommended

        return data
