import asyncio
import logging
import yaml

_LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 5  # Nombre maximal de tentatives pour trouver les input_numbers
RETRY_DELAY = 2  # Délai entre chaque tentative (secondes)

async def setup_virtual_battery(hass, input_numbers_path):
    """Setup function to create or update input_number entities."""
    _LOGGER.debug("Starting setup of virtual battery input_numbers...")
    await load_and_set_input_numbers(hass, input_numbers_path)

async def load_and_set_input_numbers(hass, yaml_path):
    """Load input_number values from a YAML file and set them."""
    _LOGGER.debug(f"Loading input_numbers from {yaml_path}...")
    try:
        with open(yaml_path, "r") as f:
            input_numbers = yaml.safe_load(f)
    except Exception as e:
        _LOGGER.error(f"Failed to load {yaml_path}: {e}")
        return

    if not input_numbers:
        _LOGGER.warning("No input_numbers found in the YAML file.")
        return

    for entity_id, attrs in input_numbers.items():
        await set_input_number_with_retry(hass, entity_id, attrs.get("initial", 0))

async def set_input_number_with_retry(hass, entity_id, value):
    """Try setting the input_number value, retrying if entity not ready."""
    attempt = 0

    while attempt < MAX_RETRIES:
        if hass.states.get(entity_id) is not None:
            _LOGGER.info(f"Setting {entity_id} to {value}")
            try:
                await hass.services.async_call(
                    "input_number",
                    "set_value",
                    {
                        "entity_id": entity_id,
                        "value": value
                    },
                    blocking=True,
                )
            except Exception as e:
                _LOGGER.error(f"Failed to set value for {entity_id}: {e}")
            return

        _LOGGER.warning(f"Entity {entity_id} not found, retrying in {RETRY_DELAY}s... (attempt {attempt+1}/{MAX_RETRIES})")
        attempt += 1
        await asyncio.sleep(RETRY_DELAY)

    _LOGGER.error(f"Entity {entity_id} not available after {MAX_RETRIES} attempts. Skipping.")
