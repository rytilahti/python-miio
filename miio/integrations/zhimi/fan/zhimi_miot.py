import enum
from typing import Any, Dict

import click

from miio import DeviceException, DeviceStatus, MiotDevice
from miio.click_common import EnumType, command, format_output
from miio.utils import deprecated


class OperationMode(enum.Enum):
    Normal = "normal"
    Nature = "nature"


class MoveDirection(enum.Enum):
    Left = "left"
    Right = "right"


MODEL_FAN_ZA5 = "zhimi.fan.za5"

MIOT_MAPPING = {
    MODEL_FAN_ZA5: {
        # https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:fan:0000A005:zhimi-za5:1
        "power": {"siid": 2, "piid": 1},
        "fan_level": {"siid": 2, "piid": 2},
        "swing_mode": {"siid": 2, "piid": 3},
        "swing_mode_angle": {"siid": 2, "piid": 5},
        "mode": {"siid": 2, "piid": 7},
        "power_off_time": {"siid": 2, "piid": 10},
        "anion": {"siid": 2, "piid": 11},
        "child_lock": {"siid": 3, "piid": 1},
        "light": {"siid": 4, "piid": 3},
        "buzzer": {"siid": 5, "piid": 1},
        "buttons_pressed": {"siid": 6, "piid": 1},
        "battery_supported": {"siid": 6, "piid": 2},
        "set_move": {"siid": 6, "piid": 3},
        "speed_rpm": {"siid": 6, "piid": 4},
        "powersupply_attached": {"siid": 6, "piid": 5},
        "fan_speed": {"siid": 6, "piid": 8},
        "humidity": {"siid": 7, "piid": 1},
        "temperature": {"siid": 7, "piid": 7},
    },
}

SUPPORTED_ANGLES = {
    MODEL_FAN_ZA5: [30, 60, 90, 120],
}


class OperationModeFanZA5(enum.Enum):
    Nature = 0
    Normal = 1


