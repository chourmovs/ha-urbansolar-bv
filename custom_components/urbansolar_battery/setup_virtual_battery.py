import logging
import os
import shutil

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import async_get_current_platform

from .const import CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR, DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_DIR = "custom_components/urbansolar_battery/config"
TARGET_DIR = "/config"

FILES_TO_COPY = {
    "input_numbers.yaml": "urban_input_numbers.yaml",
    "sensors.yaml":       "urban_sensors.yaml",
    "utility_meters.yaml":"urban_utility_meters.yaml",
    "automations.yaml":   "urban_automations.yaml",
    "dashboard.yaml":     "urban_dashboard.yaml",
}

class EnergieRestitueeSensor(SensorEntity):
    """Capteur dynamique calculant énergie restituée au réseau."""

    def __init__(self, hass, prod_sensor, conso_sensor):
        self.hass = hass
        self._prod = prod_sensor
        self._conso = conso_sensor
        self._attr_name = "Énergie Restituée au Réseau"
        self._attr_unique_id = "energie_restituee_au_reseau"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_state_class = "total"

    @property
    def native_value(self):
        prod = self._get(self._prod)
        conso = self._get(self._conso)
        if prod is None or conso is None:
            return None
        return round(prod - conso, 2)

    def _get(self, entity_id):
        state = self.hass.states.get(entity_id)
        if not state or state.state in ("unknown", "unavailable"):
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None

def ensure_fresh_copy(source_file, target_file):
    """Supprime et copie à neuf le fichier si nécessaire."""
    try:
        if os.path.exists(target_file):
            os.remove(target_file)
        shutil.copy(source_file, target_file)
        _LOGGER.debug(f"Copied {source_file} → {target_file}")
    except Exception as e:
        _LOGGER.error(f"Error copying {source_file} to {target_file}: {e}")

async def setup_virtual_battery(hass, entry):
    """Copie les YAML et crée le capteur dynamique."""
    _LOGGER.info("Setting up UrbanSolar Virtual Battery")

    # --- Copier les fichiers de config ---
    for src, dst in FILES_TO_COPY.items():
        src_path = os.path.join(CONFIG_DIR, src)
        dst_path = os.path.join(TARGET_DIR, dst)
        if os.path.exists(src_path):
            ensure_fresh_copy(src_path, dst_path)
        else:
            _LOGGER.warning("Source file missing: %s", src_path)

    # --- Récupérer les capteurs choisis dans le config flow ---
    prod = entry.data.get(CONF_PRODUCTION_SENSOR)
    conso = entry.data.get(CONF_CONSOMMATION_SENSOR)
    if not prod or not conso:
        _LOGGER.error("Missing CONF_PRODUCTION_SENSOR or CONF_CONSOMMATION_SENSOR in entry.data")
        return

    # --- Ajouter dynamiquement l'entité Sensor ---
    async def _add_sensor():
        platform = async_get_current_platform()  # récupérer la plateforme sensor courante
        platform.async_add_entities([EnergieRestitueeSensor(hass, prod, conso)], update_before_add=True)
        _LOGGER.info("EnergieRestitueeSensor added, prod=%s, conso=%s", prod, conso)

    hass.async_create_task(_add_sensor())

    _LOGGER.info("UrbanSolar Virtual Battery setup completed.")
