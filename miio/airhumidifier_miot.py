import enum
import logging
from typing import Any, Dict, Optional

import click

from .click_common import EnumType, command, format_output
from .exceptions import DeviceException
from .miot_device import MiotDevice

_LOGGER = logging.getLogger(__name__)
_MAPPING = {
    # Source http://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:humidifier:0000A00E:zhimi-ca4:2
    # Air Humidifier (siid=2)
    "power": {"siid": 2, "piid": 1},  # bool
    "fault": {"siid": 2, "piid": 2},  # [0, 15] step 1
    "mode": {"siid": 2, "piid": 5},  # 0 - Auto, 1 - lvl1, 2 - lvl2, 3 - lvl3
    "target_humidity": {"siid": 2, "piid": 6},  # [30, 80] step 1
    "water_level": {"siid": 2, "piid": 7},  # [0, 128] step 1
    "dry": {"siid": 2, "piid": 8},  # bool
    "use_time": {"siid": 2, "piid": 9},  # [0, 2147483600], step 1
    "button_pressed": {"siid": 2, "piid": 10},  # 0 - none, 1 - led, 2 - power
    "speed_level": {"siid": 2, "piid": 11},  # [200, 2000], step 10
    # Environment (siid=3)
    "temperature": {"siid": 3, "piid": 7},  # [-40, 125] step 0.1
    "fahrenheit": {"siid": 3, "piid": 8},  # [-40, 257] step 0.1
    "humidity": {"siid": 3, "piid": 9},  # [0, 100] step 1
    # Alarm (siid=4)
    "buzzer": {"siid": 4, "piid": 1},
    # Indicator Light (siid=5)
    "led_brightness": {"siid": 5, "piid": 2},  # 0 - Off, 1 - Dim, 2 - Brightest
    # Physical Control Locked (siid=6)
    "child_lock": {"siid": 6, "piid": 1},  # bool
    # Other (siid=7)
    "actual_speed": {"siid": 7, "piid": 1},  # [0, 2000] step 1
    "power_time": {"siid": 7, "piid": 3},  # [0, 4294967295] step 1
}


class AirHumidifierMiotException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Auto = 0
    Low = 1
    Mid = 2
    High = 3


class LedBrightness(enum.Enum):
    Off = 0
    Dim = 1
    Bright = 2


class PressedButton(enum.Enum):
    No = 0
    Led = 1
    Power = 2


