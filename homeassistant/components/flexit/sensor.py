"""Platform for sensor integration."""
import logging
from typing import Optional

from homeassistant.const import TEMP_CELSIUS, UNIT_PERCENTAGE
from homeassistant.helpers.entity import Entity

from . import DOMAIN

LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    for flexit_device in hass.data[DOMAIN]["devices"]:
        add_entities(
            [
                FlexitSensor(
                    flexit_device,
                    "Outside Temperature",
                    "outside_air_temp",
                    unit_of_measurement=TEMP_CELSIUS,
                    icon="mdi:thermometer",
                    display_func=lambda x: round(x, 1),
                ),
                FlexitSensor(
                    flexit_device,
                    "Extract Temperature",
                    "extract_air_temp",
                    unit_of_measurement=TEMP_CELSIUS,
                    icon="mdi:thermometer",
                    display_func=lambda x: round(x, 1),
                ),
                FlexitSensor(
                    flexit_device,
                    "Electric Heater",
                    "electric_heater_power",
                    unit_of_measurement=UNIT_PERCENTAGE,
                    icon=None,
                    display_func=lambda x: round(x, None),
                ),
                FlexitSensor(
                    flexit_device,
                    "Heat Exchanger Speed",
                    "heat_exchanger_speed",
                    unit_of_measurement=UNIT_PERCENTAGE,
                    icon=None,
                    display_func=lambda x: round(x, None),
                ),
            ]
        )
        if hasattr(flexit_device.unit, "efficiency"):
            add_entities(
                [
                    FlexitSensor(
                        flexit_device,
                        "Efficiency",
                        "efficiency",
                        unit_of_measurement=UNIT_PERCENTAGE,
                        icon=None,
                        display_func=lambda x: round(x * 100, 1),
                    )
                ]
            )


class FlexitSensor(Entity):
    """Generic Flexit sensor."""

    def __init__(
        self,
        device,
        entity_name,
        attr,
        unit_of_measurement,
        icon=None,
        display_func=lambda x: x,
    ):
        """Initialize the sensor."""
        self._state = None
        self._unit = device.unit
        self._device_name = device.name
        self._entity_name = f"{device.name} {entity_name}"
        self._unique_id = f"flexit_slave_{device.id}_{attr}"
        self._attr = attr
        self._unit_of_measurement = unit_of_measurement
        self._icon = icon
        self._display_func = display_func

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._state is None:
            return None
        return self._display_func(self._state)

    @property
    def name(self) -> Optional[str]:
        """Name of the entity."""
        return self._entity_name

    @property
    def unique_id(self) -> Optional[str]:
        """Return the unique attribute ID."""
        return self._unique_id

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self) -> Optional[str]:
        """Icon of the sensor."""
        return self._icon

    def update(self):
        """Fetch new state data for the sensor."""
        self._state = getattr(self._unit, self._attr)
