import enum
from typing import Any, Dict, Optional

import click

from miio import DeviceStatus, MiotDevice
from miio.click_common import EnumType, command, format_output


class OperationMode(enum.Enum):
    Normal = "normal"
    Nature = "nature"
    Sleep = "sleep"


class MoveDirection(enum.Enum):
    Left = "left"
    Right = "right"


MODEL_FAN_P9 = "dmaker.fan.p9"
MODEL_FAN_P10 = "dmaker.fan.p10"
MODEL_FAN_P11 = "dmaker.fan.p11"
MODEL_FAN_P15 = "dmaker.fan.p15"
MODEL_FAN_P18 = "dmaker.fan.p18"
MODEL_FAN_P33 = "dmaker.fan.p33"
MODEL_FAN_P45 = "dmaker.fan.p45"
MODEL_FAN_1C = "dmaker.fan.1c"


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
    MODEL_FAN_P11: {
        # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:fan:0000A005:dmaker-p11:1
        "power": {"siid": 2, "piid": 1},
        "fan_level": {"siid": 2, "piid": 2},
        "mode": {"siid": 2, "piid": 3},
        "swing_mode": {"siid": 2, "piid": 4},
        "swing_mode_angle": {"siid": 2, "piid": 5},
        "fan_speed": {"siid": 2, "piid": 6},
        "light": {"siid": 4, "piid": 1},
        "buzzer": {"siid": 5, "piid": 1},
        # "device_fault": {"siid": 6, "piid": 2},
        "child_lock": {"siid": 7, "piid": 1},
        "power_off_time": {"siid": 3, "piid": 1},
        "set_move": {"siid": 6, "piid": 1},
    },
    MODEL_FAN_P33: {
        # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:fan:0000A005:dmaker-p33:1
        "power": {"siid": 2, "piid": 1},
        "fan_level": {"siid": 2, "piid": 2},
        "mode": {"siid": 2, "piid": 3},
        "swing_mode": {"siid": 2, "piid": 4},
        "swing_mode_angle": {"siid": 2, "piid": 5},
        "fan_speed": {"siid": 2, "piid": 6},
        "light": {"siid": 4, "piid": 1},
        "buzzer": {"siid": 5, "piid": 1},
        # "device_fault": {"siid": 6, "piid": 2},
        "child_lock": {"siid": 7, "piid": 1},
        "power_off_time": {"siid": 3, "piid": 1},
        "set_move": {"siid": 6, "piid": 1},
    },
    MODEL_FAN_P45: {
        # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:fan:0000A005:dmaker-p45:1
        "power": {"siid": 2, "piid": 1},
        "fan_level": {"siid": 2, "piid": 2},
        "mode": {"siid": 2, "piid": 3},
        "swing_mode": {"siid": 2, "piid": 4},
        "swing_mode_angle": {"siid": 2, "piid": 5},
        "power_off_time": {"siid": 3, "piid": 1},
        "light": {"siid": 4, "piid": 1},
        "buzzer": {"siid": 5, "piid": 1},
        "child_lock": {"siid": 7, "piid": 1},
        "fan_speed": {"siid": 8, "piid": 1},
    },
}


# These mappings are based on user reports and may not cover all features
MIOT_MAPPING[MODEL_FAN_P15] = MIOT_MAPPING[MODEL_FAN_P11]  # see #1354
MIOT_MAPPING[MODEL_FAN_P18] = MIOT_MAPPING[MODEL_FAN_P10]  # see #1341


FAN1C_MAPPINGS = {
    MODEL_FAN_1C: {
        # https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:fan:0000A005:dmaker-1c:1
        "power": {"siid": 2, "piid": 1},
        "fan_level": {"siid": 2, "piid": 2},
        "child_lock": {"siid": 3, "piid": 1},
        "swing_mode": {"siid": 2, "piid": 3},
        "power_off_time": {"siid": 2, "piid": 10},
        "buzzer": {"siid": 2, "piid": 11},
        "light": {"siid": 2, "piid": 12},
        "mode": {"siid": 2, "piid": 7},
    }
}

SUPPORTED_ANGLES = {
    MODEL_FAN_P9: [30, 60, 90, 120, 150],
    MODEL_FAN_P10: [30, 60, 90, 120, 140],
    MODEL_FAN_P11: [30, 60, 90, 120, 140],
    MODEL_FAN_P15: [30, 60, 90, 120, 140],  # mapped to P11
    MODEL_FAN_P18: [30, 60, 90, 120, 140],  # mapped to P10
    MODEL_FAN_P33: [30, 60, 90, 120, 140],
    MODEL_FAN_P45: [30, 60, 90, 120, 150],
}


class OperationModeMiot(enum.Enum):
    Normal = 0
    Nature = 1


class OperationModeMiotP45(enum.Enum):
    Normal = 0
    Nature = 1
    Sleep = 2


