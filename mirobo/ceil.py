from .device import Device
from typing import Any, Dict

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
    def bright(self) -> int:
        return self.data["bright"]

    @property
    def snm(self) -> int:
        return self.data["snm"]

    @property
    def dv(self) -> int:
        return self.data["dv"]

    @property
    def cct(self) -> int:
        return self.data["cct"]

    @property
    def bl(self) -> int:
        return self.data["bl"]

    @property
    def ac(self) -> int:
        return self.data["ac"]

    def __str__(self) -> str:
        s = "<CeilStatus power=%s, bright=%s, cct=%s, snm=%s, dv=%s, " \
            "bl=%s, ac=%, >" % \
            (self.power, self.bright, self.cct, self.snm, self.dv,
             self.bl, self.ac)
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

    def set_bright(self, level: int):
        """Set brightness level."""
        return self.send("set_bright", [level])

    def set_cct(self, level: int):
        """Set Correlated Color Temperature."""
        return self.send("set_cct", [level])

    def delay_off(self, seconds: int):
        """Set delay off seconds."""
        return self.send("delay_off", [seconds])

    def set_scene(self, num: int):
        """Set scene number."""
        return self.send("apply_fixed_scene", [num])

    def bl_on(self):
        """Smart Midnight Light On."""
        return self.send("enable_bl", [1])

    def bl_off(self):
        """Smart Midnight Light off."""
        return self.send("enable_bl", [0])

    def ac_on(self):
        """Auto CCT On."""
        return self.send("enable_ac", [1])

    def ac_off(self):
        """Auto CCT Off."""
        return self.send("enable_ac", [0])

    def status(self) -> CeilStatus:
        """Retrieve properties."""
        properties = ['power', 'bright', 'cct', 'snm', 'dv', 'bl', 'ac', ]
        values = self.send(
            "get_prop",
            properties
        )
        return CeilStatus(dict(zip(properties, values)))
