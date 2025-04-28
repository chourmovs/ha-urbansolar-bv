from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import selector  # <--- AJOUTER CETTE LIGNE

from .const import DOMAIN, CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR

class UrbanSolarBatteryFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Urban Solar Battery."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            entity_registry = er.async_get(hass=self.hass)
            valid = True
            for conf in (CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR):
                if not entity_registry.async_get(user_input[conf]):
                    valid = False
                    errors["base"] = "invalid_entity"
                    break

            if valid:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Configuration Batterie Virtuelle",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_PRODUCTION_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        #device_class="energy",
                    )
                ),
                vol.Required(CONF_CONSOMMATION_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        #device_class="energy",
                    )
                ),
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return UrbanSolarBatteryOptionsFlowHandler(config_entry)

class UrbanSolarBatteryOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Urban Solar Battery."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            entity_registry = er.async_get(hass=self.hass)
            valid = True
            for conf in (CONF_PRODUCTION_SENSOR, CONF_CONSOMMATION_SENSOR):
                if not entity_registry.async_get(user_input[conf]):
                    valid = False
                    errors["base"] = "invalid_entity"
                    break

            if valid:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, **user_input}
                )
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_PRODUCTION_SENSOR, default=self.config_entry.data.get(CONF_PRODUCTION_SENSOR, "")): str,
                vol.Required(CONF_CONSOMMATION_SENSOR, default=self.config_entry.data.get(CONF_CONSOMMATION_SENSOR, "")): str,
            }),
            errors=errors,
        )
    
import logging
import os

from homeassistant import config_entries
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

CONFIG_PATH = "/config"

def ensure_file_exists(filename, content=""):
    """Créer le fichier s'il n'existe pas."""
    full_path = os.path.join(CONFIG_PATH, filename)
    if not os.path.exists(full_path):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        _LOGGER.info(f"Fichier {filename} créé automatiquement.")
    else:
        _LOGGER.info(f"Fichier {filename} déjà existant.")

def ensure_include_in_configuration(include_line):
    """Ajouter un include dans configuration.yaml s'il n'existe pas."""
    config_file = os.path.join(CONFIG_PATH, "configuration.yaml")
    try:
        with open(config_file, "r") as f:
            config_content = f.read()
    except FileNotFoundError:
        config_content = ""

    if include_line not in config_content:
        with open(config_file, "a") as f:
            f.write(f"\n{include_line}\n")
        _LOGGER.info(f"Inclusion {include_line} ajoutée à configuration.yaml")
    else:
        _LOGGER.info(f"Inclusion {include_line} déjà présente dans configuration.yaml")

def create_automation_files():
    """Créer les fichiers d'automations"""
    automations_dir = os.path.join(CONFIG_PATH, "automations")
    os.makedirs(automations_dir, exist_ok=True)

    files = {
        "gestion_horaire_batterie_virtuelle.yaml": """
- id: 'gestion_horaire_batterie_virtuelle'
  alias: "Gestion horaire batterie virtuelle"
  trigger:
    platform: time_pattern
    hours: '*'
    minutes: '59'
    seconds: '50'
  action:
    - choose:
        - conditions:
            - condition: numeric_state
              entity_id: sensor.energie_restituee_au_reseau_hourly
              above: 0
          sequence:
            - service: input_number.set_value
              target:
                entity_id: input_number.energie_battery_in_hourly
              data:
                value: "{{ (states('input_number.energie_battery_in_hourly')|float + states('sensor.energie_restituee_au_reseau_hourly')|float)|round }}"
        - conditions:
            - condition: numeric_state
              entity_id: sensor.energie_restituee_au_reseau_hourly
              below: 0
          sequence:
            - service: input_number.set_value
              target:
                entity_id: input_number.energie_battery_out_hourly
              data:
                value: "{{ (states('input_number.energie_battery_out_hourly')|float + states('sensor.energie_restituee_au_reseau_hourly')|float)|round }}"
""",
        "mettre_a_jour_batterie_stock.yaml": """
- id: 'mettre_a_jour_batterie_stock'
  alias: "Mettre à jour Batterie Virtuelle Stock"
  trigger:
    platform: time
    at: "00:01:00"
  action:
    - variables:
        stock_actuel: "{{ states('input_number.batterie_virtuelle_stock')|float }}"
        pointage: "{{ states('input_number.batterie_virtuelle_pointage')|float }}"
        diff: "{{ states('sensor.diff_energie_restituee_veille_avant_veille')|float }}"
      service: input_number.set_value
      target: 
        entity_id: input_number.batterie_virtuelle_stock
      data:
        value: >-
          {%- if pointage != 0 -%}
            {{ pointage + diff|float }}
          {%- else -%}
            {{ stock_actuel + diff|float }}
          {%- endif -%}
    - service: input_number.set_value
      target:
        entity_id: input_number.batterie_virtuelle_pointage
      data:
        value: 0
""",
        "mettre_a_jour_valeurs_veille_avant_veille.yaml": """
- id: 'mettre_a_jour_valeurs_veille_avant_veille'
  alias: "Mettre à jour les valeurs de veille et avant-veille"
  trigger:
    platform: time
    at: "00:00:00"
  action:
    - service: input_number.set_value
      target:
        entity_id: input_number.energie_restituee_avant_veille
      data:
        value: "{{ states('input_number.energie_restituee_veille')|float }}"
    - service: input_number.set_value
      target:
        entity_id: input_number.energie_restituee_veille
      data:
        value: "{{ states('sensor.energie_restituee_au_reseau')|float }}"
"""
    }

    for filename, content in files.items():
        file_path = os.path.join(automations_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(content)
            _LOGGER.info(f"Automation {filename} créé.")

class UrbanSolarBatteryConfigFlow(config_entries.ConfigFlow, domain="urbansolar_battery"):
    """Config flow pour UrbanSolar Battery."""

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # 🔥 Installer automatiquement tout à la fin du config flow
            ensure_file_exists("input_numbers.yaml")
            ensure_file_exists("utility_meters.yaml")
            ensure_file_exists("sensors.yaml")
            create_automation_files()

            ensure_include_in_configuration("input_number: !include input_numbers.yaml")
            ensure_include_in_configuration("utility_meter: !include utility_meters.yaml")
            ensure_include_in_configuration("sensor: !include sensors.yaml")
            ensure_include_in_configuration("automation: !include_dir_merge_list automations")

            _LOGGER.info("Installation automatique terminée.")
            return self.async_create_entry(title="Urban Solar Battery", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={
                "description": "Configuration de la batterie virtuelle Urban Solar."
            }
        )
