import logging
import os
import shutil
import yaml

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
    "integrations.yaml": "urban_integrations.yaml",
    "utility_meters.yaml": "urban_utility_meters.yaml",
    "automations.yaml": "urban_automations.yaml",
    "dashboard.yaml": "urban_dashboard.yaml",
}

STATIC_SENSORS_SRC = os.path.join(CONFIG_DIR, "sensors.yaml")
DYNAMIC_SENSORS_DST = os.path.join(TARGET_DIR, "urban_sensors.yaml")
DYNAMIC_INTEGRATION_DST = os.path.join(TARGET_DIR, "urban_integrations.yaml")


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

    # 4) Injecter le capteur template pour l’énergie importée
    def inject_import_power_template():
        with open(DYNAMIC_SENSORS_DST, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or []


        new_list = {
                 "sensor": [
                        {
                            "name": "Urban Énergie Restituée au Réseau",
                            "unique_id": "urban_energie_restituee_au_reseau",
                            "unit_of_measurement": "kWh",
                            "device_class": "energy",
                            "state_class": "total",
                            "state": "{{ states('sensor.urban_energie_solaire_produite') | float(0) - states('sensor.urban_energie_consommee_totale') | float(0) }}"
                        },
                        
                        {
                            "name": "Urban Puissance Import Enedis",
                            "unique_id": "urban_puissance_import_enedis",
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
                        
                        {
                            "name": "Urban Puissance Batterie Virtuelle IN",
                            "unique_id":"urban_puissance_batterie_virtuelle_in",
                            "unit_of_measurement": "W",
                            "state": (
                                f"{{% set prod = states('{prod_instant}') | float(0) * 1000 %}}\n"
                                f"{{% set conso = states('{cons_instant}') | float(0) * 1000 %}}\n"
                                f"{{% set import_enedis = states('sensor.urban_puissance_import_enedis') | float(0) %}}\n"
                                f"{{% if import_enedis == 0 and prod > conso %}}\n"
                                f"  {{{{ prod - conso }}}}\n"
                                f"{{% else %}} 0 {{% endif %}}"
                            )
                        },
                        
                         {
                            "name": "Urban Puissance Batterie Virtuelle OUT",
                            "unique_id": "urban_puissance_batterie_virtuelle_out",
                            "unit_of_measurement": "W",
                            "state": (
                                f"{{% set prod = states('{prod_instant}') | float(0) * 1000 %}}\n"
                                f"{{% set conso = states('{cons_instant}') | float(0) * 1000 %}}\n"
                                f"{{% set import_enedis = states('sensor.urban_puissance_import_enedis') | float(0) %}}\n"
                                f"{{% if import_enedis == 0 and conso > prod %}}\n"
                                f"  {{{{ conso - prod }}}}\n"
                                f"{{% else %}} 0 {{% endif %}}"
                            )
                        },
                        
                        {
                            "name": "Urban Batterie Virtuelle Sortie Horaire",
                            "unique_id": "urban_batterie_virtuelle_sortie_horaire",
                            "unit_of_measurement": "kWh",
                            "device_class": "energy",
                            "state_class": "total",
                            "state": "{{ -1 * (states('input_number.urban_energie_battery_out_hourly') | float(0)) }}"
                        },
                        
                        {
                            "name": "Urban Batterie Virtuelle Entrée Horaire",
                            "unique_id": "urban_batterie_virtuelle_entree_horaire",
                            "unit_of_measurement": "kWh",
                            "device_class": "energy",
                            "state_class": "total",
                            "state": "{{ states('input_number.urban_energie_battery_in_hourly') | float(0) }}"
                        },
                        
                        {
                            "name": "Urban Puissance Solaire Instant",
                            "unique_id": "urban_puissance_solaire_instant",
                            "unit_of_measurement": "W",
                            "state": f"{{{{ states('{prod_instant}') | float(0) * 1000}}}}"
                        },
                        
                        {
                            "name": "Urban Conso Totale Instant",
                            "unique_id": "urban_conso_totale_instant",
                            "unit_of_measurement": "W",
                            "state": f"{{{{ states('{cons_instant}') | float(0) * 1000}}}}"
                        },

                        {
                            "name": "urban_energie_importee_enedis",
                            "unique_id": "Énergie importée Enedis",
                            "unit_of_measurement": "kWh",
                            "device_class": "energy",
                            "state_class": "total_increasing",
                            "state": "{{ states('sensor.urban_energie_importee_enedis_raw') | float }}"
                        },
                      ]
                    }

        with open(DYNAMIC_SENSORS_DST, "w", encoding="utf-8") as f:
            yaml.dump(new_list, f, allow_unicode=True, sort_keys=False)

        _LOGGER.info("Injected 'urban_puissance_import_enedis' sensor")

    await hass.async_add_executor_job(inject_import_power_template)


 # 4) Injecter le capteur integration
    def inject_import_integration_sensors():
        integrations = [
            {
                "platform": "integration",
                "name": "urban_energie_solaire_produite",
                "source": prod_instant,
                "round": 3,
                "method": "left"
            },
            {
                "platform": "integration",
                "name": "urban_energie_consommee_totale",
                "source": cons_instant,
                "round": 3,
                "method": "left"
            },
            {
                "platform": "integration",
                "name": "urban_energie_importee_enedis_raw",
                "source": "sensor.urban_puissance_import_enedis",
                "round": 3,
                "method": "left",
                "unit_prefix": "k"
            },



        ]

        with open(DYNAMIC_INTEGRATION_DST, "w", encoding="utf-8") as f:
            yaml.dump(integrations, f, allow_unicode=True, sort_keys=False)

        _LOGGER.info("Injected integration sensors.")

    await hass.async_add_executor_job(inject_import_integration_sensors)