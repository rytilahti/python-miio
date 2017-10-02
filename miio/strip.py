import logging
import enum
from typing import Dict, Any, Optional
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)


class PowerMode(enum.Enum):
    Eco = 'green'
    Normal = 'normal'


class StripStatus:
    """Container for status reports from the strip."""

    def __init__(self, data: Dict[str, Any]) -> None:
        # Device model: qmi.powerstrip.v1, zimi.powerstrip.v2
        #
        # {'power': 'on', 'temperature': 48.11,
        # 'current': 0.06, 'mode': 'green'}
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def temperature(self) -> float:
        return self.data["temperature"]

    @property
    def load_power(self) -> Optional[float]:
        if self.data["current"] is not None:
            # The constant of 110V is used intentionally. The current was
            # calculated with a wrong reference voltage already.
            return self.data["current"] * 110
        return None

    @property
    def mode(self) -> PowerMode:
        return PowerMode(self.data["mode"])

    def __str__(self) -> str:
        s = "<StripStatus power=%s, temperature=%s, " \
            "load_power=%s mode=%s>" % \
            (self.power,
             self.temperature,
             self.load_power,
             self.mode)
        return s


class Strip(Device):
    """Main class representing the smart strip."""

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def status(self):
        """Retrieve properties."""
        properties = ['power', 'temperature', 'current', 'mode']
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

        return StripStatus(
            defaultdict(lambda: None, zip(properties, values)))

    def set_power_mode(self, mode: PowerMode):
        """Set mode."""

        # green, normal
        return self.send("set_power_mode", [mode.value])
