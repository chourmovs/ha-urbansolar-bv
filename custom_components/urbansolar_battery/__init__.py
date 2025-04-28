"""UrbanSolar Battery Virtual Integration"""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .setup_virtual_battery import setup_virtual_battery

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up UrbanSolar Battery from a config entry."""
    _LOGGER.info("Setting up UrbanSolar Battery Virtual Integration")

    # Démarrer le setup des fichiers
    hass.async_create_task(setup_virtual_battery(hass))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload UrbanSolar Battery."""
    _LOGGER.info("Unloading UrbanSolar Battery Virtual Integration")
    return True
