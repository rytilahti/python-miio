import logging
import enum
from typing import Any, Dict, Optional
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)


class AirPurifierException(Exception):
    pass


class OperationMode(enum.Enum):
    Auto = 'auto'
    Silent = 'silent'
    Favorite = 'favorite'
    Idle = 'idle'


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class AirPurifierStatus:
    """Container for status reports from the air purifier."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Air Purifier Pro (zhimi.airpurifier.v6):

        {'power': 'off', 'aqi': 7, 'average_aqi': 18, 'humidity': 45,
         'temp_dec': 234, 'mode': 'auto', 'favorite_level': 17,
         'filter1_life': 52, 'f1_hour_used': 1664, 'use_time': 2642700,
         'motor1_speed': 0, 'motor2_speed': 800, 'purify_volume': 62180,
         'f1_hour': 3500, 'led': 'on', 'led_b': None, 'bright': 83,
         'buzzer': None, 'child_lock': 'off', 'volume': 50}

        Response of a Air Purifier 2 (zhimi.airpurifier.m1):

        {'power': 'on, 'aqi': 10, 'average_aqi': 8, 'humidity': 62,
         'temp_dec': 186, 'mode': 'auto', 'favorite_level': 10,
        'filter1_life': 80, 'f1_hour_used': 682, 'use_time': 2457000,
        'motor1_speed': 354, 'motor2_speed': None, 'purify_volume': 25262,
        'f1_hour': 3500, 'led': 'off', 'led_b': 2, 'bright': None,
        'buzzer': 'off', 'child_lock': 'off', 'volume': None}

        A request is limited to 16 properties.
        """

        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.power == "on"

    @property
    def aqi(self) -> int:
        """Air quality index."""
        return self.data["aqi"]

    @property
    def average_aqi(self) -> int:
        """Average of the air quality index."""
        return self.data["average_aqi"]

    @property
    def humidity(self) -> int:
        """Current humidity."""
        return self.data["humidity"]

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature, if available."""
        if self.data["temp_dec"] is not None:
            return self.data["temp_dec"] / 10.0
        return None

    @property
    def mode(self) -> OperationMode:
        """Current operation mode."""
        return OperationMode(self.data["mode"])

    @property
    def led(self) -> bool:
        """Return True if LED is on."""
        return self.data["led"] == "on"

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        """Brightness of the LED."""
        if self.data["led_b"] is not None:
            return LedBrightness(self.data["led_b"])

        return None

    @property
    def illuminance(self) -> Optional[int]:
        """Environment illuminance level in lux [0-200].
        Sensor value is updated only when device is turned on."""
        return self.data["bright"]

    @property
    def buzzer(self) -> Optional[bool]:
        """Return True if buzzer is on."""
        if self.data["buzzer"] is not None:
            return self.data["buzzer"] == "on"

        return None

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"] == "on"

    @property
    def favorite_level(self) -> int:
        """Return favorite level, which is used if the mode is ``favorite``."""
        # Favorite level used when the mode is `favorite`.
        return self.data["favorite_level"]

    @property
    def filter_life_remaining(self) -> int:
        """Time until the filter should be changed."""
        return self.data["filter1_life"]

    @property
    def filter_hours_used(self) -> int:
        """How long the filter has been in use."""
        return self.data["f1_hour_used"]

    @property
    def use_time(self) -> int:
        """How long the device has been active in seconds."""
        return self.data["use_time"]

    @property
    def purify_volume(self) -> int:
        """The volume of purified air in cubic meter."""
        return self.data["purify_volume"]

    @property
    def motor_speed(self) -> int:
        """Speed of the motor."""
        return self.data["motor1_speed"]

    @property
    def motor2_speed(self) -> Optional[int]:
        """Speed of the 2nd motor."""
        return self.data["motor2_speed"]

    @property
    def volume(self) -> Optional[int]:
        """Volume of sound notifications [0-100]."""
        return self.data["volume"]

    def __repr__(self) -> str:
        s = "<AirPurifierStatus power=%s, " \
            "aqi=%s, " \
            "average_aqi=%s, " \
            "temperature=%s, " \
            "humidity=%s%%, " \
            "mode=%s, " \
            "led=%s, " \
            "led_brightness=%s, " \
            "illuminance=%s, " \
            "buzzer=%s, " \
            "child_lock=%s, " \
            "favorite_level=%s, " \
            "filter_life_remaining=%s, " \
            "filter_hours_used=%s, " \
            "use_time=%s, " \
            "purify_volume=%s, " \
            "motor_speed=%s, " \
            "motor2_speed=%s, " \
            "volume=%s>" % \
            (self.power,
             self.aqi,
             self.average_aqi,
             self.temperature,
             self.humidity,
             self.mode,
             self.led,
             self.led_brightness,
             self.illuminance,
             self.buzzer,
             self.child_lock,
             self.favorite_level,
             self.filter_life_remaining,
             self.filter_hours_used,
             self.use_time,
             self.purify_volume,
             self.motor_speed,
             self.motor2_speed,
             self.volume)
        return s


class AirPurifier(Device):
    """Main class representing the air purifier."""

    def status(self) -> AirPurifierStatus:
        """Retrieve properties."""

        properties = ['power', 'aqi', 'average_aqi', 'humidity', 'temp_dec',
                      'mode', 'favorite_level', 'filter1_life', 'f1_hour_used',
                      'use_time', 'motor1_speed', 'motor2_speed',
                      'purify_volume',
                      # Second request
                      'f1_hour', 'led', 'led_b', 'bright', 'buzzer',
                      'child_lock', 'volume', ]

        # A single request is limited to 16 properties. Therefore the
        # properties are divided in two groups here. The second group contains
        # some infrequent and independent updated properties.
        values = self.send(
            "get_prop",
            properties[0:13]
        )

        values.extend(self.send(
            "get_prop",
            properties[13:]
        ))

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return AirPurifierStatus(
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

    def set_favorite_level(self, level: int):
        """Set favorite level."""
        if level < 0 or level > 16:
            raise AirPurifierException("Invalid favorite level: %s" % level)

        # Set the favorite level used when the mode is `favorite`,
        # should be  between 0 and 16.
        return self.send("set_level_favorite", [level])  # 0 ... 16

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

    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        if lock:
            return self.send("set_child_lock", ["on"])
        else:
            return self.send("set_child_lock", ["off"])

    def set_volume(self, volume: int):
        """Set volume of sound notifications [0-100]."""
        if volume < 0 or volume > 100:
            raise AirPurifierException("Invalid volume: %s" % volume)

        return self.send("set_volume", [volume])
