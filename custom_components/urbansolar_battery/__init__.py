from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.yaml import load_yaml
import os

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up UrbanSolar Battery from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Charger dynamiquement les YAML au setup
    config_path = os.path.join(
        hass.config.path("custom_components", DOMAIN, "config")
    )

    for yaml_file in ["input_numbers.yaml", "sensors.yaml", "utility_meters.yaml", "automations/mettre_a_jour_batterie_stock.yaml", "automations/gestion_horaire_batterie_virtuelle.yaml", "automations/mettre_a_jour_valeurs_veille_avant_veille.yaml"]:
        full_path = os.path.join(config_path, yaml_file)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                yaml_data = load_yaml(f)

                # Injection directe
                await hass.services.async_call(
                    "homeassistant",
                    "reload_core_config",
                    blocking=True,
                )
                # Ou ici tu peux directement créer les input_number ou sensors dynamiquement
                # en fonction du contenu de yaml_data si besoin

    return True
