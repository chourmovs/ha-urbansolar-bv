from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
import voluptuous as vol
from homeassistant.components import config_flow 
from homeassistant.const import CONF_ENTITY_ID

from .const import DOMAIN, CONF_SOURCE_SENSOR

@config_flow.config_flow_step
class UrbanSolarBatteryFlow_Handler(config_flow.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Vérifier si l'entité existe dans l'instance Home Assistant
            if not self.hass.states.get(user_input[CONF_SOURCE_SENSOR]):
                errors[CONF_SOURCE_SENSOR] = "invalid_entity"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_true()
                return self.async_create_entry(
                    title="Battery Virtual Configuration",
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SOURCE_SENSOR): str,
            }),
            errors=errors
        )