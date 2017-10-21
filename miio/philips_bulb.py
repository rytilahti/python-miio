import logging
from .device import Device
from typing import Any, Dict
from collections import defaultdict

_LOGGER = logging.getLogger(__name__)


class PhilipsBulbStatus:
    """Container for status reports from Xiaomi Philips LED Ceiling Lamp"""

    def __init__(self, data: Dict[str, Any]) -> None:
        # ['power': 'on', 'bright': 85, 'cct': 9, 'snm': 0, 'dv': 0]
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
    def color_temperature(self) -> int:
        return self.data["cct"]

    @property
    def scene(self) -> int:
        return self.data["snm"]

    @property
    def delay_off_countdown(self) -> int:
        return self.data["dv"]

    def __str__(self) -> str:
        s = "<PhilipsBulbStatus power=%s, brightness=%s, " \
            "color_temperature=%s, scene=%s, delay_off_countdown=%s>" % \
            (self.power, self.brightness,
             self.color_temperature, self.scene, self.delay_off_countdown)
        return s


class PhilipsBulb(Device):
    """Main class representing Xiaomi Philips LED Ball Lamp."""

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

    def status(self) -> PhilipsBulbStatus:
        """Retrieve properties."""
        properties = ['power', 'bright', 'cct', 'snm', 'dv', ]
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

        return PhilipsBulbStatus(
            defaultdict(lambda: None, zip(properties, values)))
