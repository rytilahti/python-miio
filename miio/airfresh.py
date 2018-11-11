import enum
import logging
from collections import defaultdict
from typing import Any, Dict, Optional

import click

from .click_common import command, format_output, EnumType
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class AirFreshException(DeviceException):
    pass


class OperationMode(enum.Enum):
    # Supported modes of the Air Fresh VA2 (zhimi.airfresh.va2)
    Auto = 'auto'
    Silent = 'silent'
    Interval = 'interval'
    Low = 'low'
    Middle = 'middle'
    Strong = 'strong'


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class AirFreshStatus:
    """Container for status reports from the air fresh."""

    def __init__(self, data: Dict[str, Any]) -> None:
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
    def co2(self) -> int:
        """Carbon dioxide."""
        return self.data["co2"]

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
        if self.data["led_level"] is not None:
            try:
                return LedBrightness(self.data["led_level"])
            except ValueError:
                _LOGGER.error("Unsupported LED brightness discarded: %s", self.data["led_level"])
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

    def __repr__(self) -> str:
        s = "<AirFreshStatus power=%s, " \
            "aqi=%s, " \
            "average_aqi=%s, " \
            "temperature=%s, " \
            "humidity=%s%%, " \
            "co2=%s, " \
            "mode=%s, " \
            "led=%s, " \
            "led_brightness=%s, " \
            "buzzer=%s, " \
            "child_lock=%s, " \
            "filter_life_remaining=%s, " \
            "filter_hours_used=%s, " \
            "use_time=%s, " \
            "motor_speed=%s, " \
            "extra_features=%s>" % \
            (self.power,
             self.aqi,
             self.average_aqi,
             self.temperature,
             self.humidity,
             self.co2,
             self.mode,
             self.led,
             self.led_brightness,
             self.buzzer,
             self.child_lock,
             self.filter_life_remaining,
             self.filter_hours_used,
             self.use_time,
             self.motor_speed,
             self.extra_features)
        return s

    def __json__(self):
        return self.data


class AirFresh(Device):
    """Main class representing the air fresh."""

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "AQI: {result.aqi} μg/m³\n"
            "Average AQI: {result.average_aqi} μg/m³\n"
            "Temperature: {result.temperature} °C\n"
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
            "Motor speed: {result.motor_speed} rpm\n"
        )
    )
    def status(self) -> AirFreshStatus:
        """Retrieve properties."""

        properties = ["power", "temp_dec", "aqi", "average_aqi", "co2", "buzzer", "child_lock",
                      "humidity", "led_level",  "mode", "motor1_speed", "use_time",
                      "ntcT", "app_extra", "f1_hour_used", "filter_life", "f_hour",
                      "favorite_level", "led"]

        # A single request is limited to 16 properties. Therefore the
        # properties are divided into multiple requests
        _props = properties.copy()
        values = []
        while _props:
            values.extend(self.send("get_prop", _props[:15]))
            _props[:] = _props[15:]

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return AirFreshStatus(
            defaultdict(lambda: None, zip(properties, values)))

    @command(
        default_output=format_output("Powering on"),
    )
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(
        default_output=format_output("Powering off"),
    )
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("mode", type=EnumType(OperationMode, False)),
        default_output=format_output("Setting mode to '{mode.value}'")
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.send("set_mode", [mode.value])

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED"
            if led else "Turning off LED"
        )
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        if led:
            return self.send("set_led", ['on'])
        else:
            return self.send("set_led", ['off'])

    @command(
        click.argument("brightness", type=EnumType(LedBrightness, False)),
        default_output=format_output(
            "Setting LED brightness to {brightness}")
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.send("set_led_level", [brightness.value])

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer"
            if buzzer else "Turning off buzzer"
        )
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
            lambda lock: "Turning on child lock"
            if lock else "Turning off child lock"
        )
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        if lock:
            return self.send("set_child_lock", ["on"])
        else:
            return self.send("set_child_lock", ["off"])

    @command(
        click.argument("value", type=int),
        default_output=format_output("Setting extra to {value}")
    )
    def set_extra_features(self, value: int):
        """Storage register to enable extra features at the app."""
        if value < 0:
            raise AirFreshException("Invalid app extra value: %s" % value)

        return self.send("set_app_extra", [value])

    @command(
        default_output=format_output("Resetting filter")
    )
    def reset_filter(self):
        """Resets filter hours used and remaining life."""
        return self.send('reset_filter1')
