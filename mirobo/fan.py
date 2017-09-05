import logging
from .device import Device
from typing import Any, Dict, Optional
import enum

_LOGGER = logging.getLogger(__name__)


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class MoveDirection(enum.Enum):
    Left = 'left'
    Right = 'right'


class FanStatus:
    """Container for status reports from the Xiaomi Smart Fan."""

    def __init__(self, data: Dict[str, Any]) -> None:
        # ['temp_dec', 'humidity', 'angle', 'speed', 'poweroff_time', 'power',
        # 'ac_power', 'battery', 'angle_enable', 'speed_level',
        # 'natural_level', 'child_lock', 'buzzer', 'led_b', 'led']
        #
        # [232, 46, 30, 298, 0, 'on', 'off', 98, 'off', 1, 0, 'off', 'on',
        # 1, 'on']
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def humidity(self) -> int:
        return self.data["humidity"]

    @property
    def temperature(self) -> Optional[float]:
        if self.data["temp_dec"] is not None:
            return self.data["temp_dec"] / 10.0
        return None

    @property
    def led(self) -> bool:
        return self.data["led"] == "on"

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        if self.data["led_b"] is not None:
            return LedBrightness(self.data["led_b"])
        return None

    @property
    def buzzer(self) -> bool:
        return self.data["buzzer"] == "on"

    @property
    def child_lock(self) -> bool:
        return self.data["child_lock"] == "on"

    @property
    def natural_level(self) -> int:
        return self.data["natural_level"]

    @property
    def speed_level(self) -> int:
        return self.data["speed_level"]

    @property
    def oscillate(self) -> bool:
        return self.data["angle_enable"] == "on"

    @property
    def battery(self) -> int:
        return self.data["battery"]

    @property
    def ac_power(self) -> bool:
        return self.data["ac_power"] == "on"

    @property
    def poweroff_time(self) -> int:
        return self.data["poweroff_time"]

    @property
    def speed(self) -> int:
        return self.data["speed"]

    @property
    def angle(self) -> int:
        return self.data["angle"]

    def __str__(self) -> str:
        s = "<FanStatus power=%s, temperature=%s, humidity=%s, led=%s, " \
            "led_brightness=%s buzzer=%s, child_lock=%s, natural_level=%s, " \
            "speed_level=%s, oscillate=%s, battery=%s, ac_power=%s, " \
            "poweroff_time=%s, speed=%s, angle=%s" % \
            (self.power, self.temperature, self.humidity, self.led,
             self.led_brightness, self.buzzer, self.child_lock,
             self.natural_level, self.speed_level, self.oscillate,
             self.battery, self.ac_power, self.poweroff_time,
             self.speed_level, self.angle)
        return s


class Fan(Device):
    """Main class representing the Xiaomi Smart Fan."""

    def status(self):
        """Retrieve properties."""
        properties = ['temp_dec', 'humidity', 'angle', 'speed',
                      'poweroff_time', 'power', 'ac_power', 'battery',
                      'angle_enable', 'speed_level', 'natural_level',
                      'child_lock', 'buzzer', 'led_b', 'led']

        values = self.send(
            "get_prop",
            properties
        )

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.error(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return FanStatus(dict(zip(properties, values)))

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def set_natural_level(self, level: int):
        """Set natural level."""
        level = max(0, min(level, 100))
        return self.send("set_natural_level", [level])  # 0...100

    def set_speed_level(self, level: int):
        """Set speed level."""
        level = max(0, min(level, 100))
        return self.send("set_speed_level", [level])  # 0...100

    def set_direction(self, direction: MoveDirection):
        """Set move direction."""
        return self.send("set_move", [direction.value])

    def fan_set_angle(self, angle: int):
        """Set angle."""
        return self.send("set_angle", [angle])

    def oscillate_on(self):
        """Enable oscillate."""
        return self.send("set_angle_enable", ["on"])

    def oscillate_off(self):
        """Disable oscillate."""
        return self.send("set_angle_enable", ["off"])

    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.send("set_led_b", [brightness.value])

    def led_on(self):
        """Turn led on."""
        return self.send("set_led", ["on"])

    def led_off(self):
        """Turn led off."""
        return self.send("set_led", ["off"])

    def buzzer_on(self):
        """Enable buzzer."""
        return self.send("set_buzzer", ["on"])

    def buzzer_off(self):
        """Disable buzzer."""
        return self.send("set_buzzer", ["off"])
