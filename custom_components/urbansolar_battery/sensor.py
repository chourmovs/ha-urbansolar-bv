from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR

INPUT_NUMBER_DOMAIN = "input_number"
UTILITY_METER_DOMAIN = "utility_meter"
AUTOMATION_DOMAIN = "automation"

async def async_setup_entry(hass, entry, async_add_entities):
    await ensure_entities_exist(hass)

    production_entity = entry.data[CONF_PRODUCTION_SENSOR]
    consommation_entity = entry.data[CONF_CONSOMMATION_SENSOR]
    async_add_entities([
        UrbanSolarBatterySensor(production_entity, consommation_entity),
        DiffEnergieRestitueeSensor(),
        BatterieVirtuelleEntreeHoraireSensor(),
        BatterieVirtuelleSortieHoraireSensor(),
    ])

async def ensure_entities_exist(hass):
    """Ensure all required entities and automations exist."""

    # ---- Vérifier les input_numbers ----
    input_numbers = {
        "input_number.energie_restituee_veille": {"name": "Énergie Restituée Veille", "min": 0, "max": 10000},
        "input_number.energie_restituee_avant_veille": {"name": "Énergie Restituée Avant-Veille", "min": 0, "max": 100000},
        "input_number.batterie_virtuelle_pointage": {"name": "Batterie Virtuelle Pointage Manuel", "min": 0, "max": 10000},
        "input_number.batterie_virtuelle_stock": {"name": "Batterie Virtuelle Stock", "min": 0, "max": 10000},
        "input_number.energie_battery_in_hourly": {"name": "Énergie Batterie Entrée Horaire", "min": 0, "max": 10000},
        "input_number.energie_battery_out_hourly": {"name": "Énergie Batterie Sortie Horaire", "min": -10000, "max": 0},
    }
    for entity_id, params in input_numbers.items():
        if not hass.states.get(entity_id):
            await hass.services.async_call(
                INPUT_NUMBER_DOMAIN, "create", {
                    "name": params["name"],
                    "initial": 0,
                    "min": params["min"],
                    "max": params["max"],
                    "step": 1,
                    "unit_of_measurement": "kWh",
                    "entity_id": entity_id
                },
                blocking=True
            )

    # ---- Vérifier le utility_meter ----
    if not hass.states.get("sensor.energie_restituee_au_reseau_hourly"):
        await hass.services.async_call(
            UTILITY_METER_DOMAIN, "create", {
                "name": "energie_restituee_au_reseau_hourly",
                "source": "sensor.energie_restituee_au_reseau",
                "cycle": "hourly",
                "net_consumption": True
            },
            blocking=True
        )

    # ---- Vérifier les template sensors ----
    template_sensors = [
        "sensor.diff_energie_restituee_veille_avant_veille",
        "sensor.batterie_virtuelle_sortie_horaire",
        "sensor.batterie_virtuelle_entree_horaire"
    ]
    for sensor_id in template_sensors:
        if not hass.states.get(sensor_id):
            # Impossible de créer dynamiquement un template sensor en HA => notifier
            hass.helpers.event.async_call_later(0, lambda *_: hass.components.persistent_notification.create(
                f"Template sensor `{sensor_id}` manquant. Merci de le créer manuellement.", "UrbanSolarBattery"))

    # ---- Vérifier les automations ----
    existing_automations = hass.states.async_entity_ids("automation")
    automations_to_create = {
        "automation.mettre_a_jour_valeurs_veille_avant_veille": "Mettre à jour les valeurs de veille et avant-veille",
        "automation.mettre_a_jour_batterie_stock": "Mettre à jour Batterie Virtuelle Stock",
        "automation.gestion_horaire_batterie_virtuelle": "Gestion horaire batterie virtuelle",
    }
    for automation_id, alias in automations_to_create.items():
        if automation_id not in existing_automations:
            await hass.services.async_call(AUTOMATION_DOMAIN, "reload", {}, blocking=True)
            hass.helpers.event.async_call_later(0, lambda *_: hass.components.persistent_notification.create(
                f"Automation `{alias}` manquante. Merci de l'ajouter manuellement.", "UrbanSolarBattery"))

class UrbanSolarBatterySensor(SensorEntity):
    """Représentation du capteur principal Urban Solar Battery."""

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
        production = self.hass.states.get(self.production_entity_id)
        consommation = self.hass.states.get(self.consommation_entity_id)
        try:
            production_val = float(production.state) if production and production.state not in (None, "unknown", "unavailable") else 0
            consommation_val = float(consommation.state) if consommation and consommation.state not in (None, "unknown", "unavailable") else 0
        except (ValueError, TypeError):
            production_val = 0
            consommation_val = 0
        self._attr_native_value = round(production_val - consommation_val, 2)

class DiffEnergieRestitueeSensor(SensorEntity):
    """Capteur pour la différence d'énergie entre veille et avant-veille."""

    def __init__(self):
        self._attr_name = "Diff Énergie Restituée Veille - Avant-Veille"
        self._attr_unique_id = "diff_energie_restituee_veille_avant_veille"
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_state_class = "total"
        self._attr_native_value = 0

    async def async_update(self):
        veille = self.hass.states.get("input_number.energie_restituee_veille")
        avant_veille = self.hass.states.get("input_number.energie_restituee_avant_veille")
        try:
            veille_val = float(veille.state) if veille and veille.state not in (None, "unknown", "unavailable") else 0
            avant_veille_val = float(avant_veille.state) if avant_veille and avant_veille.state not in (None, "unknown", "unavailable") else 0
        except (ValueError, TypeError):
            veille_val = 0
            avant_veille_val = 0
        self._attr_native_value = round(veille_val - avant_veille_val, 2)

class BatterieVirtuelleEntreeHoraireSensor(SensorEntity):
    """Capteur pour l'entrée horaire de la batterie virtuelle."""

    def __init__(self):
        self._attr_name = "Batterie Virtuelle Entrée Horaire"
        self._attr_unique_id = "batterie_virtuelle_entree_horaire"
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_state_class = "total"
        self._attr_native_value = 0

    async def async_update(self):
        in_hourly = self.hass.states.get("input_number.energie_battery_in_hourly")
        try:
            in_val = float(in_hourly.state) if in_hourly and in_hourly.state not in (None, "unknown", "unavailable") else 0
        except (ValueError, TypeError):
            in_val = 0
        self._attr_native_value = round(in_val, 2)

class BatterieVirtuelleSortieHoraireSensor(SensorEntity):
    """Capteur pour la sortie horaire de la batterie virtuelle."""

    def __init__(self):
        self._attr_name = "Batterie Virtuelle Sortie Horaire"
        self._attr_unique_id = "batterie_virtuelle_sortie_horaire"
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_state_class = "total"
        self._attr_native_value = 0

    async def async_update(self):
        out_hourly = self.hass.states.get("input_number.energie_battery_out_hourly")
        try:
            out_val = float(out_hourly.state) if out_hourly and out_hourly.state not in (None, "unknown", "unavailable") else 0
        except (ValueError, TypeError):
            out_val = 0
        self._attr_native_value = round(-1 * out_val, 2)

