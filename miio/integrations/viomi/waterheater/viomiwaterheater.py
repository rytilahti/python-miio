import enum
import logging
from datetime import time
from typing import Any

import click

from miio.click_common import EnumType, command, format_output
from miio.device import Device, DeviceStatus
from miio.devicestatus import sensor, setting
from miio.exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

"""VIOMI Internet electric water heater 1A (60L)
https://home.miot-spec.com/spec/viomi.waterheater.e1
"""
MODEL_WATERHEATER_E1 = "viomi.waterheater.e1"
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

SUPPORTED_MODELS: dict[str, dict[str, Any]] = {
    MODEL_WATERHEATER_E1: {
        "temperature_range": (30, 75),
        "bacteriostatic_mode": True,
        "bacteriostatic_temperature": 80,
        "available_properties": AVAILABLE_PROPERTIES_E1,
    },
}


class OperationMode(enum.Enum):
    Thermostatic = 0
    Heating = 1
    Booking = 2


class OperationStatus(enum.Enum):
    Off = 0
    Heating = 1
    KeepWarm = 2


class ViomiWaterHeaterException(DeviceException):
    pass


class ViomiWaterHeaterStatus(DeviceStatus):
    """Response of a VIOMI Internet electric water heater 1A (60L)
    (viomi.waterheater.e1):

    {
        "washStatus": 1,
        "velocity": 0,
        "waterTemp": 29,
        "targetTemp": 70,
        "errStatus": 0,
        "hotWater": 60,
        "needClean": 0,
        "modeType": 1,
        "appointStart": 7,
        "appointEnd": 0
    }
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    @property
    @sensor(name="Status")
    def status(self) -> OperationStatus:
        """Device operational status."""
        return OperationStatus(self.data["washStatus"])

    @property
    @sensor(name="Power")
    def is_on(self) -> bool:
        """True if device is currently powered on."""
        return self.status != OperationStatus.Off

    @property
    @sensor(name="Velocity")
    def velocity(self) -> int:
        """Velocity parameter."""
        return self.data["velocity"]

    @property
    @sensor(name="Water Temperature", unit="°C")
    def water_temperature(self) -> int:
        """Current water temperature."""
        return self.data["waterTemp"]

    @property
    @setting(
        name="Target Temperature",
        unit="°C",
        setter_name="set_target_temperature",
        min_value=30,
        max_value=75,
    )
    def target_temperature(self) -> int:
        """Target water temperature."""
        return self.data["targetTemp"]

    @property
    @sensor(name="Error")
    def error(self) -> int:
        """Error status during operation."""
        return self.data["errStatus"]

    @property
    @sensor(name="Hot Water Volume", unit="%")
    def hot_water_volume(self) -> int:
        """Empirical assessment of the hot water supply."""
        return self.data["hotWater"]

    @property
    @sensor(name="Cleaning Required")
    def cleaning_required(self) -> bool:
        """True when cleaning the device is required."""
        return self.data["needClean"] != 0

    @property
    @setting(
        name="Mode",
        setter_name="set_mode",
        choices=OperationMode,
    )
    def mode(self) -> OperationMode:
        """Device operational mode."""
        return OperationMode(self.data["modeType"])

    @property
    @sensor(name="Booking Start Hour")
    def service_time_start(self) -> time:
        """The start time of the operation in Booking mode."""
        return time(self.data["appointStart"])

    @property
    @sensor(name="Booking End Hour")
    def service_time_end(self) -> time:
        """The end time of the operation in Booking mode."""
        return time(self.data["appointEnd"])


class ViomiWaterHeater(Device):
    """Main class representing the Viomi Waterheaters."""

    _supported_models = [MODEL_WATERHEATER_E1]

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
            "Operation mode type: {result.mode.name} ({result.mode.value})\n"
            "Booking mode start time at: {result.service_time_start}\n"
            "Booking mode end time at: {result.service_time_end}\n",
        )
    )
    def status(self) -> ViomiWaterHeaterStatus:
        """Retrieve properties."""
        properties = SUPPORTED_MODELS.get(
            self.model, SUPPORTED_MODELS[MODEL_WATERHEATER_E1]
        )["available_properties"]
        values = self.get_properties(properties, max_properties=1)

        return ViomiWaterHeaterStatus(dict(zip(properties, values)))

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
        min_temp, max_temp = SUPPORTED_MODELS.get(
            self.model, SUPPORTED_MODELS[MODEL_WATERHEATER_E1]
        )["temperature_range"]

        if not min_temp <= temperature <= max_temp:
            raise ViomiWaterHeaterException(
                f"Invalid target temperature: {temperature}. Supported range: [{min_temp}, {max_temp}]"
            )

        return self.send("set_temp", [temperature])

    @command(default_output=format_output("Setting bacteriostatic mode on"))
    def set_bacteriostatic_mode(self):
        """Set bacteriostatic operational mode (water disinfection mode)."""
        bacteriostatic_mode = SUPPORTED_MODELS.get(
            self.model, SUPPORTED_MODELS[MODEL_WATERHEATER_E1]
        )["bacteriostatic_mode"]

        if not bacteriostatic_mode:
            raise ViomiWaterHeaterException("Bacteriostatic mode is not supported.")

        mode = OperationMode(self.send("get_prop", ["modeType"])[0])
        if mode == OperationMode.Thermostatic:
            raise ViomiWaterHeaterException(
                "Bacteriostatic operational mode is not supported in Thermostatic mode."
            )

        bacteriostatic_temp = SUPPORTED_MODELS.get(
            self.model, SUPPORTED_MODELS[MODEL_WATERHEATER_E1]
        )["bacteriostatic_temperature"]

        return self.send("set_temp", [bacteriostatic_temp])

    @command(
        click.argument("time_start", type=int),
        click.argument("time_end", type=int),
        default_output=format_output(
            lambda time_start, time_end: "Setting up the Booking mode operational interval from: %02d:00 "
            % time_start
            + "to: %02d:00 " % time_end
            + "(duration: %s hours)."
            % (
                time_end - time_start
                if time_end - time_start > 0
                else time_end - time_start + 24
            )
        ),
    )
    def set_service_time(self, time_start: int, time_end: int):
        """Setting up the Booking mode operational interval."""
        if not (0 <= time_start <= 23) or not (0 <= time_end <= 23):
            raise ViomiWaterHeaterException(
                "Booking mode operational interval parameters must be within [0, 23]."
            )

        return self.send("set_appoint", [0, time_start, time_end])

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output(
            "Setting operation mode to {mode.name} ({mode.value})"
        ),
    )
    def set_mode(self, mode: OperationMode):
        """Set operation mode."""
        if mode == OperationMode.Booking:
            booking_time_start = self.send("get_prop", ["appointStart"])[0]
            booking_time_end = self.send("get_prop", ["appointEnd"])[0]
            return self.send("set_appoint", [1, booking_time_start, booking_time_end])

        return self.send("set_mode", [mode.value])
