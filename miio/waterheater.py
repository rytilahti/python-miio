import enum
import logging
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_WATERHEATER_E1 = "viomi.waterheater.e1" """ VIOMI Internet electric water heater 1A (60L) """

AVAILABLE_PROPERTIES_E1 = [
    "washStatus",
    "velocity",
    "waterTemp",
    "targetTemp",
    "errStatus",
    "hotWater",
    "needClean",
    "modeType",
    "appointStart",
    "appointEnd",
]

SUPPORTED_MODELS: Dict[str, Dict[str, Any]] = {
    MODEL_WATERHEATER_E1: {
        "temperature_range": (30, 75),
        "bacteriostatic_mode": True,
        "bacteriostatic_temperature": 80,
        "available_properties": AVAILABLE_PROPERTIES_E1,
    },
}

class OperationMode(enum.Enum):
    Termostatic = 0
    Heating = 1
    Booking = 2
 
class OperationStatus(enum.Enum):
    Off = 0
    Heating = 1
    KeepWarm = 2

class WaterHeaterException(DeviceException):
    pass

class WaterHeaterStatus (DeviceStatus):

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a Waterheater (viomi.waterheater.e1):
        {'washStatus': 1, 'velocity': 0, 'waterTemp': 29,
        'targetTemp': 70, 'errStatus': 0, 'hotWater': 60,
        'needClean': 0, 'modeType': 1, 'appointStart': 7
        'appointEnd': 0}
        """
        self.data = data

    @property
    def status(self) -> OperationStatus:
        return OperationStatus(self.data["washStatus"])

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return not self.status == OperationStatus.TurnedOff

    @property
    def velocity(self) -> int:
        return self.data["velocity"]

    @property
    def water_temperature(self) -> int:
        """Current water temperature."""
        return self.data["waterTemp"]

    @property
    def target_temperature(self) -> int:
        """Target water temperature."""
        return self.data["targetTemp"]

    @property
    def error(self) -> int:
        return self.data["errStatus"]

    @property
    def hot_water_volume(self) -> int:
        return self.data["hotWater"]

    @property
    def cleaning_required(self) -> int:
        return self.data["needClean"]

    @property
    def mode(self) -> OperationMode:
        return OperationMode(self.data["modeType"])

    @property
    def booking_time_start(self) -> int:
        return self.data["appointStart"]

    @property
    def booking_time_end(self) -> int:
        return self.data["appointEnd"]

class WaterHeater(Device):
    """Main class representing the Waterheater."""

    @command(
        default_output=format_output(
            "",
            "Operation status: {result.status.name} ({result.status.value})\n"
            "Velocity: {result.velocity}\n"
            "Water temperature: {result.water_temperature}°C\n"
            "Target temperature: {result.target_temperature}°C\n"
            "Error status: {result.error}\n"
            "Remaining hot water volume: {result.hot_water_volume}%\n"
            "Device cleaning is required: {result.cleaning_required}\n"
            "Operation mode type: {result.mode.name} ({result.mode.value}) \n"
            "Operation start time in booking mode: {result.booking_time_start}\n"
            "Operation end time in booking mode: {result.booking_time_end}\n",
        )
    )
    def status(self) -> WaterHeaterStatus:
        """Retrieve properties."""
        properties = SUPPORTED_MODELS.get(
            self.model, SUPPORTED_MODELS[MODEL_WATERHEATER_E1]
        )["available_properties"]

        # A single request is limited to 16 properties. Therefore the
        # properties are divided into multiple requests
        _props_per_request = 15

        # The E1 is limited to a single property per request
        if self.model in [MODEL_WATERHEATER_E1]:
            _props_per_request = 1

        values = self.get_properties(properties, max_properties=_props_per_request)

        return WaterHeaterStatus(dict(zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", [1])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", [0])

    @command(
        click.argument("temperature", type=int),
        default_output=format_output("Setting target temperature to {temperature}"),
    )
    def set_target_temperature(self, temperature: int):
        """Set target temperature."""
        min_temp: int
        max_temp: int
        min_temp, max_temp = SUPPORTED_MODELS.get(
            self.model, SUPPORTED_MODELS[MODEL_WATERHEATER_E1]
        )["temperature_range"]
        if not min_temp <= temperature <= max_temp:
            raise WaterHeaterException("Invalid target temperature: %s" % temperature)
        return self.send("set_temp", [temperature])

    @command(default_output=format_output("Setting bacteriostatic mode on"))
    def set_bacteriostatic_mode(self):
        """Set bacteriostatic operational mode."""
        mode: OperationMode
        bacteriostatic_mode: bool
        bacteriostatic_temp: int
        bacteriostatic_mode = SUPPORTED_MODELS.get(
            self.model, SUPPORTED_MODELS[MODEL_WATERHEATER_E1]
        )["bacteriostatic_mode"]
        if not bacteriostatic_mode:
            raise WaterHeaterException("Bacteriostatic mode is not supported.")
        bacteriostatic_temp = SUPPORTED_MODELS.get(
            self.model, SUPPORTED_MODELS[MODEL_WATERHEATER_E1]
        )["bacteriostatic_temperature"]
        mode = OperationMode(self.send("get_prop", ["modeType"])[0])
        if mode == OperationMode.Termostatic:
            raise WaterHeaterException("Bacteriostatic operational mode is not supported in Termostatic mode.")
        return self.send("set_temp", [bacteriostatic_temp])

    @command(
        click.argument("appoint_start", type=int),
        click.argument("appoint_end", type=int),
        default_output=format_output(
             lambda appoint_end, appoint_start:
            "Setting up the Booking mode operational interval from: %s " % appoint_start +
            "to: %s " % appoint_end +
            "(duration: %s)" % (appoint_end-appoint_start if appoint_end-appoint_start > 0 else appoint_end-appoint_start+24)
        ),
    )
    def set_appoint(self, appoint_start, appoint_end):
        """Setting up the Booking mode operational interval."""
        if  0 <= appoint_start < 24 and 0 <= appoint_end < 24:
            return self.send("set_appoint", [1, appoint_start, appoint_end])
        else:
            raise WaterHeaterException("Booking mode operational interval parameters must be within [0, 23].")

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting operation mode to {mode.name} ({mode.value})"),
    )
    def set_mode(self, mode: OperationMode):
        """Set operation mode."""
        appoint_start: int
        appoint_end: int
        if mode == OperationMode.Booking:
            appoint_start = self.send("get_prop", ["appointStart"])[0]
            appoint_end = self.send("get_prop", ["appointEnd"])[0]
#            raise WaterHeaterException("Booking operational mode is not supported in set_mode use set_appoint instead of.")
            return self.send("set_appoint", [1, appoint_start, appoint_end])
        else:
            return self.send("set_mode", [mode.value])
