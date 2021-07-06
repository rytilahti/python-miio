import enum
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .exceptions import DeviceException
from .miot_device import DeviceStatus, MiotDevice, MiotMapping


class YeelightDualControlModuleException(DeviceException):
    pass


class Switch(enum.Enum):
    First = 0
    Second = 1


_MAPPING: MiotMapping = {
    # http://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:switch:0000A003:yeelink-sw1:1:0000C809
    # First Switch (siid=2)
    "switch_1_state": {"siid": 2, "piid": 1},  # bool
    "switch_1_default_state": {"siid": 2, "piid": 2},  # 0 - Off, 1 - On
    "switch_1_off_delay": {"siid": 2, "piid": 3},  # -1 - Off, [1, 43200] - delay in sec
    # Second Switch (siid=3)
    "switch_2_state": {"siid": 3, "piid": 1},  # bool
    "switch_2_default_state": {"siid": 3, "piid": 2},  # 0 - Off, 1 - On
    "switch_2_off_delay": {"siid": 3, "piid": 3},  # -1 - Off, [1, 43200] - delay in sec
    # Extensions (siid=4)
    "interlock": {"siid": 4, "piid": 1},  # bool
    "flex_mode": {"siid": 4, "piid": 2},  # 0 - Off, 1 - On
    "rc_list": {"siid": 4, "piid": 3},  # string
    "rc_list_for_del": {"siid": 4, "piid": 4},  # string
    "toggle": {"siid": 4, "piid": 5},  # 0 - First switch, 1 - Second switch
}


