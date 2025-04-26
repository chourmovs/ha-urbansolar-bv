from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR

class UrbanSolarBatteryFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Urban Solar Battery."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            entity_registry = er.async_get(hass=self.hass)
            valid = True
            for conf in (CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR):
                if not entity_registry.async_get(user_input[conf]):
                    valid = False
                    errors["base"] = "invalid_entity"
                    break

            if valid:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Configuration Batterie Virtuelle",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_PRODUCTION_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="energy",
                    )
                ),
                vol.Required(CONF_CONSOMMATION_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="energy",
                    )
                ),
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return UrbanSolarBatteryOptionsFlowHandler(config_entry)

class UrbanSolarBatteryOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Urban Solar Battery."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            entity_registry = er.async_get(hass=self.hass)
            valid = True
            for conf in (CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR):
                if not entity_registry.async_get(user_input[conf]):
                    valid = False
                    errors["base"] = "invalid_entity"
                    break

            if valid:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, **user_input}
                )
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_PRODUCTION_SENSOR, default=self.config_entry.data.get(CONF_PRODUCTION_SENSOR, "")): str,
                vol.Required(CONF_CONSOMMATION_SENSOR, default=self.config_entry.data.get(CONF_CONSOMMATION_SENSOR, "")): str,
            }),
            errors=errors,
        )
