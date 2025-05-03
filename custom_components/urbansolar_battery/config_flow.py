import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import selector
from .const import DOMAIN, CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR, CONF_SOLAR_POWER_SENSOR

class VirtualBatteryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for UrbanSolar Virtual Battery."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user input."""
        errors = {}

        if user_input is not None:
            # Ajout de logs pour vérifier les entrées utilisateur
            self._log("User input:", user_input)

            # Vérification simple pour s'assurer que les entités sont valides
            if not user_input.get(CONF_PRODUCTION_SENSOR):
                errors[CONF_PRODUCTION_SENSOR] = "invalid_entity"
            if not user_input.get(CONF_CONSOMMATION_SENSOR):
                errors[CONF_CONSOMMATION_SENSOR] = "invalid_entity"
            if not user_input.get(CONF_SOLAR_POWER_SENSOR):
                errors[CONF_SOLAR_POWER_SENSOR] = "invalid_entity"

            if not errors:
                return self.async_create_entry(title="UrbanSolar Battery", data=user_input)

        # Ajout de logs pour vérifier les erreurs
        self._log("Errors:", errors)

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
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return VirtualBatteryOptionsFlowHandler(config_entry)

    @staticmethod
    def _log(message, *args):
        """Log messages with a prefix."""
        print(f"[VirtualBatteryConfigFlow] {message} {args}")

class VirtualBatteryOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for UrbanSolar Virtual Battery."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            self._log("Options flow user input:", user_input)
            return self.async_create_entry(title="", data=user_input)

        current_config = self.config_entry.data
        self._log("Current config:", current_config)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_PRODUCTION_SENSOR, 
                    default=current_config.get(CONF_PRODUCTION_SENSOR, "")
                ): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "energy",
                    }
                }),
                vol.Required(
                    CONF_CONSOMMATION_SENSOR, 
                    default=current_config.get(CONF_CONSOMMATION_SENSOR, "")
                ): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "energy",
                    }
                }),
                vol.Required(
                    CONF_SOLAR_POWER_SENSOR, 
                    default=current_config.get(CONF_SOLAR_POWER_SENSOR, "")
                ): selector({
                    "entity": {
                        "domain": "sensor",
                        "device_class": "power",
                    }
                })
            })
        )

    def _log(self, message, *args):
        """Log messages with a prefix."""
        print(f"[VirtualBatteryOptionsFlowHandler] {message} {args}")
