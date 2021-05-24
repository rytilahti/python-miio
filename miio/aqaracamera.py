"""Aqara camera support.

Support for lumi.camera.aq1

.. todo:: add alarm/sound parts (get_music_info, {get,set}_alarming_volume,
          set_default_music, play_music_new, set_sound_playing)
.. todo:: add sdcard status & fix all TODOS
.. todo:: add tests
"""
import logging
from enum import IntEnum
from typing import Any, Dict

import attr
import click

from .click_common import command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)


class CameraException(DeviceException):
    pass


@attr.s
class CameraOffset:
    """Container for camera offset data."""

    x = attr.ib()
    y = attr.ib()
    radius = attr.ib()


@attr.s
class ArmStatus:
    """Container for arm statuses."""

    is_armed: bool = attr.ib(converter=bool)
    arm_wait_time: int = attr.ib(converter=int)
    alarm_volume: int = attr.ib(converter=int)


class SDCardStatus(IntEnum):
    """State of the SD card."""

    NoCardInserted = 0
    Ok = 1
    FormatRequired = 2
    Formating = 3


class MotionDetectionSensitivity(IntEnum):
    """'Default' values for md sensitivity.

    Currently unused as the value can also be set arbitrarily.
    """

    High = 6000000
    Medium = 10000000
    Low = 11000000


class CameraStatus(DeviceStatus):
    """Container for status reports from the Aqara Camera."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a lumi.camera.aq1:

        {"p2p_id":"#################","app_type":"celing",
        "offset_x":"0","offset_y":"0","offset_radius":"0",
        "md_status":1,"video_state":1,"fullstop":0,
        "led_status":1,"ir_status":1,"mdsensitivity":6000000,
        "channel_id":0,"flip_state":0,
        "avID":"####","avPass":"####","id":65001}
        """
        self.data = data

    @property
    def type(self) -> str:
        """TODO: Type of the camera? Name?"""
        return self.data["app_type"]

    @property
    def video_status(self) -> bool:
        """Video state."""
        return bool(self.data["video_state"])

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return self.video_status == 1

    @property
    def md(self) -> bool:
        """Motion detection state."""
        return bool(self.data["md_status"])

    @property
    def md_sensitivity(self):
        """Motion detection sensitivity."""
        return self.data["mdsensitivity"]

    @property
    def ir(self):
        """IR mode."""
        return bool(self.data["ir_status"])

    @property
    def led(self):
        """LED status."""
        return bool(self.data["led_status"])

    @property
    def flipped(self) -> bool:
        """TODO: If camera is flipped?"""
        return self.data["flip_state"]

    @property
    def offsets(self) -> CameraOffset:
        """Camera offset information."""
        return CameraOffset(
            x=self.data["offset_x"],
            y=self.data["offset_y"],
            radius=self.data["offset_radius"],
        )

    @property
    def channel_id(self) -> int:
        """TODO: Zigbee channel?"""
        return self.data["channel_id"]

    @property
    def fullstop(self) -> bool:
        """Is alarm triggered by MD."""
        return self.data["fullstop"] != 0

    @property
    def p2p_id(self) -> str:
        """P2P ID for video and audio."""
        return self.data["p2p_id"]

    @property
    def av_id(self) -> str:
        """TODO: What is this? ID for the cloud?"""
        return self.data["avID"]

    @property
    def av_password(self) -> str:
        """TODO: What is this? Password for the cloud?"""
        return self.data["avPass"]


