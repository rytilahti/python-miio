import enum
import logging
from typing import Any, Dict, Optional

import click

from .airfilter_util import FilterType, FilterTypeUtil
from .click_common import EnumType, command, format_output
from .exceptions import DeviceException
from .miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)
_MAPPING = {
    # Air Purifier (siid=2)
    "power": {"siid": 2, "piid": 2},
    "fan_level": {"siid": 2, "piid": 4},
    "mode": {"siid": 2, "piid": 5},
    # Environment (siid=3)
    "humidity": {"siid": 3, "piid": 7},
    "temperature": {"siid": 3, "piid": 8},
    "aqi": {"siid": 3, "piid": 6},
    # Filter (siid=4)
    "filter_life_remaining": {"siid": 4, "piid": 3},
    "filter_hours_used": {"siid": 4, "piid": 5},
    # Alarm (siid=5)
    "buzzer": {"siid": 5, "piid": 1},
    "buzzer_volume": {"siid": 5, "piid": 2},
    # Indicator Light (siid=6)
    "led_brightness": {"siid": 6, "piid": 1},
    "led": {"siid": 6, "piid": 6},
    # Physical Control Locked (siid=7)
    "child_lock": {"siid": 7, "piid": 1},
    # Motor Speed (siid=10)
    "favorite_level": {"siid": 10, "piid": 10},
    "favorite_rpm": {"siid": 10, "piid": 7},
    "motor_speed": {"siid": 10, "piid": 8},
    # Use time (siid=12)
    "use_time": {"siid": 12, "piid": 1},
    # AQI (siid=13)
    "purify_volume": {"siid": 13, "piid": 1},
    "average_aqi": {"siid": 13, "piid": 2},
    # RFID (siid=14)
    "filter_rfid_tag": {"siid": 14, "piid": 1},
    "filter_rfid_product_id": {"siid": 14, "piid": 3},
    # Other (siid=15)
    "app_extra": {"siid": 15, "piid": 1},
}

# https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-purifier:0000A007:zhimi-mb4:2
_MODEL_AIRPURIFIER_MB4 = {
    # Air Purifier
    "power": {"siid": 2, "piid": 1},
    "mode": {"siid": 2, "piid": 4},
    # Environment
    "aqi": {"siid": 3, "piid": 4},
    # Filter
    "filter_life_remaining": {"siid": 4, "piid": 1},
    "filter_hours_used": {"siid": 4, "piid": 3},
    # Alarm
    "buzzer": {"siid": 6, "piid": 1},
    # Screen
    "led_brightness_level": {"siid": 7, "piid": 2},
    # Physical Control Locked
    "child_lock": {"siid": 8, "piid": 1},
    # custom-service
    "motor_speed": {"siid": 9, "piid": 1},
    "favorite_rpm": {"siid": 9, "piid": 3},
}


