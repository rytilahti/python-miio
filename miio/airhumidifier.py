import enum
import logging
from collections import defaultdict
from typing import Any, Dict, Optional

from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class AirHumidifierException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Silent = 'silent'
    Medium = 'medium'
    High = 'high'
    Auto = 'auto'
    Strong = 'strong'


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class AirHumidifierStatus:
    """Container for status reports from the air humidifier."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Air Humidifier (zhimi.humidifier.v1):

        {'power': 'off', 'mode': 'high', 'temp_dec': 294,
         'humidity': 33, 'buzzer': 'on', 'led_b': 0,
         'child_lock': 'on', 'limit_hum': 40, 'trans_level': 85,
         'speed': None, 'depth': None, 'dry': None, 'use_time': 941100,
         'hw_version': 0, 'button_pressed': 'led'}
        """

        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """True if device is turned on."""
        return self.power == "on"

    @property
    def mode(self) -> OperationMode:
        """Operation mode. Can be either silent, medium or high."""
        return OperationMode(self.data["mode"])

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature, if available."""
        if self.data["temp_dec"] is not None:
            return self.data["temp_dec"] / 10.0
        return None

    @property
    def humidity(self) -> int:
        """Current humidity."""
        return self.data["humidity"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"] == "on"

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        """LED brightness if available."""
        if self.data["led_b"] is not None:
            return LedBrightness(self.data["led_b"])
        return None

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"] == "on"

    @property
    def target_humidity(self) -> int:
        """Target humiditiy. Can be either 30, 40, 50, 60, 70, 80 percent."""
        return self.data["limit_hum"]

    @property
    def trans_level(self) -> int:
        """
        The meaning of the property is unknown.

        The property is used to determine the strong mode is enabled on old firmware.
        """
        return self.data["trans_level"]

    @property
    def strong_mode_enabled(self) -> bool:
        if self.firmware_version_minor == 25:
            if self.trans_level == 90:
                return True

        elif self.firmware_version_minor > 25:
            return self.mode.value == "strong"

        return False

    @property
    def firmware_version(self) -> str:
        # FIXME: Retrieve fw_ver from miIO.info
        return '1.2.9_5033'

    @property
    def firmware_version_major(self) -> str:
        major, _ = self.firmware_version.rsplit('_', 1)
        return major

    @property
    def firmware_version_minor(self) -> int:
        _, minor = self.firmware_version.rsplit('_', 1)
        return int(minor)

    @property
    def speed(self) -> Optional[int]:
        """Current fan speed."""
        return self.data["speed"]

    @property
    def depth(self) -> Optional[int]:
        """The remaining amount of water in percent."""
        return self.data["depth"]

    @property
    def dry(self) -> Optional[bool]:
        """
        Dry mode: The amount of water is not enough to continue to work for about 8 hours.

        Return True if dry mode is on if available.
        """
        if self.data["dry"] is not None:
            return self.data["dry"] == "on"
        return None

    @property
    def use_time(self) -> Optional[int]:
        """How long the device has been active in seconds."""
        return self.data["use_time"]

    @property
    def hardware_version(self) -> Optional[str]:
        """The hardware version."""
        return self.data["hw_version"]

    @property
    def button_pressed(self) -> Optional[str]:
        """Last pressed button."""
        return self.data["button_pressed"]

    def __repr__(self) -> str:
        s = "<AirHumidiferStatus power=%s, " \
            "mode=%s, " \
            "temperature=%s, " \
            "humidity=%s%%, " \
            "led_brightness=%s, " \
            "buzzer=%s, " \
            "child_lock=%s, " \
            "target_humidity=%s%%, " \
            "trans_level=%s, " \
            "speed=%s, " \
            "depth=%s, " \
            "dry=%s, " \
            "use_time=%s, " \
            "hardware_version=%s, " \
            "button_pressed=%s, " \
            "strong_mode_enabled=%s, " \
            "firmware_version_major=%s, " \
            "firmware_version_minor=%s>" % \
            (self.power,
             self.mode,
             self.temperature,
             self.humidity,
             self.led_brightness,
             self.buzzer,
             self.child_lock,
             self.target_humidity,
             self.trans_level,
             self.speed,
             self.depth,
             self.dry,
             self.use_time,
             self.hardware_version,
             self.button_pressed,
             self.strong_mode_enabled,
             self.firmware_version_major,
             self.firmware_version_minor)
        return s


class AirHumidifier(Device):
    """Implementation of Xiaomi Mi Air Humidifier."""

    def status(self) -> AirHumidifierStatus:
        """Retrieve properties."""

        properties = ['power', 'mode', 'temp_dec', 'humidity', 'buzzer',
                      'led_b', 'child_lock', 'limit_hum', 'trans_level',
                      'speed', 'depth', 'dry', 'use_time', 'button_pressed',
                      'hw_version', ]

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

    def set_target_humidity(self, humidity: int):
        """Set the target humidity."""
        if humidity not in [30, 40, 50, 60, 70, 80]:
            raise AirHumidifierException(
                "Invalid target humidity: %s" % humidity)

        return self.send("set_limit_hum", [humidity])

    def set_dry(self, dry: bool):
        """Set dry mode on/off."""
        if dry:
            return self.send("set_dry", ["on"])
        else:
            return self.send("set_dry", ["off"])
