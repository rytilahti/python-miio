import enum
import logging
from typing import Any, Dict

import click

from .airhumidifier import AirHumidifierException
from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus

_LOGGER = logging.getLogger(__name__)

# Xiaomi Zero Fog Humidifier
MODEL_HUMIDIFIER_JSQ001 = "shuii.humidifier.jsq001"

# Array of properties in same order as in humidifier response
AVAILABLE_PROPERTIES = {
    MODEL_HUMIDIFIER_JSQ001: [
        "temperature",  # (degrees, int)
        "humidity",  # (percentage, int)
        "mode",  # ( 0: Intelligent, 1: Level1, ..., 5:Level4)
        "buzzer",  # (0: off, 1: on)
        "child_lock",  # (0: off, 1: on)
        "led_brightness",  # (0: off, 1: low, 2: high)
        "power",  # (0: off, 1: on)
        "no_water",  # (0: enough, 1: add water)
        "lid_opened",  # (0: ok, 1: lid is opened)
    ]
}


class OperationMode(enum.Enum):
    Intelligent = 0
    Level1 = 1
    Level2 = 2
    Level3 = 3
    Level4 = 4


class LedBrightness(enum.Enum):
    Off = 0
    Low = 1
    High = 2


class AirHumidifierStatus(DeviceStatus):
    """Container for status reports from the air humidifier jsq."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Status of an Air Humidifier (shuii.humidifier.jsq001):

            [24, 30, 1, 1, 0, 2, 0, 0, 0]

        Parsed by AirHumidifierJsq device as:
            {'temperature': 24, 'humidity': 29, 'mode': 1, 'buzzer': 1,
             'child_lock': 0, 'led_brightness': 2, 'power': 0, 'no_water': 0,
              'lid_opened': 0}
        """
        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.data["power"] == 1 else "off"

    @property
    def is_on(self) -> bool:
        """True if device is turned on."""
        return self.power == "on"

    @property
    def mode(self) -> OperationMode:
        """Operation mode.

        Can be either low, medium, high or humidity.
        """

        try:
            mode = OperationMode(self.data["mode"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse mode: %s", e)
            return OperationMode.Intelligent

        return mode

    @property
    def temperature(self) -> int:
        """Current temperature in degree celsius."""
        return self.data["temperature"]

    @property
    def humidity(self) -> int:
        """Current humidity in percent."""
        return self.data["humidity"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"] == 1

    @property
    def led_brightness(self) -> LedBrightness:
        """Buttons illumination Brightness level."""
        try:
            brightness = LedBrightness(self.data["led_brightness"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse brightness: %s", e)
            return LedBrightness.Off

        return brightness

    @property
    def led(self) -> bool:
        """True if LED is turned on."""
        return self.led_brightness is not LedBrightness.Off

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"] == 1

    @property
    def no_water(self) -> bool:
        """True if the water tank is empty."""
        return self.data["no_water"] == 1

    @property
    def lid_opened(self) -> bool:
        """True if the water tank is detached."""
        return self.data["lid_opened"] == 1


class AirHumidifierJsq(Device):
    """Implementation of Xiaomi Zero Fog Humidifier: shuii.humidifier.jsq001."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_HUMIDIFIER_JSQ001,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        self.model = model if model in AVAILABLE_PROPERTIES else MODEL_HUMIDIFIER_JSQ001

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "Temperature: {result.temperature} °C\n"
            "Humidity: {result.humidity} %\n"
            "Buzzer: {result.buzzer}\n"
            "LED brightness: {result.led_brightness}\n"
            "Child lock: {result.child_lock}\n"
            "No water: {result.no_water}\n"
            "Lid opened: {result.lid_opened}\n",
        )
    )
    def status(self) -> AirHumidifierStatus:
        """Retrieve properties."""

        values = self.send("get_props")

        # Response of an Air Humidifier (shuii.humidifier.jsq001):
        # [24, 37, 3, 1, 0, 2, 0, 0, 0]
        #
        # status[0] : temperature (degrees, int)
        # status[1]: humidity (percentage, int)
        # status[2]: mode ( 0: Intelligent, 1: Level1, ..., 5:Level4)
        # status[3]: buzzer (0: off, 1: on)
        # status[4]: lock (0: off, 1: on)
        # status[5]: brightness (0: off, 1: low, 2: high)
        # status[6]: power (0: off, 1: on)
        # status[7]: water level state (0: ok, 1: add water)
        # status[8]: lid state (0: ok, 1: lid is opened)

        properties = AVAILABLE_PROPERTIES[self.model]
        if len(properties) != len(values):
            _LOGGER.error(
                "Count (%s) of requested properties (%s) does not match the "
                "count (%s) of received values (%s).",
                len(properties),
                properties,
                len(values),
                values,
            )

        return AirHumidifierStatus({k: v for k, v in zip(properties, values)})

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_start", [1])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_start", [0])

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        value = mode.value
        if value not in (om.value for om in OperationMode):
            raise AirHumidifierException(
                "{} is not a valid OperationMode value".format(value)
            )

        return self.send("set_mode", [value])

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        value = brightness.value
        if value not in (lb.value for lb in LedBrightness):
            raise AirHumidifierException(
                "{} is not a valid LedBrightness value".format(value)
            )

        return self.send("set_brightness", [value])

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        brightness = LedBrightness.High if led else LedBrightness.Off
        return self.set_led_brightness(brightness)

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        return self.send("set_buzzer", [int(bool(buzzer))])

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        return self.send("set_lock", [int(bool(lock))])
