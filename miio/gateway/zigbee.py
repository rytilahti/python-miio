"""Xiaomi Gateway Zigbee control implementation."""

import click

from ..click_common import command
from .gatewaydevice import GatewayDevice


class Zigbee(GatewayDevice):
    """Zigbee controls."""

    @command()
    def get_zigbee_version(self):
        """timeouts on device."""
        return self._gateway.send("get_zigbee_device_version")

    @command()
    def get_zigbee_channel(self):
        """Return currently used zigbee channel."""
        return self._gateway.send("get_zigbee_channel")[0]

    @command(click.argument("channel"))
    def set_zigbee_channel(self, channel):
        """Set zigbee channel."""
        return self._gateway.send("set_zigbee_channel", [channel])

    @command(click.argument("timeout", type=int))
    def zigbee_pair(self, timeout):
        """Start pairing, use 0 to disable."""
        return self._gateway.send("start_zigbee_join", [timeout])

    def send_to_zigbee(self):
        """How does this differ from writing?

        Unknown.
        """
        raise NotImplementedError()
        return self._gateway.send("send_to_zigbee")

    def read_zigbee_eep(self):
        """Read eeprom?"""
        raise NotImplementedError()
        return self._gateway.send("read_zig_eep", [0])  # 'ok'

    def read_zigbee_attribute(self):
        """Read zigbee data?"""
        raise NotImplementedError()
        return self._gateway.send("read_zigbee_attribute", [0x0000, 0x0080])

    def write_zigbee_attribute(self):
        """Unknown parameters."""
        raise NotImplementedError()
        return self._gateway.send("write_zigbee_attribute")

    @command()
    def zigbee_unpair_all(self):
        """Unpair all devices."""
        return self._gateway.send("remove_all_device")

    def zigbee_unpair(self, sid):
        """Unpair a device."""
        # get a device obj an call dev.unpair()
        raise NotImplementedError()
