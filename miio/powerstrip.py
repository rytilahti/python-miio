import logging
import enum
from typing import Dict, Any, Optional
from collections import defaultdict
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class PowerStripException(DeviceException):
    pass


class PowerMode(enum.Enum):
    Eco = 'green'
    Normal = 'normal'


class PowerStripStatus:
    """Container for status reports from the power strip."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Supported device models: qmi.powerstrip.v1, zimi.powerstrip.v2

        Response of a Power Strip 2 (zimi.powerstrip.v2):
        {'power','on', 'temperature': 48.7, 'current': 0.05, 'mode': None,
         'power_consume_rate': 4.09, 'wifi_led': 'on', 'power_price': 49}
        """
        self.data = data

    @property
    def power(self) -> str:
        """Current power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """True if the device is turned on."""
        return self.power == "on"

    @property
    def temperature(self) -> float:
        """Current temperature."""
        return self.data["temperature"]

    @property
    def current(self) -> Optional[float]:
        """Current, if available. Meaning and voltage reference unknown."""
        if self.data["current"] is not None:
            return self.data["current"]
        return None

    @property
    def load_power(self) -> Optional[float]:
        """Current power load, if available."""
        if self.data["power_consume_rate"] is not None:
            return self.data["power_consume_rate"]
        return None

    @property
    def mode(self) -> Optional[PowerMode]:
        """Current operation mode, can be either green or normal."""
        if self.data["mode"] is not None:
            return PowerMode(self.data["mode"])
        return None

    @property
    def wifi_led(self) -> bool:
        """True if the wifi led is turned on."""
        return self.data["wifi_led"] == "on"

    @property
    def power_price(self) -> Optional[int]:
        """The stored power price, if available."""
        if self.data["power_price"] is not None:
            return self.data["power_price"]
        return None

    def __repr__(self) -> str:
        s = "<PowerStripStatus power=%s, " \
            "temperature=%s, " \
            "load_power=%s, " \
            "current=%s, " \
            "mode=%s, " \
            "wifi_led=%s, " \
            "power_price=%s>" % \
            (self.power,
             self.temperature,
             self.load_power,
             self.current,
             self.mode,
             self.wifi_led,
             self.power_price)
        return s


class PowerStrip(Device):
    """Main class representing the smart power strip."""

    def status(self) -> PowerStripStatus:
        """Retrieve properties."""
        properties = ['power', 'temperature', 'current', 'mode',
                      'power_consume_rate', 'wifi_led', 'power_price', ]
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

        return PowerStripStatus(
            defaultdict(lambda: None, zip(properties, values)))

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def set_power_mode(self, mode: PowerMode):
        """Set the power mode."""

        # green, normal
        return self.send("set_power_mode", [mode.value])

    def set_wifi_led(self, led: bool):
        """Set the wifi led on/off."""
        if led:
            return self.send("set_wifi_led", ["on"])
        else:
            return self.send("set_wifi_led", ["off"])

    def set_power_price(self, price: int):
        """Set the power price."""
        if price < 0 or price > 999:
            raise PowerStripException("Invalid power price: %s" % price)

        return self.send("set_power_price", [price])
