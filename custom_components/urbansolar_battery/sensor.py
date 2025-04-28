from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.template import Template
from homeassistant.helpers.entity import async_generate_entity_id

from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    production_sensor = config_entry.data["sensor_production"]
    conso_totale_sensor = config_entry.data["sensor_conso_totale"]

    entities = [
        EnergieRestitueeSensor(hass, production_sensor, conso_totale_sensor),
    ]
    async_add_entities(entities, True)

class EnergieRestitueeSensor(SensorEntity):
    """Sensor to calculate énergie restituée au réseau."""

    def __init__(self, hass, production_sensor, conso_totale_sensor):
        self.hass = hass
        self.production_sensor = production_sensor
        self.conso_totale_sensor = conso_totale_sensor
        self._attr_name = "Énergie Restituée au Réseau"
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_unique_id = "energie_restituee_au_reseau"

    @property
    def native_value(self):
        production = self._get_state(self.production_sensor)
        consommation = self._get_state(self.conso_totale_sensor)
        if production is None or consommation is None:
            return None
        return round(production - consommation, 2)

    def _get_state(self, entity_id):
        """Helper to safely get state as float."""
        state = self.hass.states.get(entity_id)
        if state is None or state.state in (None, "unknown", "unavailable"):
            return None
        try:
            return float(state.state)
        except ValueError:
            return None
