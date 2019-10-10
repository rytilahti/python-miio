"""Xiaomi Chuangmi camera (chuangmi.camera.ipc009) support."""

import logging
from typing import Any, Dict

from .click_common import command, format_output
from .device import Device

_LOGGER = logging.getLogger(__name__)


class CameraStatus:
    """Container for status reports from the Xiaomi Chuangmi Camera."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Request:
        ["power", "motion_record", "light", "full_color", "flip", "improve_program", "wdr",
        "track", "sdcard_status", "watermark", "max_client", "night_mode", "mini_level"]

        Response:
        ["on","on","on","on","off","on","on","off","0","off","0","0","1"]
        """
        self.data = data

    @property
    def power(self) -> bool:
        """Camera power."""
        return self.data["power"] == "on"

    @property
    def motion_record(self) -> bool:
        """Motion record status."""
        return self.data["motion_record"] == "on"

    @property
    def light(self) -> bool:
        """Camera light status."""
        return self.data["light"] == "on"

    @property
    def full_color(self) -> bool:
        """Full color with bad lighting conditions."""
        return self.data["full_color"] == "on"

    @property
    def flip(self) -> bool:
        """Image 180 degrees flip status."""
        return self.data["flip"] == "on"

    @property
    def improve_program(self) -> bool:
        """Customer experience improvement program status."""
        return self.data["improve_program"] == "on"

    @property
    def wdr(self) -> bool:
        """Wide dynamic range status."""
        return self.data["wdr"] == "on"

    @property
    def track(self) -> bool:
        """Tracking status."""
        return self.data["track"] == "on"

    @property
    def watermark(self) -> bool:
        """Apply watermark to video."""
        return self.data["watermark"] == "on"

    @property
    def sdcard_status(self) -> int:
        """SD card status."""
        return self.data["sdcard_status"]

    @property
    def max_client(self) -> int:
        """Unknown."""
        return self.data["max_client"]

    @property
    def night_mode(self) -> int:
        """Night mode."""
        return self.data["night_mode"]

    @property
    def mini_level(self) -> int:
        """Unknown."""
        return self.data["mini_level"]

    def __repr__(self) -> str:
        s = (
            "<CameraStatus "
            "power=%s, "
            "motion_record=%s, "
            "light=%s, "
            "full_color=%s, "
            "flip=%s, "
            "improve_program=%s, "
            "wdr=%s, "
            "track=%s, "
            "watermark=%s, "
            "sdcard_status=%s, "
            "max_client=%s, "
            "night_mode=%s, "
            "mini_level=%s>"
            % (
                self.power,
                self.motion_record,
                self.light,
                self.full_color,
                self.flip,
                self.improve_program,
                self.wdr,
                self.track,
                self.sdcard_status,
                self.watermark,
                self.max_client,
                self.night_mode,
                self.mini_level,
            )
        )
        return s

    def __json__(self):
        return self.data


class ChuangmiCamera(Device):
    """Main class representing the Xiaomi Chuangmi Camera."""

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Motion record: {result.motion_record}\n"
            "Light: {result.light}\n"
            "Full color: {result.full_color}\n"
            "Flip: {result.flip}\n"
            "Improve program: {result.improve_program}\n"
            "Wdr: {result.wdr}\n"
            "Track: {result.track}\n"
            "SD card status: {result.sdcard_status}\n"
            "Watermark: {result.watermark}\n"
            "Max client: {result.max_client}\n"
            "Night mode: {result.night_mode}\n"
            "Mini level: {result.mini_level}\n"
            "\n",
        )
    )
    def status(self) -> CameraStatus:
        """Retrieve properties."""
        properties = [
            "power",
            "motion_record",
            "light",
            "full_color",
            "flip",
            "improve_program",
            "wdr",
            "track",
            "sdcard_status",
            "watermark",
            "max_client",
            "night_mode",
            "mini_level",
        ]

        values = self.send("get_prop", properties)

        return CameraStatus(dict(zip(properties, values)))

    @command(default_output=format_output("Power on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Power off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(default_output=format_output("MotionRecord on"))
    def motion_record_on(self):
        """Start recording when motion detected."""
        return self.send("set_motion_record", ["on"])

    @command(default_output=format_output("MotionRecord off"))
    def motion_record_off(self):
        """Motion record off, always record video."""
        return self.send("set_motion_record", ["off"])

    @command(default_output=format_output("MotionRecord stop"))
    def motion_record_stop(self):
        """Motion record off, video recording stopped."""
        return self.send("set_motion_record", ["stop"])

    @command(default_output=format_output("Light on"))
    def light_on(self):
        """Light on."""
        return self.send("set_light", ["on"])

    @command(default_output=format_output("Light off"))
    def light_off(self):
        """Light off."""
        return self.send("set_light", ["off"])

    @command(default_output=format_output("FullColor on"))
    def full_color_on(self):
        """Full color on."""
        return self.send("set_full_color", ["on"])

    @command(default_output=format_output("FullColor off"))
    def full_color_off(self):
        """Full color off."""
        return self.send("set_full_color", ["off"])

    @command(default_output=format_output("Flip on"))
    def flip_on(self):
        """Flip image 180 degrees on."""
        return self.send("set_flip", ["on"])

    @command(default_output=format_output("Flip off"))
    def flip_off(self):
        """Flip image 180 degrees off."""
        return self.send("set_flip", ["off"])

    @command(default_output=format_output("ImproveProgram on"))
    def improve_program_on(self):
        """Improve program on."""
        return self.send("set_improve_program", ["on"])

    @command(default_output=format_output("ImproveProgram off"))
    def improve_program_off(self):
        """Improve program off."""
        return self.send("set_improve_program", ["off"])

    @command(default_output=format_output("Watermark on"))
    def watermark_on(self):
        """Watermark on."""
        return self.send("set_watermark", ["on"])

    @command(default_output=format_output("Watermark off"))
    def watermark_off(self):
        """Watermark off."""
        return self.send("set_watermark", ["off"])

    @command(default_output=format_output("WideDynamicRange on"))
    def wdr_on(self):
        """Wide dynamic range on."""
        return self.send("set_wdr", ["on"])

    @command(default_output=format_output("WideDynamicRange off"))
    def wdr_off(self):
        """Wide dynamic range off."""
        return self.send("set_wdr", ["off"])

    @command(default_output=format_output("NightMode auto"))
    def night_mode_auto(self):
        """Auto switch to night mode."""
        return self.send("set_night_mode", [0])

    @command(default_output=format_output("NightMode off"))
    def night_mode_off(self):
        """Night mode off."""
        return self.send("set_night_mode", [1])

    @command(default_output=format_output("NightMode on"))
    def night_mode_on(self):
        """Night mode always on."""
        return self.send("set_night_mode", [2])
