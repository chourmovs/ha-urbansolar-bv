import asyncio
import logging
import os
import shutil
import yaml
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


from .const import (
    CONF_SOLAR_POWER_SENSOR,
    CONF_TOTAL_POWER_CONSO_SENSOR,
    DOMAIN
)

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


async def setup_virtual_battery(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Installe les capteurs et fichiers nécessaires à la batterie virtuelle."""
    _LOGGER.info("Setting up UrbanSolar Virtual Battery")

    # 1) Copier les fichiers statiques
    for src_name, dst_name in FILES_TO_COPY.items():
        src = os.path.join(CONFIG_DIR, src_name)
        dst = os.path.join(TARGET_DIR, dst_name)
        if os.path.exists(src):
            await hass.async_add_executor_job(shutil.copy, src, dst)
            _LOGGER.debug("Copied %s → %s", src, dst)
        else:
            _LOGGER.warning("Missing source file: %s", src)

    # 2) Initialiser ou copier sensors.yaml
    if os.path.exists(STATIC_SENSORS_SRC):
        await hass.async_add_executor_job(shutil.copy, STATIC_SENSORS_SRC, DYNAMIC_SENSORS_DST)
    else:
        def write_empty():
            with open(DYNAMIC_SENSORS_DST, "w", encoding="utf-8") as f:
                yaml.dump([], f)
        await hass.async_add_executor_job(write_empty)
        _LOGGER.warning("No static sensors.yaml found; created empty urban_sensors.yaml")

    # 3) Récupérer les capteurs configurés
    prod_instant = entry.data.get(CONF_SOLAR_POWER_SENSOR)
    cons_instant = entry.data.get(CONF_TOTAL_POWER_CONSO_SENSOR)

    if not prod_instant or not cons_instant:
        _LOGGER.error("Un ou plusieurs capteurs requis sont manquants dans la configuration.")
        return

     # 4) Injecter les capteurs dynamiques
    def inject_dynamic_sensors():
        tpl_block = {
            "sensor": [
                {
                    "platform": "template",
                    "sensors": {
                        "urban_puissance_import_enedis": {
                            "name": "urban_puissance_import_enedis",
                            "unique_id": "Urban Puissance Import Enedis",
                            "unit_of_measurement": "W",
                            "state": (
                                "{% set puissance_conso = states('" + str(cons_instant) + "') | float(0) * 1000 %}\n"
                                "{% set puissance_prod = states('" + str(prod_instant) + "') | float(0) * 1000 %}\n"
                                "{% set batterie_stock = states('input_number.urban_batterie_virtuelle_stock') | float(0) %}\n"
                                "{% if batterie_stock > 0 %} 0\n"
                                "{% elif (puissance_conso - puissance_prod) > 0 %}\n"
                                "{{ puissance_conso - puissance_prod }}\n"
                                "{% else %} 0 {% endif %}"
                            )
                        },
                        "urban_puissance_solaire_instant": {
                            "name": "urban_puissance_solaire_instant",
                            "unique_id": "Urban Puissance Solaire Instantanée (Urban)",
                            "unit_of_measurement": "W",
                            "state": f"{{{{ states('{prod_instant}') | float(0) * 1000 }}}}"
                        },
                        "urban_conso_totale_instant": {
                            "name": "urban_conso_totale_instant",
                            "unique_id": "Urban Consommation Totale Instantanée (Urban)",
                            "unit_of_measurement": "W",
                            "state": f"{{{{ states('{cons_instant}') | float(0) * 1000 }}}}"
                        }
                    }
                },
                {
                    "platform": "integration",
                    "sensors": [
                        {
                            "name": "urban_energie_solaire_produite",
                            "source": prod_instant,
                            "round": 3,
                            "method": "left"
                        },
                        {
                            "name": "urban_energie_consommee_totale",
                            "source": cons_instant,
                            "round": 3,
                            "method": "left"
                        },
                        {
                            "name": "urban_energie_importee_enedis",
                            "source": "sensor.urban_puissance_import_enedis",
                            "unit_prefix": "k",
                            "round": 3,
                            "method": "left",
                            "unit_time": "s"
                        }
                    ]
                }
            ]
        }

        with open(DYNAMIC_SENSORS_DST, "w", encoding="utf-8") as f:
            yaml.dump(tpl_block, f, allow_unicode=True, sort_keys=False)

        _LOGGER.info("Injected dynamic template and integration sensors into urban_sensors.yaml")

    await hass.async_add_executor_job(inject_dynamic_sensors)