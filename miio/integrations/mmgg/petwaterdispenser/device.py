import logging
from typing import Any, Dict, List

import click

from miio.click_common import EnumType, command, format_output
from miio.miot_device import MiotDevice

from .status import OperatingMode, PetWaterDispenserStatus

_LOGGER = logging.getLogger(__name__)

MODEL_MMGG_PET_WATERER_S1 = "mmgg.pet_waterer.s1"
MODEL_MMGG_PET_WATERER_S4 = "mmgg.pet_waterer.s4"
MODEL_MMGG_PET_WATERER_WI11 = "mmgg.pet_waterer.wi11"

S_MODELS: List[str] = [MODEL_MMGG_PET_WATERER_S1, MODEL_MMGG_PET_WATERER_S4]
WI_MODELS: List[str] = [MODEL_MMGG_PET_WATERER_WI11]

_MAPPING_COMMON: Dict[str, Dict[str, int]] = {
    "mode": {"siid": 2, "piid": 3},
    "filter_left_time": {"siid": 3, "piid": 1},
    "reset_filter_life": {"siid": 3, "aiid": 1},
    "indicator_light": {"siid": 4, "piid": 1},
    "cotton_left_time": {"siid": 5, "piid": 1},
    "reset_cotton_life": {"siid": 5, "aiid": 1},
    "remain_clean_time": {"siid": 6, "piid": 1},
    "reset_clean_time": {"siid": 6, "aiid": 1},
    "no_water_flag": {"siid": 7, "piid": 1},
    "no_water_time": {"siid": 7, "piid": 2},
    "pump_block_flag": {"siid": 7, "piid": 3},
    "lid_up_flag": {"siid": 7, "piid": 4},
    "reset_device": {"siid": 8, "aiid": 1},
    "timezone": {"siid": 9, "piid": 1},
    "location": {"siid": 9, "piid": 2},
}

_MAPPING_S: Dict[str, Dict[str, int]] = {
    "fault": {"siid": 2, "piid": 1},
    "on": {"siid": 2, "piid": 2},
}

_MAPPING_WI: Dict[str, Dict[str, int]] = {
    "on": {"siid": 2, "piid": 1},
    "fault": {"siid": 2, "piid": 2},
}

MIOT_MAPPING = {
    **{model: {**_MAPPING_COMMON, **_MAPPING_S} for model in S_MODELS},
    **{model: {**_MAPPING_COMMON, **_MAPPING_WI} for model in WI_MODELS},
}


class PetWaterDispenser(MiotDevice):
    """Main class representing the Pet Waterer / Pet Drinking Fountain / Smart Pet Water
    Dispenser."""

    _mappings = MIOT_MAPPING

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
        data = {
            prop["did"]: prop["value"] if prop["code"] == 0 else None
            for prop in self.get_properties_for_mapping()
        }

        _LOGGER.debug(data)

        return PetWaterDispenserStatus(data)

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
    def reset_sponge_filter(self) -> Dict[str, Any]:
        """Reset sponge filter."""
        return self.call_action_from_mapping("reset_filter_life")

    @command(default_output=format_output("Resetting cotton filter"))
    def reset_cotton_filter(self) -> Dict[str, Any]:
        """Reset cotton filter."""
        return self.call_action_from_mapping("reset_cotton_life")

    @command(default_output=format_output("Resetting all filters"))
    def reset_all_filters(self) -> List[Dict[str, Any]]:
        """Reset all filters [cotton, sponge]."""
        return [self.reset_cotton_filter(), self.reset_sponge_filter()]

    @command(default_output=format_output("Resetting cleaning time"))
    def reset_cleaning_time(self) -> Dict[str, Any]:
        """Reset cleaning time counter."""
        return self.call_action_from_mapping("reset_clean_time")

    @command(default_output=format_output("Resetting device"))
    def reset(self) -> Dict[str, Any]:
        """Reset device."""
        return self.call_action_from_mapping("reset_device")

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
