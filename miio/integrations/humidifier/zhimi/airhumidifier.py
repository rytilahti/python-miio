import enum
import logging
from collections import defaultdict
from typing import Any, Dict, Optional

import click

from miio import Device, DeviceError, DeviceException, DeviceInfo, DeviceStatus
from miio.click_common import EnumType, command, format_output

_LOGGER = logging.getLogger(__name__)

MODEL_HUMIDIFIER_V1 = "zhimi.humidifier.v1"
MODEL_HUMIDIFIER_CA1 = "zhimi.humidifier.ca1"
MODEL_HUMIDIFIER_CB1 = "zhimi.humidifier.cb1"
MODEL_HUMIDIFIER_CB2 = "zhimi.humidifier.cb2"

SUPPORTED_MODELS = [
    MODEL_HUMIDIFIER_V1,
    MODEL_HUMIDIFIER_CA1,
    MODEL_HUMIDIFIER_CB1,
    MODEL_HUMIDIFIER_CB2,
]

AVAILABLE_PROPERTIES_COMMON = [
    "power",
    "mode",
    "humidity",
    "buzzer",
    "led_b",
    "child_lock",
    "limit_hum",
    "use_time",
    "hw_version",
]

AVAILABLE_PROPERTIES = {
    MODEL_HUMIDIFIER_V1: AVAILABLE_PROPERTIES_COMMON
    + ["temp_dec", "trans_level", "button_pressed"],
    MODEL_HUMIDIFIER_CA1: AVAILABLE_PROPERTIES_COMMON
    + ["temp_dec", "speed", "depth", "dry"],
    MODEL_HUMIDIFIER_CB1: AVAILABLE_PROPERTIES_COMMON
    + ["temperature", "speed", "depth", "dry"],
    MODEL_HUMIDIFIER_CB2: AVAILABLE_PROPERTIES_COMMON
    + ["temperature", "speed", "depth", "dry"],
}


