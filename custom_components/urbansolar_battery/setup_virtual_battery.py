import logging
import os
import shutil

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

def ensure_fresh_copy(source_file, target_file):
    """Supprime et copie à neuf le fichier si nécessaire."""
    try:
        if os.path.exists(target_file):
            os.remove(target_file)
            _LOGGER.debug(f"Deleted existing file: {target_file}")
        shutil.copy(source_file, target_file)
        _LOGGER.info(f"Copied {source_file} → {target_file}")
    except Exception as e:
        _LOGGER.error(f"Error copying {source_file} to {target_file}: {e}")

async def setup_virtual_battery(hass):
    """Setup the UrbanSolar virtual battery by copying config files."""
    _LOGGER.info("Setting up UrbanSolar Virtual Battery - YAML copy mode")

    for src_name, dest_name in FILES_TO_COPY.items():
        src_path = os.path.join(CONFIG_DIR, src_name)
        dest_path = os.path.join(TARGET_DIR, dest_name)

        if not os.path.exists(src_path):
            _LOGGER.warning(f"Source file does not exist: {src_path}")
            continue

        ensure_fresh_copy(src_path, dest_path)

    _LOGGER.info("UrbanSolar Virtual Battery setup completed.")
