import enum
import logging
from typing import Any, Dict, Optional

import click

from miio import DeviceStatus, MiotDevice
from miio.click_common import EnumType, command, format_output

_LOGGER = logging.getLogger(__name__)


SMARTMI_EVAPORATIVE_HUMIDIFIER_3 = "zhimi.humidifier.ca6"


_MAPPINGS = {
    SMARTMI_EVAPORATIVE_HUMIDIFIER_3: {
        # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:humidifier:0000A00E:zhimi-ca6:1
        # Air Humidifier (siid=2)
        "power": {"siid": 2, "piid": 1},  # bool
        "fault": {"siid": 2, "piid": 2},  # [0, 15] step 1
        "mode": {
            "siid": 2,
            "piid": 5,
        },  # 0 - Fav, 1 - Auto, 2 - Sleep
        "target_humidity": {
            "siid": 2,
            "piid": 6,
        },  # [30, 60] step 1
        "water_level": {
            "siid": 2,
            "piid": 7,
        },  # 0 - empty/min,  1 - normal, 2 - full/max
        "dry": {"siid": 2, "piid": 8},  # Automatic Air Drying, bool
        "status": {"siid": 2, "piid": 9},  # 1 - Close, 2 - Work, 3 - Dry, 4 - Clean
        # Environment (siid=3)
        "temperature": {"siid": 3, "piid": 7},  # [-40, 125] step 0.1
        "humidity": {"siid": 3, "piid": 9},  # [0, 100] step 1
        # Alarm (siid=4)
        "buzzer": {"siid": 4, "piid": 1},
        # Indicator Light (siid=5)
        "led_brightness": {"siid": 5, "piid": 2},  # 0 - Off, 1 - Dim, 2 - Brightest
        # Physical Control Locked (siid=6)
        "child_lock": {"siid": 6, "piid": 1},  # bool
        # Other (siid=7)
        "actual_speed": {"siid": 7, "piid": 1},  # [0, 2000] step 1
        "coutry_code": {
            "siid": 7,
            "piid": 2,
        },  # 82 - KR, 44 - EU, 81 - JP, 86 - CN, 886 - TW
        "clean_mode": {"siid": 7, "piid": 5},  # bool
        "self_clean_percent": {"siid": 7, "piid": 6},  # minutes, [0, 30] step 1
        "pump_state": {"siid": 7, "piid": 7},  # bool
        "pump_cnt": {"siid": 7, "piid": 8},  # [0, 4000] step 1
    }
}


class OperationMode(enum.Enum):
    Fav = 0
    Auto = 1
    Sleep = 2


class OperationStatus(enum.Enum):
    Close = 1
    Work = 2
    Dry = 3
    Clean = 4


class LedBrightness(enum.Enum):
    Off = 0
    Dim = 1
    Bright = 2