class AirHumidifierMiotStatus:
    """Container for status reports from the air humidifier."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    # Air Humidifier

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.data["power"]

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.is_on else "off"

    @property
    def fault(self) -> int:
        """Fault state."""
        return self.data["fault"]

    @property
    def mode(self) -> OperationMode:
        """Current operation mode."""
        return OperationMode(self.data["mode"])

    @property
    def target_humidity(self) -> int:
        """Target humidity."""
        return self.data["target_humidity"]

    @property
    def water_level(self) -> int:
        """Current water level."""
        # 127 without water tank. 125 = 100% water
        return int(self.data["water_level"] / 1.25)

    @property
    def dry(self) -> Optional[bool]:
        """Return True if dry mode is on."""
        if self.data["dry"] is not None:
            return self.data["dry"]
        return None

    @property
    def use_time(self) -> int:
        """How long the device has been active in seconds."""
        return self.data["use_time"]

    @property
    def button_pressed(self) -> int:
        """Showed last pressed button."""
        return PressedButton(self.data["button_pressed"])

    @property
    def motor_speed(self) -> int:
        """Target speed of the motor."""
        return self.data["speed_level"]

    # Environment

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
    def fahrenheit(self) -> Optional[float]:
        """Current temperature in fahrenheit, if available."""
        if self.data["fahrenheit"] is not None:
            return round(self.data["fahrenheit"], 1)
        return None

    # Alarm

    @property
    def buzzer(self) -> Optional[bool]:
        """Return True if buzzer is on."""
        if self.data["buzzer"] is not None:
            return self.data["buzzer"]
        return None

    # Indicator Light

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        """Brightness of the LED."""
        if self.data["led_brightness"] is not None:
            try:
                return LedBrightness(self.data["led_brightness"])
            except ValueError:
                return None

        return None

    # Physical Control Locked

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"]

    # Other

    @property
    def actual_speed(self) -> int:
        """Real speed of the motor."""
        return self.data["actual_speed"]

    @property
    def power_time(self) -> int:
        """How long the device has been powered in seconds."""
        return self.data["power_time"]

    def __repr__(self) -> str:
        s = (
            "<AirHumidifierMiotStatus"
            "power=%s, "
            "fault=%s, "
            "mode=%s, "
            "target_humidity=%s, "
            "water_level=%s, "
            "dry=%s, "
            "use_time=%s, "
            "button_pressed=%s, "
            "motor_speed=%s, "
            "temperature=%s, "
            "fahrenheit=%s, "
            "humidity=%s, "
            "buzzer=%s, "
            "led_brightness=%s, "
            "child_lock=%s, "
            "actual_speed=%s, "
            "power_time=%s>"
            % (
                self.power,
                self.fault,
                self.mode,
                self.target_humidity,
                self.water_level,
                self.dry,
                self.use_time,
                self.button_pressed,
                self.motor_speed,
                self.temperature,
                self.fahrenheit,
                self.humidity,
                self.buzzer,
                self.led_brightness,
                self.child_lock,
                self.actual_speed,
                self.power_time,
            )
        )
        return s

    def __json__(self):
        return self.data


class AirHumidifierMiot(MiotDevice):
    """Main class representing the air humidifier which uses MIoT protocol."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(_MAPPING, ip, token, start_id, debug, lazy_discover)

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Fault: {result.fault}\n"
            "Target Humidity: {result.target_humidity} %\n"
            "Humidity: {result.humidity} %\n"
            "Temperature: {result.temperature} °C\n"
            "Temperature: {result.fahrenheit} °F\n"
            "Water Level: {result.water_level} %\n"
            "Mode: {result.mode}\n"
            "LED brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Dry mode: {result.dry}\n"
            "Button pressed {result.button_pressed}\n"
            "Target motor speed: {result.motor_speed} rpm\n"
            "Actual motor speed: {result.actual_speed} rpm\n"
            "Use time: {result.use_time} s\n"
            "Power time: {result.power_time} s\n",
        )
    )
    def status(self) -> AirHumidifierMiotStatus:
        """Retrieve properties."""

        return AirHumidifierMiotStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
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
        default_output=format_output("Setting motor speed '{rpm}' rpm"),
    )
    def set_speed(self, rpm: int):
        """Set motor speed."""
        if rpm < 200 or rpm > 2000 or rpm % 10 != 0:
            raise AirHumidifierMiotException(
                "Invalid motor speed: %s. Must be between 200 and 2000 and divisible by 10"
                % rpm
            )
        return self.set_property("speed_level", rpm)

    @command(
        click.argument("humidity", type=int),
        default_output=format_output("Setting target humidity {humidity}%"),
    )
    def set_target_humidity(self, humidity: int):
        """Set target humidity."""
        if humidity < 30 or humidity > 80:
            raise AirHumidifierMiotException(
                "Invalid target humidity: %s. Must be between 30 and 80" % humidity
            )
        return self.set_property("target_humidity", humidity)

    @command(
        click.argument("mode", type=EnumType(OperationMode, False)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set working mode."""
        return self.set_property("mode", mode.value)

    @command(
        click.argument("brightness", type=EnumType(LedBrightness, False)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.set_property("led_brightness", brightness.value)

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

    @command(
        click.argument("dry", type=bool),
        default_output=format_output(
            lambda dry: "Turning on dry mode" if dry else "Turning off dry mode"
        ),
    )
    def set_dry(self, dry: bool):
        """Set dry mode on/off."""
        return self.set_property("dry", dry)
