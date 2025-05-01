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
    "dashbord.yaml": "urban_dashboard.yaml"
}

DASHBOARD_ID = "urban_virtual_battery"
DASHBOARD_TITLE = "Batterie Virtuelle"
DASHBOARD_FILENAME = "urban_dashboard.yaml"
DASHBOARD_ICON = "mdi:battery"
STORAGE_FILE_SOURCE = os.path.join(CONFIG_DIR, "urban_dashboard_storage.json")
STORAGE_FILE_TARGET = os.path.join("/config/.storage", f"lovelace.{DASHBOARD_ID}")

def ensure_fresh_copy(source_file, target_file):
    try:
        if os.path.exists(target_file):
            os.remove(target_file)
            _LOGGER.debug(f"Deleted existing file: {target_file}")
        shutil.copy(source_file, target_file)
        _LOGGER.info(f"Copied {source_file} → {target_file}")
    except Exception as e:
        _LOGGER.error(f"Error copying {source_file} to {target_file}: {e}")

def is_yaml_mode():
    config_path = os.path.join(TARGET_DIR, "configuration.yaml")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        lovelace_cfg = config.get("lovelace", {})
        return isinstance(lovelace_cfg, dict) and lovelace_cfg.get("mode") == "yaml"
    except Exception as e:
        _LOGGER.warning(f"Unable to determine Lovelace mode: {e}")
        return False

def declare_yaml_dashboard():
    config_path = os.path.join(TARGET_DIR, "configuration.yaml")
    dashboard_config = f"""
lovelace:
  mode: yaml
  dashboards:
    {DASHBOARD_ID}:
      mode: yaml
      title: {DASHBOARD_TITLE}
      icon: {DASHBOARD_ICON}
      show_in_sidebar: true
      filename: {DASHBOARD_FILENAME}
"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        if DASHBOARD_ID not in content:
            with open(config_path, "a", encoding="utf-8") as f:
                f.write("\n" + dashboard_config.strip() + "\n")
            _LOGGER.info("Dashboard YAML ajouté à configuration.yaml.")
        else:
            _LOGGER.info("Dashboard YAML déjà présent dans configuration.yaml.")
    except Exception as e:
        _LOGGER.error(f"Erreur lors de l'ajout au configuration.yaml : {e}")

async def create_storage_dashboard(hass):
    """Crée un dashboard dans le mode storage"""
    try:
        dashboards = await hass.data["frontend_lovelace"].async_get_dashboards()
        if f"lovelace-{DASHBOARD_ID}" in dashboards:
            _LOGGER.info("Dashboard Storage déjà présent.")
            return

        await hass.services.async_call(
            "frontend",
            "lovelace_create",
            {
                "url_path": DASHBOARD_ID,
                "title": DASHBOARD_TITLE,
                "icon": DASHBOARD_ICON,
                "mode": "yaml",
                "filename": DASHBOARD_FILENAME,
                "require_admin": True,
                "show_in_sidebar": True
            },
            blocking=True
        )
        _LOGGER.info("Dashboard créé dynamiquement en mode storage.")
    except Exception as e:
        _LOGGER.error(f"Erreur lors de la création du dashboard en mode storage : {e}")

async def setup_virtual_battery(hass):
    _LOGGER.info("🟢 Setup UrbanSolar Virtual Battery - YAML copy mode")

    for src_name, dest_name in FILES_TO_COPY.items():
        src_path = os.path.join(CONFIG_DIR, src_name)
        dest_path = os.path.join(TARGET_DIR, dest_name)

        if not os.path.exists(src_path):
            _LOGGER.warning(f"Fichier source manquant : {src_path}")
            continue

        ensure_fresh_copy(src_path, dest_path)

    if is_yaml_mode():
        declare_yaml_dashboard()
    else:
        await create_storage_dashboard(hass)
        setup_storage_dashboard_file()

    _LOGGER.info("✅ UrbanSolar Virtual Battery setup terminé.")

def setup_storage_dashboard_file():
    try:
        if os.path.exists(STORAGE_FILE_TARGET):
            _LOGGER.info(f"Dashboard storage déjà présent dans .storage : {STORAGE_FILE_TARGET}")
            return

        shutil.copy(STORAGE_FILE_SOURCE, STORAGE_FILE_TARGET)
        _LOGGER.info(f"Dashboard storage copié vers .storage : {STORAGE_FILE_TARGET}")
    except Exception as e:
        _LOGGER.error(f"Erreur lors de la copie du dashboard .storage : {e}")
