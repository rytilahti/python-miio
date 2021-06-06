import enum
import logging
from collections import defaultdict
from typing import Any, Dict, Optional

import click

from .airfilter_util import FilterType, FilterTypeUtil
from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)


class AirPurifierException(DeviceException):
    pass


class OperationMode(enum.Enum):
    # Supported modes of the Air Purifier Pro, 2, V3
    Auto = "auto"
    Silent = "silent"
    Favorite = "favorite"
    # Additional supported modes of the Air Purifier 2 and V3
    Idle = "idle"
    # Additional supported modes of the Air Purifier V3
    Medium = "medium"
    High = "high"
    Strong = "strong"
    # Additional supported modes of the Air Purifier Super 2
    Low = "low"


class SleepMode(enum.Enum):
    Off = "poweroff"
    Silent = "silent"
    Idle = "idle"


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class AirPurifierStatus(DeviceStatus):
    """Container for status reports from the air purifier."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a Air Purifier Pro (zhimi.airpurifier.v6):

        {'power': 'off', 'aqi': 7, 'average_aqi': 18, 'humidity': 45,
         'temp_dec': 234, 'mode': 'auto', 'favorite_level': 17,
         'filter1_life': 52, 'f1_hour_used': 1664, 'use_time': 2642700,
         'motor1_speed': 0, 'motor2_speed': 800, 'purify_volume': 62180,
         'f1_hour': 3500, 'led': 'on', 'led_b': None, 'bright': 83,
         'buzzer': None, 'child_lock': 'off', 'volume': 50,
         'rfid_product_id': '0:0:41:30', 'rfid_tag': '80:52:86:e2:d8:86:4',
         'act_sleep': 'close'}

        Response of a Air Purifier Pro (zhimi.airpurifier.v7):

        {'power': 'on', 'aqi': 2, 'average_aqi': 3, 'humidity': 42,
         'temp_dec': 223, 'mode': 'favorite', 'favorite_level': 3,
         'filter1_life': 56, 'f1_hour_used': 1538, 'use_time': None,
         'motor1_speed': 300, 'motor2_speed': 898, 'purify_volume': None,
         'f1_hour': 3500, 'led': 'on', 'led_b': None, 'bright': 45,
         'buzzer': None, 'child_lock': 'off', 'volume': 0,
         'rfid_product_id': '0:0:30:33', 'rfid_tag': '80:6a:a9:e2:37:92:4',
         'act_sleep': None, 'sleep_mode': None, 'sleep_time': None,
         'sleep_data_num': None, 'app_extra': 0, 'act_det': None,
         'button_pressed': None}

        Response of a Air Purifier 2 (zhimi.airpurifier.m1):

        {'power': 'on, 'aqi': 10, 'average_aqi': 8, 'humidity': 62,
         'temp_dec': 186, 'mode': 'auto', 'favorite_level': 10,
        'filter1_life': 80, 'f1_hour_used': 682, 'use_time': 2457000,
        'motor1_speed': 354, 'motor2_speed': None, 'purify_volume': 25262,
        'f1_hour': 3500, 'led': 'off', 'led_b': 2, 'bright': None,
        'buzzer': 'off', 'child_lock': 'off', 'volume': None,
        'rfid_product_id': None, 'rfid_tag': None,
        'act_sleep': 'close'}

        Response of a Air Purifier 2 (zhimi.airpurifier.m2):

        {'power': 'on', 'aqi': 10, 'average_aqi': 8, 'humidity': 42,
         'temp_dec': 223, 'mode': 'favorite', 'favorite_level': 2,
         'filter1_life': 63, 'f1_hour_used': 1282, 'use_time': 16361416,
         'motor1_speed': 747, 'motor2_speed': None, 'purify_volume': 421580,
         'f1_hour': 3500, 'led': 'on', 'led_b': 1, 'bright': None,
         'buzzer': 'off', 'child_lock': 'off', 'volume': None,
         'rfid_product_id': None, 'rfid_tag': None, 'act_sleep': 'close',
         'sleep_mode': 'idle', 'sleep_time': 86168, 'sleep_data_num': 30,
         'app_extra': 0, 'act_det': None, 'button_pressed': None}

        Response of a Air Purifier V3 (zhimi.airpurifier.v3)

        {'power': 'off', 'aqi': 0, 'humidity': None, 'temp_dec': None,
         'mode': 'idle', 'led': 'off', 'led_b': 10, 'buzzer': 'on',
         'child_lock': 'off', 'bright': 43, 'favorite_level': None,
         'filter1_life': 26, 'f1_hour_used': 2573, 'use_time': None,
         'motor1_speed': 0}

        {'power': 'on', 'aqi': 18, 'humidity': None, 'temp_dec': None,
         'mode': 'silent', 'led': 'off', 'led_b': 10, 'buzzer': 'on',
         'child_lock': 'off', 'bright': 4, 'favorite_level': None,
         'filter1_life': 26, 'f1_hour_used': 2574, 'use_time': None,
         'motor1_speed': 648}

        A request is limited to 16 properties.
        """

        self.filter_type_util = FilterTypeUtil()
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
    def sleep_mode(self) -> Optional[SleepMode]:
        """Operation mode of the sleep state.

        (Idle vs. Silent)
        """
        if self.data["sleep_mode"] is not None:
            return SleepMode(self.data["sleep_mode"])

        return None

    @property
    def led(self) -> bool:
        """Return True if LED is on."""
        return self.data["led"] == "on"

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        """Brightness of the LED."""
        if self.data["led_b"] is not None:
            try:
                return LedBrightness(self.data["led_b"])
            except ValueError:
                return None

        return None

    @property
    def illuminance(self) -> Optional[int]:
        """Environment illuminance level in lux [0-200].

        Sensor value is updated only when device is turned on.
        """
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

    @property
    def filter_rfid_product_id(self) -> Optional[str]:
        """RFID product ID of installed filter."""
        return self.data["rfid_product_id"]

    @property
    def filter_rfid_tag(self) -> Optional[str]:
        """RFID tag ID of installed filter."""
        return self.data["rfid_tag"]

    @property
    def filter_type(self) -> Optional[FilterType]:
        """Type of installed filter."""
        return self.filter_type_util.determine_filter_type(
            self.filter_rfid_tag, self.filter_rfid_product_id
        )

    @property
    def learn_mode(self) -> bool:
        """Return True if Learn Mode is enabled."""
        return self.data["act_sleep"] == "single"

    @property
    def sleep_time(self) -> Optional[int]:
        return self.data["sleep_time"]

    @property
    def sleep_mode_learn_count(self) -> Optional[int]:
        return self.data["sleep_data_num"]

    @property
    def extra_features(self) -> Optional[int]:
        return self.data["app_extra"]

    @property
    def turbo_mode_supported(self) -> Optional[bool]:
        if self.data["app_extra"] is not None:
            return self.data["app_extra"] == 1

        return None

    @property
    def auto_detect(self) -> Optional[bool]:
        """Return True if auto detect is enabled."""
        if self.data["act_det"] is not None:
            return self.data["act_det"] == "on"

        return None

    @property
    def button_pressed(self) -> Optional[str]:
        """Last pressed button."""
        return self.data["button_pressed"]


