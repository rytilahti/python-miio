"""Xiaomi Smart Air Purifier 6 Plus (xiaomi.airp.mc6)."""

import enum
from typing import Any

import click

from miio import DeviceException, DeviceStatus, MiotDevice
from miio.click_common import EnumType, command
from miio.devicestatus import sensor, setting

MODEL = "xiaomi.airp.mc6"
# https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-purifier:0000A007:xiaomi-mc6:1:0000D050
_MAPPING = {
    "power": {"siid": 2, "piid": 1},
    "fault": {"siid": 2, "piid": 2},
    "mode": {"siid": 2, "piid": 3},
    "fan_level": {"siid": 2, "piid": 4},
    "anion": {"siid": 2, "piid": 5},
    "uv": {"siid": 2, "piid": 6},
    "humidity": {"siid": 3, "piid": 1},
    "temperature": {"siid": 3, "piid": 2},
    "air_quality": {"siid": 3, "piid": 3},
    "aqi": {"siid": 3, "piid": 4},
    "pm1": {"siid": 3, "piid": 9},
    "filter_life_remaining": {"siid": 4, "piid": 1},
    "filter_left_time": {"siid": 4, "piid": 2},
    "filter_hours_used": {"siid": 4, "piid": 3},
    "screen": {"siid": 6, "piid": 1},
    "screen_brightness": {"siid": 6, "piid": 2},
    "buzzer": {"siid": 7, "piid": 1},
    "child_lock": {"siid": 8, "piid": 1},
    "favorite_level": {"siid": 9, "piid": 1},
    "motor_target_speed": {"siid": 13, "piid": 3},
    "motor_speed": {"siid": 13, "piid": 4},
}


class OperationMode(enum.Enum):
    Auto = 0
    Sleep = 3
    Favorite = 5


class ScreenBrightness(enum.Enum):
    Dim = 0
    On = 1
    Mid = 2


