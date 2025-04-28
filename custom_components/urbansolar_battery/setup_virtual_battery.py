import os
import yaml
import logging
from homeassistant.helpers.entity_component import async_update_entity

_LOGGER = logging.getLogger(__name__)

async def setup_virtual_battery(hass):
    config_path = "/config/custom_components/urbansolar_battery/config"
    input_numbers_path = os.path.join(config_path, "input_numbers.yaml")
    utility_meters_path = os.path.join(config_path, "utility_meters.yaml")
    automations_path = os.path.join(config_path, "automations")

    await load_and_set_input_numbers(hass, input_numbers_path)
    await load_utility_meters(hass, utility_meters_path)
    await load_automations(hass, automations_path)

# Lecture de fichiers YAML
def load_yaml_file(filepath):
    with open(filepath, "r") as file:
        return yaml.safe_load(file)

async def load_and_set_input_numbers(hass, filepath):
    data = await hass.async_add_executor_job(load_yaml_file, filepath)
    if not data:
        _LOGGER.warning("No input_numbers found in YAML.")
        return

    for entity_id, attrs in data.items():
        if not hass.states.get(entity_id):
            _LOGGER.warning(f"Input_number {entity_id} does not exist, creating it dynamically.")

            # Création simple dynamique
            await hass.services.async_call(
                "input_number",
                "set_value",
                {
                    "entity_id": entity_id,
                    "value": attrs.get("initial", 0)
                },
                blocking=True,
            )

async def load_utility_meters(hass, filepath):
    data = await hass.async_add_executor_job(load_yaml_file, filepath)
    if not data:
        _LOGGER.warning("No utility_meters found in YAML.")
        return

    for sensor_id, attrs in data.items():
        if not hass.states.get(sensor_id):
            _LOGGER.warning(f"Utility_meter {sensor_id} not found (may require manual setup).")

async def load_automations(hass, automations_path):
    if not os.path.exists(automations_path):
        _LOGGER.warning(f"Automations path {automations_path} does not exist.")
        return

    files = await hass.async_add_executor_job(os.listdir, automations_path)
    for filename in files:
        if filename.endswith(".yaml"):
            filepath = os.path.join(automations_path, filename)
            automation = await hass.async_add_executor_job(load_yaml_file, filepath)
            if automation:
                await hass.services.async_call(
                    "automation",
                    "reload",
                    {},
                    blocking=True,
                )
                _LOGGER.info(f"Loaded automation: {filename}")
