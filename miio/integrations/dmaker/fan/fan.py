import enum
from typing import Any, Dict, Optional

import click

from miio import Device, DeviceStatus
from miio.click_common import EnumType, command, format_output


class MoveDirection(enum.Enum):
    Left = "left"
    Right = "right"


class OperationMode(enum.Enum):
    Normal = "normal"
    Nature = "nature"


MODEL_FAN_P5 = "dmaker.fan.p5"

AVAILABLE_PROPERTIES_P5 = [
    "power",
    "mode",
    "speed",
    "roll_enable",
    "roll_angle",
    "time_off",
    "light",
    "beep_sound",
    "child_lock",
]

AVAILABLE_PROPERTIES = {
    MODEL_FAN_P5: AVAILABLE_PROPERTIES_P5,
}


class FanStatusP5(DeviceStatus):
    """Container for status reports from the Xiaomi Mi Smart Pedestal Fan DMaker P5."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a Fan (dmaker.fan.p5):

        {'power': False, 'mode': 'normal', 'speed': 35, 'roll_enable': False,
         'roll_angle': 140, 'time_off': 0, 'light': True, 'beep_sound': False,
         'child_lock': False}
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
        return OperationMode(self.data["mode"])

    @property
    def speed(self) -> int:
        """Speed of the motor."""
        return self.data["speed"]

    @property
    def oscillate(self) -> bool:
        """True if oscillation is enabled."""
        return self.data["roll_enable"]

    @property
    def angle(self) -> int:
        """Oscillation angle."""
        return self.data["roll_angle"]

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in seconds."""
        return self.data["time_off"]

    @property
    def led(self) -> bool:
        """True if LED is turned on, if available."""
        return self.data["light"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["beep_sound"]

    @property
    def child_lock(self) -> bool:
        """True if child lock is on."""
        return self.data["child_lock"]


class FanP5(Device):
    """Support for dmaker.fan.p5."""

    _supported_models = [MODEL_FAN_P5]

    def __init__(
        self,
        ip: Optional[str] = None,
        token: Optional[str] = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        timeout: Optional[int] = None,
        model: str = MODEL_FAN_P5,
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
            "Angle: {result.angle}\n"
            "LED: {result.led}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Power-off time: {result.delay_off_countdown}\n",
        )
    )
    def status(self) -> FanStatusP5:
        """Retrieve properties."""
        properties = AVAILABLE_PROPERTIES[self.model]
        values = self.get_properties(properties, max_properties=15)

        return FanStatusP5(dict(zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("s_power", [True])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("s_power", [False])

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.send("s_mode", [mode.value])

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed to {speed}"),
    )
    def set_speed(self, speed: int):
        """Set speed."""
        if speed < 0 or speed > 100:
            raise ValueError("Invalid speed: %s" % speed)

        return self.send("s_speed", [speed])

    @command(
        click.argument("angle", type=int),
        default_output=format_output("Setting angle to {angle}"),
    )
    def set_angle(self, angle: int):
        """Set the oscillation angle."""
        if angle not in [30, 60, 90, 120, 140]:
            raise ValueError(
                "Unsupported angle. Supported values: 30, 60, 90, 120, 140"
            )

        return self.send("s_angle", [angle])

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
            return self.send("s_roll", [True])
        else:
            return self.send("s_roll", [False])

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        if led:
            return self.send("s_light", [True])
        else:
            return self.send("s_light", [False])

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if buzzer:
            return self.send("s_sound", [True])
        else:
            return self.send("s_sound", [False])

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        if lock:
            return self.send("s_lock", [True])
        else:
            return self.send("s_lock", [False])

    @command(
        click.argument("minutes", type=int),
        default_output=format_output("Setting delayed turn off to {minutes} minutes"),
    )
    def delay_off(self, minutes: int):
        """Set delay off minutes."""

        if minutes < 0:
            raise ValueError("Invalid value for a delayed turn off: %s" % minutes)

        return self.send("s_t_off", [minutes])

    @command(
        click.argument("direction", type=EnumType(MoveDirection)),
        default_output=format_output("Rotating the fan to the {direction}"),
    )
    def set_rotate(self, direction: MoveDirection):
        """Rotate the fan by -5/+5 degrees left/right."""
        return self.send("m_roll", [direction.value])
