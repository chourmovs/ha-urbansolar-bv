from homeassistant.helpers.entity import Entity
from homeassistant.const import DEVICE_CLASS_ENERGY

async def async_setup_entry(hass, config_entry, async_add_entities):
    source_sensor = config_entry.data[CONF_SOURCE_SENSOR]
    
    # Créer un capteur virtuel qui suit la valeur de la source
    async_add_entities([
        VirtualSensor(
            hass=hass,
            name="energie_restituee_au_reseau",
            source=source_sensor
        )
    ])

class VirtualSensor(Entity):
    def __init__(self, hass, name, source):
        self.hass = hass
        self._name = name
        self._source = source
        self._state = 0.0
    
    @property
    def name(self):
        return self._name
    
    @property
    def state(self):
        return self._state
    
    @property
    def unit_of_measurement(self):
        return "kWh"
    
    @property
    def device_class(self):
        return DEVICE_CLASS_ENERGY
    
    async def async_update(self):
        state = self.hass.states.get(self._source)
        if state:
            self._state = float(state.state)