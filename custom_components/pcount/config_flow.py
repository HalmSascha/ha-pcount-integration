"""Config flow for the p-count integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PCountApiClient, PCountApiError, PCountAuthError
from .const import CONF_CARPARK_ID, DEFAULT_HOST, DOMAIN

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
