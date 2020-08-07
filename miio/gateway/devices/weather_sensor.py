"""Xiaomi Zigbee weather sensors."""

import attr

from ...click_common import command
from ..gateway import GatewayException
from .subdevice import SubDevice


class SensorHT(SubDevice):
    """Subdevice SensorHT specific properties and methods."""

    accessor = "get_prop_sensor_ht"
    properties = ["temperature", "humidity"]
    _zigbee_model = "lumi.sensor_ht"
    _model = "WSDCGQ01LM"
    _name = "Weather sensor"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        temperature: int = None  # in degrees celsius
        humidity: int = None  # in %

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        try:
            self._props.temperature = values[0] / 100
            self._props.humidity = values[1] / 100
        except Exception as ex:
            raise GatewayException(
                "One or more unexpected results while "
                "fetching properties %s: %s" % (self.properties, values)
            ) from ex


class AqaraHT(SubDevice):
    """Subdevice AqaraHT specific properties and methods."""

    accessor = "get_prop_sensor_ht"
    properties = ["temperature", "humidity", "pressure"]
    _zigbee_model = "lumi.weather.v1"
    _model = "WSDCGQ11LM"
    _name = "Weather sensor"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        temperature: int = None  # in degrees celsius
        humidity: int = None  # in %
        pressure: int = None  # in hPa

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        try:
            self._props.temperature = values[0] / 100
            self._props.humidity = values[1] / 100
            self._props.pressure = values[2] / 100
        except Exception as ex:
            raise GatewayException(
                "One or more unexpected results while "
                "fetching properties %s: %s" % (self.properties, values)
            ) from ex
