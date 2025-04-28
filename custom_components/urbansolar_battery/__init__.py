from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS: list[Platform] = []  # À remplir plus tard si besoin (ex: [Platform.SENSOR])

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Urban Solar Battery from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    domain_data = hass.data.get(DOMAIN)
    if domain_data is not None:
        domain_data.pop(entry.entry_id, None)
        if not domain_data:
            hass.data.pop(DOMAIN, None)

    return True
