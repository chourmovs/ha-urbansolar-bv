import logging
import os
import yaml

_LOGGER = logging.getLogger(__name__)

CONFIG_DIR = "custom_components/urbansolar_battery/config"

async def setup_virtual_battery(hass):
    """Setup the virtual battery."""
    _LOGGER.debug("Setting up UrbanSolar Virtual Battery")
    
    # Chargement des fichiers YAML sans tenter de créer des entités
    await load_input_numbers(hass)
    await load_sensors(hass)
    await load_utility_meters(hass)

async def load_input_numbers(hass):
    """Load input_number entities configuration."""
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
        _LOGGER.info(f"Loaded {len(input_numbers)} input_number configurations from {filepath}")

async def load_sensors(hass):
    """Load sensor configurations."""
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
        _LOGGER.info(f"Loaded {len(sensors)} sensor configurations from {filepath}")

async def load_utility_meters(hass):
    """Load utility_meter configurations."""
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
        _LOGGER.info(f"Loaded {len(utility_meters)} utility_meter configurations from {filepath}")

async def load_automations(hass):
    """Load and reload automations."""
    automations_path = f"{CONFIG_DIR}/automations"
    if not os.path.exists(automations_path):
        _LOGGER.warning(f"Automations directory not found: {automations_path}")
        return

    # Just reload automations globally
    await hass.services.async_call("automation", "reload", blocking=True)
    _LOGGER.info("Reloaded automations.") # Ajout pour la communication de l'état d'exécution.

    # Ensuite, ajouter la fonction pour éviter les doublons dans les fichiers YAML.
    async def load_automations(automation_path):
        if not os.path.exists(automation_path):
            return

        automations = []
        for root, dirs, files in os.walk(automation_path):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    automation_file_path = os.path.join(root, file)
                    with open(automation_file_path, "r") as yaml_file:
                        try:
                            automations += [yaml.safe_load(yaml_file)]
                        except yaml.YAMLError as exc:
                            _LOGGER.error(f"Error parsing {automation_file_path}: {exc}")

        if automations:
            _LOGGER.info(f"Loaded {len(automations)} automation configurations from {automation_path}")
            await hass.services.async_call("automation", "reload", blocking=True)
            return automations

    # Appeler la fonction pour charger les automations
    automations = await load_automations(automations_path)