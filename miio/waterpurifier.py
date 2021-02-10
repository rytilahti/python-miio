import logging
from typing import Any, Dict

from .click_common import command, format_output
from .device import Device, DeviceStatus

_LOGGER = logging.getLogger(__name__)


class WaterPurifierStatus(DeviceStatus):
    """Container for status reports from the water purifier."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def mode(self) -> str:
        """Current operation mode."""
        return self.data["mode"]

    @property
    def tds(self) -> str:
        return self.data["tds"]

    @property
    def filter_life_remaining(self) -> int:
        """Time until the filter should be changed."""
        return self.data["filter1_life"]

    @property
    def filter_state(self) -> str:
        return self.data["filter1_state"]

    @property
    def filter2_life_remaining(self) -> int:
        """Time until the filter should be changed."""
        return self.data["filter_life"]

    @property
    def filter2_state(self) -> str:
        return self.data["filter_state"]

    @property
    def life(self) -> str:
        return self.data["life"]

    @property
    def state(self) -> str:
        return self.data["state"]

    @property
    def level(self) -> str:
        return self.data["level"]

    @property
    def volume(self) -> str:
        return self.data["volume"]

    @property
    def filter(self) -> str:
        return self.data["filter"]

    @property
    def usage(self) -> str:
        return self.data["usage"]

    @property
    def temperature(self) -> str:
        return self.data["temperature"]

    @property
    def uv_filter_life_remaining(self) -> int:
        """Time until the filter should be changed."""
        return self.data["uv_life"]

    @property
    def uv_filter_state(self) -> str:
        return self.data["uv_state"]

    @property
    def valve(self) -> str:
        return self.data["elecval_state"]


class WaterPurifier(Device):
    """Main class representing the waiter purifier."""

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "TDS: {result.tds}\n"
            "Filter life remaining: {result.filter_life_remaining}\n"
            "Filter state: {result.filter_state}\n"
            "Filter2 life remaining: {result.filter2_life_remaining}\n"
            "Filter2 state: {result.filter2_state}\n"
            "Life remaining: {result.life_remaining}\n"
            "State: {result.state}\n"
            "Level: {result.level}\n"
            "Volume: {result.volume}\n"
            "Filter: {result.filter}\n"
            "Usage: {result.usage}\n"
            "Temperature: {result.temperature}\n"
            "UV filter life remaining: {result.uv_filter_life_remaining}\n"
            "UV filter state: {result.uv_filter_state}\n"
            "Valve: {result.valve}\n",
        )
    )
    def status(self) -> WaterPurifierStatus:
        """Retrieve properties."""

        properties = [
            "power",
            "mode",
            "tds",
            "filter1_life",
            "filter1_state",
            "filter_life",
            "filter_state",
            "life",
            "state",
            "level",
            "volume",
            "filter",
            "usage",
            "temperature",
            "uv_life",
            "uv_state",
            "elecval_state",
        ]

        _props_per_request = 1
        values = self.get_properties(properties, max_properties=_props_per_request)

        return WaterPurifierStatus(dict(zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])
