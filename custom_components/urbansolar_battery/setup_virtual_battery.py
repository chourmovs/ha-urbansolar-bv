import logging
import os
import shutil
import yaml

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import async_get_current_platform

from .const import CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR, CONF_SOLAR_POWER_SENSOR, CONF_TOTAL_POWER_CONSO_SENSOR, DOMAIN


_LOGGER = logging.getLogger(__name__)

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
TARGET_DIR = "/config"

FILES_TO_COPY = {
    "input_numbers.yaml": "urban_input_numbers.yaml",
    "utility_meters.yaml": "urban_utility_meters.yaml",
    "automations.yaml": "urban_automations.yaml",
    "dashboard.yaml": "urban_dashboard.yaml",
}
STATIC_SENSORS_SRC = os.path.join(CONFIG_DIR, "sensors.yaml")
DYNAMIC_SENSORS_DST = os.path.join(TARGET_DIR, "urban_sensors.yaml")


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


async def setup_virtual_battery(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Copies YAML and updates dynamic sensor template without blocking HA event loop."""
    _LOGGER.info("Setting up UrbanSolar Virtual Battery")

    # 1) Copy static files
    for src_name, dst_name in FILES_TO_COPY.items():
        src = os.path.join(CONFIG_DIR, src_name)
        dst = os.path.join(TARGET_DIR, dst_name)
        if os.path.exists(src):
            await hass.async_add_executor_job(shutil.copy, src, dst)
            _LOGGER.debug("Copied %s → %s", src, dst)
        else:
            _LOGGER.warning("Missing source file: %s", src)

    # 2) Initialize or copy sensors.yaml
    if os.path.exists(STATIC_SENSORS_SRC):
        await hass.async_add_executor_job(shutil.copy, STATIC_SENSORS_SRC, DYNAMIC_SENSORS_DST)
    else:
        def write_empty():
            with open(DYNAMIC_SENSORS_DST, "w", encoding="utf-8") as f:
                yaml.dump([], f)
        await hass.async_add_executor_job(write_empty)
        _LOGGER.warning("No static sensors.yaml found; created empty urban_sensors.yaml")

    # 3) Retrieve user-chosen sensors
    prod = entry.data.get(CONF_PRODUCTION_SENSOR)
    conso = entry.data.get(CONF_CONSOMMATION_SENSOR)

    if not prod or not conso:
        _LOGGER.error("Missing production/consumption sensor in entry.data")
        return

    # 4) Inject dynamic template block
    def inject():
        # load existing
        with open(DYNAMIC_SENSORS_DST, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or []
        # remove old block
        new_list = []
        for block in existing:
            if block.get("platform") == "template":
                sensors = block.get("sensors", {})
                if "energie_restituee_au_reseau" in sensors:
                    continue
            new_list.append(block)
        # append updated block
        tpl_block = {
            "platform": "template",
            "sensors": {
                "energie_restituee_au_reseau": {
                    "friendly_name": "Énergie Restituée au Réseau",
                    "unit_of_measurement": "kWh",
                    "value_template": (
                        f"{{{{ states('{prod}') | float(0) - states('{conso}') | float(0) }}}}"
                    ),
                    "device_class": "energy"
                }
            }
        }
        new_list.append(tpl_block)
        # write back
        with open(DYNAMIC_SENSORS_DST, "w", encoding="utf-8") as f:
            yaml.dump(new_list, f, allow_unicode=True)
        _LOGGER.info("Injected dynamic template sensor into %s", DYNAMIC_SENSORS_DST)

    await hass.async_add_executor_job(inject)

    _LOGGER.info("UrbanSolar Virtual Battery setup completed.")
       

    prod_instant  = entry.data.get(CONF_SOLAR_POWER_SENSOR)
    cons_instant  = entry.data.get(CONF_TOTAL_POWER_CONSO_SENSOR)

    if not cons_instant or not prod_instant:
     raise ValueError("Les capteurs de consommation ou production ne sont pas définis.")

    # 5) Inject sensor for énergie importée Enedis (based on power)
    def inject_import_power_template():
        # load existing
        with open(DYNAMIC_SENSORS_DST, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or []

        # remove old block if exists
        new_list = []
        for block in existing:
            if block.get("platform") == "template":
                sensors = block.get("sensors", {})
                if "puissance_import_enedis" in sensors:
                    continue
            new_list.append(block)

        tpl_block = {
            "platform": "template",
            "sensors": {
                "puissance_import_enedis": {
                    "friendly_name": "Puissance Import Enedis",
                    "unit_of_measurement": "W",
                    "value_template": (
                        f"{{% set puissance_conso = states('{cons_instant}') | float(0) %}}\n"
                        f"{{% set puissance_prod = states('{prod_instant}') | float(0) %}}\n"
                        "{{% set batterie_stock = states('input_number.batterie_virtuelle_stock') | float(0) %}}\n"
                        "{% if batterie_stock > 0 %} 0\n"
                        "{% elif (puissance_conso - puissance_prod) > 0 %}\n"
                        "{{ puissance_conso - puissance_prod }}\n"
                        "{% else %} 0 {% endif %}"
                    ),
                    "device_class": "power"
                }
            }
        }

        new_list.append(tpl_block)

        # write back
        with open(DYNAMIC_SENSORS_DST, "w", encoding="utf-8") as f:
            yaml.dump(new_list, f, allow_unicode=True)

        _LOGGER.info("Injected 'energie_importee_enedis' sensor")

    if prod_instant:
        await hass.async_add_executor_job(inject_import_power_template)
    else:
        _LOGGER.warning("No instant production sensor provided; skipping import sensor injection.")


    # 6) Inject integration sensors for energy totals
    def inject_integration_sensors():
        with open(DYNAMIC_SENSORS_DST, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or []

        # Remove existing integration sensors if already there
        new_list = []
        for block in existing:
            if block.get("platform") == "integration":
                name = block.get("name", "")
                if name in ("energie_produite_quotidienne", "energie_consommee_totale"):
                    continue
            new_list.append(block)

        # Append integration sensors
        integration_blocks = [
            {
                "platform": "integration",
                "source": prod_instant,
                "name": "energie_produite_quotidienne",
                "unit_prefix": "k",
                "round": 2,
                "method": "trapezoidal"
            },
            {
                "platform": "integration",
                "source": cons_instant,
                "name": "energie_consommee_totale",
                "unit_prefix": "k",
                "round": 2,
                "method": "trapezoidal"
            }
        ]

        new_list.extend(integration_blocks)

        with open(DYNAMIC_SENSORS_DST, "w", encoding="utf-8") as f:
            yaml.dump(new_list, f, allow_unicode=True)

        _LOGGER.info("Injected integration sensors for solar production and total consumption")

    await hass.async_add_executor_job(inject_integration_sensors)
