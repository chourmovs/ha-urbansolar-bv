from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR

async def async_setup_entry(hass, entry, async_add_entities):
    production_entity = entry.data[CONF_PRODUCTION_SENSOR]
    consommation_entity = entry.data[CONF_CONSOMMATION_SENSOR]
    async_add_entities([
        UrbanSolarBatterySensor(production_entity, consommation_entity)
    ])

class UrbanSolarBatterySensor(SensorEntity):
    """Representation of the Urban Solar Battery virtual sensor."""

    def __init__(self, production_entity_id, consommation_entity_id):
        self._attr_name = "Énergie Restituée au Réseau"
        self._attr_unique_id = "energie_restituee_au_reseau"
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_state_class = "total"
        self.production_entity_id = production_entity_id
        self.consommation_entity_id = consommation_entity_id
        self._attr_native_value = 0

    async def async_update(self):
        """Fetch new state data for the sensor."""
        production = self.hass.states.get(self.production_entity_id)
        consommation = self.hass.states.get(self.consommation_entity_id)
        production_val = float(production.state) if production and production.state not in (None, "unknown", "unavailable") else 0
        consommation_val = float(consommation.state) if consommation and consommation.state not in (None, "unknown", "unavailable") else 0
        self._attr_native_value = round(production_val - consommation_val, 2)
