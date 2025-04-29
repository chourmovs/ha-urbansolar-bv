import logging
import os
import yaml

_LOGGER = logging.getLogger(__name__)

CONFIG_DIR = "custom_components/urbansolar_battery/config"

async def setup_virtual_battery(hass):
    """Setup the virtual battery."""
    _LOGGER.debug("Setting up UrbanSolar Virtual Battery")
    
    await load_input_numbers(hass)
    await load_sensors(hass)
    await load_utility_meters(hass)
    await load_automations(hass)

async def load_input_numbers(hass):
    """Load and create input_number entities."""
    filepath = f"{CONFIG_DIR}/input_numbers.yaml"
    if not os.path.exists(filepath):
        _LOGGER.warning(f"Input_numbers file not found: {filepath}")
        return

    with open(filepath, "r") as file:
        try:
            input_numbers = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            _LOGGER.error(f"Error parsing {filepath}: {exc}")
            return

    if input_numbers:
        for object_id, config in input_numbers.items():
            service_data = {
                "object_id": object_id,
                **config,
            }
            await hass.services.async_call(
                "input_number",
                "create",
                service_data,
                blocking=True
            )
            _LOGGER.info(f"Created input_number.{object_id}")

async def load_sensors(hass):
    """Load and create template sensors."""
    filepath = f"{CONFIG_DIR}/sensors.yaml"
    if not os.path.exists(filepath):
        _LOGGER.warning(f"Sensors file not found: {filepath}")
        return

    with open(filepath, "r") as file:
        try:
            sensors = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            _LOGGER.error(f"Error parsing {filepath}: {exc}")
            return

    if sensors:
        for sensor_name, config in sensors.items():
            service_data = {
                "object_id": sensor_name,
                **config,
            }
            await hass.services.async_call(
                "template",
                "create",
                service_data,
                blocking=True
            )
            _LOGGER.info(f"Created sensor.{sensor_name}")

async def load_utility_meters(hass):
    """Load and create utility_meter sensors."""
    filepath = f"{CONFIG_DIR}/utility_meters.yaml"
    if not os.path.exists(filepath):
        _LOGGER.warning(f"Utility_meters file not found: {filepath}")
        return

    with open(filepath, "r") as file:
        try:
            utility_meters = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            _LOGGER.error(f"Error parsing {filepath}: {exc}")
            return

    if utility_meters:
        for meter_name, config in utility_meters.items():
            service_data = {
                "object_id": meter_name,
                **config,
            }
            await hass.services.async_call(
                "utility_meter",
                "create",
                service_data,
                blocking=True
            )
            _LOGGER.info(f"Created utility_meter.{meter_name}")

async def load_automations(hass):
    """Load and reload automations."""
    automations_path = f"{CONFIG_DIR}/automations"
    if not os.path.exists(automations_path):
        _LOGGER.warning(f"Automations directory not found: {automations_path}")
        return

    # Just reload automations globally
    await hass.services.async_call("automation", "reload", blocking=True)
    _LOGGER.info("Reloaded automations.")
