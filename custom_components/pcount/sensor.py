"""Sensor platform for p-count."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import PCountData, PCountSection
from .const import CONF_CARPARK_ID, DOMAIN
from .coordinator import PCountCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up p-count sensors from a config entry.

    One "free spots" sensor is created per parking section reported by the
    API (e.g. P1+2, P3), based on the sections seen on the first refresh.
    """
    coordinator: PCountCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        PCountFreeSpotsSensor(coordinator, entry, section.short_name)
        for section in coordinator.data.sections
    )


class PCountFreeSpotsSensor(CoordinatorEntity[PCountCoordinator], SensorEntity):
    """Free parking spots for a single section of a p-count carpark."""

    _attr_native_unit_of_measurement = "spots"
    _attr_icon = "mdi:parking"

    def __init__(
        self, coordinator: PCountCoordinator, entry: ConfigEntry, section_key: str
    ) -> None:
        super().__init__(coordinator)
        self._section_key = section_key
        self._entry = entry

        section = self._section()
        display_name = section.long_name if section else section_key
        self._attr_name = f"Freie Plätze {display_name}"
        self._attr_unique_id = f"{entry.entry_id}_{section_key}_free_spots"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"p-count {entry.data[CONF_CARPARK_ID]}",
            manufacturer="p-count.de",
            configuration_url=f"https://{entry.data[CONF_HOST]}",
        )

    def _section(self) -> PCountSection | None:
        """Return the current data for this sensor's section, if present."""
        data: PCountData = self.coordinator.data
        return next(
            (s for s in data.sections if s.short_name == self._section_key), None
        )

    @property
    def native_value(self) -> int | None:
        section = self._section()
        return section.free_spots if section else None

    @property
    def extra_state_attributes(self) -> dict:
        section = self._section()
        if not section:
            return {}
        return {
            "short_name": section.short_name,
            "long_name": section.long_name,
            "occupied_spots": section.occupied_spots,
            "measured_at": self.coordinator.data.measured_at,
        }