class AirHumidifierException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Silent = "silent"
    Medium = "medium"
    High = "high"
    Auto = "auto"
    Strong = "strong"


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class AirHumidifierStatus(DeviceStatus):
    """Container for status reports from the air humidifier."""

    def __init__(self, data: Dict[str, Any], device_info: DeviceInfo) -> None:
        """Response of a Air Humidifier (zhimi.humidifier.v1):

        {'power': 'off', 'mode': 'high', 'temp_dec': 294,
         'humidity': 33, 'buzzer': 'on', 'led_b': 0,
         'child_lock': 'on', 'limit_hum': 40, 'trans_level': 85,
         'speed': None, 'depth': None, 'dry': None, 'use_time': 941100,
         'hw_version': 0, 'button_pressed': 'led'}
        """

        self.data = data
        self.device_info = device_info

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
        """Operation mode.

        Can be either silent, medium or high.
        """
        return OperationMode(self.data["mode"])

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature, if available."""
        if "temp_dec" in self.data and self.data["temp_dec"] is not None:
            return self.data["temp_dec"] / 10.0
        if "temperature" in self.data and self.data["temperature"] is not None:
            return self.data["temperature"]
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
        """Target humidity.

        Can be either 30, 40, 50, 60, 70, 80 percent.
        """
        return self.data["limit_hum"]

    @property
    def trans_level(self) -> Optional[int]:
        """The meaning of the property is unknown.

        The property is used to determine the strong mode is enabled on old firmware.
        """
        if "trans_level" in self.data and self.data["trans_level"] is not None:
            return self.data["trans_level"]
        return None

    @property
    def strong_mode_enabled(self) -> bool:
        if self.firmware_version_minor == 25:
            if self.trans_level == 90:
                return True

        elif self.firmware_version_minor > 25 or self.firmware_version_minor == 0:
            return self.mode.value == "strong"

        return False

    @property
    def firmware_version(self) -> str:
        """Returns the fw_ver of miIO.info.

        For example 1.2.9_5033.
        """
        if self.device_info.firmware_version is None:
            raise AirHumidifierException("Missing firmware information")

        return self.device_info.firmware_version

    @property
    def firmware_version_major(self) -> str:
        parts = self.firmware_version.rsplit("_", 1)
        return parts[0]

    @property
    def firmware_version_minor(self) -> int:
        parts = self.firmware_version.rsplit("_", 1)
        try:
            return int(parts[1])
        except IndexError:
            return 0

    @property
    def motor_speed(self) -> Optional[int]:
        """Current fan speed."""
        if "speed" in self.data and self.data["speed"] is not None:
            return self.data["speed"]
        return None

    @property
    def depth(self) -> Optional[int]:
        """Return raw value of depth."""
        _LOGGER.warning(
            "The 'depth' property is deprecated and will be removed in the future. Use 'water_level' and 'water_tank_detached' properties instead."
        )
        if "depth" in self.data:
            return self.data["depth"]
        return None

    @property
    def water_level(self) -> Optional[int]:
        """Return current water level in percent.

        If water tank is full, depth is 120. If water tank is overfilled, depth is 125.
        """
        depth = self.data.get("depth")
        if depth is None or depth > 125:
            return None

        if depth < 0:
            return 0

        return int(min(depth / 1.2, 100))

    @property
    def water_tank_detached(self) -> Optional[bool]:
        """True if the water tank is detached.

        If water tank is detached, depth is 127.
        """
        if self.data.get("depth") is not None:
            return self.data["depth"] == 127
        return None

    @property
    def dry(self) -> Optional[bool]:
        """Dry mode: The amount of water is not enough to continue to work for about 8
        hours.

        Return True if dry mode is on if available.
        """
        if "dry" in self.data and self.data["dry"] is not None:
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
        if "button_pressed" in self.data and self.data["button_pressed"] is not None:
            return self.data["button_pressed"]
        return None


class AirHumidifier(Device):
    """Implementation of Xiaomi Mi Air Humidifier."""

    _supported_models = SUPPORTED_MODELS

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "Temperature: {result.temperature} °C\n"
            "Humidity: {result.humidity} %\n"
            "LED brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Target humidity: {result.target_humidity} %\n"
            "Trans level: {result.trans_level}\n"
            "Speed: {result.motor_speed}\n"
            "Depth: {result.depth}\n"
            "Water Level: {result.water_level} %\n"
            "Water tank detached: {result.water_tank_detached}\n"
            "Dry: {result.dry}\n"
            "Use time: {result.use_time}\n"
            "Hardware version: {result.hardware_version}\n"
            "Button pressed: {result.button_pressed}\n",
        )
    )
    def status(self) -> AirHumidifierStatus:
        """Retrieve properties."""

        properties = AVAILABLE_PROPERTIES.get(
            self.model, AVAILABLE_PROPERTIES[MODEL_HUMIDIFIER_V1]
        )

        # A single request is limited to 16 properties. Therefore the
        # properties are divided into multiple requests
        _props_per_request = 15

        # The CA1, CB1 and CB2 are limited to a single property per request
        if self.model in [
            MODEL_HUMIDIFIER_CA1,
            MODEL_HUMIDIFIER_CB1,
            MODEL_HUMIDIFIER_CB2,
        ]:
            _props_per_request = 1

        values = self.get_properties(properties, max_properties=_props_per_request)

        return AirHumidifierStatus(
            defaultdict(lambda: None, zip(properties, values)), self.info()
        )

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        try:
            return self.send("set_mode", [mode.value])
        except DeviceError as error:
            # {'code': -6011, 'message': 'device_poweroff'}
            if error.code == -6011:
                self.on()
                return self.send("set_mode", [mode.value])
            raise

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        if self.model in [MODEL_HUMIDIFIER_CA1, MODEL_HUMIDIFIER_CB1]:
            return self.send("set_led_b", [str(brightness.value)])

        return self.send("set_led_b", [brightness.value])

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        if led:
            return self.set_led_brightness(LedBrightness.Bright)
        else:
            return self.set_led_brightness(LedBrightness.Off)

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if buzzer:
            return self.send("set_buzzer", ["on"])
        else:
            return self.send("set_buzzer", ["off"])

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        if lock:
            return self.send("set_child_lock", ["on"])
        else:
            return self.send("set_child_lock", ["off"])

    @command(
        click.argument("humidity", type=int),
        default_output=format_output("Setting target humidity to {humidity}"),
    )
    def set_target_humidity(self, humidity: int):
        """Set the target humidity."""
        if humidity not in [30, 40, 50, 60, 70, 80]:
            raise AirHumidifierException("Invalid target humidity: %s" % humidity)

        return self.send("set_limit_hum", [humidity])

    @command(
        click.argument("dry", type=bool),
        default_output=format_output(
            lambda dry: "Turning on dry mode" if dry else "Turning off dry mode"
        ),
    )
    def set_dry(self, dry: bool):
        """Set dry mode on/off."""
        if dry:
            return self.send("set_dry", ["on"])
        else:
            return self.send("set_dry", ["off"])
