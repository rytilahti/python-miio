"""Xiaomi Chuangmi camera (chuangmi.camera.ipc009, ipc019) support."""

import enum
import logging
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus

_LOGGER = logging.getLogger(__name__)


class Direction(enum.Enum):
    """Rotation direction."""

    Left = 1
    Right = 2
    Up = 3
    Down = 4


class MotionDetectionSensitivity(enum.IntEnum):
    """Motion detection sensitivity."""

    High = 3
    Low = 1


class HomeMonitoringMode(enum.IntEnum):
    """Home monitoring mode."""

    Off = 0
    AllDay = 1
    Custom = 2


class NASState(enum.IntEnum):
    """NAS state."""

    Off = 2
    On = 3


class NASSyncInterval(enum.IntEnum):
    """NAS sync interval."""

    Realtime = 300
    Hour = 3600
    Day = 86400


class NASVideoRetentionTime(enum.IntEnum):
    """NAS video retention time."""

    Week = 604800
    Month = 2592000
    Quarter = 7776000
    HalfYear = 15552000
    Year = 31104000


CONST_HIGH_SENSITIVITY = [MotionDetectionSensitivity.High] * 32
CONST_LOW_SENSITIVITY = [MotionDetectionSensitivity.Low] * 32


class CameraStatus(DeviceStatus):
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

        values = self.get_properties(properties)

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

    @command(
        click.argument("direction", type=EnumType(Direction)),
        default_output=format_output("Rotating to direction '{direction.name}'"),
    )
    def rotate(self, direction: Direction):
        """Rotate camera to given direction (left, right, up, down)."""
        return self.send("set_motor", {"operation": direction.value})

    @command()
    def alarm(self):
        """Sound a loud alarm for 10 seconds."""
        return self.send("alarm_sound")

    @command(
        click.argument("sensitivity", type=EnumType(MotionDetectionSensitivity)),
        default_output=format_output("Setting motion sensitivity '{sensitivity.name}'"),
    )
    def set_motion_sensitivity(self, sensitivity: MotionDetectionSensitivity):
        """Set motion sensitivity (high, low)."""
        return self.send(
            "set_motion_region",
            CONST_HIGH_SENSITIVITY
            if sensitivity == MotionDetectionSensitivity.High
            else CONST_LOW_SENSITIVITY,
        )

    @command(
        click.argument("mode", type=EnumType(HomeMonitoringMode)),
        click.argument("start-hour", default=10),
        click.argument("start-minute", default=0),
        click.argument("end-hour", default=17),
        click.argument("end-minute", default=0),
        click.argument("notify", default=1),
        click.argument("interval", default=5),
        default_output=format_output("Setting alarm config to '{mode.name}'"),
    )
    def set_home_monitoring_config(
        self,
        mode: HomeMonitoringMode = HomeMonitoringMode.AllDay,
        start_hour: int = 10,
        start_minute: int = 0,
        end_hour: int = 17,
        end_minute: int = 0,
        notify: int = 1,
        interval: int = 5,
    ):
        """Set home monitoring configuration."""
        return self.send(
            "setAlarmConfig",
            [mode, start_hour, start_minute, end_hour, end_minute, notify, interval],
        )

    @command(default_output=format_output("Clearing NAS directory"))
    def clear_nas_dir(self):
        """Clear NAS directory."""
        return self.send("nas_clear_dir", [[]])

    @command(default_output=format_output("Getting NAS config info"))
    def get_nas_config(self):
        """Get NAS config info."""
        return self.send("nas_get_config", {})

    @command(
        click.argument("state", type=EnumType(NASState)),
        click.argument("share"),
        click.argument("sync-interval", type=EnumType(NASSyncInterval)),
        click.argument("video-retention-time", type=EnumType(NASVideoRetentionTime)),
        default_output=format_output("Setting NAS config to '{state.name}'"),
    )
    def set_nas_config(
        self,
        state: NASState,
        share=None,
        sync_interval: NASSyncInterval = NASSyncInterval.Realtime,
        video_retention_time: NASVideoRetentionTime = NASVideoRetentionTime.Week,
    ):
        """Set NAS configuration."""
        if share is None:
            share = {}
        return self.send(
            "nas_set_config",
            {
                "state": state,
                "sync_interval": sync_interval,
                "video_retention_time": video_retention_time,
            },
        )
