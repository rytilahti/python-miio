import logging
from .device import Device
from typing import Any, Dict
from collections import defaultdict

_LOGGER = logging.getLogger(__name__)


class CeilStatus:
    """Container for status reports from Xiaomi Philips LED Ceiling Lamp"""

    def __init__(self, data: Dict[str, Any]) -> None:
        # ['power', 'bright', 'snm', 'dv', 'cctsw', 'bl', 'mb', 'ac', 'ms'
        #  'sw', 'cct']
        # ['off', 0, 4, 0, [[0, 3], [0, 2], [0, 1]], 1, 1, 1, 1, 99]
        # NOTE: Only 8 properties can be requested at the same time
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def brightness(self) -> int:
        return self.data["bright"]

    @property
    def scene(self) -> int:
        return self.data["snm"]

    @property
    def delay_off_countdown(self) -> int:
        return self.data["dv"]

    @property
    def color_temperature(self) -> int:
        return self.data["cct"]

    @property
    def smart_night_light(self) -> int:
        return self.data["bl"]

    @property
    def automatic_color_temperature(self) -> int:
        return self.data["ac"]

    def __str__(self) -> str:
        s = "<CeilStatus power=%s, brightness=%s, " \
            "color_temperature=%s, scene=%s, delay_off_countdown=%s, " \
            "smart_night_light=%s, automatic_color_temperature=%s>" % \
            (self.power, self.brightness,
             self.color_temperature, self.scene, self.delay_off_countdown,
             self.smart_night_light, self.automatic_color_temperature)
        return s


class Ceil(Device):
    """Main class representing Xiaomi Philips LED Ceiling Lamp."""

    # TODO: - Auto On/Off Not Supported
    #       - Adjust Scenes with Wall Switch Not Supported

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def set_brightness(self, level: int):
        """Set brightness level."""
        return self.send("set_bright", [level])

    def set_color_temperature(self, level: int):
        """Set Correlated Color Temperature."""
        return self.send("set_cct", [level])

    def delay_off(self, seconds: int):
        """Set delay off seconds."""
        return self.send("delay_off", [seconds])

    def set_scene(self, num: int):
        """Set scene number."""
        return self.send("apply_fixed_scene", [num])

    def smart_night_light_on(self):
        """Smart Night Light On."""
        return self.send("enable_bl", [1])

    def smart_night_light_off(self):
        """Smart Night Light off."""
        return self.send("enable_bl", [0])

    def automatic_color_temperature_on(self):
        """Automatic color temperature on."""
        return self.send("enable_ac", [1])

    def automatic_color_temperature_off(self):
        """Automatic color temperature off."""
        return self.send("enable_ac", [0])

    def status(self) -> CeilStatus:
        """Retrieve properties."""
        properties = ['power', 'bright', 'cct', 'snm', 'dv', 'bl', 'ac', ]
        values = self.send(
            "get_prop",
            properties
        )

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return CeilStatus(defaultdict(lambda: None, zip(properties, values)))
