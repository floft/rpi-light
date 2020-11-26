"""
rpi-lights integration for Home Assistant

Based on:
https://github.com/home-assistant/example-custom-config/blob/master/custom_components/example_light/light.py

In the config, add:
    light:
      - platform: rpi_lights
        host: example.com/lights
        password: your_key_here

Copy this and the manifest file to <config_dir>/custom_components/rpi_lights/
e.g. /var/lib/hass/custom_components/rpi_lights/
"""
import json
import logging
import urllib.error
import urllib.request

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
# Import the device class from the component that you want to support
from homeassistant.components.light import PLATFORM_SCHEMA, LightEntity
from homeassistant.const import CONF_HOST, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the rpi-lights platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    host = config[CONF_HOST]
    key = config[CONF_PASSWORD]

    # Add devices
    add_entities([RPiLight(host, key)])


class RPiLight(LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, host, key):
        """Initialize an AwesomeLight."""
        self._host = host
        self._key = key
        self._name = "RPi Lights"
        self._state = None

    def _url(self, state):
        return "{host}/hook?action={state}&key={key}".format(
            host=self._host,
            state=state,
            key=self._key,
        )

    def _call(self, state):
        url = self._url(state)
        state = None

        try:
            with urllib.request.urlopen(url) as response:
                result = json.loads(response.read().decode("utf-8"))

                if "result" in result:
                    if result["result"] == "on":
                        state = True
                    else:
                        state = False
                elif "error" in result:
                    _LOGGER.error("RPi Lights Error: " + result["error"])
        except ValueError:
            _LOGGER.error("RPi Lights Error: Could not parse JSON")
        except TypeError:
            _LOGGER.error("RPi Lights Error: type error, e.g. connection refused")
        except urllib.error.HTTPError as e:
            _LOGGER.error('RPi Lights Error HTTP Code: ' + e.code)
        except urllib.error.URLError as e:
            _LOGGER.error('RPi Lights Error: ' + e.reason)

        return state

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        self._state = self._call("on")

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._state = self._call("off")

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self._call("state")
