import logging
import os
import shutil
import yaml

_LOGGER = logging.getLogger(__name__)

CONFIG_DIR = "custom_components/urbansolar_battery/config"
TARGET_DIR = "/config"

FILES_TO_COPY = {
    "input_numbers.yaml": "urban_input_numbers.yaml",
    "sensors.yaml": "urban_sensors.yaml",
    "utility_meters.yaml": "urban_utility_meters.yaml",
    "automations.yaml": "urban_automations.yaml",
    "dashboard.yaml": "urban_dashboard.yaml",

}

async def setup_virtual_battery(hass, entry):
    """Setup the UrbanSolar virtual battery by copying config files and injecting sensors."""
    _LOGGER.info("Setting up UrbanSolar Virtual Battery - YAML copy mode")

    CONFIG_DIR = "custom_components/urbansolar_battery/config"
    TARGET_DIR = "/config"

    FILES_TO_COPY = {
        "input_numbers.yaml": "urban_input_numbers.yaml",
        "utility_meters.yaml": "urban_utility_meters.yaml",
        "automations.yaml": "urban_automations.yaml",
        "dashboard.yaml": "urban_dashboard.yaml",
    }

    # Copier les fichiers standards
    for src_name, dest_name in FILES_TO_COPY.items():
        src_path = os.path.join(CONFIG_DIR, src_name)
        dest_path = os.path.join(TARGET_DIR, dest_name)

        if not os.path.exists(src_path):
            _LOGGER.warning(f"Fichier source manquant : {src_path}")
            continue

        try:
            if os.path.exists(dest_path):
                os.remove(dest_path)
            shutil.copy(src_path, dest_path)
            _LOGGER.info(f"Copié {src_path} → {dest_path}")
        except Exception as e:
            _LOGGER.error(f"Erreur lors de la copie de {src_path} vers {dest_path} : {e}")

    # Ajouter le capteur dynamique à urban_sensors.yaml
    production_sensor = entry.data.get("production_sensor")
    consommation_sensor = entry.data.get("consommation_sensor")
    sensors_yaml_path = os.path.join(TARGET_DIR, "urban_sensors.yaml")

    add_dynamic_template_sensor(production_sensor, consommation_sensor, sensors_yaml_path)

    _LOGGER.info("UrbanSolar Virtual Battery setup completed.")





def add_dynamic_template_sensor(production_sensor, consommation_sensor, yaml_path):
    """Ajoute un sensor template dynamique à urban_sensors.yaml."""
    template_sensor = {
        "platform": "template",
        "sensors": {
            "energie_restituee_au_reseau": {
                "friendly_name": "Énergie Restituée au Réseau",
                "unit_of_measurement": "kWh",
                "value_template": f"{{{{ states('{production_sensor}') | float - states('{consommation_sensor}') | float }}}}"
            }
        }
    }

    try:
        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                existing_data = yaml.safe_load(f) or []
        else:
            existing_data = []

        # Supprimer l'ancien sensor si déjà présent
        existing_data = [
            block for block in existing_data
            if not (isinstance(block, dict) and block.get("platform") == "template" and "energie_restituee_au_reseau" in block.get("sensors", {}))
        ]

        existing_data.append(template_sensor)

        with open(yaml_path, "w") as f:
            yaml.dump(existing_data, f, allow_unicode=True)

        _LOGGER.info(f"Sensor dynamique ajouté dans {yaml_path}")
    except Exception as e:
        _LOGGER.error(f"Erreur lors de la mise à jour de {yaml_path} : {e}")
