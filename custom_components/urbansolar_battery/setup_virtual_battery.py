import yaml
import os
import logging

_LOGGER = logging.getLogger(__name__)

async def setup_virtual_battery(hass):
    """Setup input_numbers, utility_meters, and automations for UrbanSolar Battery."""
    base_path = hass.config.path("custom_components/urbansolar_battery/config")

    # Charger input_numbers
    await load_and_set_input_numbers(hass, os.path.join(base_path, "input_numbers.yaml"))

    # Charger utility_meters (on ne peut pas créer mais on log que c'est chargé)
    await load_utility_meters(hass, os.path.join(base_path, "utility_meters.yaml"))

    # Charger toutes les automations
    automations_path = os.path.join(base_path, "automations")
    if os.path.exists(automations_path):
        for file in os.listdir(automations_path):
            if file.endswith(".yaml"):
                await load_automation(hass, os.path.join(automations_path, file))

async def load_and_set_input_numbers(hass, filepath):
    """Load and set input_numbers values."""
    if not os.path.exists(filepath):
        _LOGGER.warning("Input numbers file not found: %s", filepath)
        return

    with open(filepath, "r") as file:
        data = yaml.safe_load(file)

    if not data:
        _LOGGER.info("No input_numbers found in %s", filepath)
        return

    for object_id, config in data.items():
        entity_id = f"input_number.{object_id}"
        value = config.get("initial", 0)

        # On essaie de définir la valeur uniquement si l'entité existe
        if hass.states.get(entity_id):
            await hass.services.async_call(
                "input_number",
                "set_value",
                {
                    "entity_id": entity_id,
                    "value": value
                },
                blocking=True,
            )
            _LOGGER.info("Set input_number %s to %s", entity_id, value)
        else:
            _LOGGER.warning("Input_number entity %s does not exist, skipping.", entity_id)

async def load_utility_meters(hass, filepath):
    """Load utility_meters info."""
    if not os.path.exists(filepath):
        _LOGGER.warning("Utility meters file not found: %s", filepath)
        return

    with open(filepath, "r") as file:
        data = yaml.safe_load(file)

    if not data:
        _LOGGER.info("No utility_meters found in %s", filepath)
        return

    for object_id in data.keys():
        entity_id = f"sensor.{object_id}"
        if hass.states.get(entity_id):
            _LOGGER.info("Utility_meter %s found.", entity_id)
        else:
            _LOGGER.warning("Utility_meter %s not found (may require manual setup).", entity_id)

async def load_automation(hass, filepath):
    """Load automations and reload."""
    if not os.path.exists(filepath):
        _LOGGER.warning("Automation file not found: %s", filepath)
        return

    with open(filepath, "r") as file:
        _ = yaml.safe_load(file)

    _LOGGER.info("Loaded automation from %s", filepath)

    # Reload automations globally
    await hass.services.async_call(
        "automation",
        "reload",
        {},
        blocking=True,
    )
    _LOGGER.info("Automation reloaded after loading %s", filepath)
