import enum
import logging
from datetime import timedelta
from typing import Any, Dict, List

import click

from miio.click_common import EnumType, command, format_output
from miio.miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)

MODEL_MMGG_PET_WATERER_S1 = "mmgg.pet_waterer.s1"
MODEL_MMGG_PET_WATERER_S4 = "mmgg.pet_waterer.s4"

SUPPORTED_MODELS: List[str] = [MODEL_MMGG_PET_WATERER_S1, MODEL_MMGG_PET_WATERER_S4]

_MAPPING: Dict[str, Dict[str, int]] = {
    # https://home.miot-spec.com/spec/mmgg.pet_waterer.s1
    # https://home.miot-spec.com/spec/mmgg.pet_waterer.s4
    "cotton_left_time": {"siid": 5, "piid": 1},
    "reset_cotton_life": {"siid": 5, "aiid": 1},
    "reset_clean_time": {"siid": 6, "aiid": 1},
    "fault": {"siid": 2, "piid": 1},
    "filter_left_time": {"siid": 3, "piid": 1},
    "indicator_light": {"siid": 4, "piid": 1},
    "lid_up_flag": {"siid": 7, "piid": 4},  # missing on mmgg.pet_waterer.s4
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
    Normal = 1
    Smart = 2


class PetWaterDispenserStatus(DeviceStatus):
    """Container for status reports from Pet Water Dispenser."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of Pet Water Dispenser (mmgg.pet_waterer.s1)
        [
            {'code': 0, 'did': 'cotton_left_time', 'piid': 1, 'siid': 5, 'value': 10},
            {'code': 0, 'did': 'fault', 'piid': 1, 'siid': 2, 'value': 0},
            {'code': 0, 'did': 'filter_left_time', 'piid': 1, 'siid': 3, 'value': 10},
            {'code': 0, 'did': 'indicator_light', 'piid': 1, 'siid': 4, 'value': True},
            {'code': 0, 'did': 'lid_up_flag', 'piid': 4, 'siid': 7, 'value': False},
            {'code': 0, 'did': 'location', 'piid': 2, 'siid': 9, 'value': 'ru'},
            {'code': 0, 'did': 'mode', 'piid': 3, 'siid': 2, 'value': 1},
            {'code': 0, 'did': 'no_water_flag', 'piid': 1, 'siid': 7, 'value': True},
            {'code': 0, 'did': 'no_water_time', 'piid': 2, 'siid': 7, 'value': 0},
            {'code': 0, 'did': 'on', 'piid': 2, 'siid': 2, 'value': True},
            {'code': 0, 'did': 'pump_block_flag', 'piid': 3, 'siid': 7, 'value': False},
            {'code': 0, 'did': 'remain_clean_time', 'piid': 1, 'siid': 6, 'value': 4},
            {'code': 0, 'did': 'timezone', 'piid': 1, 'siid': 9, 'value': 3}
        ]
        """
        self.data = data

    @property
    def sponge_filter_left_days(self) -> timedelta:
        """Filter life time remaining in days."""
        return timedelta(days=self.data["filter_left_time"])

    @property
    def is_on(self) -> bool:
        """True if device is on."""
        return self.data["on"]

    @property
    def mode(self) -> OperatingMode:
        """OperatingMode."""
        return OperatingMode(self.data["mode"])

    @property
    def is_led_on(self) -> bool:
        """True if enabled."""
        return self.data["indicator_light"]

    @property
    def cotton_left_days(self) -> timedelta:
        """Cotton filter life time remaining in days."""
        return timedelta(days=self.data["cotton_left_time"])

    @property
    def before_cleaning_days(self) -> timedelta:
        """Days before cleaning."""
        return timedelta(days=self.data["remain_clean_time"])

    @property
    def is_no_water(self) -> bool:
        """True if there is no water left."""
        if self.data["no_water_flag"]:
            return False
        return True

    @property
    def no_water_minutes(self) -> timedelta:
        """Minutes without water."""
        return timedelta(minutes=self.data["no_water_time"])

    @property
    def is_pump_blocked(self) -> bool:
        """True if pump is blocked."""
        return self.data["pump_block_flag"]

    @property
    def is_lid_up(self) -> bool:
        """True if lid is up."""
        return self.data["lid_up_flag"]

    @property
    def timezone(self) -> int:
        """Timezone from -12 to +12."""
        return self.data["timezone"]

    @property
    def location(self) -> str:
        """Device location string."""
        return self.data["location"]

    @property
    def is_error_detected(self) -> bool:
        """True if fault detected."""
        return self.data["fault"] > 0


class PetWaterDispenser(MiotDevice):
    """Main class representing the Pet Waterer / Pet Drinking Fountain / Smart Pet Water
    Dispenser."""

    mapping = _MAPPING
    _supported_models = SUPPORTED_MODELS

    @command(
        default_output=format_output(
            "",
            "On: {result.is_on}\n"
            "Mode: {result.mode}\n"
            "LED on: {result.is_led_on}\n"
            "Lid up: {result.is_lid_up}\n"
            "No water: {result.is_no_water}\n"
            "Time without water: {result.no_water_minutes}\n"
            "Pump blocked: {result.is_pump_blocked}\n"
            "Error detected: {result.is_error_detected}\n"
            "Days before cleaning left: {result.before_cleaning_days}\n"
            "Cotton filter live left: {result.cotton_left_days}\n"
            "Sponge filter live left: {result.sponge_filter_left_days}\n"
            "Location: {result.location}\n"
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

    @command(default_output=format_output("Turning device on"))
    def on(self) -> List[Dict[str, Any]]:
        """Turn device on."""
        return self.set_property("on", True)

    @command(default_output=format_output("Turning device off"))
    def off(self) -> List[Dict[str, Any]]:
        """Turn device off."""
        return self.set_property("on", False)

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning LED on" if led else "Turning LED off"
        ),
    )
    def set_led(self, led: bool) -> List[Dict[str, Any]]:
        """Toggle indicator light on/off."""
        if led:
            return self.set_property("indicator_light", True)
        return self.set_property("indicator_light", False)

    @command(
        click.argument("mode", type=EnumType(OperatingMode)),
        default_output=format_output('Changing mode to "{mode.name}"'),
    )
    def set_mode(self, mode: OperatingMode) -> List[Dict[str, Any]]:
        """Switch operation mode."""
        return self.set_property("mode", mode.value)

    @command(default_output=format_output("Resetting sponge filter"))
    def reset_sponge_filter(self) -> List[Dict[str, Any]]:
        """Reset sponge filter."""
        return self.call_action("reset_filter_life")

    @command(default_output=format_output("Resetting cotton filter"))
    def reset_cotton_filter(self) -> List[Dict[str, Any]]:
        """Reset cotton filter."""
        return self.call_action("reset_cotton_life")

    @command(default_output=format_output("Resetting all filters"))
    def reset_all_filters(self) -> List[Dict[str, Any]]:
        """Reset all filters."""
        return self.reset_sponge_filter() + self.reset_cotton_filter()

    @command(default_output=format_output("Resetting cleaning time"))
    def reset_cleaning_time(self) -> List[Dict[str, Any]]:
        """Reset cleaning time counter."""
        return self.call_action("reset_clean_time")

    @command(default_output=format_output("Resetting device"))
    def reset(self) -> List[Dict[str, Any]]:
        """Reset device."""
        return self.call_action("reset_device")

    @command(
        click.argument("timezone", type=click.IntRange(-12, 12)),
        default_output=format_output('Changing timezone to "{timezone}"'),
    )
    def set_timezone(self, timezone: int) -> List[Dict[str, Any]]:
        """Change timezone."""
        return self.set_property("timezone", timezone)

    @command(
        click.argument("location", type=str),
        default_output=format_output('Changing location to "{location}"'),
    )
    def set_location(self, location: str) -> List[Dict[str, Any]]:
        """Change location."""
        return self.set_property("location", location)