class AirPurifier(Device):
    """Main class representing the air purifier."""

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "AQI: {result.aqi} μg/m³\n"
            "Average AQI: {result.average_aqi} μg/m³\n"
            "Temperature: {result.temperature} °C\n"
            "Humidity: {result.humidity} %\n"
            "Mode: {result.mode.value}\n"
            "LED: {result.led}\n"
            "LED brightness: {result.led_brightness}\n"
            "Illuminance: {result.illuminance} lx\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Favorite level: {result.favorite_level}\n"
            "Filter life remaining: {result.filter_life_remaining} %\n"
            "Filter hours used: {result.filter_hours_used}\n"
            "Use time: {result.use_time} s\n"
            "Purify volume: {result.purify_volume} m³\n"
            "Motor speed: {result.motor_speed} rpm\n"
            "Motor 2 speed: {result.motor2_speed} rpm\n"
            "Sound volume: {result.volume} %\n"
            "Filter RFID product id: {result.filter_rfid_product_id}\n"
            "Filter RFID tag: {result.filter_rfid_tag}\n"
            "Filter type: {result.filter_type}\n"
            "Learn mode: {result.learn_mode}\n"
            "Sleep mode: {result.sleep_mode}\n"
            "Sleep time: {result.sleep_time}\n"
            "Sleep mode learn count: {result.sleep_mode_learn_count}\n"
            "AQI sensor enabled on power off: {result.auto_detect}\n",
        )
    )
    def status(self) -> AirPurifierStatus:
        """Retrieve properties."""

        properties = [
            "power",
            "aqi",
            "average_aqi",
            "humidity",
            "temp_dec",
            "mode",
            "favorite_level",
            "filter1_life",
            "f1_hour_used",
            "use_time",
            "motor1_speed",
            "motor2_speed",
            "purify_volume",
            "f1_hour",
            "led",
            # Second request
            "led_b",
            "bright",
            "buzzer",
            "child_lock",
            "volume",
            "rfid_product_id",
            "rfid_tag",
            "act_sleep",
            "sleep_mode",
            "sleep_time",
            "sleep_data_num",
            "app_extra",
            "act_det",
            "button_pressed",
        ]

        values = self.get_properties(properties, max_properties=15)

        return AirPurifierStatus(defaultdict(lambda: None, zip(properties, values)))

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
        click.argument("level", type=int),
        default_output=format_output("Setting favorite level to {level}"),
    )
    def set_favorite_level(self, level: int):
        """Set favorite level."""
        if level < 0 or level > 17:
            raise AirPurifierException("Invalid favorite level: %s" % level)

        # Possible alternative property: set_speed_favorite

        # Set the favorite level used when the mode is `favorite`,
        # should be  between 0 and 17.
        return self.send("set_level_favorite", [level])  # 0 ... 17

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
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
            return self.send("set_led", ["on"])
        else:
            return self.send("set_led", ["off"])

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
        click.argument("volume", type=int),
        default_output=format_output("Setting sound volume to {volume}"),
    )
    def set_volume(self, volume: int):
        """Set volume of sound notifications [0-100]."""
        if volume < 0 or volume > 100:
            raise AirPurifierException("Invalid volume: %s" % volume)

        return self.send("set_volume", [volume])

    @command(
        click.argument("learn_mode", type=bool),
        default_output=format_output(
            lambda learn_mode: "Turning on learn mode"
            if learn_mode
            else "Turning off learn mode"
        ),
    )
    def set_learn_mode(self, learn_mode: bool):
        """Set the Learn Mode on/off."""
        if learn_mode:
            return self.send("set_act_sleep", ["single"])
        else:
            return self.send("set_act_sleep", ["close"])

    @command(
        click.argument("auto_detect", type=bool),
        default_output=format_output(
            lambda auto_detect: "Turning on auto detect"
            if auto_detect
            else "Turning off auto detect"
        ),
    )
    def set_auto_detect(self, auto_detect: bool):
        """Set auto detect on/off.

        It's a feature of the AirPurifier V1 & V3
        """
        if auto_detect:
            return self.send("set_act_det", ["on"])
        else:
            return self.send("set_act_det", ["off"])

    @command(
        click.argument("value", type=int),
        default_output=format_output("Setting extra to {value}"),
    )
    def set_extra_features(self, value: int):
        """Storage register to enable extra features at the app.

        app_extra=1 unlocks a turbo mode supported feature
        """
        if value < 0:
            raise AirPurifierException("Invalid app extra value: %s" % value)

        return self.send("set_app_extra", [value])

    @command(default_output=format_output("Resetting filter"))
    def reset_filter(self):
        """Resets filter hours used and remaining life."""
        return self.send("reset_filter1")
