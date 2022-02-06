import enum
import logging
from typing import Any, Dict, Optional

import click

from .airhumidifier import AirHumidifierException
from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus

_LOGGER = logging.getLogger(__name__)

# Xiaomi Zero Fog Humidifier
MODEL_HUMIDIFIER_JSQ001 = "shuii.humidifier.jsq001"
# Xiaomi Zero Fog DWZF(G)-4500Z
MODEL_HUMIDIFIER_JSQ002 = "shuii.humidifier.jsq002"

# Array of several common commands
SHARED_COMMANDS = {
    MODEL_HUMIDIFIER_JSQ001: dict(power_on_off="set_start", buzzer_on_off="set_buzzer"),
    MODEL_HUMIDIFIER_JSQ002: dict(power_on_off="on_off", buzzer_on_off="buzzer_on"),
}

# Array of properties in same order as in humidifier response
AVAILABLE_PROPERTIES = {
    MODEL_HUMIDIFIER_JSQ001: [
        # Example of 'Air Humidifier (shuii.humidifier.jsq001)' response:
        # [24, 37, 3, 1, 0, 2, 0, 0, 0]
        "temperature",  # 24 (degrees, int)
        "humidity",  # 37 (percentage, int)
        "mode",  # 3 ( 0: Intelligent, 1: Level1, ..., 5:Level4)
        "buzzer",  # 1 (0: off, 1: on)
        "child_lock",  # 0 (0: off, 1: on)
        "led_brightness",  # 2 (0: off, 1: low, 2: high)
        "power",  # 0 (0: off, 1: on)
        "no_water",  # 0 (water level state  - 0: enough, 1: add water)
        "lid_opened",  # 0 (0: ok, 1: lid is opened)
    ],
    MODEL_HUMIDIFIER_JSQ002: [
        # Example of Xiaomi 'Zero Fog DWZF(G)-4500Z` (shuii.humidifier.jsq002)'
        #   Model: shuii.humidifier.jsq002
        #   Hardware version: ESP8266
        #   Firmware version: 1.4.0
        #
        # > fast_set [bea, lock, temperature, humidity, led]
        #           0/1,  0/1,          25,       50, 0/1]
        #
        #  Properties:
        # > dev.send("get_props","")
        #  [1, 2, 36, 2, 46, 4, 1, 1, 1, 50, 51, 0]
        # res[0]=1 Values (0: off/sleep, 1: on);
        "power",  # CMD: on_off [int]
        # res[1]=2 Values (1, 2, 3); fan speed in UI: {Gear: level 1, level 2, level 3};
        "mode",  # CMD: set_gear [int]
        # res[2]=36 Value (is  % [int] );  Environment humidity;
        "humidity",
        # res[3]=2 Values (1, 2, 3) // Light 1 - Off; 2 - low; 3 - high
        "led_brightness",  # CMD: set_led [int]
        # res[4]=26 Values(is "ambient temp degrees int"+20, i.e. 46 corresponds to 26);
        "temperature",
        # res[5]=4 (0,1,2,3,4,5). '5' is full, if pour more water, warning signal will sound
        "water_level",  # Get cmd: corrected_water []
        # res[6]=1, Water heater values (0: off, 1: on)
        "heat",  # CMD: warm_on [int]
        # res[7]=1 BeaPower values (0: off, 1: on)
        "buzzer",  # CMD: buzzer_on [int]
        # res[8]=1, Values (0: off, 1: on)
        "child_lock",  # CMD: set_lock [int]
        # res[9]=50 Values (water heater target temp in degrees, [int]: 30..60)
        "target_temperature",  # CMD: set_temp [int]
        # res[10]=51 Values (% [int])
        "target_humidity",  # CMD: set_humidity [int]
        # res[11]=0 Values: <Unknown> We failed to find when it changes, is not lid opened event
        "reserved",
    ],
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


class OperationModeJsq002(enum.Enum):
    Level1 = 1
    Level2 = 2
    Level3 = 3


class LedBrightnessJsq002(enum.Enum):
    Off = 1
    Low = 2
    High = 3


class AirHumidifierStatusJsqCommon(DeviceStatus):
    def __init__(self, data: Dict[str, Any]) -> None:
        """Status of an Air Humidifier:"""
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
    def humidity(self) -> int:
        """Current humidity in percent."""
        return self.data["humidity"]

    @property
    def temperature(self) -> int:
        """Current temperature in degree celsius."""
        return self.data["temperature"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"] == 1

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"] == 1


class AirHumidifierStatus(AirHumidifierStatusJsqCommon):
    """Container for status reports from the air humidifier jsq."""

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
    def no_water(self) -> bool:
        """True if the water tank is empty."""
        return self.data["no_water"] == 1

    @property
    def lid_opened(self) -> bool:
        """True if the water tank is detached."""
        return self.data["lid_opened"] == 1

    @property
    def use_time(self) -> Optional[int]:
        """How long the device has been active in seconds.

        Not supported by the device, so we return none here.
        """
        return None


class AirHumidifierStatusJsq002(AirHumidifierStatusJsqCommon):
    @property
    def mode(self) -> OperationModeJsq002:
        """Operation mode.

        Can be either low, medium, high or humidity.
        """

        try:
            mode = OperationModeJsq002(self.data["mode"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse mode: %s", e)
            return OperationModeJsq002.Level1

        return mode

    @property
    def temperature(self) -> int:
        """Current temperature in degree celsius."""

        # Real temp is 'value - 20', were value from device
        return self.data["temperature"] - 20

    _supported_models = [MODEL_HUMIDIFIER_JSQ001]

    @property
    def water_level(self) -> int:
        """Water level: 0,1,2,3,4,5."""

        level = self.data["water_level"]
        if level not in [0, 1, 2, 3, 4, 5]:
            _LOGGER.exception(
                "Water level should be 0,1,2,3,4,5. But was: %s", str(level)
            )
            return 5

        return level

    @property
    def heater(self) -> bool:
        """Return True if child lock is on."""
        return self.data["heat"] == 1

    @property
    def water_target_temperature(self) -> int:
        """Return Target Water Temperature, degrees C, 30..60."""
        target_temp = self.data["target_temperature"]
        target_temp_int = int(target_temp)
        if target_temp_int not in range(30, 61):
            _LOGGER.exception(
                "Target water heater temp should be in [30..60]. But was: %s",
                str(target_temp),
            )
            return 30

        return target_temp_int

    @property
    def target_humidity(self) -> int:
        """Return Target Water Temperature, degrees C, 30..60."""
        target_humidity = self.data["target_humidity"]
        target_humidity_int = int(target_humidity)
        if target_humidity_int not in range(0, 100):
            _LOGGER.exception(
                "Target humidity should be in [0..99]. But was: %s",
                str(target_humidity),
            )
            return 30

        return target_humidity_int

    @property
    def led_brightness(self) -> LedBrightnessJsq002:
        """Buttons illumination Brightness level."""
        try:
            brightness = LedBrightnessJsq002(self.data["led_brightness"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse brightness: %s", e)
            return LedBrightnessJsq002.Off

        return brightness

    @property
    def no_water(self) -> bool:
        """True if the water tank is empty."""
        return self.water_level == 0


class AirHumidifierJsqCommon(Device):
    _supported_models = sorted(AVAILABLE_PROPERTIES.keys())

    def _get_props(self) -> Dict:
        """Retrieve properties."""

        values = self.send("get_props")

        if self.model not in AVAILABLE_PROPERTIES:
            raise AirHumidifierException("Unsupported model: %s" % self.model)

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

        return {k: v for k, v in zip(properties, values)}

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        if self.model not in SHARED_COMMANDS:
            raise AirHumidifierException("Unsupported model: %s" % self.model)

        return self.send(SHARED_COMMANDS[self.model]["power_on_off"], [1])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        if self.model not in SHARED_COMMANDS:
            raise AirHumidifierException("Unsupported model: %s" % self.model)

        return self.send(SHARED_COMMANDS[self.model]["power_on_off"], [0])

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off.

        Supported args one of: true, false, 0, 1
        """
        if self.model not in SHARED_COMMANDS:
            raise AirHumidifierException("Unsupported model: %s" % self.model)

        return self.send(
            SHARED_COMMANDS[self.model]["buzzer_on_off"], [int(bool(buzzer))]
        )

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off.

        Supported args one of: true, false, 0, 1
        """
        return self.send("set_lock", [int(bool(lock))])


class AirHumidifierJsq(AirHumidifierJsqCommon):
    """Implementation of Xiaomi Zero Fog Humidifier: shuii.humidifier.jsq001."""

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
        return AirHumidifierStatus(self._get_props())

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode.

        Supported args one of: 'intelligent', 'level1', 'level2', 'level3', 'level4'
        """
        value = mode.value
        if value not in (om.value for om in OperationMode):
            raise AirHumidifierException(f"{value} is not a valid OperationMode value")

        return self.send("set_mode", [value])

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness.

        Supported args one of: 'high', 'low', 'off'.
        """
        value = brightness.value
        if value not in (lb.value for lb in LedBrightness):
            raise AirHumidifierException(f"{value} is not a valid LedBrightness value")

        return self.send("set_brightness", [value])

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off.

        Supported args one of: true, false, 0, 1
        """
        brightness = LedBrightness.High if led else LedBrightness.Off
        return self.set_led_brightness(brightness)


class AirHumidifierJsq002(AirHumidifierJsqCommon):
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
            "Water level: {result.water_level}\n"
            "Water heater: {result.heater}\n"
            "Water target temperature: {result.water_target_temperature} °C\n"
            "Target humidity: {result.target_humidity} %\n",
        )
    )
    def status(self) -> AirHumidifierStatusJsq002:
        return AirHumidifierStatusJsq002(self._get_props())

    @command(
        click.argument("mode", type=EnumType(OperationModeJsq002)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationModeJsq002):
        """Set mode.

        Supported args one of: 'level1', 'level2', 'level3'
        """
        value = mode.value
        if value not in (om.value for om in OperationModeJsq002):
            raise AirHumidifierException(
                f"{value} is not a valid OperationModeJsq2 value"
            )

        return self.send("set_gear", [value])

    @command(
        click.argument("brightness", type=EnumType(LedBrightnessJsq002)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightnessJsq002):
        """Set led brightness.

        Supported args one of: 'high', 'low', 'off'.
        """
        value = brightness.value
        if value not in (lb.value for lb in LedBrightnessJsq002):
            raise AirHumidifierException(
                f"{value} is not a valid LedBrightnessJsq2 value"
            )

        return self.send("set_led", [value])

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off.

        Supported args one of: true, false, 0, 1
        """
        brightness = LedBrightnessJsq002.High if led else LedBrightnessJsq002.Off
        return self.set_led_brightness(brightness)

    @command(
        click.argument("heater", type=bool),
        default_output=format_output(
            lambda heater: "Turning on water heater"
            if heater
            else "Turning off water heater"
        ),
    )
    def set_heater(self, heater: bool):
        """Set water heater on/off.

        Supported args one of: true, false, 0, 1
        """
        return self.send("warm_on", [int(bool(heater))])

    @command(
        click.argument("temperature", type=int),
        default_output=format_output(
            "Setting target water temperature to {temperature}"
        ),
    )
    def set_target_water_temperature(self, temperature: int):
        """Set the target water temperature degrees C, supported integer numbers in
        range 30..60."""

        if temperature not in range(30, 61):
            raise AirHumidifierException(
                "Invalid water target temperature, should be in [30..60]. But was: %s"
                % temperature
            )

        return self.send("set_temp", [temperature])

    @command(
        click.argument("humidity", type=int),
        default_output=format_output("Setting target humidity to {humidity}"),
    )
    def set_target_humidity(self, humidity: int):
        """Set the target humidity %, supported integer numbers in range 0..99."""

        if humidity not in range(0, 100):
            raise AirHumidifierException(
                "Invalid target humidity, should be in [0..99]. But was: %s" % humidity
            )

        return self.send("set_humidity", [humidity])

    @command(
        default_output=format_output("Running `rst_clean` command"),
    )
    def rst_clean(self):
        """Run 'rst_clean' command (unknown function)."""
        return self.send("rst_clean", [])

    @command(
        default_output=format_output("Calibrating water level as zero"),
    )
    def corrected_water(self):
        """Calibrate current water level as zero level."""
        return self.send("corrected_water", [])
