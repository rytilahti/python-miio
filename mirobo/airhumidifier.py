import logging
import enum
from typing import Any, Dict, Optional
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)


class OperationMode(enum.Enum):
    Silent = 'silent'
    Medium = 'medium'
    High = 'high'


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class AirHumidifier(Device):
    """Main class representing the air humidifier."""

    def status(self):
        """Retrieve properties."""

        properties = ['power', 'mode', 'temp_dec', 'humidity', 'buzzer',
                      'led_b', ]

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

        return AirHumidifierStatus(
            defaultdict(lambda: None, zip(properties, values)))

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.send("set_mode", [mode.value])

    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.send("set_led_b", [brightness.value])

    def set_led(self, led: bool):
        """Turn led on/off."""
        if led:
            return self.send("set_led", ['on'])
        else:
            return self.send("set_led", ['off'])

    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if buzzer:
            return self.send("set_buzzer", ["on"])
        else:
            return self.send("set_buzzer", ["off"])


class AirHumidifierStatus:
    """Container for status reports from the air humidifier."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def mode(self) -> OperationMode:
        return OperationMode(self.data["mode"])

    @property
    def temperature(self) -> Optional[float]:
        if self.data["temp_dec"] is not None:
            return self.data["temp_dec"] / 10.0
        return None

    @property
    def humidity(self) -> int:
        return self.data["humidity"]

    @property
    def buzzer(self) -> bool:
        return self.data["buzzer"] == "on"

    @property
    def led(self) -> bool:
        return self.data["led"] == "on"

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        if self.data["led_b"] is not None:
            return LedBrightness(self.data["led_b"])
        return None

    def __str__(self) -> str:
        s = "<AirHumidiferStatus power=%s, mode=%s, temperature=%s, " \
            "humidity=%s%%, led=%s, led_brightness=%s, buzzer=%s>" % \
            (self.power, self.mode, self.temperature,
             self.humidity, self.led, self.led_brightness, self.buzzer)
        return s
