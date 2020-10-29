import logging
from typing import Any, Dict, Optional

import click

from .click_common import EnumType, command, format_output
from .device import Device
from .fan_common import FanException, LedBrightness, MoveDirection, OperationMode

_LOGGER = logging.getLogger(__name__)

MODEL_FAN_V2 = "zhimi.fan.v2"
MODEL_FAN_V3 = "zhimi.fan.v3"
MODEL_FAN_SA1 = "zhimi.fan.sa1"
MODEL_FAN_ZA1 = "zhimi.fan.za1"
MODEL_FAN_ZA3 = "zhimi.fan.za3"
MODEL_FAN_ZA4 = "zhimi.fan.za4"
MODEL_FAN_P5 = "dmaker.fan.p5"

AVAILABLE_PROPERTIES_COMMON = [
    "angle",
    "speed",
    "poweroff_time",
    "power",
    "ac_power",
    "angle_enable",
    "speed_level",
    "natural_level",
    "child_lock",
    "buzzer",
    "led_b",
    "use_time",
]

AVAILABLE_PROPERTIES_COMMON_V2_V3 = [
    "temp_dec",
    "humidity",
    "battery",
    "bat_charge",
    "button_pressed",
] + AVAILABLE_PROPERTIES_COMMON

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
    MODEL_FAN_V2: ["led", "bat_state"] + AVAILABLE_PROPERTIES_COMMON_V2_V3,
    MODEL_FAN_V3: AVAILABLE_PROPERTIES_COMMON_V2_V3,
    MODEL_FAN_SA1: AVAILABLE_PROPERTIES_COMMON,
    MODEL_FAN_ZA1: AVAILABLE_PROPERTIES_COMMON,
    MODEL_FAN_ZA3: AVAILABLE_PROPERTIES_COMMON,
    MODEL_FAN_ZA4: AVAILABLE_PROPERTIES_COMMON,
    MODEL_FAN_P5: AVAILABLE_PROPERTIES_P5,
}


