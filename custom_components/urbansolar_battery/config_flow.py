from homeassistant import config_entries
import voluptuous as vol
from homeassistant.core import callback

from .const import DOMAIN

class VirtualBatteryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Virtual Battery."""

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Virtual Battery", data=user_input)

        schema = vol.Schema({
            vol.Required("sensor_production"): str,
            vol.Required("sensor_conso_totale"): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return VirtualBatteryOptionsFlowHandler(config_entry)

class VirtualBatteryOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Virtual Battery."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required("sensor_production", default=self.config_entry.data.get("sensor_production", "")): str,
            vol.Required("sensor_conso_totale", default=self.config_entry.data.get("sensor_conso_totale", "")): str,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