class FanStatusZA5(DeviceStatus):
    """Container for status reports for FanZA5."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of FanZA5 (zhimi.fan.za5):

        {'code': -4005, 'did': 'set_move', 'piid': 3, 'siid': 6},
        {'code': 0, 'did': 'anion', 'piid': 11, 'siid': 2, 'value': True},
        {'code': 0, 'did': 'battery_supported', 'piid': 2, 'siid': 6, 'value': False},
        {'code': 0, 'did': 'buttons_pressed', 'piid': 1, 'siid': 6, 'value': 0},
        {'code': 0, 'did': 'buzzer', 'piid': 1, 'siid': 5, 'value': False},
        {'code': 0, 'did': 'child_lock', 'piid': 1, 'siid': 3, 'value': False},
        {'code': 0, 'did': 'fan_level', 'piid': 2, 'siid': 2, 'value': 4},
        {'code': 0, 'did': 'fan_speed', 'piid': 8, 'siid': 6, 'value': 100},
        {'code': 0, 'did': 'humidity', 'piid': 1, 'siid': 7, 'value': 55},
        {'code': 0, 'did': 'light', 'piid': 3, 'siid': 4, 'value': 100},
        {'code': 0, 'did': 'mode', 'piid': 7, 'siid': 2, 'value': 0},
        {'code': 0, 'did': 'power', 'piid': 1, 'siid': 2, 'value': False},
        {'code': 0, 'did': 'power_off_time', 'piid': 10, 'siid': 2, 'value': 0},
        {'code': 0, 'did': 'powersupply_attached', 'piid': 5, 'siid': 6, 'value': True},
        {'code': 0, 'did': 'speed_rpm', 'piid': 4, 'siid': 6, 'value': 0},
        {'code': 0, 'did': 'swing_mode', 'piid': 3, 'siid': 2, 'value': True},
        {'code': 0, 'did': 'swing_mode_angle', 'piid': 5, 'siid': 2, 'value': 60},
        {'code': 0, 'did': 'temperature', 'piid': 7, 'siid': 7, 'value': 26.4},
        """
        self.data = data

    @property
    def ionizer(self) -> bool:
        """True if negative ions generation is enabled."""
        return self.data["anion"]

    @property
    def battery_supported(self) -> bool:
        """True if battery is supported."""
        return self.data["battery_supported"]

    @property
    def buttons_pressed(self) -> str:
        """What buttons on the fan are pressed now."""
        code = self.data["buttons_pressed"]
        if code == 0:
            return "None"
        if code == 1:
            return "Power"
        if code == 2:
            return "Swing"
        return "Unknown"

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"]

    @property
    def child_lock(self) -> bool:
        """True if child lock if on."""
        return self.data["child_lock"]

    @property
    def fan_level(self) -> int:
        """Fan level (1-4)."""
        return self.data["fan_level"]

    @property  # type: ignore
    @deprecated("Use speed()")
    def fan_speed(self) -> int:
        """Fan speed (1-100)."""
        return self.speed

    @property
    def speed(self) -> int:
        """Fan speed (1-100)."""
        return self.data["fan_speed"]

    @property
    def humidity(self) -> int:
        """Air humidity in percent."""
        return self.data["humidity"]

    @property
    def led_brightness(self) -> int:
        """LED brightness (1-100)."""
        return self.data["light"]

    @property
    def mode(self) -> OperationMode:
        """Operation mode (normal or nature)."""
        return OperationMode[OperationModeFanZA5(self.data["mode"]).name]

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.data["power"] else "off"

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return self.data["power"]

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in minutes."""
        return self.data["power_off_time"]

    @property
    def powersupply_attached(self) -> bool:
        """True is power supply is attached."""
        return self.data["powersupply_attached"]

    @property
    def speed_rpm(self) -> int:
        """Fan rotations per minute."""
        return self.data["speed_rpm"]

    @property
    def oscillate(self) -> bool:
        """True if oscillation is enabled."""
        return self.data["swing_mode"]

    @property
    def angle(self) -> int:
        """Oscillation angle."""
        return self.data["swing_mode_angle"]

    @property
    def temperature(self) -> Any:
        """Air temperature (degree celsius)."""
        return self.data["temperature"]


class FanZA5(MiotDevice):
    _mappings = MIOT_MAPPING

    @command(
        default_output=format_output(
            "",
            "Angle: {result.angle}\n"
            "Battery Supported: {result.battery_supported}\n"
            "Buttons Pressed: {result.buttons_pressed}\n"
            "Buzzer: {result.buzzer}\n"
            "Child Lock: {result.child_lock}\n"
            "Delay Off Countdown: {result.delay_off_countdown}\n"
            "Fan Level: {result.fan_level}\n"
            "Fan Speed: {result.fan_speed}\n"
            "Humidity: {result.humidity}\n"
            "Ionizer: {result.ionizer}\n"
            "LED Brightness: {result.led_brightness}\n"
            "Mode: {result.mode.name}\n"
            "Oscillate: {result.oscillate}\n"
            "Power: {result.power}\n"
            "Powersupply Attached: {result.powersupply_attached}\n"
            "Speed RPM: {result.speed_rpm}\n"
            "Temperature: {result.temperature}\n",
        )
    )
    def status(self) -> FanStatusZA5:
        """Retrieve properties."""
        return FanStatusZA5(
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
        click.argument("on", type=bool),
        default_output=format_output(
            lambda on: "Turning on ionizer" if on else "Turning off ionizer"
        ),
    )
    def set_ionizer(self, on: bool):
        """Set ionizer on/off."""
        return self.set_property("anion", on)

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed to {speed}%"),
    )
    def set_speed(self, speed: int):
        """Set fan speed."""
        if speed < 1 or speed > 100:
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
        click.argument("brightness", type=int),
        default_output=format_output("Setting LED brightness to {brightness}%"),
    )
    def set_led_brightness(self, brightness: int):
        """Set LED brightness."""
        if brightness < 0 or brightness > 100:
            raise ValueError("Invalid brightness: %s" % brightness)

        return self.set_property("light", brightness)

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.set_property("mode", OperationModeFanZA5[mode.name].value)

    @command(
        click.argument("seconds", type=int),
        default_output=format_output("Setting delayed turn off to {seconds} seconds"),
    )
    def delay_off(self, seconds: int):
        """Set delay off seconds."""

        if seconds < 0 or seconds > 10 * 60 * 60:
            raise ValueError("Invalid value for a delayed turn off: %s" % seconds)

        return self.set_property("power_off_time", seconds)

    @command(
        click.argument("direction", type=EnumType(MoveDirection)),
        default_output=format_output("Rotating the fan to the {direction}"),
    )
    def set_rotate(self, direction: MoveDirection):
        """Rotate fan 7.5 degrees horizontally to given direction."""
        status = self.status()
        if status.oscillate:
            raise DeviceException(
                "Rotation requires oscillation to be turned off to function."
            )
        return self.set_property("set_move", direction.name.lower())