class AqaraCamera(Device):
    """Main class representing the Xiaomi Aqara Camera."""

    @command(
        default_output=format_output(
            "",
            "Type: {result.type}\n"
            "Video: {result.is_on}\n"
            "Offsets: {result.offsets}\n"
            "IR: {result.ir_status} %\n"
            "MD: {result.md_status} (sensitivity: {result.md_sensitivity}\n"
            "LED: {result.led}\n"
            "Flipped: {result.flipped}\n"
            "Full stop: {result.fullstop}\n"
            "P2P ID: {result.p2p_id}\n"
            "AV ID: {result.av_id}\n"
            "AV password: {result.av_password}\n"
            "\n",
        )
    )
    def status(self) -> CameraStatus:
        """Camera status."""
        return CameraStatus(self.send("get_ipcprop", ["all"]))

    @command(default_output=format_output("Camera on"))
    def on(self):
        """Camera on."""
        return self.send("set_video", ["on"])

    @command(default_output=format_output("Camera off"))
    def off(self):
        """Camera off."""
        return self.send("set_video", ["off"])

    @command(default_output=format_output("IR on"))
    def ir_on(self):
        """IR on."""
        return self.send("set_ir", ["on"])

    @command(default_output=format_output("IR off"))
    def ir_off(self):
        """IR off."""
        return self.send("set_ir", ["off"])

    @command(default_output=format_output("MD on"))
    def md_on(self):
        """IR on."""
        return self.send("set_md", ["on"])

    @command(default_output=format_output("MD off"))
    def md_off(self):
        """MD off."""
        return self.send("set_md", ["off"])

    @command(click.argument("sensitivity", type=int, required=False))
    def md_sensitivity(self, sensitivity):
        """Get or set the motion detection sensitivity."""
        if sensitivity:
            click.echo("Setting MD sensitivity to %s" % sensitivity)
            return self.send("set_mdsensitivity", [sensitivity])[0] == "ok"
        else:
            return self.send("get_mdsensitivity")

    @command(default_output=format_output("LED on"))
    def led_on(self):
        """LED on."""
        return self.send("set_led", ["on"])

    @command(default_output=format_output("LED off"))
    def led_off(self):
        """LED off."""
        return self.send("set_led", ["off"])

    @command(default_output=format_output("Flip on"))
    def flip_on(self):
        """Flip on."""
        return self.send("set_flip", ["on"])

    @command(default_output=format_output("Flip off"))
    def flip_off(self):
        """Flip off."""
        return self.send("set_flip", ["off"])

    @command(default_output=format_output("Fullstop on"))
    def fullstop_on(self):
        """Fullstop on."""
        return self.send("set_fullstop", ["on"])

    @command(default_output=format_output("Fullstop off"))
    def fullstop_off(self):
        """Fullstop off."""
        return self.send("set_fullstop", ["off"])

    @command(
        click.argument("time", type=int, default=30),
        default_output=format_output("Start pairing for {time} seconds"),
    )
    def pair(self, timeout: int):
        """Start (or stop with "0") pairing."""
        if timeout < 0:
            raise CameraException("Invalid timeout: %s" % timeout)

        return self.send("start_zigbee_join", [timeout])

    @command()
    def sd_status(self):
        """SD card status."""
        return SDCardStatus(self.send("get_sdstatus"))

    @command()
    def sd_format(self):
        """Format the SD card.

        Returns True when formating has started successfully.
        """
        return bool(self.send("sdformat"))

    @command()
    def arm_status(self):
        """Return arming information."""
        is_armed = self.send("get_arming")
        arm_wait_time = self.send("get_arm_wait_time")
        alarm_volume = self.send("get_alarming_volume")

        return ArmStatus(
            is_armed=bool(is_armed),
            arm_wait_time=arm_wait_time,
            alarm_volume=alarm_volume,
        )

    @command(
        click.argument("volume", type=int, default=100),
        default_output=format_output("Setting alarm volume to {volume}"),
    )
    def set_alarm_volume(self, volume):
        """Set alarm volume."""
        if volume < 0 or volume > 100:
            raise CameraException("Volume has to be [0,100], was %s" % volume)
        return self.send("set_alarming_volume", [volume])[0] == "ok"

    @command(click.argument("sound_id", type=str, required=False, default=None))
    def alarm_sound(self, sound_id):
        """List or set the alarm sound."""
        if id is None:
            sound_status = self.send("get_music_info", [0])

            # TODO: make a list out from this.
            @attr.s
            class SoundList:
                default = attr.ib()
                total = attr.ib(type=int)
                sounds = attr.ib(type=list)

            return sound_status

        click.echo("Setting alarm sound to %s" % sound_id)
        return self.send("set_default_music", [0, sound_id])[0] == "ok"

    @command(default_output=format_output("Arming"))
    def arm(self):
        """Arm the camera?"""
        return self.send("set_arming", ["on"])

    @command(default_output=format_output("Disarming"))
    def disarm(self):
        """Disarm the camera?"""
        return self.send("set_arming", ["off"])
