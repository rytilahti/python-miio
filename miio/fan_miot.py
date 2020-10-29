import enum
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .fan_common import FanException, MoveDirection, OperationMode
from .miot_device import MiotDevice

MODEL_FAN_P9 = "dmaker.fan.p9"
MODEL_FAN_P10 = "dmaker.fan.p10"

MIOT_MAPPING = {
    MODEL_FAN_P9: {
        # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:fan:0000A005:dmaker-p9:1
        "power": {"siid": 2, "piid": 1},
        "fan_level": {"siid": 2, "piid": 2},
        "child_lock": {"siid": 3, "piid": 1},
        "fan_speed": {"siid": 2, "piid": 11},
        "swing_mode": {"siid": 2, "piid": 5},
        "swing_mode_angle": {"siid": 2, "piid": 6},
        "power_off_time": {"siid": 2, "piid": 8},
        "buzzer": {"siid": 2, "piid": 7},
        "light": {"siid": 2, "piid": 9},
        "mode": {"siid": 2, "piid": 4},
        "set_move": {"siid": 2, "piid": 10},
    },
    MODEL_FAN_P10: {
        # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:fan:0000A005:dmaker-p10:1
        "power": {"siid": 2, "piid": 1},
        "fan_level": {"siid": 2, "piid": 2},
        "child_lock": {"siid": 3, "piid": 1},
        "fan_speed": {"siid": 2, "piid": 10},
        "swing_mode": {"siid": 2, "piid": 4},
        "swing_mode_angle": {"siid": 2, "piid": 5},
        "power_off_time": {"siid": 2, "piid": 6},
        "buzzer": {"siid": 2, "piid": 8},
        "light": {"siid": 2, "piid": 7},
        "mode": {"siid": 2, "piid": 3},
        "set_move": {"siid": 2, "piid": 9},
    },
}


class OperationModeMiot(enum.Enum):
    Normal = 0
    Nature = 1


class FanStatusMiot:
    """Container for status reports from the Xiaomi Mi Smart Pedestal Fan DMaker P9/P10."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a FanMiot (dmaker.fan.p10):

        {
          'id': 1,
          'result': [
            {'did': 'power', 'siid': 2, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'fan_level', 'siid': 2, 'piid': 2, 'code': 0, 'value': 2},
            {'did': 'child_lock', 'siid': 3, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'fan_speed', 'siid': 2, 'piid': 10, 'code': 0, 'value': 54},
            {'did': 'swing_mode', 'siid': 2, 'piid': 4, 'code': 0, 'value': False},
            {'did': 'swing_mode_angle', 'siid': 2, 'piid': 5, 'code': 0, 'value': 30},
            {'did': 'power_off_time', 'siid': 2, 'piid': 6, 'code': 0, 'value': 0},
            {'did': 'buzzer', 'siid': 2, 'piid': 8, 'code': 0, 'value': False},
            {'did': 'light', 'siid': 2, 'piid': 7, 'code': 0, 'value': True},
            {'did': 'mode', 'siid': 2, 'piid': 3, 'code': 0, 'value': 0},
            {'did': 'set_move', 'siid': 2, 'piid': 9, 'code': -4003}
          ],
          'exe_time': 280
        }
        """
        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.data["power"] else "off"

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return self.data["power"]

    @property
    def mode(self) -> OperationMode:
        """Operation mode."""
        return OperationMode[OperationModeMiot(self.data["mode"]).name]

    @property
    def speed(self) -> int:
        """Speed of the motor."""
        return self.data["fan_speed"]

    @property
    def oscillate(self) -> bool:
        """True if oscillation is enabled."""
        return self.data["swing_mode"]

    @property
    def angle(self) -> int:
        """Oscillation angle."""
        return self.data["swing_mode_angle"]

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in seconds."""
        return self.data["power_off_time"]

    @property
    def led(self) -> bool:
        """True if LED is turned on, if available."""
        return self.data["light"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"]

    @property
    def child_lock(self) -> bool:
        """True if child lock is on."""
        return self.data["child_lock"]

    def __repr__(self) -> str:
        s = (
            "<FanStatus power=%s, "
            "mode=%s, "
            "speed=%s, "
            "oscillate=%s, "
            "angle=%s, "
            "led=%s, "
            "buzzer=%s, "
            "child_lock=%s, "
            "delay_off_countdown=%s>"
            % (
                self.power,
                self.mode,
                self.speed,
                self.oscillate,
                self.angle,
                self.led,
                self.buzzer,
                self.child_lock,
                self.delay_off_countdown,
            )
        )
        return s


class FanMiot(MiotDevice):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FAN_P10,
    ) -> None:
        if model in MIOT_MAPPING:
            self.model = model
        else:
            raise FanException("Invalid FanMiot model: %s" % model)
        super().__init__(MIOT_MAPPING[model], ip, token, start_id, debug, lazy_discover)

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Operation mode: {result.mode}\n"
            "Speed: {result.speed}\n"
            "Oscillate: {result.oscillate}\n"
            "Angle: {result.angle}\n"
            "LED: {result.led}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Power-off time: {result.delay_off_countdown}\n",
        )
    )
    def status(self) -> FanStatusMiot:
        """Retrieve properties."""
        return FanStatusMiot(
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
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.set_property("mode", OperationModeMiot[mode.name].value)

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed to {speed}"),
    )
    def set_speed(self, speed: int):
        """Set speed."""
        if speed < 0 or speed > 100:
            raise FanException("Invalid speed: %s" % speed)

        return self.set_property("fan_speed", speed)

    @command(
        click.argument("angle", type=int),
        default_output=format_output("Setting angle to {angle}"),
    )
    def set_angle(self, angle: int):
        """Set the oscillation angle."""
        if angle not in [30, 60, 90, 120, 140]:
            raise FanException(
                "Unsupported angle. Supported values: 30, 60, 90, 120, 140"
            )

        return self.set_property("swing_mode_angle", angle)

    @command(
        click.argument("oscillate", type=bool),
        default_output=format_output(
            lambda oscillate: "Turning on oscillate"
            if oscillate
            else "Turning off oscillate"
        ),
    )
    def set_oscillate(self, oscillate: bool):
        """Set oscillate on/off."""
        if oscillate:
            return self.set_property("swing_mode", True)
        else:
            return self.set_property("swing_mode", False)

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        if led:
            return self.set_property("light", True)
        else:
            return self.set_property("light", False)

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if buzzer:
            return self.set_property("buzzer", True)
        else:
            return self.set_property("buzzer", False)

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
        click.argument("minutes", type=int),
        default_output=format_output("Setting delayed turn off to {minutes} minutes"),
    )
    def delay_off(self, minutes: int):
        """Set delay off minutes."""

        if minutes < 0:
            raise FanException("Invalid value for a delayed turn off: %s" % minutes)

        return self.set_property("power_off_time", minutes)

    @command(
        click.argument("direction", type=EnumType(MoveDirection)),
        default_output=format_output("Rotating the fan to the {direction}"),
    )
    def set_rotate(self, direction: MoveDirection):
        return self.set_property("set_move", [direction.value])


class FanP9(FanMiot):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=MODEL_FAN_P9)


class FanP10(FanMiot):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=MODEL_FAN_P10)
