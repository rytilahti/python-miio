import logging
from collections import defaultdict
from typing import Dict, Any

import click

from .click_common import command, format_output
from .device import Device

_LOGGER = logging.getLogger(__name__)

MODEL_PWZN_RELAY_APPLE = "pwzn.relay.apple"
MODEL_PWZN_RELAY_BANANA = "pwzn.relay.banana"

AVAILABLE_PROPERTIES = {
    MODEL_PWZN_RELAY_APPLE: [
        "relay_status",
        "on_count",
        "name0",
        "name1",
        "name2",
        "name3",
        "name4",
        "name5",
        "name6",
        "name7",
        "name8",
        "name9",
        "name10",
        "name11",
        "name12",
        "name13",
        "name14",
        "name15",
    ],
    MODEL_PWZN_RELAY_BANANA: [
        "relay_status",
        "on_count",
        "name0",
        "name1",
        "name2",
        "name3",
        "name4",
        "name5",
        "name6",
        "name7",
        "name8",
        "name9",
        "name10",
        "name11",
        "name12",
        "name13",
        "name14",
        "name15",
    ],
}


class PwznRelayStatus:
    """Container for status reports from the plug."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a PWZN Relay Apple (pwzn.relay.apple)
        { 'relay_status': 9, 'on_count': 2, 'name0': 'channel1', 'name1': '',
        'name2': '', 'name3': '', 'name4': '', 'name5': '', 'name6': '',
        'name7': '', 'name8': '', 'name9': '', 'name10': '', 'name11': '',
        'name12': '', 'name13': '', 'name14': '', 'name15': '' }
        """
        self.data = data

    @property
    def relay_state(self) -> int:
        """Current relay state."""
        if "relay_status" in self.data:
            return self.data["relay_status"]

    @property
    def relay_names(self) -> Dict[int, str]:
        def _extract_index_from_key(name) -> int:
            """extract the index from the variable"""
            return int(name[4:])

        return {
            _extract_index_from_key(name): value
            for name, value in self.data.items()
            if name.startswith("name")
        }

    @property
    def on_count(self) -> int:
        """Number of on relay."""
        if "on_count" in self.data:
            return self.data["on_count"]

    def __repr__(self) -> str:
        s = (
            "<PwznRelayStatus "
            "relay_status=%s, "
            "relay_names=%s, "
            "on_count=%s>" % (self.relay_state, self.relay_names, self.on_count)
        )
        return s

    def __json__(self):
        return self.data


class PwznRelay(Device):
    """Main class representing the PWZN Relay."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_PWZN_RELAY_APPLE,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_PWZN_RELAY_APPLE

    @command(default_output=format_output("", "on_count: {result.on_count}\n"))
    def status(self) -> PwznRelayStatus:
        """Retrieve properties."""

        properties = AVAILABLE_PROPERTIES[self.model].copy()

        values = self.send("get_prop", properties)

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count,
                values_count,
            )

        return PwznRelayStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(
        click.argument("number", type=int),
        default_output=format_output("Turn on relay {number}"),
    )
    def relay_on(self, number: int = 0):
        """Relay X on."""
        if self.send("power_on", [number]) == [0]:
            return ["ok"]

    @command(
        click.argument("number", type=int),
        default_output=format_output("Turn off relay {number}"),
    )
    def relay_off(self, number: int = 0):
        """Relay X off."""
        if self.send("power_off", [number]) == [0]:
            return ["ok"]

    @command(default_output=format_output("Turn on all relay"))
    def all_relay_on(self):
        """Relay all on."""
        return self.send("power_all", [1])

    @command(default_output=format_output("Turn off all relay"))
    def all_relay_off(self):
        """Relay all off."""
        return self.send("power_all", [0])

    @command(
        click.argument("number", type=int),
        click.argument("name", type=str),
        default_output=format_output("Set relay {number} name to {name}"),
    )
    def set_name(self, number: int = 0, name: str = ""):
        """Set relay X name."""
        return self.send("set_name", [number, name])
