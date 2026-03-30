import logging
from typing import Any

import click

from miio.click_common import EnumType, command, format_output
from miio.miot_device import MiotDevice

from .status import PetFountainMode, XiaomiPetFountainStatus, _time_to_seconds

_LOGGER = logging.getLogger(__name__)

MODEL_XIAOMI_PET_WATERER_70M2 = "xiaomi.pet_waterer.70m2"

MIOT_MAPPING = {
    MODEL_XIAOMI_PET_WATERER_70M2: {
        "fault_code": {"siid": 2, "piid": 1},
        "status": {"siid": 2, "piid": 3},
        "mode": {"siid": 2, "piid": 4},
        "water_shortage": {"siid": 2, "piid": 10},
        "water_interval": {"siid": 2, "piid": 11},
        "filter_life_remaining": {"siid": 3, "piid": 1},
        "filter_left_time": {"siid": 3, "piid": 2},
        "reset_filter_life": {"siid": 3, "aiid": 1},
        "child_lock": {"siid": 4, "piid": 1},
        "battery": {"siid": 5, "piid": 1},
        "charging_state": {"siid": 5, "piid": 2},
        "do_not_disturb": {"siid": 6, "piid": 1},
        "low_battery": {"siid": 9, "piid": 5},
        "usb_power": {"siid": 9, "piid": 6},
        "dnd_start": {"siid": 9, "piid": 10},
        "dnd_end": {"siid": 9, "piid": 11},
        "pump_blocked": {"siid": 9, "piid": 12},
    }
}


class XiaomiPetFountain(MiotDevice):
    """Main class representing Xiaomi Pet Fountain 2."""

    _mappings = MIOT_MAPPING

    @command(
        default_output=format_output(
            "",
            "Status: {result.status}\n"
            "Mode: {result.mode}\n"
            "Water shortage: {result.water_shortage}\n"
            "Pump blocked: {result.pump_blocked}\n"
            "Filter life remaining: {result.filter_life_remaining}\n"
            "Filter time remaining: {result.filter_left_time}\n"
            "Battery: {result.battery}\n"
            "Charging state: {result.charging_state}\n"
            "Do not disturb: {result.do_not_disturb}\n"
            "DND start: {result.dnd_start}\n"
            "DND end: {result.dnd_end}\n"
            "Child lock: {result.child_lock}\n"
            "Fault code: {result.fault_code}\n",
        )
    )
    def status(self) -> XiaomiPetFountainStatus:
        """Retrieve properties."""
        data = {
            prop["did"]: prop["value"] if prop["code"] == 0 else None
            for prop in self.get_properties_for_mapping()
        }
        _LOGGER.debug(data)
        return XiaomiPetFountainStatus(data)

    @command(
        click.argument("mode", type=EnumType(PetFountainMode)),
        default_output=format_output('Changing mode to "{mode.name}"'),
    )
    def set_mode(self, mode: PetFountainMode) -> list[dict[str, Any]]:
        """Set the water dispensing mode."""
        raw_mode = {
            PetFountainMode.Auto: 0,
            PetFountainMode.Interval: 1,
            PetFountainMode.Continuous: 2,
        }[mode]
        return self.set_property("mode", raw_mode)

    @command(
        click.argument("minutes", type=click.IntRange(10, 120)),
        default_output=format_output('Changing water interval to "{minutes}" minutes'),
    )
    def set_water_interval(self, minutes: int) -> list[dict[str, Any]]:
        """Set the interval mode water interval in minutes."""
        if minutes % 5 != 0:
            raise ValueError("Water interval must be set in 5 minute increments")
        return self.set_property("water_interval", minutes)

    @command(
        click.argument("enabled", type=bool),
        default_output=format_output(
            lambda enabled: "Enabling child lock" if enabled else "Disabling child lock"
        ),
    )
    def set_child_lock(self, enabled: bool) -> list[dict[str, Any]]:
        """Set the child lock."""
        return self.set_property("child_lock", enabled)

    @command(
        click.argument("enabled", type=bool),
        default_output=format_output(
            lambda enabled: "Enabling do not disturb"
            if enabled
            else "Disabling do not disturb"
        ),
    )
    def set_do_not_disturb(self, enabled: bool) -> list[dict[str, Any]]:
        """Set do not disturb mode."""
        return self.set_property("do_not_disturb", enabled)

    @command(default_output=format_output("Resetting filter life"))
    def reset_filter_life(self) -> dict[str, Any]:
        """Reset filter life."""
        return self.call_action_from_mapping("reset_filter_life")

    @command(
        click.argument("value", type=click.DateTime(formats=["%H:%M:%S", "%H:%M"])),
        default_output=format_output('Changing DnD start to "{value}"'),
    )
    def set_dnd_start(self, value) -> list[dict[str, Any]]:
        """Set the DnD start time."""
        parsed = value.time() if hasattr(value, "time") else value
        return self.set_property("dnd_start", _time_to_seconds(parsed))

    @command(
        click.argument("value", type=click.DateTime(formats=["%H:%M:%S", "%H:%M"])),
        default_output=format_output('Changing DnD end to "{value}"'),
    )
    def set_dnd_end(self, value) -> list[dict[str, Any]]:
        """Set the DnD end time."""
        parsed = value.time() if hasattr(value, "time") else value
        return self.set_property("dnd_end", _time_to_seconds(parsed))
