import enum
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .fan_common import FanException, MoveDirection, OperationMode
from .miot_device import DeviceStatus, MiotDevice

MODEL_FAN_P9 = "dmaker.fan.p9"
MODEL_FAN_P10 = "dmaker.fan.p10"
MODEL_FAN_P11 = "dmaker.fan.p11"
MODEL_FAN_1C = "dmaker.fan.1c"
MODEL_FAN_ZA5 = "zhimi.fan.za5"

MIOT_MAPPING = {
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
    },
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
    MODEL_FAN_P9: [30, 60, 90, 120, 150],
    MODEL_FAN_P10: [30, 60, 90, 120, 140],
    MODEL_FAN_P11: [30, 60, 90, 120, 140],
    MODEL_FAN_ZA5: [30, 60, 90, 120],
}


class OperationModeMiot(enum.Enum):
    Normal = 0
    Nature = 1


class FanStatusMiot(DeviceStatus):
    """Container for status reports for Xiaomi Mi Smart Pedestal Fan DMaker P9/P10."""

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
        self.data = data
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
    mapping = MIOT_MAPPING[MODEL_FAN_P10]

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FAN_P10,
    ) -> None:
        if model not in MIOT_MAPPING:
            raise FanException("Invalid FanMiot model: %s" % model)

        super().__init__(ip, token, start_id, debug, lazy_discover)
        self.model = model

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
        if angle not in SUPPORTED_ANGLES[self.model]:
            raise FanException(
                "Unsupported angle. Supported values: "
                + ", ".join("{0}".format(i) for i in SUPPORTED_ANGLES[self.model])
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
            raise FanException("Invalid value for a delayed turn off: %s" % minutes)

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


class FanP9(FanMiot):
    mapping = MIOT_MAPPING[MODEL_FAN_P9]


class FanP10(FanMiot):
    mapping = MIOT_MAPPING[MODEL_FAN_P10]


class FanP11(FanMiot):
    mapping = MIOT_MAPPING[MODEL_FAN_P11]


class Fan1C(MiotDevice):
    mapping = MIOT_MAPPING[MODEL_FAN_1C]

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FAN_1C,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)
        self.model = model

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
            raise FanException("Invalid speed: %s" % speed)

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
            raise FanException("Invalid value for a delayed turn off: %s" % minutes)

        return self.set_property("power_off_time", minutes)


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

    @property
    def fan_speed(self) -> int:
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
    mapping = MIOT_MAPPING[MODEL_FAN_ZA5]

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FAN_ZA5,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)
        self.model = model

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
    def status(self):
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
            raise FanException("Invalid speed: %s" % speed)

        return self.set_property("fan_speed", speed)

    @command(
        click.argument("angle", type=int),
        default_output=format_output("Setting angle to {angle}"),
    )
    def set_angle(self, angle: int):
        """Set the oscillation angle."""
        if angle not in SUPPORTED_ANGLES[self.model]:
            raise FanException(
                "Unsupported angle. Supported values: "
                + ", ".join("{0}".format(i) for i in SUPPORTED_ANGLES[self.model])
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
            raise FanException("Invalid brightness: %s" % brightness)

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
            raise FanException("Invalid value for a delayed turn off: %s" % seconds)

        return self.set_property("power_off_time", seconds)

    @command(
        click.argument("direction", type=EnumType(MoveDirection)),
        default_output=format_output("Rotating the fan to the {direction}"),
    )
    def set_rotate(self, direction: MoveDirection):
        """Rotate fan 7.5 degrees horizontally to given direction."""
        status = self.status()
        if status.oscillate:
            raise FanException(
                "Rotation requires oscillation to be turned off to function."
            )
        return self.set_property("set_move", direction.name.lower())
