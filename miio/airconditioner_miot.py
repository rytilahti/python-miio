import enum
import logging
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .exceptions import DeviceException
from .miot_device import MiotDevice

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
    "fan_level": {"siid": 3, "piid": 2},
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
    "fan_percent": {"siid": 10, "piid": 1},
    "timer": {"siid": 10, "piid": 3},
}


class AirConditionerMiotException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Cool = 2
    Dry = 3
    Fan = 4
    Heat = 5


class FanLevel(enum.Enum):
    Auto = 0
    Level1 = 1
    Level2 = 2
    Level3 = 3
    Level4 = 4
    Level5 = 5
    Level6 = 6
    Level7 = 7


class AirConditionerMiotStatus:
    """Container for status reports from the air conditioner which uses MIoT protocol."""

    def __init__(self, data: Dict[str, Any]) -> None:
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
    def fan_level(self) -> FanLevel:
        """Current Fan level."""
        return FanLevel(self.data["fan_level"])

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
    def clean(self) -> str:
        """Auto clean mode indicator."""
        return self.data["clean"]

    @property
    def running_duration(self) -> float:
        """Total running duration in hours."""
        return self.data["running_duration"]

    @property
    def fan_percent(self) -> int:
        """Current fan level in percent."""
        return self.data["fan_percent"]

    @property
    def timer(self) -> str:
        """Timer indicator."""
        return self.data["timer"]

    def __repr__(self) -> str:
        s = (
            "<AirConditionerMiotStatus power=%s, "
            "mode=%s, "
            "target_temperature=%s, "
            "eco=%s, "
            "heater=%s, "
            "dryer=%s, "
            "sleep_mode=%s, "
            "fan_level=%s, "
            "vertical_swing=%s, "
            "temperature=%s, "
            "buzzer=%s, "
            "led=%s"
            "electricity=%s"
            "clean=%s"
            "running_duration=%s"
            "fan_percent=%s"
            "timer=%s"
            % (
                self.power,
                self.mode,
                self.target_temperature,
                self.eco,
                self.heater,
                self.dryer,
                self.sleep_mode,
                self.fan_level,
                self.vertical_swing,
                self.temperature,
                self.buzzer,
                self.led,
                self.electricity,
                self.clean,
                self.running_duration,
                self.fan_percent,
                self.timer,
            )
        )
        return s

    def __json__(self):
        return self.data


class AirConditionerMiot(MiotDevice):
    """Main class representing the air conditioner which uses MIoT protocol."""

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
            "Mode: {result.mode}\n"
            "Target Temperature: {result.target_temperature} ℃\n"
            "ECO Mode: {result.eco}\n"
            "Heater: {result.heater}\n"
            "Dryer: {result.dryer}\n"
            "Sleep Mode: {result.sleep_mode}\n"
            "Fan Level: {result.fan_level}\n"
            "Vertical Swing: {result.vertical_swing}\n"
            "Room Temperature: {result.temperature} ℃\n"
            "Buzzer: {result.buzzer}\n"
            "LED: {result.led}\n"
            "Electricity: {result.electricity}kWh\n"
            "Clean: {result.clean}\n"
            "Running Duration: {result.running_duration}h\n"
            "Fan percent: {result.fan_percent}\n"
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
        click.argument("fan_level", type=EnumType(FanLevel)),
        default_output=format_output("Setting fan level to {fan_level}"),
    )
    def set_fan_level(self, fan_level: FanLevel):
        """Set fan level."""
        return self.set_property("fan_level", fan_level.value)

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
        click.argument("fan_percent", type=int),
        default_output=format_output("Setting fan percent to {fan_percent}"),
    )
    def set_fan_percent(self, fan_percent):
        """Set fan level in percent, should be  between 1 to 100 or 101(auto)."""
        if fan_percent < 1 or fan_percent > 101:
            raise AirConditionerMiotException("Invalid fan percent: %s" % fan_percent)
        return self.set_property("fan_percent", fan_percent)

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
        """Set timer."""
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
        """Set clean mode."""
        return self.set_property("clean", str(int(clean)))
