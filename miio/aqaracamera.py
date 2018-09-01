"""Aqara camera support.

Support for lumi.camera.aq1

TODO: add alarm/sound parts (get_music_info, {get,set}_alarming_volume, set_default_music, play_music_new, set_sound_playing)
TODO: add sdcard status & fix all TODOS
TODO: add tests
"""
import attr
import logging
from typing import Any, Dict

import click

from .click_common import command, format_output
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class CameraException(DeviceException):
    pass


@attr.s
class CameraOffset:
    """Container for camera offset data."""
    x = attr.ib()
    y = attr.ib()
    radius = attr.ib()


class CameraStatus:
    """Container for status reports from the Aqara Camera."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a lumi.camera.aq1:

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
        """TODO what is md? motion detection?"""
        return bool(self.data["md_status"])

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
        return CameraOffset(x=self.data["offset_x"],
                            y=self.data["offset_y"],
                            radius=self.data["offset_radius"])

    @property
    def channel_id(self) -> int:
        """TODO: Zigbee channel?"""
        return self.data["channel_id"]

    @property
    def fullstop(self) -> bool:
        """TODO: What is this?"""
        return bool(self.data["fullstop"])

    @property
    def p2p_id(self) -> str:
        """TODO: What is this? Cloud?"""
        return self.data["p2p_id"]

    @property
    def av_id(self) -> str:
        """TODO: What is this? ID for the cloud?"""
        return self.data["avID"]

    @property
    def av_password(self) -> str:
        """TODO: What is this? Password for the cloud?"""
        return self.data["avPass"]

    def __repr__(self) -> str:
        s = "<CameraStatus is_on=%s, " \
            "type=%s, " \
            "offset=%s, " \
            "ir=%s, " \
            "md=%s, " \
            "led=%s, " \
            "flip=%s, " \
            "fullstop=%s>" \
            % (self.is_on,
               self.type,
               self.offsets,
               self.ir,
               self.md,
               self.led,
               self.flipped,
               self.fullstop
               )
        return s

    def __json__(self):
        return self.data


class AqaraCamera(Device):
    """Main class representing the Xiaomi Aqara Camera."""

    @command(
        default_output=format_output(
            "",
            "Type: {result.type}\n"
            "Video: {result.is_on}\n"
            "Offsets: {result.offsets}\n"
            "IR: {result.ir_status} %\n"
            "MD: {result.md_status}\n"
            "LED: {result.led}\n"
            "Flipped: {result.flipped}\n"
            "Full stop: {result.fullstop}\n"
            "P2P ID: {result.p2p_id}\n"
            "AV ID: {result.av_id}\n"
            "AV password: {result.av_password}\n"
            "\n"
        )
    )
    def status(self) -> CameraStatus:
        """Camera status."""
        return CameraStatus(self.send("get_ipcprop", ["all"]))

    @command(
        default_output=format_output("Camera on"),
    )
    def on(self):
        """Camera on."""
        return self.send("set_video", ["on"])

    @command(
        default_output=format_output("Camera off"),
    )
    def off(self):
        """Camera off."""
        return self.send("set_video", ["off"])

    @command(
        default_output=format_output("IR on")
    )
    def ir_on(self):
        """IR on."""
        return self.send("set_ir", ["on"])

    @command(
        default_output=format_output("IR off")
    )
    def ir_off(self):
        """IR off."""
        return self.send("set_ir", ["off"])

    @command(
        default_output=format_output("MD on")
    )
    def md_on(self):
        """IR on."""
        return self.send("set_md", ["on"])

    @command(
        default_output=format_output("MD off")
    )
    def md_off(self):
        """MD off."""
        return self.send("set_md", ["off"])

    @command(
        default_output=format_output("LED on")
    )
    def led_on(self):
        """LED on."""
        return self.send("set_led", ["on"])

    @command(
        default_output=format_output("LED off")
    )
    def led_off(self):
        """LED off."""
        return self.send("set_led", ["off"])

    @command(
        default_output=format_output("Flip on")
    )
    def flip_on(self):
        """Flip on."""
        return self.send("set_flip", ["on"])

    @command(
        default_output=format_output("Flip off")
    )
    def flip_off(self):
        """Flip off."""
        return self.send("set_flip", ["off"])

    @command(
        default_output=format_output("Fullstop on")
    )
    def fullstop_on(self):
        """Fullstop on."""
        return self.send("set_fullstop", ["on"])

    @command(
        default_output=format_output("Fullstop off")
    )
    def fullstop_off(self):
        """Fullstop off."""
        return self.send("set_fullstop", ["off"])

    @command(
        click.argument("time", type=int, default=30),
        default_output=format_output(
            "Start pairing for {time} seconds")
    )
    def pair(self, timeout: int):
        """Start (or stop with "0") pairing."""
        if timeout < 0:
            raise CameraException("Invalid timeout: %s" % timeout)

        return self.send("start_zigbee_join", [timeout])

    @command()
    def sd_status(self):
        """SD card status. TODO: please report output."""
        return self.send("get_sdstatus")

    @command()
    def sd_format(self):
        """TODO: Format SD card? parameters & result unknown."""
        return self.send("sdformat")

    @command()
    def arm_status(self):
        """Return arming information."""
        # TODO: return a container
        is_armed = self.send("get_arming")
        arm_wait_time = self.send("get_arm_wait_time")
        return {'is_armed': is_armed, 'wait_time': arm_wait_time}

    @command(
        default_output=format_output("Arming")
    )
    def arm(self):
        """Arm the camera?"""
        return self.send("set_arming", ["on"])

    @command(
        default_output=format_output("Disarming")
    )
    def disarm(self):
        """Disarm the camera?"""
        return self.send("set_arming", ["off"])
