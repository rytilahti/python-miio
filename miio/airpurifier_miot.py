import enum
import logging
from typing import Any, Dict, Optional

import click

from miio.utils import deprecated

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
    "aqi_realtime_update_duration": {"siid": 13, "piid": 9},
    # RFID (siid=14)
    "filter_rfid_tag": {"siid": 14, "piid": 1},
    "filter_rfid_product_id": {"siid": 14, "piid": 3},
    # Other (siid=15)
    "app_extra": {"siid": 15, "piid": 1},
}

# https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-purifier:0000A007:zhimi-mb4:2
_MAPPING_MB4 = {
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

# https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-purifier:0000A007:zhimi-va2:2
_MAPPING_VA2 = {
    # Air Purifier
    "power": {"siid": 2, "piid": 1},
    "mode": {"siid": 2, "piid": 4},
    "fan_level": {"siid": 2, "piid": 5},
    "anion": {"siid": 2, "piid": 6},
    # Environment
    "humidity": {"siid": 3, "piid": 1},
    "aqi": {"siid": 3, "piid": 4},
    "temperature": {"siid": 3, "piid": 7},
    # Filter
    "filter_life_remaining": {"siid": 4, "piid": 1},
    "filter_hours_used": {"siid": 4, "piid": 3},
    "filter_left_time": {"siid": 4, "piid": 4},
    # Alarm
    "buzzer": {"siid": 6, "piid": 1},
    # Physical Control Locked
    "child_lock": {"siid": 8, "piid": 1},
    # custom-service
    "motor_speed": {"siid": 9, "piid": 1},
    "favorite_rpm": {"siid": 9, "piid": 3},
    "favorite_level": {"siid": 9, "piid": 5},
    # aqi
    "purify_volume": {"siid": 11, "piid": 1},
    "average_aqi": {"siid": 11, "piid": 2},
    "aqi_realtime_update_duration": {"siid": 11, "piid": 4},
    # RFID
    "filter_rfid_tag": {"siid": 12, "piid": 1},
    "filter_rfid_product_id": {"siid": 12, "piid": 3},
    # Screen
    "led_brightness": {"siid": 13, "piid": 2},
}

_MAPPINGS = {
    "zhimi.airpurifier.ma4": _MAPPING,  # airpurifier 3
    "zhimi.airpurifier.mb3": _MAPPING,  # airpurifier 3h
    "zhimi.airpurifier.va1": _MAPPING,  # airpurifier proh
    "zhimi.airpurifier.vb2": _MAPPING,  # airpurifier proh
    "zhimi.airpurifier.mb4": _MAPPING_MB4,  # airpurifier 3c
    "zhimi.airp.mb4a": _MAPPING_MB4,  # airpurifier 3c
    "zhimi.airp.va2": _MAPPING_VA2,  # airpurifier 4 pro
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


class AirPurifierMiotStatus(DeviceStatus):
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

    def __init__(self, data: Dict[str, Any], model: str) -> None:
        self.filter_type_util = FilterTypeUtil()
        self.data = data
        self.model = model

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.data["power"]

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.is_on else "off"

    @property
    def aqi(self) -> Optional[int]:
        """Air quality index."""
        return self.data.get("aqi")

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
        return self.data.get("buzzer")

    @property
    def child_lock(self) -> Optional[bool]:
        """Return True if child lock is on."""
        return self.data.get("child_lock")

    @property
    def filter_life_remaining(self) -> Optional[int]:
        """Time until the filter should be changed."""
        return self.data.get("filter_life_remaining")

    @property
    def filter_hours_used(self) -> Optional[int]:
        """How long the filter has been in use."""
        return self.data.get("filter_hours_used")

    @property
    def motor_speed(self) -> Optional[int]:
        """Speed of the motor."""
        return self.data.get("motor_speed")

    @property
    def favorite_rpm(self) -> Optional[int]:
        """Return favorite rpm level."""
        return self.data.get("favorite_rpm")

    @property
    def average_aqi(self) -> Optional[int]:
        """Average of the air quality index."""
        return self.data.get("average_aqi")

    @property
    def humidity(self) -> Optional[int]:
        """Current humidity."""
        return self.data.get("humidity")

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature, if available."""
        temperate = self.data.get("temperature")
        return round(temperate, 1) if temperate is not None else None

    @property
    def fan_level(self) -> Optional[int]:
        """Current fan level."""
        return self.data.get("fan_level")

    @property
    def led(self) -> Optional[bool]:
        """Return True if LED is on."""
        return self.data.get("led")

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        """Brightness of the LED."""

        value = self.data.get("led_brightness")
        if value is not None:
            if self.model == "zhimi.airp.va2":
                value = 2 - value
            try:
                return LedBrightness(value)
            except ValueError:
                return None

        return None

    @property
    def buzzer_volume(self) -> Optional[int]:
        """Return buzzer volume."""
        return self.data.get("buzzer_volume")

    @property
    def favorite_level(self) -> Optional[int]:
        """Return favorite level, which is used if the mode is ``favorite``."""
        # Favorite level used when the mode is `favorite`.
        return self.data.get("favorite_level")

    @property
    def use_time(self) -> Optional[int]:
        """How long the device has been active in seconds."""
        return self.data.get("use_time")

    @property
    def purify_volume(self) -> Optional[int]:
        """The volume of purified air in cubic meter."""
        return self.data.get("purify_volume")

    @property
    def filter_rfid_product_id(self) -> Optional[str]:
        """RFID product ID of installed filter."""
        return self.data.get("filter_rfid_product_id")

    @property
    def filter_rfid_tag(self) -> Optional[str]:
        """RFID tag ID of installed filter."""
        return self.data.get("filter_rfid_tag")

    @property
    def filter_type(self) -> Optional[FilterType]:
        """Type of installed filter."""
        return self.filter_type_util.determine_filter_type(
            self.filter_rfid_tag, self.filter_rfid_product_id
        )

    @property
    def led_brightness_level(self) -> Optional[int]:
        """Return brightness level."""
        return self.data.get("led_brightness_level")

    @property
    def anion(self) -> Optional[bool]:
        """Return whether anion is on."""
        return self.data.get("anion")

    @property
    def filter_left_time(self) -> Optional[int]:
        """How many days can the filter still be used."""
        return self.data.get("filter_left_time")


class AirPurifierMiot(MiotDevice):
    """Main class representing the air purifier which uses MIoT protocol."""

    _supported_models = list(_MAPPINGS.keys())
    _mappings = _MAPPINGS

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Anion: {result.anion}\n"
            "AQI: {result.aqi} μg/m³\n"
            "Average AQI: {result.average_aqi} μg/m³\n"
            "Humidity: {result.humidity} %\n"
            "Temperature: {result.temperature} °C\n"
            "Fan Level: {result.fan_level}\n"
            "Mode: {result.mode}\n"
            "LED: {result.led}\n"
            "LED brightness: {result.led_brightness}\n"
            "LED brightness level: {result.led_brightness_level}\n"
            "Buzzer: {result.buzzer}\n"
            "Buzzer vol.: {result.buzzer_volume}\n"
            "Child lock: {result.child_lock}\n"
            "Favorite level: {result.favorite_level}\n"
            "Filter life remaining: {result.filter_life_remaining} %\n"
            "Filter hours used: {result.filter_hours_used}\n"
            "Filter left time: {result.filter_left_time} days\n"
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
        # Some devices update the aqi information only every 30min.
        # This forces the device to poll the sensor for 5 seconds,
        # so that we get always the most recent values. See #1281.
        if self.model == "zhimi.airpurifier.mb3":
            self.set_property("aqi_realtime_update_duration", 5)

        return AirPurifierMiotStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            },
            self.model,
        )

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
        if "favorite_rpm" not in self._get_mapping():
            raise AirPurifierMiotException(
                "Unsupported favorite rpm for model '%s'" % self.model
            )

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
        click.argument("anion", type=bool),
        default_output=format_output(
            lambda anion: "Turning on anion" if anion else "Turing off anion",
        ),
    )
    def set_anion(self, anion: bool):
        """Set anion on/off."""
        if "anion" not in self._get_mapping():
            raise AirPurifierMiotException(
                "Unsupported anion for model '%s'" % self.model
            )
        return self.set_property("anion", anion)

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if "buzzer" not in self._get_mapping():
            raise AirPurifierMiotException(
                "Unsupported buzzer for model '%s'" % self.model
            )

        return self.set_property("buzzer", buzzer)

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        if "child_lock" not in self._get_mapping():
            raise AirPurifierMiotException(
                "Unsupported child lock for model '%s'" % self.model
            )
        return self.set_property("child_lock", lock)

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting fan level to '{level}'"),
    )
    def set_fan_level(self, level: int):
        """Set fan level."""
        if "fan_level" not in self._get_mapping():
            raise AirPurifierMiotException(
                "Unsupported fan level for model '%s'" % self.model
            )

        if level < 1 or level > 3:
            raise AirPurifierMiotException("Invalid fan level: %s" % level)
        return self.set_property("fan_level", level)

    @command(
        click.argument("volume", type=int),
        default_output=format_output("Setting sound volume to {volume}"),
    )
    def set_volume(self, volume: int):
        """Set buzzer volume."""
        if "volume" not in self._get_mapping():
            raise AirPurifierMiotException(
                "Unsupported volume for model '%s'" % self.model
            )

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
        if "favorite_level" not in self._get_mapping():
            raise AirPurifierMiotException(
                "Unsupported favorite level for model '%s'" % self.model
            )

        if level < 0 or level > 14:
            raise AirPurifierMiotException("Invalid favorite level: %s" % level)

        return self.set_property("favorite_level", level)

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        if "led_brightness" not in self._get_mapping():
            raise AirPurifierMiotException(
                "Unsupported led brightness for model '%s'" % self.model
            )

        value = brightness.value
        if self.model == "zhimi.airp.va2" and value:
            value = 2 - value
        return self.set_property("led_brightness", value)

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        if "led" not in self._get_mapping():
            raise AirPurifierMiotException(
                "Unsupported led for model '%s'" % self.model
            )
        return self.set_property("led", led)

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting LED brightness level to {level}"),
    )
    def set_led_brightness_level(self, level: int):
        """Set led brightness level (0..8)."""
        if "led_brightness_level" not in self._get_mapping():
            raise AirPurifierMiotException(
                "Unsupported led brightness level for model '%s'" % self.model
            )
        if level < 0 or level > 8:
            raise AirPurifierMiotException("Invalid brightness level: %s" % level)

        return self.set_property("led_brightness_level", level)


class AirPurifierMB4(AirPurifierMiot):
    @deprecated("Use AirPurifierMiot")
    def __init__(*args, **kwargs):
        super().__init__(*args, **kwargs)
