from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_SOURCE_SENSOR
import homeassistant.helpers.entity_registry as er

class UrbanSolarBatteryFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Urban Solar Battery."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step to configure the source sensor."""
        errors = {}
        if user_input is not None:
            # Vérifie si l'entité source existe
            entity_id = user_input[CONF_SOURCE_SENSOR]
            entity_registry = await self.hass.helpers.entity_registry.async_get_registry()
            if not entity_registry.async_is_registered(entity_id):
                errors["base"] = "invalid_entity"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_true()
                return self.async_create_entry(
                    title="Batterie Virtuelle Configuration",
                    data=user_input
                )
        
        # Interface utilisateur du flux : requiert une entité source
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SOURCE_SENSOR,
                    default="sensor.default_energy_sensor"
                ): cv.entity_id
            }),
            errors=errors
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Retourn la classe d'option pour le flux."""
        return UrbanSolarBatteryOptionsFlowHandler(config_entry)

class UrbanSolarBatteryOptionsFlowHandler(config_entries.OptionsFlow):
    """Gère les options de configuration."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Gère les options."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input}
            )
            return self.async_create_entry(title="", data=user_input)
        
        # Option de changement de source
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_SOURCE_SENSOR,
                    default=self.config_entry.data.get(CONF_SOURCE_SENSOR)
                ): cv.entity_id
            })
        )