class FanStatus:
    """Container for status reports from the Xiaomi Mi Smart Pedestal Fan."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Fan (zhimi.fan.v3):

        {'temp_dec': 232, 'humidity': 46, 'angle': 118, 'speed': 298,
         'poweroff_time': 0, 'power': 'on', 'ac_power': 'off', 'battery': 98,
         'angle_enable': 'off', 'speed_level': 1, 'natural_level': 0,
         'child_lock': 'off', 'buzzer': 'on', 'led_b': 1, 'led': None,
         'natural_enable': None, 'use_time': 0, 'bat_charge': 'complete',
         'bat_state': None, 'button_pressed':'speed'}

        Response of a Fan (zhimi.fan.sa1):
        {'angle': 120, 'speed': 277, 'poweroff_time': 0, 'power': 'on',
         'ac_power': 'on', 'angle_enable': 'off', 'speed_level': 1, 'natural_level': 2,
         'child_lock': 'off', 'buzzer': 0, 'led_b': 0, 'use_time': 2318}

        Response of a Fan (zhimi.fan.sa4):
        {'angle': 120, 'speed': 327, 'poweroff_time': 0, 'power': 'on',
         'ac_power': 'on', 'angle_enable': 'off', 'speed_level': 1, 'natural_level': 0,
         'child_lock': 'off', 'buzzer': 2, 'led_b': 0, 'use_time': 85}
        """
        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return self.power == "on"

    @property
    def humidity(self) -> Optional[int]:
        """Current humidity."""
        if "humidity" in self.data and self.data["humidity"] is not None:
            return self.data["humidity"]
        return None

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature, if available."""
        if "temp_dec" in self.data and self.data["temp_dec"] is not None:
            return self.data["temp_dec"] / 10.0
        return None

    @property
    def led(self) -> Optional[bool]:
        """True if LED is turned on, if available."""
        if "led" in self.data and self.data["led"] is not None:
            return self.data["led"] == "on"
        return None

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        """LED brightness, if available."""
        if self.data["led_b"] is not None:
            return LedBrightness(self.data["led_b"])
        return None

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"] in ["on", 1, 2]

    @property
    def child_lock(self) -> bool:
        """True if child lock is on."""
        return self.data["child_lock"] == "on"

    @property
    def natural_speed(self) -> Optional[int]:
        """Speed level in natural mode."""
        if "natural_level" in self.data and self.data["natural_level"] is not None:
            return self.data["natural_level"]

    @property
    def direct_speed(self) -> Optional[int]:
        """Speed level in direct mode."""
        if "speed_level" in self.data and self.data["speed_level"] is not None:
            return self.data["speed_level"]

    @property
    def oscillate(self) -> bool:
        """True if oscillation is enabled."""
        return self.data["angle_enable"] == "on"

    @property
    def battery(self) -> Optional[int]:
        """Current battery level."""
        if "battery" in self.data and self.data["battery"] is not None:
            return self.data["battery"]

    @property
    def battery_charge(self) -> Optional[str]:
        """State of the battery charger, if available."""
        if "bat_charge" in self.data and self.data["bat_charge"] is not None:
            return self.data["bat_charge"]
        return None

    @property
    def battery_state(self) -> Optional[str]:
        """State of the battery, if available."""
        if "bat_state" in self.data and self.data["bat_state"] is not None:
            return self.data["bat_state"]
        return None

    @property
    def ac_power(self) -> bool:
        """True if powered by AC."""
        return self.data["ac_power"] == "on"

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in seconds."""
        return self.data["poweroff_time"]

    @property
    def speed(self) -> int:
        """Speed of the motor."""
        return self.data["speed"]

    @property
    def angle(self) -> int:
        """Current angle."""
        return self.data["angle"]

    @property
    def use_time(self) -> int:
        """How long the device has been active in seconds."""
        return self.data["use_time"]

    @property
    def button_pressed(self) -> Optional[str]:
        """Last pressed button."""
        if "button_pressed" in self.data and self.data["button_pressed"] is not None:
            return self.data["button_pressed"]
        return None

    def __repr__(self) -> str:
        s = (
            "<FanStatus power=%s, "
            "temperature=%s, "
            "humidity=%s, "
            "led=%s, "
            "led_brightness=%s, "
            "buzzer=%s, "
            "child_lock=%s, "
            "natural_speed=%s, "
            "direct_speed=%s, "
            "speed=%s, "
            "oscillate=%s, "
            "angle=%s, "
            "ac_power=%s, "
            "battery=%s, "
            "battery_charge=%s, "
            "battery_state=%s, "
            "use_time=%s, "
            "delay_off_countdown=%s, "
            "button_pressed=%s>"
            % (
                self.power,
                self.temperature,
                self.humidity,
                self.led,
                self.led_brightness,
                self.buzzer,
                self.child_lock,
                self.natural_speed,
                self.direct_speed,
                self.speed,
                self.oscillate,
                self.angle,
                self.ac_power,
                self.battery,
                self.battery_charge,
                self.battery_state,
                self.use_time,
                self.delay_off_countdown,
                self.button_pressed,
            )
        )
        return s


