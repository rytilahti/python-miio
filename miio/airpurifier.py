import logging
import enum
import re
from typing import Any, Dict, Optional
from collections import defaultdict
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class AirPurifierException(DeviceException):
    pass


class OperationMode(enum.Enum):
    # Supported modes of the Air Purifier Pro, 2, V3
    Auto = 'auto'
    Silent = 'silent'
    Favorite = 'favorite'
    # Additional supported modes of the Air Purifier 2 and V3
    Idle = 'idle'
    # Additional supported modes of the Air Purifier V3
    Medium = 'medium'
    High = 'high'
    Strong = 'strong'


class SleepMode(enum.Enum):
    Off = 'poweroff'
    Silent = 'silent'
    Idle = 'idle'


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class FilterType(enum.Enum):
    Regular = 'regular'
    AntiBacterial = 'anti-bacterial'
    AntiFormaldehyde = 'anti-formaldehyde'
    Unknown = 'unknown'


FILTER_TYPE_RE = (
    (re.compile(r'^\d+:\d+:41:30$'), FilterType.AntiBacterial),
    (re.compile(r'^\d+:\d+:(30|0|00):31$'), FilterType.AntiFormaldehyde),
    (re.compile(r'.*'), FilterType.Regular),
)


class AirPurifierStatus:
    """Container for status reports from the air purifier."""

    _filter_type_cache = {}

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Air Purifier Pro (zhimi.airpurifier.v6):

        {'power': 'off', 'aqi': 7, 'average_aqi': 18, 'humidity': 45,
         'temp_dec': 234, 'mode': 'auto', 'favorite_level': 17,
         'filter1_life': 52, 'f1_hour_used': 1664, 'use_time': 2642700,
         'motor1_speed': 0, 'motor2_speed': 800, 'purify_volume': 62180,
         'f1_hour': 3500, 'led': 'on', 'led_b': None, 'bright': 83,
         'buzzer': None, 'child_lock': 'off', 'volume': 50,
         'rfid_product_id': '0:0:41:30', 'rfid_tag': '80:52:86:e2:d8:86:4',
         'act_sleep': 'close'}

        Response of a Air Purifier 2 (zhimi.airpurifier.m1):

        {'power': 'on, 'aqi': 10, 'average_aqi': 8, 'humidity': 62,
         'temp_dec': 186, 'mode': 'auto', 'favorite_level': 10,
        'filter1_life': 80, 'f1_hour_used': 682, 'use_time': 2457000,
        'motor1_speed': 354, 'motor2_speed': None, 'purify_volume': 25262,
        'f1_hour': 3500, 'led': 'off', 'led_b': 2, 'bright': None,
        'buzzer': 'off', 'child_lock': 'off', 'volume': None,
        'rfid_product_id': None, 'rfid_tag': None,
        'act_sleep': 'close'}

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
        """Operation mode of the sleep state. (Idle vs. Silent)"""
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
        if self.filter_rfid_tag is None:
            return None
        if self.filter_rfid_tag == '0:0:0:0:0:0:0':
            return FilterType.Unknown
        if self.filter_rfid_product_id is None:
            return FilterType.Regular
        return self._get_filter_type(self.filter_rfid_product_id)

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

    @classmethod
    def _get_filter_type(cls, product_id: str) -> FilterType:
        ft = cls._filter_type_cache.get(product_id, None)
        if ft is None:
            for filter_re, filter_type in FILTER_TYPE_RE:
                if filter_re.match(product_id):
                    ft = cls._filter_type_cache[product_id] = filter_type
                    break
        return ft

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
            "volume=%s, " \
            "filter_rfid_product_id=%s, " \
            "filter_rfid_tag=%s, " \
            "filter_type=%s, " \
            "learn_mode=%s, " \
            "sleep_mode=%s, " \
            "sleep_time=%s, " \
            "sleep_mode_learn_count=%s, " \
            "extra_features=%s, " \
            "turbo_mode_supported=%s, " \
            "auto_detect=%s, " \
            "button_pressed=%s>" % \
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
             self.volume,
             self.filter_rfid_product_id,
             self.filter_rfid_tag,
             self.filter_type,
             self.learn_mode,
             self.sleep_mode,
             self.sleep_time,
             self.sleep_mode_learn_count,
             self.extra_features,
             self.turbo_mode_supported,
             self.auto_detect,
             self.button_pressed)
        return s


class AirPurifier(Device):
    """Main class representing the air purifier."""

    def status(self) -> AirPurifierStatus:
        """Retrieve properties."""

        properties = ['power', 'aqi', 'average_aqi', 'humidity', 'temp_dec',
                      'mode', 'favorite_level', 'filter1_life', 'f1_hour_used',
                      'use_time', 'motor1_speed', 'motor2_speed',
                      'purify_volume', 'f1_hour', 'led',
                      # Second request
                      'led_b', 'bright', 'buzzer', 'child_lock', 'volume',
                      'rfid_product_id', 'rfid_tag', 'act_sleep', 'sleep_mode',
                      'sleep_time', 'sleep_data_num', 'app_extra', 'act_det',
                      'button_pressed']

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

        # Possible alternative property: set_speed_favorite

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

    def set_learn_mode(self, learn_mode: bool):
        """Set the Learn Mode on/off."""
        if learn_mode:
            return self.send("set_act_sleep", ["single"])
        else:
            return self.send("set_act_sleep", ["close"])

    def set_auto_detect(self, auto_detect: bool):
        """Set auto detect on/off. It's a feature of the AirPurifier V1 & V3"""
        if auto_detect:
            return self.send("set_act_det", ["on"])
        else:
            return self.send("set_act_det", ["off"])

    def set_extra_features(self, value: int):
        """Storage register to enable extra features at the app.

        app_extra=1 unlocks a turbo mode supported feature
        """
        if value < 0:
            raise AirPurifierException("Invalid app extra value: %s" % value)

        return self.send("set_app_extra", [value])

    def reset_filter(self):
        """Resets filter hours used and remaining life."""
        return self.send('reset_filter1')
