import enum
import logging
from typing import Any

import click

from miio.click_common import EnumType, command, format_output
from miio.devicestatus import sensor, setting
from miio.miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)

_MAPPING = {
    # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:dehumidifier:0000A02D:xiaomi-lite:1
    # Dehumidifier (siid=2)
    "power": {"siid": 2, "piid": 1},  # bool
    "fault": {"siid": 2, "piid": 2},  # 0 - 9
    "mode": {"siid": 2, "piid": 3},  # 0 - Smart, 1 - Sleep, 2 - Clothes Drying
    "target_humidity": {"siid": 2, "piid": 5},  # [40, 70] step 1
    # Environment (siid=3)
    "relative_humidity": {"siid": 3, "piid": 1},  # [0, 100] step 1
    "temperature": {"siid": 3, "piid": 2},  # [-30, 100] step 1
    # Alarm (siid=4)
    "buzzer": {"siid": 4, "piid": 1},  # bool
    # Indicator Light (siid=5)
    "led": {"siid": 5, "piid": 1},  # bool
    "led_brightness": {"siid": 5, "piid": 2},  # 0 - Close, 1 - Dim, 2 - Bright
    # Physical Control Locked (siid=6)
    "child_lock": {"siid": 6, "piid": 1},  # bool
    # dm-service (siid=7)
    "dry_after_off": {"siid": 7, "piid": 1},  # bool
    "dry_left_time": {"siid": 7, "piid": 2},  # [0, 2400] step 1, seconds
    "is_warming_up": {"siid": 7, "piid": 3},  # bool
    # Delay (siid=8)
    "delay": {"siid": 8, "piid": 1},  # bool
    "delay_time": {"siid": 8, "piid": 2},  # [0, 720] step 1, minutes
    "delay_remain_time": {"siid": 8, "piid": 3},  # [0, 720] step 1, minutes
}

SUPPORTED_MODELS = ["xiaomi.derh.lite"]
MIOT_MAPPING = {model: _MAPPING for model in SUPPORTED_MODELS}


class OperationMode(enum.Enum):
    Smart = 0
    Sleep = 1
    ClothesDrying = 2


class LedBrightness(enum.Enum):
    Off = 0
    Dim = 1
    Bright = 2


class FaultStatus(enum.Enum):
    NoFaults = 0
    WaterFull = 1
    TempHumError = 2
    CopperPipeTempError = 3
    CommunicationFailure = 4
    FilterClean = 5
    Defrost = 6
    MotorStuck = 7
    OverloadProtect = 8
    LackOfRefrigerant = 9


