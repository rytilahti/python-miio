import logging
from typing import Any, Dict
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)


class WaterPurifierStatus:
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

    def __repr__(self) -> str:
        return "<WaterPurifierStatus " \
               "power=%s, " \
               "mode=%s, " \
               "tds=%s, " \
               "filter_life_remaining=%s, " \
               "filter_state=%s, " \
               "filter2_life_remaining=%s, " \
               "filter2_state=%s, " \
               "life=%s, " \
               "state=%s, " \
               "level=%s, " \
               "volume=%s, " \
               "filter=%s, " \
               "usage=%s, " \
               "temperature=%s, " \
               "uv_filter_life_remaining=%s, " \
               "uv_filter_state=%s, " \
               "valve=%s>" % \
               (self.power,
                self.mode,
                self.tds,
                self.filter_life_remaining,
                self.filter_state,
                self.filter2_life_remaining,
                self.filter2_state,
                self.life,
                self.state,
                self.level,
                self.volume,
                self.filter,
                self.usage,
                self.temperature,
                self.uv_filter_life_remaining,
                self.uv_filter_state,
                self.valve)


class WaterPurifier(Device):
    """Main class representing the waiter purifier."""

    def status(self) -> WaterPurifierStatus:
        """Retrieve properties."""

        properties = ['power', 'mode', 'tds', 'filter1_life', 'filter1_state',
                      'filter_life', 'filter_state', 'life', 'state', 'level',
                      'volume', 'filter', 'usage', 'temperature', 'uv_life',
                      'uv_state', 'elecval_state']

        values = self.send(
            "get_prop",
            properties
        )

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return WaterPurifierStatus(
            defaultdict(lambda: None, zip(properties, values)))

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])
