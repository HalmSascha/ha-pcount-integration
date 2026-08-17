"""Config flow for the p-count integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PCountApiClient, PCountApiError, PCountAuthError
from .const import (
    CONF_CARPARK_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_HOST,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_CARPARK_ID): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class PCountConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for p-count."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> PCountOptionsFlowHandler:
        """Get the options flow for this handler."""
        return PCountOptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial (and only) step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}_{user_input[CONF_CARPARK_ID]}"
            )
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = PCountApiClient(
                session,
                user_input[CONF_HOST],
                user_input[CONF_CARPARK_ID],
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            try:
                await client.async_get_data()
            except PCountAuthError:
                errors["base"] = "invalid_auth"
            except PCountApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001 - guard against config flow crashing
                _LOGGER.exception("Unexpected exception during config flow validation")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"{user_input[CONF_CARPARK_ID]} ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )


class PCountOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle p-count options - currently just the poll interval.

    self.config_entry is provided automatically by the config entries
    manager once the flow is instantiated; no __init__ override needed
    (assigning it manually here is deprecated on newer Home Assistant
    cores).
    """

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            scan_interval = user_input[CONF_SCAN_INTERVAL]
            if scan_interval < MIN_SCAN_INTERVAL:
                errors[CONF_SCAN_INTERVAL] = "scan_interval_too_low"
            else:
                return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL, default=current_interval
                ): vol.Coerce(int),
            }
        )
        return self.async_show_form(
            step_id="init", data_schema=schema, errors=errors
        )
