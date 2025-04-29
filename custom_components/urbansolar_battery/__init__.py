"""UrbanSolar Virtual Battery integration."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .setup_virtual_battery import setup_virtual_battery

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up UrbanSolar Virtual Battery from yaml configuration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up UrbanSolar Virtual Battery from a config entry."""
    _LOGGER.info("Setting up UrbanSolar Virtual Battery integration")
    hass.data.setdefault(DOMAIN, {})

    # Appelle la fonction pour créer les entités virtuelles
    await setup_virtual_battery(hass)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Unloading UrbanSolar Virtual Battery integration")

    # Ici on pourrait ajouter du cleanup si nécessaire
    hass.data.pop(DOMAIN, None)

    return True
