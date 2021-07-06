import enum
import logging
from datetime import timedelta
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .exceptions import DeviceException
from .miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)
_MAPPING = {
    # Source http://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-conditioner:0000A004:xiaomi-mc4:1
    # Air Conditioner (siid=2)
    "power": {"siid": 2, "piid": 1},
    "mode": {"siid": 2, "piid": 2},
    "target_temperature": {"siid": 2, "piid": 4},
    "eco": {"siid": 2, "piid": 7},
    "heater": {"siid": 2, "piid": 9},
    "dryer": {"siid": 2, "piid": 10},
    "sleep_mode": {"siid": 2, "piid": 11},
    # Fan Control (siid=3)
    "fan_speed": {"siid": 3, "piid": 2},
    "vertical_swing": {"siid": 3, "piid": 4},
    # Environment (siid=4)
    "temperature": {"siid": 4, "piid": 7},
    # Alarm (siid=5)
    "buzzer": {"siid": 5, "piid": 1},
    # Indicator Light (siid=6)
    "led": {"siid": 6, "piid": 1},
    # Electricity (siid=8)
    "electricity": {"siid": 8, "piid": 1},
    # Maintenance (siid=9)
    "clean": {"siid": 9, "piid": 1},
    "running_duration": {"siid": 9, "piid": 5},
    # Enhance (siid=10)
    "fan_speed_percent": {"siid": 10, "piid": 1},
    "timer": {"siid": 10, "piid": 3},
}

CLEANING_STAGES = [
    "Stopped",
    "Condensing water",
    "Frosting the surface",
    "Defrosting the surface",
    "Drying",
]


class AirConditionerMiotException(DeviceException):
    pass


class CleaningStatus(DeviceStatus):
    def __init__(self, status: str):
        """Auto clean mode indicator.

        Value format: <int>,<int>,<int>,<int>
        Integer 1: whether auto cleaning mode started.
        Integer 2: current progress in percent.
        Integer 3: which stage it is currently under (see CLEANING_STAGE list).
        Integer 4: if current operation could be cancelled.

        Example auto clean indicator 1: 0,100,0,1
        indicates the auto clean mode has finished or not started yet.
        Example auto clean indicator 2: 1,22,1,1
        indicates auto clean mode finished 22%, it is condensing water and can be cancelled.
        Example auto clean indicator 3: 1,72,4,0
        indicates auto clean mode finished 72%, it is drying and cannot be cancelled.

        Only write 1 or 0 to it would start or abort the auto clean mode.
        """
        self.status = [int(value) for value in status.split(",")]

    @property
    def cleaning(self) -> bool:
        return bool(self.status[0])

    @property
    def progress(self) -> int:
        return int(self.status[1])

    @property
    def stage(self) -> str:
        try:
            return CLEANING_STAGES[self.status[2]]
        except KeyError:
            return "Unknown stage"

    @property
    def cancellable(self) -> bool:
        return bool(self.status[3])


class OperationMode(enum.Enum):
    Cool = 2
    Dry = 3
    Fan = 4
    Heat = 5


class FanSpeed(enum.Enum):
    Auto = 0
    Level1 = 1
    Level2 = 2
    Level3 = 3
    Level4 = 4
    Level5 = 5
    Level6 = 6
    Level7 = 7


class TimerStatus(DeviceStatus):
    def __init__(self, status):
        """Countdown timer indicator.

        Value format: <int>,<int>,<int>,<int>
        Integer 1: whether the timer is enabled.
        Integer 2: countdown timer setting value in minutes.
        Integer 3: the device would be powered on (1) or powered off (0) after timeout.
        Integer 4: the remaining countdown time in minutes.

        Example timer value 1: 1,120,0,103
        indicates the device would be turned off after 120 minutes, remaining 103 minutes.
        Example timer value 2: 1,60,1,60
        indicates the device would be turned on after 60 minutes, remaining 60 minutes.
        Example timer value 3: 0,0,0,0
        indicates countdown timer not set.

        Write the first three integers would set the correct countdown timer.
        Also, if the countdown minutes set to 0, the timer would be disabled.
        """
        self.status = [int(value) for value in status.split(",")]

    @property
    def enabled(self) -> bool:
        return bool(self.status[0])

    @property
    def countdown(self) -> timedelta:
        return timedelta(minutes=self.status[1])

    @property
    def power_on(self) -> bool:
        return bool(self.status[2])

    @property
    def time_left(self) -> timedelta:
        return timedelta(minutes=self.status[3])


