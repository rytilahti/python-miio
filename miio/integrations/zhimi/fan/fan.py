import enum
import logging
from typing import Any, Dict, Optional

import click

from miio import Device, DeviceStatus
from miio.click_common import EnumType, command, format_output
from miio.devicestatus import sensor, setting


class MoveDirection(enum.Enum):
    Left = "left"
    Right = "right"


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


_LOGGER = logging.getLogger(__name__)

MODEL_FAN_V2 = "zhimi.fan.v2"
MODEL_FAN_V3 = "zhimi.fan.v3"
MODEL_FAN_SA1 = "zhimi.fan.sa1"
MODEL_FAN_ZA1 = "zhimi.fan.za1"
MODEL_FAN_ZA3 = "zhimi.fan.za3"
MODEL_FAN_ZA4 = "zhimi.fan.za4"

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


AVAILABLE_PROPERTIES = {
    MODEL_FAN_V3: AVAILABLE_PROPERTIES_COMMON_V2_V3,
    MODEL_FAN_V2: ["led", "bat_state"] + AVAILABLE_PROPERTIES_COMMON_V2_V3,
    MODEL_FAN_SA1: AVAILABLE_PROPERTIES_COMMON,
    MODEL_FAN_ZA1: AVAILABLE_PROPERTIES_COMMON,
    MODEL_FAN_ZA3: AVAILABLE_PROPERTIES_COMMON,
    MODEL_FAN_ZA4: AVAILABLE_PROPERTIES_COMMON,
}


class FanStatus(DeviceStatus):
    """Container for status reports from the Xiaomi Mi Smart Pedestal Fan."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a Fan (zhimi.fan.v3):

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
    @setting("Power", setter_name="set_power")
    def is_on(self) -> bool:
        """True if device is currently on."""
        return self.power == "on"

    @property
    @sensor("Humidity")
    def humidity(self) -> Optional[int]:
        """Current humidity."""
        if "humidity" in self.data and self.data["humidity"] is not None:
            return self.data["humidity"]
        return None

    @property
    @sensor("Temperature", unit="C")
    def temperature(self) -> Optional[float]:
        """Current temperature, if available."""
        if "temp_dec" in self.data and self.data["temp_dec"] is not None:
            return self.data["temp_dec"] / 10.0
        return None

    @property
    @setting("LED", setter_name="set_led")
    def led(self) -> Optional[bool]:
        """True if LED is turned on, if available."""
        if "led" in self.data and self.data["led"] is not None:
            return self.data["led"] == "on"
        return None

    @property
    @setting("LED Brightness", choices=LedBrightness, setter_name="set_led_brightness")
    def led_brightness(self) -> Optional[LedBrightness]:
        """LED brightness, if available."""
        if self.data["led_b"] is not None:
            return LedBrightness(self.data["led_b"])
        return None

    @property
    @setting("Buzzer", setter_name="set_buzzer")
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"] in ["on", 1, 2]

    @property
    @setting("Child Lock", setter_name="set_child_lock")
    def child_lock(self) -> bool:
        """True if child lock is on."""
        return self.data["child_lock"] == "on"

    @property
    @setting("Natural Speed Level", setter_name="set_natural_speed", max_value=100)
    def natural_speed(self) -> Optional[int]:
        """Speed level in natural mode."""
        if "natural_level" in self.data and self.data["natural_level"] is not None:
            return self.data["natural_level"]
        return None

    @property
    @setting("Direct Speed", setter_name="set_direct_speed", max_value=100)
    def direct_speed(self) -> Optional[int]:
        """Speed level in direct mode."""
        if "speed_level" in self.data and self.data["speed_level"] is not None:
            return self.data["speed_level"]
        return None

    @property
    @setting("Oscillate", setter_name="set_oscillate")
    def oscillate(self) -> bool:
        """True if oscillation is enabled."""
        return self.data["angle_enable"] == "on"

    @property
    @sensor("Battery", unit="%")
    def battery(self) -> Optional[int]:
        """Current battery level."""
        if "battery" in self.data and self.data["battery"] is not None:
            return self.data["battery"]
        return None

    @property
    @sensor("Battery Charge State")
    def battery_charge(self) -> Optional[str]:
        """State of the battery charger, if available."""
        if "bat_charge" in self.data and self.data["bat_charge"] is not None:
            return self.data["bat_charge"]
        return None

    @property
    @sensor("Battery State")
    def battery_state(self) -> Optional[str]:
        """State of the battery, if available."""
        if "bat_state" in self.data and self.data["bat_state"] is not None:
            return self.data["bat_state"]
        return None

    @property
    @sensor("AC Powered")
    def ac_power(self) -> bool:
        """True if powered by AC."""
        return self.data["ac_power"] == "on"

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in seconds."""
        return self.data["poweroff_time"]

    @property
    @sensor("Motor Speed", unit="RPM")
    def speed(self) -> int:
        """Speed of the motor."""
        return self.data["speed"]

    @property
    @setting("Oscillation Angle", setter_name="set_angle", max_value=120)
    def angle(self) -> int:
        """Current angle."""
        return self.data["angle"]

    @property
    def use_time(self) -> int:
        """How long the device has been active in seconds."""
        return self.data["use_time"]

    @property
    @sensor("Last Pressed Button")
    def button_pressed(self) -> Optional[str]:
        """Last pressed button."""
        if "button_pressed" in self.data and self.data["button_pressed"] is not None:
            return self.data["button_pressed"]
        return None


class Fan(Device):
    """Main class representing the Xiaomi Mi Smart Pedestal Fan."""

    _supported_models = list(AVAILABLE_PROPERTIES.keys())

    @command()
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
        click.argument("power", type=bool),
    )
    def set_power(self, power: bool):
        """Turn device on or off."""
        if power:
            self.on()
        else:
            self.off()

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed of the natural mode to {speed}"),
    )
    def set_natural_speed(self, speed: int):
        """Set natural level."""
        if speed < 0 or speed > 100:
            raise ValueError("Invalid speed: %s" % speed)

        return self.send("set_natural_level", [speed])

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed of the direct mode to {speed}"),
    )
    def set_direct_speed(self, speed: int):
        """Set speed of the direct mode."""
        if speed < 0 or speed > 100:
            raise ValueError("Invalid speed: %s" % speed)

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
            raise ValueError("Invalid angle: %s" % angle)

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
        """Turn led on/off.

        Not supported by model SA1.
        """
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
            raise ValueError("Invalid value for a delayed turn off: %s" % seconds)

        return self.send("set_poweroff_time", [seconds])
