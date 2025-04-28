from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR

from .const import DOMAIN, CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR

async def async_setup_entry(hass, config_entry, async_add_entities):
    production_sensor = config_entry.data[CONF_PRODUCTION_SENSOR]
    consommation_sensor = config_entry.data[CONF_CONSOMMATION_SENSOR]

    entities = [
        EnergieRestitueeSensor(hass, production_sensor, consommation_sensor),
    ]
    async_add_entities(entities, True)

class EnergieRestitueeSensor(SensorEntity):
    """Sensor to calculate énergie restituée au réseau."""

    def __init__(self, hass, production_sensor, consommation_sensor):
        self.hass = hass
        self.production_sensor = production_sensor
        self.consommation_sensor = consommation_sensor
        self._attr_name = "Énergie Restituée au Réseau"
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_unique_id = "energie_restituee_au_reseau"

    @property
    def native_value(self):
        production = self._get_state(self.production_sensor)
        consommation = self._get_state(self.consommation_sensor)
        if production is None or consommation is None:
            return None
        return round(production - consommation, 2)

    def _get_state(self, entity_id):
        """Safely retrieve the state of an entity as a float."""
        state = self.hass.states.get(entity_id)
        if state is None or state.state in (None, "unknown", "unavailable"):
            return None
        try:
            return float(state.state)
        except ValueError:
            return None