class FanStatusP5:
    """Container for status reports from the Xiaomi Mi Smart Pedestal Fan DMaker P5."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Fan (dmaker.fan.p5):
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


class Fan(Device):
    """Main class representing the Xiaomi Mi Smart Pedestal Fan."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FAN_V3,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_FAN_V3

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Battery: {result.battery} %\n"
            "AC power: {result.ac_power}\n"
            "Temperature: {result.temperature} °C\n"
            "Humidity: {result.humidity} %\n"
            "LED: {result.led}\n"
            "LED brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Speed: {result.speed}\n"
            "Natural speed: {result.natural_speed}\n"
            "Direct speed: {result.direct_speed}\n"
            "Oscillate: {result.oscillate}\n"
            "Power-off time: {result.delay_off_countdown}\n"
            "Angle: {result.angle}\n",
        )
    )
    def status(self) -> FanStatus:
        """Retrieve properties."""
        properties = AVAILABLE_PROPERTIES[self.model]

        # A single request is limited to 16 properties. Therefore the
        # properties are divided into multiple requests
        _props_per_request = 15

        # The SA1, ZA1, ZA3 and ZA4 is limited to a single property per request
        if self.model in [MODEL_FAN_SA1, MODEL_FAN_ZA1, MODEL_FAN_ZA3, MODEL_FAN_ZA4]:
            _props_per_request = 1

        values = self.get_properties(properties, max_properties=_props_per_request)

        return FanStatus(dict(zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed of the natural mode to {speed}"),
    )
    def set_natural_speed(self, speed: int):
        """Set natural level."""
        if speed < 0 or speed > 100:
            raise FanException("Invalid speed: %s" % speed)

        return self.send("set_natural_level", [speed])

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed of the direct mode to {speed}"),
    )
    def set_direct_speed(self, speed: int):
        """Set speed of the direct mode."""
        if speed < 0 or speed > 100:
            raise FanException("Invalid speed: %s" % speed)

        return self.send("set_speed_level", [speed])

    @command(
        click.argument("direction", type=EnumType(MoveDirection)),
        default_output=format_output("Rotating the fan to the {direction}"),
    )
    def set_rotate(self, direction: MoveDirection):
        """Rotate the fan by -5/+5 degrees left/right."""
        return self.send("set_move", [direction.value])

    @command(
        click.argument("angle", type=int),
        default_output=format_output("Setting angle to {angle}"),
    )
    def set_angle(self, angle: int):
        """Set the oscillation angle."""
        if angle < 0 or angle > 120:
            raise FanException("Invalid angle: %s" % angle)

        return self.send("set_angle", [angle])

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
            return self.send("set_angle_enable", ["on"])
        else:
            return self.send("set_angle_enable", ["off"])

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.send("set_led_b", [brightness.value])

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off. Not supported by model SA1."""
        if led:
            return self.send("set_led", ["on"])
        else:
            return self.send("set_led", ["off"])

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if self.model in [MODEL_FAN_SA1, MODEL_FAN_ZA1, MODEL_FAN_ZA3, MODEL_FAN_ZA4]:
            if buzzer:
                return self.send("set_buzzer", [2])
            else:
                return self.send("set_buzzer", [0])

        if buzzer:
            return self.send("set_buzzer", ["on"])
        else:
            return self.send("set_buzzer", ["off"])

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        if lock:
            return self.send("set_child_lock", ["on"])
        else:
            return self.send("set_child_lock", ["off"])

    @command(
        click.argument("seconds", type=int),
        default_output=format_output("Setting delayed turn off to {seconds} seconds"),
    )
    def delay_off(self, seconds: int):
        """Set delay off seconds."""

        if seconds < 0:
            raise FanException("Invalid value for a delayed turn off: %s" % seconds)

        return self.send("set_poweroff_time", [seconds])


class FanV2(Fan):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=MODEL_FAN_V2)


class FanSA1(Fan):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=MODEL_FAN_SA1)


class FanZA1(Fan):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=MODEL_FAN_ZA1)


class FanZA3(Fan):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=MODEL_FAN_ZA3)


class FanZA4(Fan):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=MODEL_FAN_ZA4)


class FanP5(Device):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FAN_P5,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_FAN_P5

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
            raise FanException("Invalid speed: %s" % speed)

        return self.send("s_speed", [speed])

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
            raise FanException("Invalid value for a delayed turn off: %s" % minutes)

        return self.send("s_t_off", [minutes])

    @command(
        click.argument("direction", type=EnumType(MoveDirection)),
        default_output=format_output("Rotating the fan to the {direction}"),
    )
    def set_rotate(self, direction: MoveDirection):
        """Rotate the fan by -5/+5 degrees left/right."""
        return self.send("m_roll", [direction.value])
