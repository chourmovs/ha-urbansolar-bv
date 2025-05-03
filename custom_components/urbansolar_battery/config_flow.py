from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers.selector import (
    selector,
)
from .const import DOMAIN, CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR, CONF_SOLAR_POWER_SENSOR

class VirtualBatteryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for UrbanSolar Virtual Battery."""
    def __init__(self):
        """Initialize the config flow."""
        pass

    async def async_step_user(self, user_input=None):
        """Handle user input."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="UrbanSolar Battery", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_PRODUCTION_SENSOR): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "energy",
                        "unit_of_measurement": "kWh"
                    }
                }),
                vol.Required(CONF_CONSOMMATION_SENSOR): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "energy",
                        "unit_of_measurement": "kWh"
                    }
                }),
                vol.Required(CONF_SOLAR_POWER_SENSOR): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "power"
                    }
                }),
            }),
            errors=errors,
            description_placeholders={},
        )

    async def async_get_options_flow(config_entry):
        """Create the options flow."""
        return VirtualBatteryOptionsFlowHandler(config_entry)

class VirtualBatteryOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for UrbanSolar Virtual Battery."""
    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_PRODUCTION_SENSOR, 
                    default=self.config_entry.data.get(CONF_PRODUCTION_SENSOR, "")
                ): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "energy",
                    }
                }),
                vol.Required(
                    CONF_CONSOMMATION_SENSOR, 
                    default=self.config_entry.data.get(CONF_CONSOMMATION_SENSOR, "")
                ): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "energy",
                    }
                }),
                vol.Required(
                    CONF_SOLAR_POWER_SENSOR, 
                    default=self.config_entry.data.get(CONF_SOLAR_POWER_SENSOR, "")
                ): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "power",
                    }
                })
            })
        )