class AirHumidifierMiotCA6Status(DeviceStatus):
    """Container for status reports from the air humidifier.

    Xiaomi Smartmi Evaporation Air Humidifier 3 (zhimi.humidifier.ca6) respone (MIoT format)::

        [
            {'did': 'power', 'siid': 2, 'piid': 1, 'code': 0, 'value': True},
            {'did': 'fault', 'siid': 2, 'piid': 2, 'code': 0, 'value': 0},
            {'did': 'mode', 'siid': 2, 'piid': 5, 'code': 0, 'value': 0},
            {'did': 'target_humidity', 'siid': 2, 'piid': 6, 'code': 0, 'value': 50},
            {'did': 'water_level', 'siid': 2, 'piid': 7, 'code': 0, 'value': 1},
            {'did': 'dry', 'siid': 2, 'piid': 8, 'code': 0, 'value': True},
            {'did': 'status', 'siid': 2, 'piid': 9, 'code': 0, 'value': 2},
            {'did': 'temperature', 'siid': 3, 'piid': 7, 'code': 0, 'value': 19.0},
            {'did': 'humidity', 'siid': 3, 'piid': 9, 'code': 0, 'value': 51},
            {'did': 'buzzer', 'siid': 4, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'led_brightness', 'siid': 5, 'piid': 2, 'code': 0, 'value': 2},
            {'did': 'child_lock', 'siid': 6, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'actual_speed', 'siid': 7, 'piid': 1, 'code': 0, 'value': 1100},
            {'did': 'clean_mode', 'siid': 7, 'piid': 5, 'code': 0, 'value': False}
            {'did': 'self_clean_percent, 'siid': 7, 'piid': 6, 'code': 0, 'value': 0},
            {'did': 'pump_state, 'siid': 7, 'piid': 7, 'code': 0, 'value': False},
            {'did': 'pump_cnt', 'siid': 7, 'piid': 8, 'code': 0, 'value': 1000},
        ]
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data
        _LOGGER.debug("Status : %s", repr(data))

    # Air Humidifier

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.data["power"]

    @property
    def power(self) -> str:
        """Return power state."""
        return "on" if self.is_on else "off"

    @property
    def error(self) -> int:
        """Return error state."""
        return self.data["fault"]

    @property
    def mode(self) -> OperationMode:
        """Return current operation mode."""

        try:
            mode = OperationMode(self.data["mode"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse mode: %s", e)
            return OperationMode.Auto

        return mode

    @property
    def target_humidity(self) -> int:
        """Return target humidity."""
        return self.data["target_humidity"]

    @property
    def water_level(self) -> Optional[int]:
        """Return current water level (empty/min, normal, full/max).

        0 - empty/min,  1 - normal, 2 - full/max
        """
        water_level = self.data["water_level"]
        return {0: 0, 1: 50, 2: 100}.get(water_level)

    @property
    def dry(self) -> Optional[bool]:
        """Return True if dry mode is on."""
        if self.data["dry"] is not None:
            return self.data["dry"]
        return None

    @property
    def status(self) -> OperationStatus:
        """Return current status."""

        try:
            status = OperationStatus(self.data["status"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse status: %s", e)
            return OperationStatus.Close

        return status

    # Environment

    @property
    def humidity(self) -> int:
        """Return current humidity."""
        return self.data["humidity"]

    @property
    def temperature(self) -> Optional[float]:
        """Return current temperature, if available."""
        if self.data["temperature"] is not None:
            return round(self.data["temperature"], 1)
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
        """Return brightness of the LED."""

        if self.data["led_brightness"] is not None:
            try:
                return LedBrightness(self.data["led_brightness"])
            except ValueError as e:
                _LOGGER.exception("Cannot parse led_brightness: %s", e)
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
        """Return real speed of the motor."""
        return self.data["actual_speed"]

    @property
    def clean_mode(self) -> bool:
        """Return True if clean mode is active."""
        return self.data["clean_mode"]

    @property
    def self_clean_percent(self) -> int:
        """Return time in minutes (from 0 to 30) of self-cleaning procedure."""
        return self.data["self_clean_percent"]

    @property
    def pump_state(self) -> bool:
        """Return pump statue."""
        return self.data["pump_state"]

    @property
    def pump_cnt(self) -> int:
        """Return pump-cnt."""
        return self.data["pump_cnt"]


class AirHumidifierMiotCA6(MiotDevice):
    """Main class representing zhimi.humidifier.ca6 air humidifier which uses MIoT protocol."""

    _mappings = _MAPPINGS

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Error: {result.error}\n"
            "Target Humidity: {result.target_humidity} %\n"
            "Humidity: {result.humidity} %\n"
            "Temperature: {result.temperature} °C\n"
            "Water Level: {result.water_level} %\n"
            "Mode: {result.mode}\n"
            "Status: {result.status}\n"
            "LED brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Dry mode: {result.dry}\n"
            "Actual motor speed: {result.actual_speed} rpm\n"
            "Clean mode: {result.clean_mode}\n"
            "Self clean percent: {result.self_clean_percent} minutes\n"
            "Pump state: {result.pump_state}\n"
            "Pump cnt: {result.pump_cnt}\n",
        )
    )
    def status(self) -> AirHumidifierMiotCA6Status:
        """Retrieve properties."""

        return AirHumidifierMiotCA6Status(
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
        click.argument("humidity", type=int),
        default_output=format_output("Setting target humidity {humidity}%"),
    )
    def set_target_humidity(self, humidity: int):
        """Set target humidity."""
        if humidity < 30 or humidity > 60:
            raise ValueError(
                "Invalid target humidity: %s. Must be between 30 and 60" % humidity
            )
        # HA sends humidity in float, e.g. 45.0
        # ca6 does accept only int values, e.g. 45
        return self.set_property("target_humidity", int(humidity))

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set working mode."""
        return self.set_property("mode", mode.value)

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
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

    @command(
        click.argument("clean_mode", type=bool),
        default_output=format_output(
            lambda clean_mode: "Turning on clean mode"
            if clean_mode
            else "Turning off clean mode"
        ),
    )
    def set_clean_mode(self, clean_mode: bool):
        """Set clean mode on/off."""
        return self.set_property("clean_mode", clean_mode)