class DualControlModuleStatus(DeviceStatus):
    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of Yeelight Dual Control Module
        {
            'id': 1,
            'result': [
                {'did': 'switch_1_state', 'siid': 2, 'piid': 1, 'code': 0, 'value': False},
                {'did': 'switch_1_default_state', 'siid': 2, 'piid': 2, 'code': 0, 'value': True},
                {'did': 'switch_1_off_delay', 'siid': 2, 'piid': 3, 'code': 0, 'value': 300},
                {'did': 'switch_2_state', 'siid': 3, 'piid': 1, 'code': 0, 'value': False},
                {'did': 'switch_2_default_state', 'siid': 3, 'piid': 2, 'code': 0, 'value': False},
                {'did': 'switch_2_off_delay', 'siid': 3, 'piid': 3, 'code': 0, 'value': 0},
                {'did': 'interlock', 'siid': 4, 'piid': 1, 'code': 0, 'value': False},
                {'did': 'flex_mode', 'siid': 4, 'piid': 2, 'code': 0, 'value': True},
                {'did': 'rc_list', 'siid': 4, 'piid': 2, 'code': 0, 'value': '[{"mac":"9db0eb4124f8","evtid":4097,"pid":339,"beaconkey":"3691bc0679eef9596bb63abf"}]'},
            ]
        }
        """
        self.data = data

    @property
    def switch_1_state(self) -> bool:
        """First switch state."""
        return bool(self.data["switch_1_state"])

    @property
    def switch_1_default_state(self) -> bool:
        """First switch default state."""
        return bool(self.data["switch_1_default_state"])

    @property
    def switch_1_off_delay(self) -> int:
        """First switch off delay."""
        return self.data["switch_1_off_delay"]

    @property
    def switch_2_state(self) -> bool:
        """Second switch state."""
        return bool(self.data["switch_2_state"])

    @property
    def switch_2_default_state(self) -> bool:
        """Second switch default state."""
        return bool(self.data["switch_2_default_state"])

    @property
    def switch_2_off_delay(self) -> int:
        """Second switch off delay."""
        return self.data["switch_2_off_delay"]

    @property
    def interlock(self) -> bool:
        """Interlock."""
        return bool(self.data["interlock"])

    @property
    def flex_mode(self) -> int:
        """Flex mode."""
        return self.data["flex_mode"]

    @property
    def rc_list(self) -> str:
        """List of paired remote controls."""
        return self.data["rc_list"]


class YeelightDualControlModule(MiotDevice):
    """Main class representing the Yeelight Dual Control Module (yeelink.switch.sw1)
    which uses MIoT protocol."""

    mapping = _MAPPING

    @command(
        default_output=format_output(
            "",
            "First Switch Status: {result.switch_1_state}\n"
            "First Switch Default State: {result.switch_1_default_state}\n"
            "First Switch Delay: {result.switch_1_off_delay}\n"
            "Second Switch Status: {result.switch_2_state}\n"
            "Second Switch Default State: {result.switch_2_default_state}\n"
            "Second Switch Delay: {result.switch_2_off_delay}\n"
            "Interlock: {result.interlock}\n"
            "Flex Mode: {result.flex_mode}\n"
            "RC list: {result.rc_list}\n",
        )
    )
    def status(self) -> DualControlModuleStatus:
        """Retrieve properties."""
        p = [
            "switch_1_state",
            "switch_1_default_state",
            "switch_1_off_delay",
            "switch_2_state",
            "switch_2_default_state",
            "switch_2_off_delay",
            "interlock",
            "flex_mode",
            "rc_list",
        ]
        """Filter only readable properties for status"""
        properties = [
            {"did": k, **v}
            for k, v in filter(lambda item: item[0] in p, _MAPPING.items())
        ]
        values = self.get_properties(properties)
        return DualControlModuleStatus(
            dict(map(lambda v: (v["did"], v["value"]), values))
        )

    @command(
        click.argument("switch", type=EnumType(Switch)),
        default_output=format_output("Turn {switch} switch on"),
    )
    def on(self, switch: Switch):
        """Turn switch on."""
        if switch == Switch.First:
            return self.set_property("switch_1_state", True)
        elif switch == Switch.Second:
            return self.set_property("switch_2_state", True)

    @command(
        click.argument("switch", type=EnumType(Switch)),
        default_output=format_output("Turn {switch} switch off"),
    )
    def off(self, switch: Switch):
        """Turn switch off."""
        if switch == Switch.First:
            return self.set_property("switch_1_state", False)
        elif switch == Switch.Second:
            return self.set_property("switch_2_state", False)

    @command(
        click.argument("switch", type=EnumType(Switch)),
        default_output=format_output("Toggle {switch} switch"),
    )
    def toggle(self, switch: Switch):
        """Toggle switch."""
        return self.set_property("toggle", switch.value)

    @command(
        click.argument("state", type=bool),
        click.argument("switch", type=EnumType(Switch)),
        default_output=format_output("Set {switch} switch default state to: {state}"),
    )
    def set_default_state(self, state: bool, switch: Switch):
        """Set switch default state."""
        if switch == Switch.First:
            return self.set_property("switch_1_default_state", int(state))
        elif switch == Switch.Second:
            return self.set_property("switch_2_default_state", int(state))

    @command(
        click.argument("delay", type=int),
        click.argument("switch", type=EnumType(Switch)),
        default_output=format_output("Set {switch} switch off delay to {delay} sec."),
    )
    def set_switch_off_delay(self, delay: int, switch: Switch):
        """Set switch off delay, should be between -1 to 43200 (in seconds)"""
        if delay < -1 or delay > 43200:
            raise YeelightDualControlModuleException(
                "Invalid switch delay: %s (should be between -1 to 43200)" % delay
            )

        if switch == Switch.First:
            return self.set_property("switch_1_off_delay", delay)
        elif switch == Switch.Second:
            return self.set_property("switch_2_off_delay", delay)

    @command(
        click.argument("flex_mode", type=bool),
        default_output=format_output("Set flex mode to: {flex_mode}"),
    )
    def set_flex_mode(self, flex_mode: bool):
        """Set flex mode."""
        return self.set_property("flex_mode", int(flex_mode))

    @command(
        click.argument("rc_mac", type=str),
        default_output=format_output("Delete remote control with MAC: {rc_mac}"),
    )
    def delete_rc(self, rc_mac: str):
        """Delete remote control by MAC."""
        return self.set_property("rc_list_for_del", rc_mac)

    @command(
        click.argument("interlock", type=bool),
        default_output=format_output("Set interlock to: {interlock}"),
    )
    def set_interlock(self, interlock: bool):
        """Set interlock."""
        return self.set_property("interlock", interlock)
