import logging
from collections import defaultdict
from typing import Dict, Any

import click

from .click_common import command, format_output
from .device import Device

_LOGGER = logging.getLogger(__name__)

MODEL_PWZN_RELAY_APPLE = 'pwzn.relay.apple'
MODEL_PWZN_RELAY_BANANA = 'pwzn.relay.banana'

AVAILABLE_PROPERTIES = {
    MODEL_PWZN_RELAY_APPLE: [
        'relay_status', 'on_count', 'name0', 'name1', 'name2', 'name3',
        'name4', 'name5', 'name6', 'name7', 'name8', 'name9', 'name10',
        'name11', 'name12', 'name13', 'name14', 'name15'
    ],
    MODEL_PWZN_RELAY_BANANA: [
        'relay_status', 'on_count', 'name0', 'name1', 'name2', 'name3',
        'name4', 'name5', 'name6', 'name7', 'name8', 'name9', 'name10',
        'name11', 'name12', 'name13', 'name14', 'name15'
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
    def name0(self) -> str:
        """Name of relay0."""
        if "name0" in self.data:
            return self.data["name0"]

    @property
    def name1(self) -> str:
        """Name of relay1."""
        if "name1" in self.data:
            return self.data["name1"]

    @property
    def name2(self) -> str:
        """Name of relay2."""
        if "name2" in self.data:
            return self.data["name2"]

    @property
    def name3(self) -> str:
        """Name of relay3."""
        if "name3" in self.data:
            return self.data["name3"]

    @property
    def name4(self) -> str:
        """Name of relay4."""
        if "name4" in self.data:
            return self.data["name4"]

    @property
    def name5(self) -> str:
        """Name of relay5."""
        if "name5" in self.data:
            return self.data["name5"]

    @property
    def name6(self) -> str:
        """Name of relay6."""
        if "name6" in self.data:
            return self.data["name6"]

    @property
    def name7(self) -> str:
        """Name of relay7."""
        if "name7" in self.data:
            return self.data["name7"]

    @property
    def name8(self) -> str:
        """Name of relay8."""
        if "name8" in self.data:
            return self.data["name8"]

    @property
    def name9(self) -> str:
        """Name of relay9."""
        if "name9" in self.data:
            return self.data["name9"]

    @property
    def name10(self) -> str:
        """Name of relay10."""
        if "name10" in self.data:
            return self.data["name10"]

    @property
    def name11(self) -> str:
        """Name of relay11."""
        if "name11" in self.data:
            return self.data["name11"]

    @property
    def name12(self) -> str:
        """Name of relay12."""
        if "name12" in self.data:
            return self.data["name12"]

    @property
    def name13(self) -> str:
        """Name of relay13."""
        if "name13" in self.data:
            return self.data["name13"]

    @property
    def name14(self) -> str:
        """Name of relay14."""
        if "name14" in self.data:
            return self.data["name14"]

    @property
    def name15(self) -> str:
        """Name of relay15."""
        if "name15" in self.data:
            return self.data["name15"]

    @property
    def on_count(self) -> int:
        """Number of on relay."""
        if "on_count" in self.data:
            return self.data["on_count"]

    def __repr__(self) -> str:
        s = "<PwznRelayStatus " \
            "relay_status=%s, " \
            "name0=%s, " \
            "name1=%s, " \
            "name2=%s, " \
            "name3=%s, " \
            "name4=%s, " \
            "name5=%s, " \
            "name6=%s, " \
            "name7=%s, " \
            "name8=%s, " \
            "name9=%s, " \
            "name10=%s, " \
            "name11=%s, " \
            "name12=%s, " \
            "name13=%s, " \
            "name14=%s, " \
            "name15=%s, " \
            "on_count=%s>" % \
            (self.relay_state,
             self.name0,
             self.name1,
             self.name2,
             self.name3,
             self.name4,
             self.name5,
             self.name6,
             self.name7,
             self.name8,
             self.name9,
             self.name10,
             self.name11,
             self.name12,
             self.name13,
             self.name14,
             self.name15,
             self.on_count)
        return s

    def __json__(self):
        return self.data


class PwznRelay(Device):
    """Main class representing the PWZN Relay."""
    def __init__(self, ip: str = None, token: str = None, start_id: int = 0,
                 debug: int = 0, lazy_discover: bool = True,
                 model: str = MODEL_PWZN_RELAY_APPLE) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_PWZN_RELAY_APPLE

    @command(
        default_output=format_output(
            "",
            "on_count: {result.on_count}\n"
        )
    )
    def status(self) -> PwznRelayStatus:
        """Retrieve properties."""

        properties = AVAILABLE_PROPERTIES[self.model].copy()

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

        return PwznRelayStatus(
            defaultdict(lambda: None, zip(properties, values)))

    @command(
        click.argument("number", type=int),
        default_output=format_output(
            "Turn on relay {number}")
    )
    def relay_on(self, number: int = 0):
        """Relay X on."""
        if self.send("power_on", [number]) == [0]:
            return ['ok']

    @command(
        click.argument("number", type=int),
        default_output=format_output(
            "Turn off relay {number}")
    )
    def relay_off(self, number: int = 0):
        """Relay X off."""
        if self.send("power_off", [number]) == [0]:
            return ['ok']

    @command(
        default_output=format_output(
            "Turn on all relay")
    )
    def all_relay_on(self):
        """Relay all on."""
        return self.send("power_all", [1])

    @command(
        default_output=format_output(
            "Turn off all relay")
    )
    def all_relay_off(self):
        """Relay all off."""
        return self.send("power_all", [0])

    @command(
        click.argument("number", type=int),
        click.argument("name", type=str),
        default_output=format_output(
            "Set relay {number} name to {name}")
    )
    def set_name(self, number: int = 0, name: str = ''):
        """Set relay X name."""
        return self.send("set_name", [number, name])
