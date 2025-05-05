import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import selector
from homeassistant.const import UnitOfEnergy, UnitOfPower

from .const import (
    DOMAIN,
    CONF_SOLAR_POWER_SENSOR,
    CONF_TOTAL_POWER_CONSO_SENSOR,
)


class VirtualBatteryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for UrbanSolar Virtual Battery."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user input."""
        errors = {}

        if user_input is not None:
    
            power = user_input[CONF_SOLAR_POWER_SENSOR]
            powercons = user_input[CONF_TOTAL_POWER_CONSO_SENSOR]


            power_state = self.hass.states.get(power)
            powercons_state = self.hass.states.get(powercons)


            if not power_state or power_state.attributes.get("unit_of_measurement") != UnitOfPower.KILO_WATT:
                errors[CONF_SOLAR_POWER_SENSOR] = "invalid_unit"
            if not powercons_state or powercons_state.attributes.get("unit_of_measurement") != UnitOfPower.KILO_WATT:
                errors[CONF_TOTAL_POWER_CONSO_SENSOR] = "invalid_unit"

            self._log("Validation errors:", errors)

            if not errors:
                return self.async_create_entry(title="UrbanSolar Battery", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({

                vol.Required(CONF_SOLAR_POWER_SENSOR): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "power"
                    }
                }),
                vol.Required(CONF_TOTAL_POWER_CONSO_SENSOR): selector({
                    "entity": {
                        "domain": "sensor"
                    }
                }),
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return VirtualBatteryOptionsFlowHandler(config_entry)

    @staticmethod
    def _log(message, *args):
        """Simple logger."""
        print(f"[VirtualBatteryConfigFlow] {message} {args}")


class VirtualBatteryOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for UrbanSolar Virtual Battery."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the options form."""
        if user_input is not None:
            self._log("Options flow user input:", user_input)
            return self.async_create_entry(title="", data=user_input)

        current_config = self.config_entry.data
        self._log("Current config:", current_config)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SOLAR_POWER_SENSOR,
                    default=current_config.get(CONF_SOLAR_POWER_SENSOR, "")
                ): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "power"
                    }
                }),
                vol.Required(
                    CONF_TOTAL_POWER_CONSO_SENSOR,
                    default=current_config.get(CONF_TOTAL_POWER_CONSO_SENSOR, "")
                ): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "power"
                    }
                }),
            })
        )

    def _log(self, message, *args):
        print(f"[VirtualBatteryOptionsFlowHandler] {message} {args}")
