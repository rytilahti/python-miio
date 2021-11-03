import enum
import logging
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .exceptions import DeviceException
from .miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)

MODEL_MMGG_PET_WATERER_S1 = "mmgg.pet_waterer.s1"

SUPPORTED_MODELS = [
    MODEL_MMGG_PET_WATERER_S1,
]

_MAPPING = {
    # https://home.miot-spec.com/spec/mmgg.pet_waterer.s1
    "cotton_left_time": {"siid": 5, "piid": 1},
    "reset_cotton_life": {"siid": 5, "aiid": 1},
    "reset_clean_time": {"siid": 6, "aiid": 1},
    "fault": {"siid": 2, "piid": 1},
    "filter_left_time": {"siid": 3, "piid": 1},
    "indicator_light": {"siid": 4, "piid": 1},
    "lid_up_flag": {"siid": 7, "piid": 4},
    "location": {"siid": 9, "piid": 2},
    "mode": {"siid": 2, "piid": 3},
    "no_water_flag": {"siid": 7, "piid": 1},
    "no_water_time": {"siid": 7, "piid": 2},
    "on": {"siid": 2, "piid": 2},
    "pump_block_flag": {"siid": 7, "piid": 3},
    "remain_clean_time": {"siid": 6, "piid": 1},
    "reset_filter_life": {"siid": 3, "aiid": 1},
    "reset_device": {"siid": 8, "aiid": 1},
    "timezone": {"siid": 9, "piid": 1},
}


class OperatingMode(enum.Enum):
    common = 1
    smart = 2


class PetWaterDispenserException(DeviceException):
    pass


class PetWaterDispenserStatus(DeviceStatus):
    """Container for status reports from the Pet Water Dispenser."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Pet Waterer / Pet Drinking Fountain / Smart Pet Water Dispenser
        (mmgg.pet_waterer.s1)"""
        self.data = data

    @property
    def filter_left_time(self) -> int:
        """Filter life time remaining in days."""
        return self.data["filter_left_time"]

    @property
    def is_on(self) -> bool:
        """True if device is on."""
        return self.data["on"]

    @property
    def mode(self) -> str:
        """OperatingMode."""
        return OperatingMode(self.data["mode"]).name

    @property
    def indicator_light_enabled(self) -> bool:
        """True if enabled."""
        return self.data["indicator_light"]

    @property
    def cotton_left_time(self) -> int:
        return self.data["cotton_left_time"]

    @property
    def days_before_cleaning(self) -> int:
        return self.data["remain_clean_time"]

    @property
    def no_water(self) -> bool:
        """True if there is no water left."""
        if self.data["no_water_flag"]:
            return False
        return True

    @property
    def minutes_without_water(self) -> int:
        return self.data["no_water_time"]

    @property
    def pump_is_blocked(self) -> bool:
        """True if pump is blocked."""
        return self.data["pump_block_flag"]

    @property
    def lid_is_up(self) -> bool:
        """True if lid is up."""
        return self.data["lid_up_flag"]

    @property
    def timezone(self) -> int:
        return self.data["timezone"]

    @property
    def location(self) -> str:
        return self.data["location"]

    @property
    def error_detected(self) -> bool:
        """True if fault detected."""
        return self.data["fault"] > 0


class PetWaterDispenser(MiotDevice):
    """Main class representing the pet water dispenser."""

    mapping = _MAPPING

    @command(
        default_output=format_output(
            "",
            "Cotton filter live: {result.cotton_left_time} day(s) left\n"
            "Days before cleaning: {result.days_before_cleaning} day(s)\n"
            "Error detected: {result.error_detected}\n"
            "Filter live: {result.filter_left_time} day(s) left\n"
            "Indicator light enabled: {result.indicator_light_enabled}\n"
            "Lid is up: {result.lid_is_up}\n"
            "Location: {result.location}\n"
            "Mode: {result.mode}\n"
            "Minutes without water: {result.minutes_without_water} minute(s)\n"
            "No water: {result.no_water}\n"
            "Is turned on: {result.is_on}\n"
            "Pump is blocked: {result.pump_is_blocked}\n"
            "Timezone: {result.timezone}\n",
        )
    )
    def status(self) -> PetWaterDispenserStatus:
        """Retrieve properties."""
        return PetWaterDispenserStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(
        click.argument("power", type=bool),
        default_output=format_output(
            lambda power: "Turning device on" if power else "Turning device off"
        ),
    )
    def set_power(self, power: bool) -> Dict[str, Any]:
        """Toggle device power on/off."""
        if power:
            return self.set_property("on", True)
        return self.set_property("on", False)

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning LED on" if led else "Turning LED off"
        ),
    )
    def set_led(self, led: bool) -> Dict[str, Any]:
        """Toggle idicator light on/off."""
        if led:
            return self.set_property("indicator_light", True)
        return self.set_property("indicator_light", False)

    @command(
        click.argument("mode", type=EnumType(OperatingMode)),
        default_output=format_output('Changing mode to "{mode.name}"'),
    )
    def set_mode(self, mode: OperatingMode) -> Dict[str, Any]:
        """Switch operation mode."""
        return self.set_property("mode", mode.value)

    @command(default_output=format_output("Resetting filter"))
    def reset_filter(self) -> Dict[str, Any]:
        """Reset filter life counter."""
        return self.call_action("reset_filter_life")

    @command(default_output=format_output("Resetting cotton filter"))
    def reset_cotton_filter(self) -> Dict[str, Any]:
        """Reset cotton filter life counter."""
        return self.call_action("reset_cotton_life")

    @command(default_output=format_output("Resetting cleaning time"))
    def reset_cleaning_time(self) -> Dict[str, Any]:
        """Reset cleaning time counter."""
        return self.call_action("reset_clean_time")

    @command(default_output=format_output("Resetting device"))
    def reset(self) -> Dict[str, Any]:
        """Reset device."""
        return self.call_action("reset_device")

    @command(
        click.argument("timezone", type=click.IntRange(-12, 12)),
        default_output=format_output('Changing timezone to "{timezone}"'),
    )
    def set_timezone(self, timezone: int) -> Dict[str, Any]:
        """Change timezone."""
        return self.set_property("timezone", timezone)

    @command(
        click.argument("location", type=str),
        default_output=format_output('Changing location to "{location}"'),
    )
    def set_location(self, location: str) -> Dict[str, Any]:
        """Change location."""
        return self.set_property("location", location)
