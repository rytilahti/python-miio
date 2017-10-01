import warnings
import logging
from .device import Device

_LOGGER = logging.getLogger(__name__)


class WifiSpeakerStatus:
    def __init__(self, data):
        self.data = data

    @property
    def device_name(self) -> str:
        return self.data["DeviceName"]

    @property
    def channel(self) -> str:
        return self.data["channel_title"]

    @property
    def state(self) -> str:
        # note: this can be enumized when all values are known
        return self.data["current_state"]

    @property
    def hardware_version(self) -> str:
        return self.data["hardware_version"]

    @property
    def play_mode(self):
        # note: this can be enumized when all values are known
        return self.data["play_mode"]

    @property
    def track_artist(self) -> str:
        return self.data["track_artist"]

    @property
    def track_title(self) -> str:
        return self.data["track_title"]

    @property
    def track_duration(self) -> str:
        return self.data["track_duration"]

    @property
    def transport_channel(self) -> str:
        # note: this can be enumized when all values are known
        return self.data["transport_channel"]


class WifiSpeaker(Device):
    def __init__(self, *args, **kwargs):
        warnings.warn("Please help to complete this by providing more "
                      "information about possible values for `state`, "
                      "`play_mode` and `transport_channel`.", stacklevel=2)
        super().__init__(*args, **kwargs)

    def status(self):
        return WifiSpeakerStatus(self.command("get_prop", ["umi"]))

    def power(self):
        # is this a toggle?
        return self.send("power")

    def volume_up(self, amount: int = 5):
        return self.send("vol_up", [amount])

    def volume_down(self, amount: int = 5):
        return self.send("vol_down", [amount])

    def track_previous(self):
        return self.send("previous_track")

    def track_next(self):
        return self.send("next_track")

    def track_location(self):
        return self.send("get_prop", ["rel_time"])
