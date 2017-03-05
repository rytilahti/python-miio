"""
Demo platform that has two fake switches.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/demo/
"""
from homeassistant.components.switch import SwitchDevice
from homeassistant.const import DEVICE_DEFAULT_NAME, CONF_NAME, CONF_HOST
import logging

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['python-mirobo']

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Setup the demo switches."""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get('token')

    add_devices_callback([
        MiroboSwitch(name, host, token)
    ])


class MiroboSwitch(SwitchDevice):
    """Representation of a demo switch."""

    def __init__(self, name, host, token):
        """Initialize the Demo switch."""
        self._name = name or DEVICE_DEFAULT_NAME
        self.host = host
        self.token = token
        self._vacuum = None
        self._state = None
        self._state = None

    @property
    def should_poll(self):
        """No polling needed for a demo switch."""
        return True

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return 'mdi:broom'

    @property
    def available(self):
        return self._state is not None

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    @property
    def vacuum(self):
        if not self._vacuum:
            from mirobo import Vacuum
            _LOGGER.info("initializing with host %s token %s" % (self.host, self.token))
            self._vacuum = Vacuum(self.host, self.token)

        return self._vacuum

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._vacuum.start()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._vacuum.stop()
        self._vacuum.home()

    def update(self):
        try:
            state = self.vacuum.status()
            _LOGGER.info("got state from robo: %s" % state)

            self._state_attrs = {'status': state.state, 'error': state.error,
                                 'battery': state.battery, 'fan': state.fanspeed,
                                 'cleaning time': str(state.clean_time), 'cleaned area': state.clean_area}
            self._state = state.state_code
        except Exception as ex:
            _LOGGER.error("Got exception while fetching the state: %s" % ex)