class AirPurifierMC6Status(DeviceStatus):
    """MC6 readings; failed optional properties remain unavailable."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    @property
    def is_on(self) -> bool:
        """Return whether the purifier is powered on."""
        return self.data["power"]

    @property
    @sensor("Fault code")
    def fault(self) -> int | None:
        """Return fault code."""
        return self.data.get("fault")

    @property
    @setting("Mode", setter_name="set_mode")
    def mode(self) -> OperationMode | None:
        """Return mode."""
        value = self.data.get("mode")
        try:
            return OperationMode(value)
        except (ValueError, TypeError):
            return None

    @property
    @setting("Fan level", setter_name="set_fan_level", min_value=0, max_value=2, step=1)
    def fan_level(self) -> int | None:
        """Return fan level."""
        return self.data.get("fan_level")

    @property
    @setting("Ionizer", setter_name="set_anion")
    def anion(self) -> bool | None:
        """Return ionizer."""
        return self.data.get("anion")

    @property
    @setting("UV light", setter_name="set_uv")
    def uv(self) -> bool | None:
        """Return uv light."""
        return self.data.get("uv")

    @property
    @sensor("Humidity", unit="%")
    def humidity(self) -> int | None:
        """Return humidity."""
        return self.data.get("humidity")

    @property
    @sensor("Temperature", unit="°C")
    def temperature(self) -> float | None:
        """Return temperature."""
        return self.data.get("temperature")

    @property
    @sensor("Air quality category")
    def air_quality(self) -> int | None:
        """Return air quality category."""
        return self.data.get("air_quality")

    @property
    @sensor("PM2.5", unit="µg/m³")
    def aqi(self) -> int | None:
        """Return pm2.5."""
        return self.data.get("aqi")

    @property
    @sensor("PM1", unit="µg/m³")
    def pm1(self) -> int | None:
        """Return pm1."""
        return self.data.get("pm1")

    @property
    @sensor("Filter life remaining", unit="%")
    def filter_life_remaining(self) -> int | None:
        """Return filter life remaining."""
        return self.data.get("filter_life_remaining")

    @property
    @sensor("Filter time left", unit="h")
    def filter_left_time(self) -> int | None:
        """Return filter time left."""
        return self.data.get("filter_left_time")

    @property
    @sensor("Filter hours used", unit="h")
    def filter_hours_used(self) -> int | None:
        """Return filter hours used."""
        return self.data.get("filter_hours_used")

    @property
    @setting("Screen", setter_name="set_screen")
    def screen(self) -> bool | None:
        """Return screen."""
        return self.data.get("screen")

    @property
    @setting("Screen brightness", setter_name="set_screen_brightness")
    def screen_brightness(self) -> ScreenBrightness | None:
        """Return screen brightness."""
        value = self.data.get("screen_brightness")
        try:
            return ScreenBrightness(value)
        except (ValueError, TypeError):
            return None

    @property
    @setting("Buzzer", setter_name="set_buzzer")
    def buzzer(self) -> bool | None:
        """Return buzzer."""
        return self.data.get("buzzer")

    @property
    @setting("Child lock", setter_name="set_child_lock")
    def child_lock(self) -> bool | None:
        """Return child lock."""
        return self.data.get("child_lock")

    @property
    @setting(
        "Favorite level",
        setter_name="set_favorite_level",
        min_value=0,
        max_value=9,
        step=1,
    )
    def favorite_level(self) -> int | None:
        """Return favorite level."""
        return self.data.get("favorite_level")

    @property
    @sensor("Motor target speed", unit="rpm")
    def motor_target_speed(self) -> int | None:
        """Return motor target speed."""
        return self.data.get("motor_target_speed")

    @property
    @sensor("Motor speed", unit="rpm")
    def motor_speed(self) -> int | None:
        """Return motor speed."""
        return self.data.get("motor_speed")


class AirPurifierMC6(MiotDevice):
    """Local MIoT controls for MC6, with its distinct mode values."""

    _mappings = {MODEL: _MAPPING}

    @command()
    def status(self) -> AirPurifierMC6Status:
        """Read status without changing the device's reporting configuration."""
        data = dict.fromkeys(_MAPPING)
        pairs = {(p["siid"], p["piid"]): key for key, p in _MAPPING.items()}
        for prop in self.get_properties_for_mapping(max_properties=5):
            key = pairs.get((prop.get("siid"), prop.get("piid")))
            if key is not None and prop.get("code") == 0:
                data[key] = prop.get("value")
        if type(data["power"]) is not bool:
            raise DeviceException("MC6 power property is unavailable")
        return AirPurifierMC6Status(data)

    def _write(self, key: str, value: bool | int):
        result = self.set_property(key, value)
        prop = _MAPPING[key]
        if (
            not isinstance(result, list)
            or len(result) != 1
            or not isinstance(result[0], dict)
            or result[0].get("code") != 0
            or result[0].get("siid") != prop["siid"]
            or result[0].get("piid") != prop["piid"]
        ):
            raise DeviceException(f"MC6 rejected {key}")
        return result

    @command()
    def on(self):
        """Power on."""
        return self._write("power", True)

    @command()
    def off(self):
        """Power off."""
        return self._write("power", False)

    @command(click.argument("value", type=EnumType(OperationMode)))
    def set_mode(self, value: OperationMode):
        """Set mode."""
        if not isinstance(value, OperationMode):
            raise ValueError("Invalid mode")
        return self._write("mode", value.value)

    @command(click.argument("value", type=click.IntRange(0, 2)))
    def set_fan_level(self, value: int):
        """Set fan level."""
        if type(value) is not int or not 0 <= value <= 2:
            raise ValueError("Invalid fan_level")
        return self._write("fan_level", value)

    @command(click.argument("value", type=bool))
    def set_anion(self, value: bool):
        """Set ionizer."""
        if type(value) is not bool:
            raise ValueError("Invalid anion")
        return self._write("anion", value)

    @command(click.argument("value", type=bool))
    def set_uv(self, value: bool):
        """Set uv light."""
        if type(value) is not bool:
            raise ValueError("Invalid uv")
        return self._write("uv", value)

    @command(click.argument("value", type=bool))
    def set_screen(self, value: bool):
        """Set screen."""
        if type(value) is not bool:
            raise ValueError("Invalid screen")
        return self._write("screen", value)

    @command(click.argument("value", type=EnumType(ScreenBrightness)))
    def set_screen_brightness(self, value: ScreenBrightness):
        """Set screen brightness."""
        if not isinstance(value, ScreenBrightness):
            raise ValueError("Invalid screen_brightness")
        return self._write("screen_brightness", value.value)

    @command(click.argument("value", type=bool))
    def set_buzzer(self, value: bool):
        """Set buzzer."""
        if type(value) is not bool:
            raise ValueError("Invalid buzzer")
        return self._write("buzzer", value)

    @command(click.argument("value", type=bool))
    def set_child_lock(self, value: bool):
        """Set child lock."""
        if type(value) is not bool:
            raise ValueError("Invalid child_lock")
        return self._write("child_lock", value)

    @command(click.argument("value", type=click.IntRange(0, 9)))
    def set_favorite_level(self, value: int):
        """Set favorite level."""
        if type(value) is not int or not 0 <= value <= 9:
            raise ValueError("Invalid favorite_level")
        return self._write("favorite_level", value)
