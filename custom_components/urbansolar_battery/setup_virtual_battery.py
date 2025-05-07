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
    "utility_meters.yaml": "urban_utility_meters.yaml",
    "automations.yaml": "urban_automations.yaml",
    "templates.yaml": "urban_templates.yaml",
    "dashboard.yaml": "urban_dashboard.yaml",
}

STATIC_SENSORS_SRC = os.path.join(CONFIG_DIR, "sensors.yaml")
DYNAMIC_SENSORS_DST = os.path.join(TARGET_DIR, "urban_sensors.yaml")
DYNAMIC_TEMPLATE_DST = os.path.join(TARGET_DIR, "urban_templates.yaml")


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
            with open(DYNAMIC_TEMPLATE_DST, "w", encoding="utf-8") as f:
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
        with open(DYNAMIC_TEMPLATE_DST, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or []

        new_list = [
            block for block in existing
            if not (block.get("platform") == "template" and "urban_puissance_import_enedis" in block.get("sensors", {}))
        ]

        tpl_block = {
                    "- platform" : "template",
                    "sensors":{

                        "Urban Énergie Restituée au Réseau":{    
                            "name": "Urban Énergie Restituée au Réseau",
                            "unique_id": "urban_energie_restituee_au_reseau",
                            "unit_of_measurement": "kWh",
                            "device_class": "energy",
                            "state_class": "total",
                            "state": "{{ states('sensor.urban_energie_solaire_produite') | float(0) - states('sensor.urban_energie_consommee_totale') | float(0) }}"
                        },
                     
                        "urban_puissance_import_enedis": {
                        {
                            
                            "name" : "urban_puissance_import_enedis",
                            "unique_id" :  "Urban Puissance Import Enedis",
                            "unit_of_measurement": "W",
                            "state":  (
                                "{% set puissance_conso = states('" + str(cons_instant) + "') | float(0) * 1000 %}\n"
                                "{% set puissance_prod = states('" + str(prod_instant) + "') | float(0) * 1000 %}\n"
                                "{% set batterie_stock = states('input_number.urban_batterie_virtuelle_stock') | float(0) %}\n"
                                "{% if batterie_stock > 0 %} 0\n"
                                "{% elif (puissance_conso - puissance_prod) > 0 %}\n"
                                "{{ puissance_conso - puissance_prod }}\n"
                                "{% else %} 0 {% endif %}"
                            )
                        }
                        },
                        "urban_puissance_batterie_virtuelle_in": {
                        {
                            "name": "urban_puissance_batterie_virtuelle_in",
                            "unique_id" :  "Urban Puissance Batterie Virtuelle IN",
                            "unit_of_measurement": "W",
                            "state": (
                                f"{{% set prod = states('{prod_instant}') | float(0) * 1000 %}}\n"
                                f"{{% set conso = states('{cons_instant}') | float(0) * 1000 %}}\n"
                                f"{{% set import_enedis = states('sensor.urban_puissance_import_enedis') | float(0) %}}\n"
                                f"{{% if import_enedis == 0 and prod > conso %}}\n"
                                f"  {{{{ prod - conso }}}}\n"
                                f"{{% else %}} 0 {{% endif %}}"
                            ),
                        }
                        },
                        
                        "urban_puissance_batterie_virtuelle_out": {
                        {
                            "name": "urban_puissance_batterie_virtuelle_out",
                            "unique_id" :  "Urban Puissance Batterie Virtuelle OUT",
                            "unit_of_measurement": "W",
                            "state":(
                                f"{{% set prod = states('{prod_instant}') | float(0) * 1000 %}}\n"
                                f"{{% set conso = states('{cons_instant}') | float(0) * 1000 %}}\n"
                                f"{{% set import_enedis = states('sensor.urban_puissance_import_enedis') | float(0) %}}\n"
                                f"{{% if import_enedis == 0 and conso > prod %}}\n"
                                f"  {{{{ conso - prod }}}}\n"
                                f"{{% else %}} 0 {{% endif %}}"
                            ),
                        }
                        },

                        "urban_batterie_virtuelle_sortie_horaire": {
                            {
                                "name": "urban_batterie_virtuelle_sortie_horaire",
                                "unique_id" :  "Urban Batterie Virtuelle Sortie Horaire",
                                "unit_of_measurement": "kWh",
                                "device_class": "energy",
                                "state_class": "total",
                                "state": "{{ -1 * (states('input_number.urban_energie_battery_out_hourly') | float(0)) }}"
                    
                            }
                            },

                        "urban_batterie_virtuelle_entrée_horaire": {
                            {

                                "name": "urban_batterie_virtuelle_entree_horaire", 
                                "unique_id" : "Urban Batterie Virtuelle Entrée Horaire",
                                "unit_of_measurement": "kWh",
                                "device_class": "energy",
                                "state_class": "total",
                                "state": "{{ states('input_number.urban_energie_battery_in_hourly') | float(0) }}"
                            }
                            },
                        
                        
                        "urban_puissance_solaire_instant": {
                            {

                                "name": "urban_puissance_solaire_instant", 
                                "unique_id" :  "Urban Puissance Solaire Instantanée (Urban)",
                                "unit_of_measurement": "W",
                                "state":  f"{{{{ states('{prod_instant}') | float(0) * 1000}}}}"
                            },
                            },

                        "urban_conso_totale_instant": {
                            {
                                "name" : "urban_conso_totale_instant",
                                "unique_id" :  "Urban Consommation Totale Instantanée (Urban)",
                                "unit_of_measurement": "W",
                                "state":  f"{{{{ states('{cons_instant}') | float(0) * 1000}}}}"
                            }
                        }
                  } 
                }   
    
            

        new_list.append(tpl_block)

        with open(DYNAMIC_TEMPLATE_DST, "w", encoding="utf-8") as f:
            yaml.dump(new_list, f, allow_unicode=True)

        _LOGGER.info("Injected 'urban_puissance_import_enedis' sensor")

    await hass.async_add_executor_job(inject_import_power_template)





    # 5) Injecter les sensors 'integration'
    def inject_integration_sensors():
        with open(DYNAMIC_SENSORS_DST, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or []

        new_list = [
            block for block in existing
            if not (block.get("platform") == "integration" and block.get("name") in (
                "urban_energie_solaire_produite", "urban_energie_consommee_totale"
            ))
        ]

        integration_blocks = [
            {

                "platform": "integration",
                "source": str(prod_instant),
                "name": "urban_energie_solaire_produite",
                "round": 3,
                "method": "left"
            },
            {

                "platform": "integration",
                "source": str(cons_instant),
                "name": "urban_energie_consommee_totale",
                "round": 3,
                "method": "left"
            }
        ]

        new_list.extend(integration_blocks)

        with open(DYNAMIC_SENSORS_DST, "w", encoding="utf-8") as f:
            yaml.dump(new_list, f, allow_unicode=True)

        _LOGGER.info("Injected integration sensors")

    await hass.async_add_executor_job(inject_integration_sensors)


    #  # 6) Injecter les sensors 'puissance battery'
    # def inject_battery_power_sensors():
    #     with open(DYNAMIC_TEMPLATE_DST, "r", encoding="utf-8") as f:
    #         existing = yaml.safe_load(f) or []

    #     # Remove old battery sensors if they exist
    #     new_list = []
    #     for block in existing:
    #         if block.get("platform") == "template":
    #             sensors = block.get("sensors", {})
    #             if "urban_puissance_batterie_virtuelle_in" in sensors or "urban_puissance_batterie_virtuelle_out" in sensors:
    #                 continue
    #         new_list.append(block)

    #     tpl_block = {

    #            "urban_puissance_batterie_virtuelle_in": {
    #              {
    #                 "name": "urban_puissance_batterie_virtuelle_in",
    #                 "unique_id" :  "Urban Puissance Batterie Virtuelle IN",
    #                 "unit_of_measurement": "W",
    #                 "state": (
    #                     f"{{% set prod = states('{prod_instant}') | float(0) * 1000 %}}\n"
    #                     f"{{% set conso = states('{cons_instant}') | float(0) * 1000 %}}\n"
    #                     f"{{% set import_enedis = states('sensor.urban_puissance_import_enedis') | float(0) %}}\n"
    #                     f"{{% if import_enedis == 0 and prod > conso %}}\n"
    #                     f"  {{{{ prod - conso }}}}\n"
    #                     f"{{% else %}} 0 {{% endif %}}"
    #                 ),
    #             }
    #             },
                
    #             "urban_puissance_batterie_virtuelle_out": {
    #             {
    #                 "name": "urban_puissance_batterie_virtuelle_out",
    #                 "unique_id" :  "Urban Puissance Batterie Virtuelle OUT",
    #                 "unit_of_measurement": "W",
    #                 "state":(
    #                     f"{{% set prod = states('{prod_instant}') | float(0) * 1000 %}}\n"
    #                     f"{{% set conso = states('{cons_instant}') | float(0) * 1000 %}}\n"
    #                     f"{{% set import_enedis = states('sensor.urban_puissance_import_enedis') | float(0) %}}\n"
    #                     f"{{% if import_enedis == 0 and conso > prod %}}\n"
    #                     f"  {{{{ conso - prod }}}}\n"
    #                     f"{{% else %}} 0 {{% endif %}}"
    #                 ),
    #             }
    #             }
                
    #         }



    #     new_list.append(tpl_block)

    #     with open(DYNAMIC_TEMPLATE_DST, "w", encoding="utf-8") as f:
    #         yaml.dump(new_list, f, allow_unicode=True)

    #     _LOGGER.info("Injected battery charge/discharge sensors")

    # await hass.async_add_executor_job(inject_battery_power_sensors)

    #  # 7) Injecter les sensors 'puissance battery'
    # def inject_mirror_power_sensors():
    #     with open(DYNAMIC_TEMPLATE_DST, "r", encoding="utf-8") as f:
    #         existing = yaml.safe_load(f) or []

    #     # Remove any existing mirrors
    #     new_list = []
    #     for block in existing:
    #         if block.get("platform") == "template":
    #             sensors = block.get("sensors", {})
    #             if "urban_puissance_solaire_instant" in sensors or "urban_conso_totale_instant" in sensors:
    #                 continue
    #         new_list.append(block)

    #     tpl_block = {
    #         "sensor": [
    #             {

    #                 "name": "urban_puissance_solaire_instant", 
    #                 "unique_id" :  "Urban Puissance Solaire Instantanée (Urban)",
    #                 "unit_of_measurement": "W",
    #                 "state":  f"{{{{ states('{prod_instant}') | float(0) * 1000}}}}"
    #             },
    #              {
                     
    #                 "name" : "urban_conso_totale_instant",
    #                 "unique_id" :  "Urban Consommation Totale Instantanée (Urban)",
    #                 "unit_of_measurement": "W",
    #                 "state":  f"{{{{ states('{cons_instant}') | float(0) * 1000}}}}"
    #             }
    #         ]
    #     }

    #     new_list.append(tpl_block)

    #     with open(DYNAMIC_TEMPLATE_DST, "w", encoding="utf-8") as f:
    #         yaml.dump(new_list, f, allow_unicode=True)

    #     _LOGGER.info("Injected mirror power sensors")

    # await hass.async_add_executor_job(inject_mirror_power_sensors)


    #         # 8) Injecter les sensors modernes pour batterie virtuelle in/out horaire
    # def inject_modern_energy_sensors():
    #     with open(DYNAMIC_TEMPLATE_DST, "r", encoding="utf-8") as f:
    #         existing = yaml.safe_load(f) or []

    #     # Supprimer les anciennes définitions s’il y en a
    #     new_list = []
    #     for block in existing:
    #         if block.get("platform") == "template":
    #             sensors = block.get("sensors", {})
    #             if "urban_batterie_virtuelle_sortie_horaire" in sensors or "urban_batterie_virtuelle_entree_horaire" in sensors:
    #                 continue
    #         new_list.append(block)

    #     tpl_block = {

    #         "urban_batterie_virtuelle_sortie_horaire": {
    #              {
    #                 "name": "urban_batterie_virtuelle_sortie_horaire",
    #                 "unique_id" :  "Urban Batterie Virtuelle Sortie Horaire",
    #                 "unit_of_measurement": "kWh",
    #                 "device_class": "energy",
    #                 "state_class": "total",
    #                 "state": "{{ -1 * (states('input_number.urban_energie_battery_out_hourly') | float(0)) }}"
        
    #             }
    #             },

    #             "urban_batterie_virtuelle_entrée_horaire": {
    #             {

    #                 "name": "urban_batterie_virtuelle_entree_horaire", 
    #                 "unique_id" : "Urban Batterie Virtuelle Entrée Horaire",
    #                 "unit_of_measurement": "kWh",
    #                 "device_class": "energy",
    #                 "state_class": "total",
    #                 "state": "{{ states('input_number.urban_energie_battery_in_hourly') | float(0) }}"
    #             }
    #         }
    #         }
        

    #     new_list.append(tpl_block)

    #     with open(DYNAMIC_TEMPLATE_DST, "w", encoding="utf-8") as f:
    #         yaml.dump(new_list, f, allow_unicode=True)

    #     _LOGGER.info("Injected modern template energy sensors")

    # await hass.async_add_executor_job(inject_modern_energy_sensors)
