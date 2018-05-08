import enum
import logging
import warnings

import click

from .click_common import command, format_output
from .device import Device

_LOGGER = logging.getLogger(__name__)


class PlayState(enum.Enum):
    Playing = "PLAYING"
    Stopped = "STOPPED"
    Paused = "PAUSED_PLAYBACK"
    NoMedia = "NO_MEDIA_PRESENT"
    Transitioning = "TRANSITIONING"


class TransportChannel(enum.Enum):
    Playlist = "PLAYLIST"
    OneTime = "ONETIME"
    Auxiliary = "AUX"
    Bluetooth = "BT"
    Radio = "RADIO"
    Air = "AIR"
    Qplay = "QPLAY"


class WifiSpeakerStatus:
    """Container of a speaker state.
    This contains information such as the name of the device,
    and what is currently being played by it."""
    def __init__(self, data):
        """
        Example response of a xiaomi.wifispeaker.v2:

        {"DeviceName": "Mi Internet Speaker", "channel_title\": "XXX",
         "current_state": "PLAYING", "hardware_version": "S602",
         "play_mode": "REPEAT_ALL", "track_artist": "XXX",
         "track_duration": "00:04:58", "track_title": "XXX",
         "transport_channel": "PLAYLIST"}
        """
        self.data = data

    @property
    def device_name(self) -> str:
        """Name of the device."""
        return self.data["DeviceName"]

    @property
    def channel(self) -> str:
        """Name of the channel."""
        return self.data["channel_title"]

    @property
    def state(self) -> PlayState:
        """State of the device, e.g. PLAYING."""
        return PlayState(self.data["current_state"])

    @property
    def hardware_version(self) -> str:
        return self.data["hardware_version"]

    @property
    def play_mode(self):
        """Play mode such as REPEAT_ALL."""
        # note: this can be enumized when all values are known
        return self.data["play_mode"]

    @property
    def track_artist(self) -> str:
        """Artist of the current track."""
        return self.data["track_artist"]

    @property
    def track_title(self) -> str:
        """Title of the current track."""
        return self.data["track_title"]

    @property
    def track_duration(self) -> str:
        """Total duration of the current track."""
        return self.data["track_duration"]

    @property
    def transport_channel(self) -> TransportChannel:
        """Transport channel, e.g. PLAYLIST"""
        return TransportChannel(self.data["transport_channel"])

    def __repr__(self) -> str:
        s = "<WifiSpeakerStatus " \
            "device_name=%s, " \
            "channel=%s, " \
            "state=%s, " \
            "play_mode=%s, " \
            "track_artist=%s, " \
            "track_title=%s, " \
            "track_duration=%s, " \
            "transport_channel=%s, " \
            "hardware_version=%s>" % \
            (self.device_name,
             self.channel,
             self.state,
             self.play_mode,
             self.track_artist,
             self.track_title,
             self.track_duration,
             self.transport_channel,
             self.hardware_version)

        return s

    def __json__(self):
        return self.data


class WifiSpeaker(Device):
    """Device class for Xiaomi Smart Wifi Speaker."""
    def __init__(self, *args, **kwargs):
        warnings.warn("Please help to complete this by providing more "
                      "information about possible values for `state`, "
                      "`play_mode` and `transport_channel`.", stacklevel=2)
        super().__init__(*args, **kwargs)

    @command(
        default_output=format_output(
            "",
            "Device name: {result.device_name}\n"
            "Channel: {result.channel}\n"
            "State: {result.state}\n"
            "Play mode: {result.play_mode}\n"
            "Track artist: {result.track_artist}\n"
            "Track title: {result.track_title}\n"
            "Track duration: {result.track_duration}\n"
            "Transport channel: {result.transport_channel}\n"
            "Hardware version: {result.hardware_version}\n"
        )
    )
    def status(self) -> WifiSpeakerStatus:
        """Return device status."""
        return WifiSpeakerStatus(self.send("get_prop", ["umi"]))

    @command(
        default_output=format_output("Powering on"),
    )
    def power(self):
        """Toggle power on and off."""
        # is this a toggle?
        return self.send("power")

    @command(
        default_output=format_output("Toggling play"),
    )
    def toggle(self):
        """Toggle play."""
        return self.send("toggle")

    @command(
        click.argument("amount", type=int),
        default_output=format_output("Increasing volume by {amount} percent")
    )
    def volume_up(self, amount: int = 5):
        """Set volume up."""
        return self.send("vol_up", [amount])

    @command(
        click.argument("amount", type=int),
        default_output=format_output("Decreasing volume by {amount} percent")
    )
    def volume_down(self, amount: int = 5):
        """Set volume down."""
        return self.send("vol_down", [amount])

    @command(
        default_output=format_output("Playing previous track"),
    )
    def track_previous(self):
        """Move to previous track."""
        return self.send("previous_track")

    @command(
        default_output=format_output("Playing next track"),
    )
    def track_next(self):
        """Move to next track."""
        return self.send("next_track")

    @command(
        default_output=format_output("Switching to the next transport channel"),
    )
    def channel_next(self):
        """Change transport channel."""
        return self.send("next_channel")

    @command(
        default_output=format_output("Track position: {result.rel_time}"),
    )
    def track_position(self):
        """Return current track position."""
        return self.send("get_prop", ["rel_time"])

    def volume(self):
        """Speaker volume."""
        return self.send("get_prop", ["volume"])