class FanStatusMiot(DeviceStatus):
    """Container for status reports for Xiaomi Mi Smart Pedestal Fan DMaker P9/P10."""

    def __init__(self, data: Dict[str, Any], model: str) -> None:
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
        self.model = model

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
        if self.model == MODEL_FAN_P45:
            return OperationMode[OperationModeMiotP45(self.data["mode"]).name]
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
        """Countdown until turning off in minutes."""
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


class FanStatus1C(DeviceStatus):
    """Container for status reports for Xiaomi Mi Smart Pedestal Fan DMaker 1C."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a Fan1C (dmaker.fan.1c):

        {
          'id': 1,
          'result': [
            {'did': 'power', 'siid': 2, 'piid': 1, 'code': 0, 'value': True},
            {'did': 'fan_level', 'siid': 2, 'piid': 2, 'code': 0, 'value': 2},
            {'did': 'child_lock', 'siid': 3, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'swing_mode', 'siid': 2, 'piid': 3, 'code': 0, 'value': False},
            {'did': 'power_off_time', 'siid': 2, 'piid': 10, 'code': 0, 'value': 0},
            {'did': 'buzzer', 'siid': 2, 'piid': 11, 'code': 0, 'value': False},
            {'did': 'light', 'siid': 2, 'piid': 12, 'code': 0, 'value': True},
            {'did': 'mode', 'siid': 2, 'piid': 7, 'code': 0, 'value': 0},
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
        return self.data["fan_level"]

    @property
    def oscillate(self) -> bool:
        """True if oscillation is enabled."""
        return self.data["swing_mode"]

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in minutes."""
        return self.data["power_off_time"]

    @property
    def led(self) -> bool:
        """True if LED is turned on."""
        return self.data["light"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"]

    @property
    def child_lock(self) -> bool:
        """True if child lock is on."""
        return self.data["child_lock"]


class FanMiot(MiotDevice):
    _mappings = MIOT_MAPPING

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
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        if self.model == MODEL_FAN_P45:
            return self.set_property("mode", OperationModeMiotP45[mode.name].value)

        return self.set_property("mode", OperationModeMiot[mode.name].value)

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed to {speed}"),
    )
    def set_speed(self, speed: int):
        """Set speed."""
        if speed < 0 or speed > 100:
            raise ValueError("Invalid speed: %s" % speed)

        return self.set_property("fan_speed", speed)

    @command(
        click.argument("angle", type=int),
        default_output=format_output("Setting angle to {angle}"),
    )
    def set_angle(self, angle: int):
        """Set the oscillation angle."""
        if angle not in SUPPORTED_ANGLES[self.model]:
            raise ValueError(
                "Unsupported angle. Supported values: "
                + ", ".join(f"{i}" for i in SUPPORTED_ANGLES[self.model])
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
        return self.set_property("swing_mode", oscillate)

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        return self.set_property("light", led)

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
        click.argument("minutes", type=int),
        default_output=format_output("Setting delayed turn off to {minutes} minutes"),
    )
    def delay_off(self, minutes: int):
        """Set delay off minutes."""

        if minutes < 0 or minutes > 480:
            raise ValueError("Invalid value for a delayed turn off: %s" % minutes)

        return self.set_property("power_off_time", minutes)

    @command(
        click.argument("direction", type=EnumType(MoveDirection)),
        default_output=format_output("Rotating the fan to the {direction}"),
    )
    def set_rotate(self, direction: MoveDirection):
        """Rotate fan to given direction."""
        # Values for: P9,P10,P11,P15,P18,...
        # { "value": 0, "description": "NONE" },
        # { "value": 1, "description": "LEFT" },
        # { "value": 2, "description": "RIGHT" }
        value = 0
        if direction == MoveDirection.Left:
            value = 1
        elif direction == MoveDirection.Right:
            value = 2
        return self.set_property("set_move", value)


class Fan1C(MiotDevice):
    # TODO Fan1C should be merged to FanMiot, or moved into its separate file
    _mappings = FAN1C_MAPPINGS

    def __init__(
        self,
        ip: Optional[str] = None,
        token: Optional[str] = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        timeout: Optional[int] = None,
        model: str = MODEL_FAN_1C,
    ) -> None:
        super().__init__(
            ip, token, start_id, debug, lazy_discover, timeout=timeout, model=model
        )

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Operation mode: {result.mode}\n"
            "Speed: {result.speed}\n"
            "Oscillate: {result.oscillate}\n"
            "LED: {result.led}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Power-off time: {result.delay_off_countdown}\n",
        )
    )
    def status(self) -> FanStatus1C:
        """Retrieve properties."""
        return FanStatus1C(
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
        if speed not in (1, 2, 3):
            raise ValueError("Invalid speed: %s" % speed)

        return self.set_property("fan_level", speed)

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
        return self.set_property("swing_mode", oscillate)

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        return self.set_property("light", led)

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
        click.argument("minutes", type=int),
        default_output=format_output("Setting delayed turn off to {minutes} minutes"),
    )
    def delay_off(self, minutes: int):
        """Set delay off minutes."""

        if minutes < 0 or minutes > 480:
            raise ValueError("Invalid value for a delayed turn off: %s" % minutes)

        return self.set_property("power_off_time", minutes)