class AirConditionerMiotStatus(DeviceStatus):
    """Container for status reports from the air conditioner (MIoT)."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response (MIoT format) of a Mi Smart Air Conditioner A (xiaomi.aircondition.mc4)
        [
            {'did': 'power', 'siid': 2, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'mode', 'siid': 2, 'piid': 2, 'code': 0, 'value': 2},
            {'did': 'target_temperature', 'siid': 2, 'piid': 4, 'code': 0, 'value': 26.5},
            {'did': 'eco', 'siid': 2, 'piid': 7, 'code': 0, 'value': False},
            {'did': 'heater', 'siid': 2, 'piid': 9, 'code': 0, 'value': True},
            {'did': 'dryer', 'siid': 2, 'piid': 10, 'code': 0, 'value': True},
            {'did': 'sleep_mode', 'siid': 2, 'piid': 11, 'code': 0, 'value': False},
            {'did': 'fan_speed', 'siid': 3, 'piid': 2, 'code': 0, 'value': 0},
            {'did': 'vertical_swing', 'siid': 3, 'piid': 4, 'code': 0, 'value': True},
            {'did': 'temperature', 'siid': 4, 'piid': 7, 'code': 0, 'value': 28.4},
            {'did': 'buzzer', 'siid': 5, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'led', 'siid': 6, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'electricity', 'siid': 8, 'piid': 1, 'code': 0, 'value': 0.0},
            {'did': 'clean', 'siid': 9, 'piid': 1, 'code': 0, 'value': '0,100,1,1'},
            {'did': 'running_duration', 'siid': 9, 'piid': 5, 'code': 0, 'value': 151.0},
            {'did': 'fan_speed_percent', 'siid': 10, 'piid': 1, 'code': 0, 'value': 101},
            {'did': 'timer', 'siid': 10, 'piid': 3, 'code': 0, 'value': '0,0,0,0'}
        ]

        """
        self.data = data

    @property
    def is_on(self) -> bool:
        """True if the device is turned on."""
        return self.data["power"]

    @property
    def power(self) -> str:
        """Current power state."""
        return "on" if self.is_on else "off"

    @property
    def mode(self) -> OperationMode:
        """Current operation mode."""
        return OperationMode(self.data["mode"])

    @property
    def target_temperature(self) -> float:
        """Target temperature in Celsius."""
        return self.data["target_temperature"]

    @property
    def eco(self) -> bool:
        """True if ECO mode is on."""
        return self.data["eco"]

    @property
    def heater(self) -> bool:
        """True if aux heat mode is on."""
        return self.data["heater"]

    @property
    def dryer(self) -> bool:
        """True if aux dryer mode is on."""
        return self.data["dryer"]

    @property
    def sleep_mode(self) -> bool:
        """True if sleep mode is on."""
        return self.data["sleep_mode"]

    @property
    def fan_speed(self) -> FanSpeed:
        """Current Fan speed."""
        return FanSpeed(self.data["fan_speed"])

    @property
    def vertical_swing(self) -> bool:
        """True if vertical swing is on."""
        return self.data["vertical_swing"]

    @property
    def temperature(self) -> float:
        """Current ambient temperature in Celsius."""
        return self.data["temperature"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is on."""
        return self.data["buzzer"]

    @property
    def led(self) -> bool:
        """True if LED is on."""
        return self.data["led"]

    @property
    def electricity(self) -> float:
        """Power consumption accumulation in kWh."""
        return self.data["electricity"]

    @property
    def clean(self) -> CleaningStatus:
        """Auto clean mode indicator."""
        return CleaningStatus(self.data["clean"])

    @property
    def total_running_duration(self) -> timedelta:
        """Total running duration in hours."""
        return timedelta(hours=self.data["running_duration"])

    @property
    def fan_speed_percent(self) -> int:
        """Current fan speed in percent."""
        return self.data["fan_speed_percent"]

    @property
    def timer(self) -> TimerStatus:
        """Countdown timer indicator."""
        return TimerStatus(self.data["timer"])


class AirConditionerMiot(MiotDevice):
    """Main class representing the air conditioner which uses MIoT protocol."""

    mapping = _MAPPING

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "Target Temperature: {result.target_temperature} ℃\n"
            "ECO Mode: {result.eco}\n"
            "Heater: {result.heater}\n"
            "Dryer: {result.dryer}\n"
            "Sleep Mode: {result.sleep_mode}\n"
            "Fan Speed: {result.fan_speed}\n"
            "Vertical Swing: {result.vertical_swing}\n"
            "Room Temperature: {result.temperature} ℃\n"
            "Buzzer: {result.buzzer}\n"
            "LED: {result.led}\n"
            "Electricity: {result.electricity}kWh\n"
            "Clean: {result.clean}\n"
            "Running Duration: {result.total_running_duration}\n"
            "Fan percent: {result.fan_speed_percent}\n"
            "Timer: {result.timer}\n",
        )
    )
    def status(self) -> AirConditionerMiotStatus:
        """Retrieve properties."""

        return AirConditionerMiotStatus(
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
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting operation mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set operation mode."""
        return self.set_property("mode", mode.value)

    @command(
        click.argument("target_temperature", type=float),
        default_output=format_output(
            "Setting target temperature to {target_temperature}"
        ),
    )
    def set_target_temperature(self, target_temperature: float):
        """Set target temperature in Celsius."""
        if (
            target_temperature < 16.0
            or target_temperature > 31.0
            or target_temperature % 0.5 != 0
        ):
            raise AirConditionerMiotException(
                "Invalid target temperature: %s" % target_temperature
            )
        return self.set_property("target_temperature", target_temperature)

    @command(
        click.argument("eco", type=bool),
        default_output=format_output(
            lambda eco: "Turning on ECO mode" if eco else "Turning off ECO mode"
        ),
    )
    def set_eco(self, eco: bool):
        """Turn ECO mode on/off."""
        return self.set_property("eco", eco)

    @command(
        click.argument("heater", type=bool),
        default_output=format_output(
            lambda heater: "Turning on heater" if heater else "Turning off heater"
        ),
    )
    def set_heater(self, heater: bool):
        """Turn aux heater mode on/off."""
        return self.set_property("heater", heater)

    @command(
        click.argument("dryer", type=bool),
        default_output=format_output(
            lambda dryer: "Turning on dryer" if dryer else "Turning off dryer"
        ),
    )
    def set_dryer(self, dryer: bool):
        """Turn aux dryer mode on/off."""
        return self.set_property("dryer", dryer)

    @command(
        click.argument("sleep_mode", type=bool),
        default_output=format_output(
            lambda sleep_mode: "Turning on sleep mode"
            if sleep_mode
            else "Turning off sleep mode"
        ),
    )
    def set_sleep_mode(self, sleep_mode: bool):
        """Turn sleep mode on/off."""
        return self.set_property("sleep_mode", sleep_mode)

    @command(
        click.argument("fan_speed", type=EnumType(FanSpeed)),
        default_output=format_output("Setting fan speed to {fan_speed}"),
    )
    def set_fan_speed(self, fan_speed: FanSpeed):
        """Set fan speed."""
        return self.set_property("fan_speed", fan_speed.value)

    @command(
        click.argument("vertical_swing", type=bool),
        default_output=format_output(
            lambda vertical_swing: "Turning on vertical swing"
            if vertical_swing
            else "Turning off vertical swing"
        ),
    )
    def set_vertical_swing(self, vertical_swing: bool):
        """Turn vertical swing on/off."""
        return self.set_property("vertical_swing", vertical_swing)

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        return self.set_property("led", led)

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
        click.argument("percent", type=int),
        default_output=format_output("Setting fan percent to {percent}%"),
    )
    def set_fan_speed_percent(self, fan_speed_percent):
        """Set fan speed in percent, should be  between 1 to 100 or 101(auto)."""
        if fan_speed_percent < 1 or fan_speed_percent > 101:
            raise AirConditionerMiotException(
                "Invalid fan percent: %s" % fan_speed_percent
            )
        return self.set_property("fan_speed_percent", fan_speed_percent)

    @command(
        click.argument("minutes", type=int),
        click.argument("delay_on", type=bool),
        default_output=format_output(
            lambda minutes, delay_on: "Setting timer to delay on after "
            + str(minutes)
            + " minutes"
            if delay_on
            else "Setting timer to delay off after " + str(minutes) + " minutes"
        ),
    )
    def set_timer(self, minutes, delay_on):
        """Set countdown timer minutes and if it would be turned on after timeout.

        Set minutes to 0 would disable the timer.
        """
        return self.set_property(
            "timer", ",".join(["1", str(minutes), str(int(delay_on))])
        )

    @command(
        click.argument("clean", type=bool),
        default_output=format_output(
            lambda clean: "Begin auto cleanning" if clean else "Abort auto cleaning"
        ),
    )
    def set_clean(self, clean):
        """Start or abort clean mode."""
        return self.set_property("clean", str(int(clean)))
