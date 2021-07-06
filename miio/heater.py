import enum
import logging
from typing import Any, Dict, Optional

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_HEATER_ZA1 = "zhimi.heater.za1"
MODEL_HEATER_MA1 = "zhimi.elecheater.ma1"

AVAILABLE_PROPERTIES_COMMON = [
    "power",
    "target_temperature",
    "brightness",
    "buzzer",
    "child_lock",
    "temperature",
    "use_time",
]
AVAILABLE_PROPERTIES_ZA1 = ["poweroff_time", "relative_humidity"]
AVAILABLE_PROPERTIES_MA1 = ["poweroff_level", "poweroff_value"]

SUPPORTED_MODELS: Dict[str, Dict[str, Any]] = {
    MODEL_HEATER_ZA1: {
        "available_properties": AVAILABLE_PROPERTIES_COMMON + AVAILABLE_PROPERTIES_ZA1,
        "temperature_range": (16, 32),
        "delay_off_range": (0, 9 * 3600),
    },
    MODEL_HEATER_MA1: {
        "available_properties": AVAILABLE_PROPERTIES_COMMON + AVAILABLE_PROPERTIES_MA1,
        "temperature_range": (20, 32),
        "delay_off_range": (0, 5 * 3600),
    },
}


class HeaterException(DeviceException):
    pass


class Brightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class HeaterStatus(DeviceStatus):
    """Container for status reports from the Smartmi Zhimi Heater."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a Heater (zhimi.heater.za1):

        {'power': 'off', 'target_temperature': 24, 'brightness': 1,
        'buzzer': 'on', 'child_lock': 'off', 'temperature': 22.3,
        'use_time': 43117, 'poweroff_time': 0, 'relative_humidity': 34}
        """
        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return self.power == "on"

    @property
    def humidity(self) -> Optional[int]:
        """Current humidity."""
        if (
            "relative_humidity" in self.data
            and self.data["relative_humidity"] is not None
        ):
            return self.data["relative_humidity"]

        return None

    @property
    def temperature(self) -> float:
        """Current temperature."""
        return self.data["temperature"]

    @property
    def target_temperature(self) -> int:
        """Target temperature."""
        return self.data["target_temperature"]

    @property
    def brightness(self) -> Brightness:
        """Display brightness."""
        return Brightness(self.data["brightness"])

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"] in ["on", 1, 2]

    @property
    def child_lock(self) -> bool:
        """True if child lock is on."""
        return self.data["child_lock"] == "on"

    @property
    def use_time(self) -> int:
        """How long the device has been active in seconds."""
        return self.data["use_time"]

    @property
    def delay_off_countdown(self) -> Optional[int]:
        """Countdown until turning off in seconds."""
        if "poweroff_time" in self.data and self.data["poweroff_time"] is not None:
            return self.data["poweroff_time"]

        if "poweroff_level" in self.data and self.data["poweroff_level"] is not None:
            return self.data["poweroff_level"]

        return None


class Heater(Device):
    """Main class representing the Smartmi Zhimi Heater."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_HEATER_ZA1,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in SUPPORTED_MODELS:
            self.model = model
        else:
            self.model = MODEL_HEATER_ZA1

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Target temperature: {result.target_temperature} °C\n"
            "Temperature: {result.temperature} °C\n"
            "Humidity: {result.humidity} %\n"
            "Display brightness: {result.brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Power-off time: {result.delay_off_countdown}\n",
        )
    )
    def status(self) -> HeaterStatus:
        """Retrieve properties."""
        properties = SUPPORTED_MODELS[self.model]["available_properties"]

        # A single request is limited to 16 properties. Therefore the
        # properties are divided into multiple requests
        _props_per_request = 15

        # The MA1, ZA1 is limited to a single property per request
        if self.model in [MODEL_HEATER_MA1, MODEL_HEATER_ZA1]:
            _props_per_request = 1

        values = self.get_properties(properties, max_properties=_props_per_request)

        return HeaterStatus(dict(zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("temperature", type=int),
        default_output=format_output("Setting target temperature to {temperature}"),
    )
    def set_target_temperature(self, temperature: int):
        """Set target temperature."""
        min_temp: int
        max_temp: int
        min_temp, max_temp = SUPPORTED_MODELS[self.model]["temperature_range"]
        if not min_temp <= temperature <= max_temp:
            raise HeaterException("Invalid target temperature: %s" % temperature)

        return self.send("set_target_temperature", [temperature])

    @command(
        click.argument("brightness", type=EnumType(Brightness)),
        default_output=format_output("Setting display brightness to {brightness}"),
    )
    def set_brightness(self, brightness: Brightness):
        """Set display brightness."""
        return self.send("set_brightness", [brightness.value])

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
        click.argument("seconds", type=int),
        default_output=format_output("Setting delayed turn off to {seconds} seconds"),
    )
    def delay_off(self, seconds: int):
        """Set delay off seconds."""
        min_delay: int
        max_delay: int
        min_delay, max_delay = SUPPORTED_MODELS[self.model]["delay_off_range"]
        if not min_delay <= seconds <= max_delay:
            raise HeaterException("Invalid delay time: %s" % seconds)

        if self.model == MODEL_HEATER_ZA1:
            return self.send("set_poweroff_time", [seconds])
        elif self.model == MODEL_HEATER_MA1:
            return self.send("set_poweroff_level", [seconds // 3600])

        return None
