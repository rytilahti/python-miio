"""Xiaomi Gateway Alarm implementation."""

from datetime import datetime

import click

from ..click_common import command, format_output
from .gatewaydevice import GatewayDevice


class Alarm(GatewayDevice):
    """Class representing the Xiaomi Gateway Alarm."""

    @command(default_output=format_output("[alarm_status]"))
    def status(self) -> str:
        """Return the alarm status from the device."""
        # Response: 'on', 'off', 'oning'
        return self._gateway.send("get_arming").pop()

    @command(default_output=format_output("Turning alarm on"))
    def on(self):
        """Turn alarm on."""
        return self._gateway.send("set_arming", ["on"])

    @command(default_output=format_output("Turning alarm off"))
    def off(self):
        """Turn alarm off."""
        return self._gateway.send("set_arming", ["off"])

    @command()
    def arming_time(self) -> int:
        """Return time in seconds the alarm stays 'oning' before transitioning to
        'on'."""
        # Response: 5, 15, 30, 60
        return self._gateway.send("get_arm_wait_time").pop()

    @command(click.argument("seconds"))
    def set_arming_time(self, seconds):
        """Set time the alarm stays at 'oning' before transitioning to 'on'."""
        return self._gateway.send("set_arm_wait_time", [seconds])

    @command()
    def triggering_time(self) -> int:
        """Return the time in seconds the alarm is going off when triggered."""
        # Response: 30, 60, etc.
        return self._gateway.get_prop("alarm_time_len").pop()

    @command(click.argument("seconds"))
    def set_triggering_time(self, seconds):
        """Set the time in seconds the alarm is going off when triggered."""
        return self._gateway.set_prop("alarm_time_len", seconds)

    @command()
    def triggering_light(self) -> int:
        """Return the time the gateway light blinks when the alarm is triggerd."""
        # Response: 0=do not blink, 1=always blink, x>1=blink for x seconds
        return self._gateway.get_prop("en_alarm_light").pop()

    @command(click.argument("seconds"))
    def set_triggering_light(self, seconds):
        """Set the time the gateway light blinks when the alarm is triggerd."""
        # values: 0=do not blink, 1=always blink, x>1=blink for x seconds
        return self._gateway.set_prop("en_alarm_light", seconds)

    @command()
    def triggering_volume(self) -> int:
        """Return the volume level at which alarms go off [0-100]."""
        return self._gateway.send("get_alarming_volume").pop()

    @command(click.argument("volume"))
    def set_triggering_volume(self, volume):
        """Set the volume level at which alarms go off [0-100]."""
        return self._gateway.send("set_alarming_volume", [volume])

    @command()
    def last_status_change_time(self) -> datetime:
        """Return the last time the alarm changed status."""
        return datetime.fromtimestamp(self._gateway.send("get_arming_time").pop())
