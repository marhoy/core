"""The flexit component."""
import logging

import pyflexit
import voluptuous as vol

from homeassistant.components.modbus import (
    CONF_HUB,
    DEFAULT_HUB,
    DOMAIN as MODBUS_DOMAIN,
)
from homeassistant.const import CONF_NAME, CONF_SLAVE, DEVICE_DEFAULT_NAME
from homeassistant.helpers import config_validation as cv

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_HUB, default=DEFAULT_HUB): cv.string,
        vol.Required(CONF_SLAVE): vol.All(int, vol.Range(min=0, max=32)),
        vol.Optional(CONF_NAME, default=DEVICE_DEFAULT_NAME): cv.string,
    }
)

DOMAIN = "flexit"

LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Set up the component."""
    hass.data[DOMAIN] = {"devices": []}

    # Loop over the configuration, adding Flexit units to hass.data
    for i, unit_config in enumerate(config[DOMAIN]):
        modbus_hub = hass.data[MODBUS_DOMAIN][unit_config[CONF_HUB]]
        modbus_slave = unit_config[CONF_SLAVE]
        if unit_config[CONF_NAME] == DEVICE_DEFAULT_NAME:
            name = f"Device {i}"
        else:
            name = unit_config[CONF_NAME]
        LOGGER.info("Setting up Flexit device %s", name)
        hass.data[DOMAIN]["devices"].append(
            FlexitDevice(modbus_hub, modbus_slave, name)
        )

    # Load the different platforms
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)

    # Return boolean to indicate that initialization was successful.
    return True


class FlexitDevice:
    """A Flexit ventilation aggregata."""

    def __init__(self, modbus_hub, modbus_slave, name):
        """Initialize the object."""
        self.name = name
        self.id = modbus_slave
        self.unit = pyflexit.aggregate(
            client=modbus_hub, unit=modbus_slave, model="Nordic"
        )
