import logging
from typing import Any

from miio import Device, DeviceStatus
from miio.click_common import command, format_output
from miio.devicestatus import sensor

_LOGGER = logging.getLogger(__name__)


class WaterPurifierStatus(DeviceStatus):
    """Container for status reports from the water purifier."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    @property
    @sensor("Power", icon="mdi:power")
    def power(self) -> str:
        return self.data["power"]

    @property
    @sensor("Is On", icon="mdi:power")
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    @sensor("Mode", icon="mdi:water")
    def mode(self) -> str:
        """Current operation mode."""
        return self.data["mode"]

    @property
    @sensor("TDS", unit="ppm", icon="mdi:water-opacity")
    def tds(self) -> str:
        return self.data["tds"]

    @property
    @sensor("Filter Life Remaining", unit="%", icon="mdi:filter")
    def filter_life_remaining(self) -> int:
        """Time until the filter should be changed."""
        return self.data["filter1_life"]

    @property
    @sensor("Filter State", icon="mdi:filter")
    def filter_state(self) -> str:
        return self.data["filter1_state"]

    @property
    @sensor("Filter 2 Life Remaining", unit="%", icon="mdi:filter")
    def filter2_life_remaining(self) -> int:
        """Time until the filter should be changed."""
        return self.data["filter_life"]

    @property
    @sensor("Filter 2 State", icon="mdi:filter")
    def filter2_state(self) -> str:
        return self.data["filter_state"]

    @property
    @sensor("Life", icon="mdi:clock-outline")
    def life(self) -> str:
        return self.data["life"]

    @property
    @sensor("State", icon="mdi:information-outline")
    def state(self) -> str:
        return self.data["state"]

    @property
    @sensor("Level", icon="mdi:water")
    def level(self) -> str:
        return self.data["level"]

    @property
    @sensor("Volume", icon="mdi:cup-water")
    def volume(self) -> str:
        return self.data["volume"]

    @property
    @sensor("Filter", icon="mdi:filter")
    def filter(self) -> str:
        return self.data["filter"]

    @property
    @sensor("Usage", icon="mdi:chart-line")
    def usage(self) -> str:
        return self.data["usage"]

    @property
    @sensor(
        "Temperature", unit="°C", device_class="temperature", icon="mdi:thermometer"
    )
    def temperature(self) -> str:
        return self.data["temperature"]

    @property
    @sensor("UV Filter Life Remaining", unit="%", icon="mdi:filter")
    def uv_filter_life_remaining(self) -> int:
        """Time until the filter should be changed."""
        return self.data["uv_life"]

    @property
    @sensor("UV Filter State", icon="mdi:filter")
    def uv_filter_state(self) -> str:
        return self.data["uv_state"]

    @property
    @sensor("Valve", icon="mdi:valve")
    def valve(self) -> str:
        return self.data["elecval_state"]


class WaterPurifier(Device):
    """Main class representing the water purifier."""

    _supported_models = [
        "yunmi.waterpuri.v2",  # unknown if correct, based on mdns response
    ]

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