class AirDehumidifierMiotStatus(DeviceStatus):
    """Container for status reports from the air dehumidifier.

    Xiaomi Smart Dehumidifier Lite (xiaomi.derh.lite) response (MIoT format)::

        [
            {'did': 'power', 'siid': 2, 'piid': 1, 'code': 0, 'value': True},
            {'did': 'fault', 'siid': 2, 'piid': 2, 'code': 0, 'value': 0},
            {'did': 'mode', 'siid': 2, 'piid': 3, 'code': 0, 'value': 0},
            {'did': 'target_humidity', 'siid': 2, 'piid': 5, 'code': 0, 'value': 50},
            {'did': 'relative_humidity', 'siid': 3, 'piid': 1, 'code': 0, 'value': 62},
            {'did': 'temperature', 'siid': 3, 'piid': 2, 'code': 0, 'value': 21.6},
            {'did': 'buzzer', 'siid': 4, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'led', 'siid': 5, 'piid': 1, 'code': 0, 'value': True},
            {'did': 'led_brightness', 'siid': 5, 'piid': 2, 'code': 0, 'value': 2},
            {'did': 'child_lock', 'siid': 6, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'dry_after_off', 'siid': 7, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'dry_left_time', 'siid': 7, 'piid': 2, 'code': 0, 'value': 0},
            {'did': 'is_warming_up', 'siid': 7, 'piid': 3, 'code': 0, 'value': False},
            {'did': 'delay', 'siid': 8, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'delay_time', 'siid': 8, 'piid': 2, 'code': 0, 'value': 0},
            {'did': 'delay_remain_time', 'siid': 8, 'piid': 3, 'code': 0, 'value': 0}
        ]
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    # Dehumidifier

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.data["power"]

    @property
    @sensor(name="Power")
    def power(self) -> str:
        """Return power state."""
        return "on" if self.is_on else "off"

    @property
    @sensor(name="Fault")
    def fault(self) -> FaultStatus:
        """Return device fault status."""
        try:
            return FaultStatus(self.data["fault"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse fault: %s", e)
            return FaultStatus.NoFaults

    @property
    @sensor(name="Tank Full")
    def tank_full(self) -> bool:
        """Return True if the water tank is full."""
        return self.fault is FaultStatus.WaterFull

    @property
    @setting(
        name="Mode",
        setter_name="set_mode",
        choices=OperationMode,
    )
    def mode(self) -> OperationMode:
        """Return current operation mode."""
        try:
            return OperationMode(self.data["mode"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse mode: %s", e)
            return OperationMode.Smart

    @property
    @setting(
        name="Target Humidity",
        unit="%",
        setter_name="set_target_humidity",
        min_value=40,
        max_value=70,
        step=1,
    )
    def target_humidity(self) -> int | None:
        """Return target humidity."""
        return self.data.get("target_humidity")

    # Environment

    @property
    @sensor(name="Relative Humidity", unit="%")
    def relative_humidity(self) -> int | None:
        """Return current humidity."""
        return self.data.get("relative_humidity")

    @property
    @sensor(name="Temperature", unit="C")
    def temperature(self) -> float | None:
        """Return current temperature, if available."""
        return self.data.get("temperature")

    # Alarm

    @property
    @setting(name="Buzzer", setter_name="set_buzzer")
    def buzzer(self) -> bool | None:
        """Return True if buzzer is on."""
        return self.data.get("buzzer")

    # Indicator Light

    @property
    @setting(name="LED", setter_name="set_led")
    def led(self) -> bool | None:
        """Return True if LED is on."""
        return self.data.get("led")

    @property
    @setting(
        name="LED Brightness",
        setter_name="set_led_brightness",
        choices=LedBrightness,
    )
    def led_brightness(self) -> LedBrightness | None:
        """Return brightness of the indicator light."""
        value = self.data.get("led_brightness")
        if value is None:
            return None
        try:
            return LedBrightness(value)
        except ValueError as e:
            _LOGGER.exception("Cannot parse led_brightness: %s", e)
            return None

    # Physical Control Locked

    @property
    @setting(name="Child Lock", setter_name="set_child_lock")
    def child_lock(self) -> bool | None:
        """Return True if child lock is on."""
        return self.data.get("child_lock")

    # dm-service

    @property
    @setting(name="Dry After Off", setter_name="set_dry_after_off")
    def dry_after_off(self) -> bool | None:
        """Return True if drying after power off is enabled."""
        return self.data.get("dry_after_off")

    @property
    @sensor(name="Dry Left Time", unit="s")
    def dry_left_time(self) -> int | None:
        """Return remaining drying time in seconds."""
        return self.data.get("dry_left_time")

    @property
    @sensor(name="Warming Up")
    def is_warming_up(self) -> bool | None:
        """Return True if the device is warming up."""
        return self.data.get("is_warming_up")

    # Delay

    @property
    @setting(name="Delayed Turn Off", setter_name="set_delay")
    def delay(self) -> bool | None:
        """Return True if delayed turn off is enabled."""
        return self.data.get("delay")

    @property
    @setting(
        name="Delay Time",
        unit="min",
        setter_name="set_delay_time",
        min_value=0,
        max_value=720,
        step=1,
    )
    def delay_time(self) -> int | None:
        """Return the configured delayed turn off time in minutes."""
        return self.data.get("delay_time")

    @property
    @sensor(name="Delay Remaining Time", unit="min")
    def delay_remain_time(self) -> int | None:
        """Return remaining time until turn off in minutes."""
        return self.data.get("delay_remain_time")


class AirDehumidifierMiot(MiotDevice):
    """Main class representing the Xiaomi Smart Dehumidifier Lite (MIoT protocol)."""

    _mappings = MIOT_MAPPING

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Fault: {result.fault}\n"
            "Mode: {result.mode}\n"
            "Target Humidity: {result.target_humidity} %\n"
            "Relative Humidity: {result.relative_humidity} %\n"
            "Temperature: {result.temperature} °C\n"
            "Tank full: {result.tank_full}\n"
            "Buzzer: {result.buzzer}\n"
            "LED: {result.led}\n"
            "LED brightness: {result.led_brightness}\n"
            "Child lock: {result.child_lock}\n"
            "Dry after off: {result.dry_after_off}\n"
            "Delayed turn off: {result.delay}\n"
            "Delay time: {result.delay_time} min\n",
        )
    )
    def status(self) -> AirDehumidifierMiotStatus:
        """Retrieve properties."""

        return AirDehumidifierMiotStatus(
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
        if humidity < 40 or humidity > 70:
            raise ValueError(
                f"Invalid target humidity: {humidity}. Must be between 40 and 70"
            )
        return self.set_property("target_humidity", humidity)

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set working mode."""
        return self.set_property("mode", mode.value)

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn LED on/off."""
        return self.set_property("led", led)

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness.name}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set the brightness of the indicator light."""
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
            lambda dry: (
                "Turning on dry after off" if dry else "Turning off dry after off"
            )
        ),
    )
    def set_dry_after_off(self, dry: bool):
        """Enable/disable drying after power off."""
        return self.set_property("dry_after_off", dry)

    @command(
        click.argument("delay", type=bool),
        default_output=format_output(
            lambda delay: (
                "Turning on delayed turn off"
                if delay
                else "Turning off delayed turn off"
            )
        ),
    )
    def set_delay(self, delay: bool):
        """Enable/disable delayed turn off."""
        return self.set_property("delay", delay)

    @command(
        click.argument("minutes", type=int),
        default_output=format_output("Setting delayed turn off to {minutes} minutes"),
    )
    def set_delay_time(self, minutes: int):
        """Set the delayed turn off time in minutes."""
        if minutes < 0 or minutes > 720:
            raise ValueError(f"Invalid delay time: {minutes}. Must be between 0 and 720")
        return self.set_property("delay_time", minutes)