class AirPurifierMiotException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Unknown = -1
    Auto = 0
    Silent = 1
    Favorite = 2
    Fan = 3


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class BasicAirPurifierMiotStatus(DeviceStatus):
    """Container for status reports from the air purifier."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.filter_type_util = FilterTypeUtil()
        self.data = data

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.data["power"]

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.is_on else "off"

    @property
    def aqi(self) -> int:
        """Air quality index."""
        return self.data["aqi"]

    @property
    def mode(self) -> OperationMode:
        """Current operation mode."""
        mode = self.data["mode"]
        try:
            return OperationMode(mode)
        except ValueError:
            _LOGGER.debug("Unknown mode: %s", mode)
            return OperationMode.Unknown

    @property
    def buzzer(self) -> Optional[bool]:
        """Return True if buzzer is on."""
        if self.data["buzzer"] is not None:
            return self.data["buzzer"]

        return None

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"]

    @property
    def filter_life_remaining(self) -> int:
        """Time until the filter should be changed."""
        return self.data["filter_life_remaining"]

    @property
    def filter_hours_used(self) -> int:
        """How long the filter has been in use."""
        return self.data["filter_hours_used"]

    @property
    def motor_speed(self) -> int:
        """Speed of the motor."""
        return self.data["motor_speed"]

    @property
    def favorite_rpm(self) -> Optional[int]:
        """Return favorite rpm level."""
        return self.data.get("favorite_rpm")


class AirPurifierMiotStatus(BasicAirPurifierMiotStatus):
    """Container for status reports from the air purifier.

    Mi Air Purifier 3/3H (zhimi.airpurifier.mb3) response (MIoT format)

    [
        {'did': 'power', 'siid': 2, 'piid': 2, 'code': 0, 'value': True},
        {'did': 'fan_level', 'siid': 2, 'piid': 4, 'code': 0, 'value': 1},
        {'did': 'mode', 'siid': 2, 'piid': 5, 'code': 0, 'value': 2},
        {'did': 'humidity', 'siid': 3, 'piid': 7, 'code': 0, 'value': 38},
        {'did': 'temperature', 'siid': 3, 'piid': 8, 'code': 0, 'value': 22.299999},
        {'did': 'aqi', 'siid': 3, 'piid': 6, 'code': 0, 'value': 2},
        {'did': 'filter_life_remaining', 'siid': 4, 'piid': 3, 'code': 0, 'value': 45},
        {'did': 'filter_hours_used', 'siid': 4, 'piid': 5, 'code': 0, 'value': 1915},
        {'did': 'buzzer', 'siid': 5, 'piid': 1, 'code': 0, 'value': False},
        {'did': 'buzzer_volume', 'siid': 5, 'piid': 2, 'code': -4001},
        {'did': 'led_brightness', 'siid': 6, 'piid': 1, 'code': 0, 'value': 1},
        {'did': 'led', 'siid': 6, 'piid': 6, 'code': 0, 'value': True},
        {'did': 'child_lock', 'siid': 7, 'piid': 1, 'code': 0, 'value': False},
        {'did': 'favorite_level', 'siid': 10, 'piid': 10, 'code': 0, 'value': 2},
        {'did': 'favorite_rpm', 'siid': 10, 'piid': 7, 'code': 0, 'value': 770},
        {'did': 'motor_speed', 'siid': 10, 'piid': 8, 'code': 0, 'value': 769},
        {'did': 'use_time', 'siid': 12, 'piid': 1, 'code': 0, 'value': 6895800},
        {'did': 'purify_volume', 'siid': 13, 'piid': 1, 'code': 0, 'value': 222564},
        {'did': 'average_aqi', 'siid': 13, 'piid': 2, 'code': 0, 'value': 2},
        {'did': 'filter_rfid_tag', 'siid': 14, 'piid': 1, 'code': 0, 'value': '81:6b:3f:32:84:4b:4'},
        {'did': 'filter_rfid_product_id', 'siid': 14, 'piid': 3, 'code': 0, 'value': '0:0:31:31'},
        {'did': 'app_extra', 'siid': 15, 'piid': 1, 'code': 0, 'value': 0}
    ]
    """

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
        if self.data["temperature"] is not None:
            return round(self.data["temperature"], 1)

        return None

    @property
    def fan_level(self) -> int:
        """Current fan level."""
        return self.data["fan_level"]

    @property
    def led(self) -> bool:
        """Return True if LED is on."""
        return self.data["led"]

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        """Brightness of the LED."""
        if self.data["led_brightness"] is not None:
            try:
                return LedBrightness(self.data["led_brightness"])
            except ValueError:
                return None

        return None

    @property
    def buzzer_volume(self) -> Optional[int]:
        """Return buzzer volume."""
        if self.data["buzzer_volume"] is not None:
            return self.data["buzzer_volume"]

        return None

    @property
    def favorite_level(self) -> int:
        """Return favorite level, which is used if the mode is ``favorite``."""
        # Favorite level used when the mode is `favorite`.
        return self.data["favorite_level"]

    @property
    def use_time(self) -> int:
        """How long the device has been active in seconds."""
        return self.data["use_time"]

    @property
    def purify_volume(self) -> int:
        """The volume of purified air in cubic meter."""
        return self.data["purify_volume"]

    @property
    def filter_rfid_product_id(self) -> Optional[str]:
        """RFID product ID of installed filter."""
        return self.data["filter_rfid_product_id"]

    @property
    def filter_rfid_tag(self) -> Optional[str]:
        """RFID tag ID of installed filter."""
        return self.data["filter_rfid_tag"]

    @property
    def filter_type(self) -> Optional[FilterType]:
        """Type of installed filter."""
        return self.filter_type_util.determine_filter_type(
            self.filter_rfid_tag, self.filter_rfid_product_id
        )


class AirPurifierMB4Status(BasicAirPurifierMiotStatus):
    """
    Container for status reports from the  Mi Air Purifier 3C (zhimi.airpurifier.mb4).

    {
        'power': True,
        'mode': 1,
        'aqi': 2,
        'filter_life_remaining': 97,
        'filter_hours_used': 100,
        'buzzer': True,
        'led_brightness_level': 8,
        'child_lock': False,
        'motor_speed': 392,
        'favorite_rpm': 500
    }

    Response (MIoT format)

    [
        {'did': 'power', 'siid': 2, 'piid': 1, 'code': 0, 'value': True},
        {'did': 'mode', 'siid': 2, 'piid': 4, 'code': 0, 'value': 1},
        {'did': 'aqi', 'siid': 3, 'piid': 4, 'code': 0, 'value': 3},
        {'did': 'filter_life_remaining', 'siid': 4, 'piid': 1, 'code': 0, 'value': 97},
        {'did': 'filter_hours_used', 'siid': 4, 'piid': 3, 'code': 0, 'value': 100},
        {'did': 'buzzer', 'siid': 6, 'piid': 1, 'code': 0, 'value': True},
        {'did': 'led_brightness_level', 'siid': 7, 'piid': 2, 'code': 0, 'value': 8},
        {'did': 'child_lock', 'siid': 8, 'piid': 1, 'code': 0, 'value': False},
        {'did': 'motor_speed', 'siid': 9, 'piid': 1, 'code': 0, 'value': 388},
        {'did': 'favorite_rpm', 'siid': 9, 'piid': 3, 'code': 0, 'value': 500}
    ]

    """

    @property
    def led_brightness_level(self) -> int:
        """Return brightness level."""
        return self.data["led_brightness_level"]


class BasicAirPurifierMiot(MiotDevice):
    """Main class representing the air purifier which uses MIoT protocol."""

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.set_property("power", True)

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.set_property("power", False)

    @command(
        click.argument("rpm", type=int),
        default_output=format_output("Setting favorite motor speed '{rpm}' rpm"),
    )
    def set_favorite_rpm(self, rpm: int):
        """Set favorite motor speed."""
        # Note: documentation says the maximum is 2300, however, the purifier may return an error for rpm over 2200.
        if rpm < 300 or rpm > 2300 or rpm % 10 != 0:
            raise AirPurifierMiotException(
                "Invalid favorite motor speed: %s. Must be between 300 and 2300 and divisible by 10"
                % rpm
            )
        return self.set_property("favorite_rpm", rpm)

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.set_property("mode", mode.value)

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        return self.set_property("buzzer", buzzer)

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        return self.set_property("child_lock", lock)


class AirPurifierMiot(BasicAirPurifierMiot):
    """Main class representing the air purifier which uses MIoT protocol."""

    mapping = _MAPPING

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "AQI: {result.aqi} μg/m³\n"
            "Average AQI: {result.average_aqi} μg/m³\n"
            "Humidity: {result.humidity} %\n"
            "Temperature: {result.temperature} °C\n"
            "Fan Level: {result.fan_level}\n"
            "Mode: {result.mode}\n"
            "LED: {result.led}\n"
            "LED brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Buzzer vol.: {result.buzzer_volume}\n"
            "Child lock: {result.child_lock}\n"
            "Favorite level: {result.favorite_level}\n"
            "Filter life remaining: {result.filter_life_remaining} %\n"
            "Filter hours used: {result.filter_hours_used}\n"
            "Use time: {result.use_time} s\n"
            "Purify volume: {result.purify_volume} m³\n"
            "Motor speed: {result.motor_speed} rpm\n"
            "Filter RFID product id: {result.filter_rfid_product_id}\n"
            "Filter RFID tag: {result.filter_rfid_tag}\n"
            "Filter type: {result.filter_type}\n",
        )
    )
    def status(self) -> AirPurifierMiotStatus:
        """Retrieve properties."""

        return AirPurifierMiotStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting fan level to '{level}'"),
    )
    def set_fan_level(self, level: int):
        """Set fan level."""
        if level < 1 or level > 3:
            raise AirPurifierMiotException("Invalid fan level: %s" % level)
        return self.set_property("fan_level", level)

    @command(
        click.argument("volume", type=int),
        default_output=format_output("Setting sound volume to {volume}"),
    )
    def set_volume(self, volume: int):
        """Set buzzer volume."""
        if volume < 0 or volume > 100:
            raise AirPurifierMiotException(
                "Invalid volume: %s. Must be between 0 and 100" % volume
            )
        return self.set_property("buzzer_volume", volume)

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting favorite level to {level}"),
    )
    def set_favorite_level(self, level: int):
        """Set the favorite level used when the mode is `favorite`.

        Needs to be between 0 and 14.
        """
        if level < 0 or level > 14:
            raise AirPurifierMiotException("Invalid favorite level: %s" % level)

        return self.set_property("favorite_level", level)

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.set_property("led_brightness", brightness.value)

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        return self.set_property("led", led)


class AirPurifierMB4(BasicAirPurifierMiot):
    """Main class representing the air purifier which uses MIoT protocol."""

    mapping = _MODEL_AIRPURIFIER_MB4

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "AQI: {result.aqi} μg/m³\n"
            "Mode: {result.mode}\n"
            "LED brightness level: {result.led_brightness_level}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Filter life remaining: {result.filter_life_remaining} %\n"
            "Filter hours used: {result.filter_hours_used}\n"
            "Motor speed: {result.motor_speed} rpm\n"
            "Favorite RPM: {result.favorite_rpm} rpm\n",
        )
    )
    def status(self) -> AirPurifierMB4Status:
        """Retrieve properties."""

        return AirPurifierMB4Status(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting LED brightness level to {level}"),
    )
    def set_led_brightness_level(self, level: int):
        """Set led brightness level (0..8)."""
        if level < 0 or level > 8:
            raise AirPurifierMiotException("Invalid brightness level: %s" % level)

        return self.set_property("led_brightness_level", level)
