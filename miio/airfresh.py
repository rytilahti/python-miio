import enum
import logging
from collections import defaultdict
from typing import Any, Dict, Optional

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_AIRFRESH_VA2 = "zhimi.airfresh.va2"
MODEL_AIRFRESH_VA4 = "zhimi.airfresh.va4"

AVAILABLE_PROPERTIES_COMMON = [
    "power",
    "temp_dec",
    "aqi",
    "average_aqi",
    "co2",
    "buzzer",
    "child_lock",
    "humidity",
    "led_level",
    "mode",
    "motor1_speed",
    "use_time",
    "ntcT",
    "app_extra",
    "f1_hour_used",
    "filter_life",
    "f_hour",
    "favorite_level",
    "led",
]

AVAILABLE_PROPERTIES = {
    MODEL_AIRFRESH_VA2: AVAILABLE_PROPERTIES_COMMON,
    MODEL_AIRFRESH_VA4: AVAILABLE_PROPERTIES_COMMON + ["ptc_state"],
}


class AirFreshException(DeviceException):
    pass


class OperationMode(enum.Enum):
    # Supported modes of the Air Fresh VA2 (zhimi.airfresh.va2)
    Auto = "auto"
    Silent = "silent"
    Interval = "interval"
    Low = "low"
    Middle = "middle"
    Strong = "strong"


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class AirFreshStatus(DeviceStatus):
    """Container for status reports from the air fresh."""

    def __init__(self, data: Dict[str, Any], model: str) -> None:
        """
        Response of a Air Fresh VA4 (zhimi.airfresh.va4):

        {
            'power': 'on',
            'temp_dec': 28.5,
            'aqi': 1,
            'average_aqi': 1,
            'co2': 1081,
            'buzzer': 'off',
            'child_lock': 'off',
            'humidity': 40,
            'led_level': 1,
            'mode': 'silent',
            'motor1_speed': 400,
            'use_time': 510000,
            'ntcT': 33.53,
            'app_extra': None,
            'f1_hour_used': 141,
            'filter_life': None,
            'f_hour': None,
            'favorite_level': None,
            'led': None,
            'ptc_state': 'off',
        }
        """

        self.data = data
        self.model = model

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
    def co2(self) -> int:
        """Carbon dioxide."""
        return self.data["co2"]

    @property
    def humidity(self) -> int:
        """Current humidity."""
        return self.data["humidity"]

    @property
    def ptc(self) -> Optional[bool]:
        """Return True if PTC is on."""
        if self.data["ptc_state"] is not None:
            return self.data["ptc_state"] == "on"

        return None

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature, if available."""
        if self.data["temp_dec"] is not None:
            if self.model == MODEL_AIRFRESH_VA4:
                return self.data["temp_dec"]
            else:
                return self.data["temp_dec"] / 10.0

        return None

    @property
    def ntc_temperature(self) -> Optional[float]:
        """Current ntc temperature, if available."""
        if self.data["ntcT"] is not None:
            return self.data["ntcT"]

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
        if self.data["led_level"] is not None:
            try:
                return LedBrightness(self.data["led_level"])
            except ValueError:
                _LOGGER.error(
                    "Unsupported LED brightness discarded: %s", self.data["led_level"]
                )
                return None

        return None

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
    def filter_life_remaining(self) -> int:
        """Time until the filter should be changed."""
        return self.data["filter_life"]

    @property
    def filter_hours_used(self) -> int:
        """How long the filter has been in use."""
        return self.data["f1_hour_used"]

    @property
    def use_time(self) -> int:
        """How long the device has been active in seconds."""
        return self.data["use_time"]

    @property
    def motor_speed(self) -> int:
        """Speed of the motor."""
        return self.data["motor1_speed"]

    @property
    def extra_features(self) -> Optional[int]:
        return self.data["app_extra"]


class AirFresh(Device):
    """Main class representing the air fresh."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_AIRFRESH_VA2,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_AIRFRESH_VA2

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Heater (PTC): {result.ptc}\n"
            "AQI: {result.aqi} μg/m³\n"
            "Average AQI: {result.average_aqi} μg/m³\n"
            "Temperature: {result.temperature} °C\n"
            "NTC temperature: {result.ntc_temperature} °C\n"
            "Humidity: {result.humidity} %\n"
            "CO2: {result.co2} %\n"
            "Mode: {result.mode.value}\n"
            "LED: {result.led}\n"
            "LED brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Filter life remaining: {result.filter_life_remaining} %\n"
            "Filter hours used: {result.filter_hours_used}\n"
            "Use time: {result.use_time} s\n"
            "Motor speed: {result.motor_speed} rpm\n",
        )
    )
    def status(self) -> AirFreshStatus:
        """Retrieve properties."""

        properties = AVAILABLE_PROPERTIES[self.model]
        values = self.get_properties(properties, max_properties=15)

        return AirFreshStatus(
            defaultdict(lambda: None, zip(properties, values)), self.model
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
        return self.send("set_mode", [mode.value])

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        if led:
            return self.send("set_led", ["on"])
        else:
            return self.send("set_led", ["off"])

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.send("set_led_level", [brightness.value])

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
        click.argument("value", type=int),
        default_output=format_output("Setting extra to {value}"),
    )
    def set_extra_features(self, value: int):
        """Storage register to enable extra features at the app."""
        if value < 0:
            raise AirFreshException("Invalid app extra value: %s" % value)

        return self.send("set_app_extra", [value])

    @command(default_output=format_output("Resetting filter"))
    def reset_filter(self):
        """Resets filter hours used and remaining life."""
        return self.send("reset_filter1")

    @command(
        click.argument("ptc", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on PTC" if buzzer else "Turning off PTC"
        ),
    )
    def set_ptc(self, ptc: bool):
        """Set PTC on/off."""
        if ptc:
            return self.send("set_ptc_state", ["on"])
        else:
            return self.send("set_ptc_state", ["off"])


class AirFreshVA4(AirFresh):
    """Main class representing the air fresh va4."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(
            ip, token, start_id, debug, lazy_discover, model=MODEL_AIRFRESH_VA4
        )
