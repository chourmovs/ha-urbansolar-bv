import logging
import os
import shutil
import yaml

from .const import CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR, DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_DIR = "custom_components/urbansolar_battery/config"
TARGET_DIR = "/config"

FILES_TO_COPY = {
    "input_numbers.yaml": "urban_input_numbers.yaml",
    "utility_meters.yaml": "urban_utility_meters.yaml",
    "automations.yaml": "urban_automations.yaml",
    "dashboard.yaml": "urban_dashboard.yaml",
    # on ne copie pas sensors.yaml directement ici ; on le traitera ci-dessous
}

STATIC_SENSORS_SRC = os.path.join(CONFIG_DIR, "sensors.yaml")
DYNAMIC_SENSORS_DST = os.path.join(TARGET_DIR, "urban_sensors.yaml")

def ensure_fresh_copy(src: str, dst: str) -> None:
    """Supprime et recopie un fichier YAML statique si nécessaire."""
    try:
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy(src, dst)
        _LOGGER.debug("Copied %s → %s", src, dst)
    except Exception as e:
        _LOGGER.error("Error copying %s to %s: %s", src, dst, e)

def inject_dynamic_sensor(prod: str, conso: str, dst_path: str) -> None:
    """Ajoute ou remplace le template sensor énergie restituée dans urban_sensors.yaml."""
    tpl_block = {
      "platform": "template",
      "sensors": {
        "energie_restituee_au_reseau": {
          "friendly_name": "Énergie Restituée au Réseau",
          "unit_of_measurement": "kWh",
          "value_template": (
            "{{ states('" + prod + "') | float(0) "
            "- states('" + conso + "') | float(0) }}"
          )
        }
      }
    }

    try:
        # 1) Charger l'existant (liste de blocks ou dict)
        if os.path.exists(dst_path):
            with open(dst_path, "r", encoding="utf-8") as f:
                existing = yaml.safe_load(f) or []
        else:
            existing = []

        # 2) Filtrer les anciens blocks "template" pour ce sensor
        cleaned = []
        for block in existing:
            if isinstance(block, dict) and block.get("platform") == "template":
                sensors = block.get("sensors", {})
                if "energie_restituee_au_reseau" in sensors:
                    continue
            cleaned.append(block)

        # 3) Ajouter notre block à la fin
        cleaned.append(tpl_block)

        # 4) Réécrire le fichier
        with open(dst_path, "w", encoding="utf-8") as f:
            yaml.dump(cleaned, f, allow_unicode=True)
        _LOGGER.info("Injected dynamic template sensor into %s", dst_path)

    except Exception as e:
        _LOGGER.error("Error injecting dynamic sensor: %s", e)

async def setup_virtual_battery(hass, entry) -> None:
    """Copie les configs statiques, puis génère/maintiens urban_sensors.yaml dynamique."""
    _LOGGER.info("Setting up UrbanSolar Virtual Battery")

    # --- 1) Copier les fichiers statiques ---
    for src_name, dst_name in FILES_TO_COPY.items():
        src = os.path.join(CONFIG_DIR, src_name)
        dst = os.path.join(TARGET_DIR, dst_name)
        if os.path.exists(src):
            ensure_fresh_copy(src, dst)
        else:
            _LOGGER.warning("Missing source file: %s", src)

    # --- 2) Copier initial sensors.yaml si dst absent ---
    if os.path.exists(STATIC_SENSORS_SRC):
        ensure_fresh_copy(STATIC_SENSORS_SRC, DYNAMIC_SENSORS_DST)
    else:
        # pas d'existant statique : on commence avec liste vide
        with open(DYNAMIC_SENSORS_DST, "w", encoding="utf-8") as f:
            yaml.dump([], f)
        _LOGGER.warning("No static sensors.yaml found; created empty urban_sensors.yaml")

    # --- 3) Récupérer les capteurs choisis par l'utilisateur ---
    prod = entry.data.get(CONF_PRODUCTION_SENSOR)
    conso = entry.data.get(CONF_CONSOMMATION_SENSOR)
    if not prod or not conso:
        _LOGGER.error("Missing production/consumption sensor in entry.data")
        return

    # --- 4) Injecter ou mettre à jour le template sensor dynamique ---
    inject_dynamic_sensor(prod, conso, DYNAMIC_SENSORS_DST)

    _LOGGER.info("UrbanSolar Virtual Battery setup completed.")