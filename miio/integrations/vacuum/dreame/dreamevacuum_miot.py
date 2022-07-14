"""Dreame Vacuum."""

import logging
import threading
from enum import Enum
from typing import Dict, Optional

import click

from miio.click_common import command, format_output
from miio.exceptions import DeviceException
from miio.interfaces import FanspeedPresets, VacuumInterface
from miio.miot_device import DeviceStatus as DeviceStatusContainer
from miio.miot_device import MiotDevice, MiotMapping
from miio.updater import OneShotServer

_LOGGER = logging.getLogger(__name__)


DREAME_1C = "dreame.vacuum.mc1808"
DREAME_F9 = "dreame.vacuum.p2008"
DREAME_D9 = "dreame.vacuum.p2009"
DREAME_Z10_PRO = "dreame.vacuum.p2028"
DREAME_MOP_2_PRO_PLUS = "dreame.vacuum.p2041o"
DREAME_MOP_2_ULTRA = "dreame.vacuum.p2150a"
DREAME_MOP_2 = "dreame.vacuum.p2150o"

_DREAME_1C_MAPPING: MiotMapping = {
    # https://home.miot-spec.com/spec/dreame.vacuum.mc1808
    "battery_level": {"siid": 2, "piid": 1},
    "charging_state": {"siid": 2, "piid": 2},
    "device_fault": {"siid": 3, "piid": 1},
    "device_status": {"siid": 3, "piid": 2},
    "brush_left_time": {"siid": 26, "piid": 1},
    "brush_life_level": {"siid": 26, "piid": 2},
    "filter_life_level": {"siid": 27, "piid": 1},
    "filter_left_time": {"siid": 27, "piid": 2},
    "brush_left_time2": {"siid": 28, "piid": 1},
    "brush_life_level2": {"siid": 28, "piid": 2},
    "operating_mode": {"siid": 18, "piid": 1},
    "cleaning_mode": {"siid": 18, "piid": 6},
    "delete_timer": {"siid": 18, "piid": 8},
    "cleaning_time": {"siid": 18, "piid": 2},
    "cleaning_area": {"siid": 18, "piid": 4},
    "first_clean_time": {"siid": 18, "piid": 12},
    "total_clean_time": {"siid": 18, "piid": 13},
    "total_clean_times": {"siid": 18, "piid": 14},
    "total_clean_area": {"siid": 18, "piid": 15},
    "life_sieve": {"siid": 19, "piid": 1},
    "life_brush_side": {"siid": 19, "piid": 2},
    "life_brush_main": {"siid": 19, "piid": 3},
    "timer_enable": {"siid": 20, "piid": 1},
    "start_time": {"siid": 20, "piid": 2},
    "stop_time": {"siid": 20, "piid": 3},
    "deg": {"siid": 21, "piid": 1, "access": ["write"]},
    "speed": {"siid": 21, "piid": 2, "access": ["write"]},
    "map_view": {"siid": 23, "piid": 1},
    "frame_info": {"siid": 23, "piid": 2},
    "volume": {"siid": 24, "piid": 1},
    "voice_package": {"siid": 24, "piid": 3},
    "timezone": {"siid": 25, "piid": 1},
    "home": {"siid": 2, "aiid": 1},
    "locate": {"siid": 17, "aiid": 1},
    "start_clean": {"siid": 3, "aiid": 1},
    "stop_clean": {"siid": 3, "aiid": 2},
    "reset_mainbrush_life": {"siid": 26, "aiid": 1},
    "reset_filter_life": {"siid": 27, "aiid": 1},
    "reset_sidebrush_life": {"siid": 28, "aiid": 1},
    "move": {"siid": 21, "aiid": 1},
    "play_sound": {"siid": 24, "aiid": 3},
    "set_voice": {"siid": 24, "aiid": 2},
}


_DREAME_F9_MAPPING: MiotMapping = {
    # https://home.miot-spec.com/spec/dreame.vacuum.p2008
    # https://home.miot-spec.com/spec/dreame.vacuum.p2009
    # https://home.miot-spec.com/spec/dreame.vacuum.p2028
    # https://home.miot-spec.com/spec/dreame.vacuum.p2041o
    # https://home.miot-spec.com/spec/dreame.vacuum.p2150a
    # https://home.miot-spec.com/spec/dreame.vacuum.p2150o
    "battery_level": {"siid": 3, "piid": 1},
    "charging_state": {"siid": 3, "piid": 2},
    "device_fault": {"siid": 2, "piid": 2},
    "device_status": {"siid": 2, "piid": 1},
    "brush_left_time": {"siid": 9, "piid": 1},
    "brush_life_level": {"siid": 9, "piid": 2},
    "filter_life_level": {"siid": 11, "piid": 1},
    "filter_left_time": {"siid": 11, "piid": 2},
    "brush_left_time2": {"siid": 10, "piid": 1},
    "brush_life_level2": {"siid": 10, "piid": 2},
    "operating_mode": {"siid": 4, "piid": 1},
    "cleaning_mode": {"siid": 4, "piid": 4},
    "delete_timer": {"siid": 18, "piid": 8},
    "timer_enable": {"siid": 5, "piid": 1},
    "cleaning_time": {"siid": 4, "piid": 2},
    "cleaning_area": {"siid": 4, "piid": 3},
    "first_clean_time": {"siid": 12, "piid": 1},
    "total_clean_time": {"siid": 12, "piid": 2},
    "total_clean_times": {"siid": 12, "piid": 3},
    "total_clean_area": {"siid": 12, "piid": 4},
    "start_time": {"siid": 5, "piid": 2},
    "stop_time": {"siid": 5, "piid": 3},
    "map_view": {"siid": 6, "piid": 1},
    "frame_info": {"siid": 6, "piid": 2},
    "volume": {"siid": 7, "piid": 1},
    "voice_package": {"siid": 7, "piid": 2},
    "water_flow": {"siid": 4, "piid": 5},
    "water_box_carriage_status": {"siid": 4, "piid": 6},
    "timezone": {"siid": 8, "piid": 1},
    "home": {"siid": 3, "aiid": 1},
    "locate": {"siid": 7, "aiid": 1},
    "start_clean": {"siid": 4, "aiid": 1},
    "stop_clean": {"siid": 4, "aiid": 2},
    "reset_mainbrush_life": {"siid": 9, "aiid": 1},
    "reset_filter_life": {"siid": 11, "aiid": 1},
    "reset_sidebrush_life": {"siid": 10, "aiid": 1},
    "move": {"siid": 21, "aiid": 1},
    "play_sound": {"siid": 7, "aiid": 2},
}

MIOT_MAPPING: Dict[str, MiotMapping] = {
    DREAME_1C: _DREAME_1C_MAPPING,
    DREAME_F9: _DREAME_F9_MAPPING,
    DREAME_D9: _DREAME_F9_MAPPING,
    DREAME_Z10_PRO: _DREAME_F9_MAPPING,
    DREAME_MOP_2_PRO_PLUS: _DREAME_F9_MAPPING,
    DREAME_MOP_2_ULTRA: _DREAME_F9_MAPPING,
    DREAME_MOP_2: _DREAME_F9_MAPPING,
}


class FormattableEnum(Enum):
    def __str__(self):
        return f"{self.name}"


class ChargingState(FormattableEnum):
    Charging = 1
    Discharging = 2
    Charging2 = 4
    GoCharging = 5


class CleaningModeDreame1C(FormattableEnum):
    Quiet = 0
    Default = 1
    Medium = 2
    Strong = 3


class CleaningModeDreameF9(FormattableEnum):
    Quiet = 0
    Standart = 1
    Strong = 2
    Turbo = 3


class OperatingMode(FormattableEnum):
    Paused = 1
    Cleaning = 2
    GoCharging = 3
    Charging = 6
    ManualCleaning = 13
    Sleeping = 14
    ManualPaused = 17
    ZonedCleaning = 19


class FaultStatus(FormattableEnum):
    NoFaults = 0


class DeviceStatus(FormattableEnum):
    Sweeping = 1
    Idle = 2
    Paused = 3
    Error = 4
    GoCharging = 5
    Charging = 6
    Mopping = 7
    ManualSweeping = 13


class WaterFlow(FormattableEnum):
    Low = 1
    Medium = 2
    High = 3


def _enum_as_dict(cls):
    return {x.name: x.value for x in list(cls)}


def _get_cleaning_mode_enum_class(model):
    """Return cleaning mode enum class for model if found or None."""
    if model == DREAME_1C:
        return CleaningModeDreame1C
    elif model in (
        DREAME_F9,
        DREAME_D9,
        DREAME_Z10_PRO,
        DREAME_MOP_2_PRO_PLUS,
        DREAME_MOP_2_ULTRA,
        DREAME_MOP_2,
    ):
        return CleaningModeDreameF9
    return None


class DreameVacuumStatus(DeviceStatusContainer):
    """Container for status reports from the dreame vacuum.

    Dreame vacuum respone
    {
        'battery_level': 100,
        'brush_left_time': 260,
        'brush_left_time2': 200,
        'brush_life_level': 90,
        'brush_life_level2': 90,
        'charging_state': 1,
        'cleaning_area': 22,
        'cleaning_mode': 2,
        'cleaning_time': 17,
        'device_fault': 0,
        'device_status': 6,
        'filter_left_time': 120,
        'filter_life_level': 40,
        'first_clean_time': 1620154830,
        'operating_mode': 6,
        'start_time': '22:00',
        'stop_time': '08:00',
        'timer_enable': True,
        'timezone': 'Europe/Berlin',
        'total_clean_area': 205,
        'total_clean_time': 186,
        'total_clean_times': 21,
        'voice_package': 'DR0',
        'volume': 65,
        'water_box_carriage_status': 0,
        'water_flow': 3
    }
    """

    def __init__(self, data, model):
        self.data = data
        self.model = model

    @property
    def battery_level(self) -> str:
        return self.data["battery_level"]

    @property
    def brush_left_time(self) -> str:
        return self.data["brush_left_time"]

    @property
    def brush_left_time2(self) -> str:
        return self.data["brush_left_time2"]

    @property
    def brush_life_level2(self) -> str:
        return self.data["brush_life_level2"]

    @property
    def brush_life_level(self) -> str:
        return self.data["brush_life_level"]

    @property
    def filter_left_time(self) -> str:
        return self.data["filter_left_time"]

    @property
    def filter_life_level(self) -> str:
        return self.data["filter_life_level"]

    @property
    def device_fault(self) -> Optional[FaultStatus]:
        try:
            return FaultStatus(self.data["device_fault"])
        except ValueError:
            _LOGGER.error("Unknown FaultStatus (%s)", self.data["device_fault"])
            return None

    @property
    def charging_state(self) -> Optional[ChargingState]:
        try:
            return ChargingState(self.data["charging_state"])
        except ValueError:
            _LOGGER.error("Unknown ChargingStats (%s)", self.data["charging_state"])
            return None

    @property
    def operating_mode(self) -> Optional[OperatingMode]:
        try:
            return OperatingMode(self.data["operating_mode"])
        except ValueError:
            _LOGGER.error("Unknown OperatingMode (%s)", self.data["operating_mode"])
            return None

    @property
    def device_status(self) -> Optional[DeviceStatus]:
        try:
            return DeviceStatus(self.data["device_status"])
        except TypeError:
            _LOGGER.error("Unknown DeviceStatus (%s)", self.data["device_status"])
            return None

    @property
    def timer_enable(self) -> str:
        return self.data["timer_enable"]

    @property
    def start_time(self) -> str:
        return self.data["start_time"]

    @property
    def stop_time(self) -> str:
        return self.data["stop_time"]

    @property
    def map_view(self) -> str:
        return self.data["map_view"]

    @property
    def volume(self) -> str:
        return self.data["volume"]

    @property
    def voice_package(self) -> str:
        return self.data["voice_package"]

    @property
    def timezone(self) -> str:
        return self.data["timezone"]

    @property
    def cleaning_time(self) -> str:
        return self.data["cleaning_time"]

    @property
    def cleaning_area(self) -> str:
        return self.data["cleaning_area"]

    @property
    def first_clean_time(self) -> str:
        return self.data["first_clean_time"]

    @property
    def total_clean_time(self) -> str:
        return self.data["total_clean_time"]

    @property
    def total_clean_times(self) -> str:
        return self.data["total_clean_times"]

    @property
    def total_clean_area(self) -> str:
        return self.data["total_clean_area"]

    @property
    def cleaning_mode(self):
        cleaning_mode = self.data["cleaning_mode"]
        cleaning_mode_enum_class = _get_cleaning_mode_enum_class(self.model)

        if not cleaning_mode_enum_class:
            _LOGGER.error(f"Unknown model for cleaning mode ({self.model})")
            return None
        try:
            return cleaning_mode_enum_class(cleaning_mode)
        except ValueError:
            _LOGGER.error(f"Unknown CleaningMode ({cleaning_mode})")
            return None

    @property
    def life_sieve(self) -> Optional[str]:
        return self.data.get("life_sieve")

    @property
    def life_brush_side(self) -> Optional[str]:
        return self.data.get("life_brush_side")

    @property
    def life_brush_main(self) -> Optional[str]:
        return self.data.get("life_brush_main")

    # TODO: get/set water flow for Dreame 1C
    @property
    def water_flow(self) -> Optional[WaterFlow]:
        try:
            water_flow = self.data["water_flow"]
        except KeyError:
            return None
        try:
            return WaterFlow(water_flow)
        except ValueError:
            _LOGGER.error("Unknown WaterFlow (%s)", self.data["water_flow"])
            return None

    @property
    def is_water_box_carriage_attached(self) -> Optional[bool]:
        """Return True if water box carriage (mop) is installed, None if sensor not
        present."""
        if "water_box_carriage_status" in self.data:
            return self.data["water_box_carriage_status"] == 1
        return None


class DreameVacuum(MiotDevice, VacuumInterface):
    _mappings = MIOT_MAPPING

    @command(
        default_output=format_output(
            "\n",
            "Battery level: {result.battery_level}\n"
            "Brush life level: {result.brush_life_level}\n"
            "Brush left time: {result.brush_left_time}\n"
            "Charging state: {result.charging_state}\n"
            "Cleaning mode: {result.cleaning_mode}\n"
            "Device fault: {result.device_fault}\n"
            "Device status: {result.device_status}\n"
            "Filter left level: {result.filter_left_time}\n"
            "Filter life level: {result.filter_life_level}\n"
            "Life brush main: {result.life_brush_main}\n"
            "Life brush side: {result.life_brush_side}\n"
            "Life sieve: {result.life_sieve}\n"
            "Map view: {result.map_view}\n"
            "Operating mode: {result.operating_mode}\n"
            "Side cleaning brush left time: {result.brush_left_time2}\n"
            "Side cleaning brush life level: {result.brush_life_level2}\n"
            "Time zone: {result.timezone}\n"
            "Timer enabled: {result.timer_enable}\n"
            "Timer start time: {result.start_time}\n"
            "Timer stop time: {result.stop_time}\n"
            "Voice package: {result.voice_package}\n"
            "Volume: {result.volume}\n"
            "Water flow: {result.water_flow}\n"
            "Water box attached: {result.is_water_box_carriage_attached} \n"
            "Cleaning time: {result.cleaning_time}\n"
            "Cleaning area: {result.cleaning_area}\n"
            "First clean time: {result.first_clean_time}\n"
            "Total clean time: {result.total_clean_time}\n"
            "Total clean times: {result.total_clean_times}\n"
            "Total clean area: {result.total_clean_area}\n",
        )
    )
    def status(self) -> DreameVacuumStatus:
        """State of the vacuum."""

        return DreameVacuumStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping(max_properties=10)
            },
            self.model,
        )

    # TODO: check the actual limit for this
    MANUAL_ROTATION_MAX = 120
    MANUAL_ROTATION_MIN = -MANUAL_ROTATION_MAX
    MANUAL_DISTANCE_MAX = 300
    MANUAL_DISTANCE_MIN = -300

    @command()
    def start(self) -> None:
        """Start cleaning."""
        return self.call_action("start_clean")

    @command()
    def stop(self) -> None:
        """Stop cleaning."""
        return self.call_action("stop_clean")

    @command()
    def home(self) -> None:
        """Return to home."""
        return self.call_action("home")

    @command()
    def identify(self) -> None:
        """Locate the device (i am here)."""
        return self.call_action("locate")

    @command()
    def reset_mainbrush_life(self) -> None:
        """Reset main brush life."""
        return self.call_action("reset_mainbrush_life")

    @command()
    def reset_filter_life(self) -> None:
        """Reset filter life."""
        return self.call_action("reset_filter_life")

    @command()
    def reset_sidebrush_life(self) -> None:
        """Reset side brush life."""
        return self.call_action("reset_sidebrush_life")

    @command()
    def play_sound(self) -> None:
        """Play sound."""
        return self.call_action("play_sound")

    @command()
    def fan_speed(self):
        """Return fan speed."""
        dreame_vacuum_status = self.status()
        fanspeed = dreame_vacuum_status.cleaning_mode
        if not fanspeed or fanspeed.value == -1:
            _LOGGER.warning("Unknown fanspeed value received")
            return
        return {fanspeed.name: fanspeed.value}

    @command(click.argument("speed", type=int))
    def set_fan_speed(self, speed: int):
        """Set fan speed.

        :param int speed: Fan speed to set
        """
        fanspeeds_enum = _get_cleaning_mode_enum_class(self.model)
        fanspeed = None
        if not fanspeeds_enum:
            return
        try:
            fanspeed = fanspeeds_enum(speed)
        except ValueError:
            _LOGGER.error(f"Unknown fanspeed value passed {speed}")
            return None
        click.echo(f"Setting fanspeed to {fanspeed.name}")
        return self.set_property("cleaning_mode", fanspeed.value)

    @command()
    def fan_speed_presets(self) -> FanspeedPresets:
        """Return available fan speed presets."""
        fanspeeds_enum = _get_cleaning_mode_enum_class(self.model)
        if not fanspeeds_enum:
            return {}
        return _enum_as_dict(fanspeeds_enum)

    @command(click.argument("speed", type=int))
    def set_fan_speed_preset(self, speed_preset: int) -> None:
        """Set fan speed preset speed."""
        if speed_preset not in self.fan_speed_presets().values():
            raise ValueError(
                f"Invalid preset speed {speed_preset}, not in: {self.fan_speed_presets().values()}"
            )
        self.set_fan_speed(speed_preset)

    @command()
    def waterflow(self):
        """Get water flow setting."""
        dreame_vacuum_status = self.status()
        waterflow = dreame_vacuum_status.water_flow
        if not waterflow or waterflow.value == -1:
            _LOGGER.warning("Unknown waterflow value received")
            return
        return {waterflow.name: waterflow.value}

    @command(click.argument("value", type=int))
    def set_waterflow(self, value: int):
        """Set water flow.

        :param int value: Water flow value to set
        """
        mapping = self._get_mapping()
        if "water_flow" not in mapping:
            return None
        waterflow = None
        try:
            waterflow = WaterFlow(value)
        except ValueError:
            _LOGGER.error(f"Unknown waterflow value passed {value}")
            return None
        click.echo(f"Setting waterflow to {waterflow.name}")
        return self.set_property("water_flow", waterflow.value)

    @command()
    def waterflow_presets(self) -> Dict[str, int]:
        """Return dictionary containing supported water flow."""
        mapping = self._get_mapping()
        if "water_flow" not in mapping:
            return {}
        return _enum_as_dict(WaterFlow)

    @command(
        click.argument("distance", default=30, type=int),
    )
    def forward(self, distance: int) -> None:
        """Move forward."""
        if distance < self.MANUAL_DISTANCE_MIN or distance > self.MANUAL_DISTANCE_MAX:
            raise DeviceException(
                "Given distance is invalid, should be [%s, %s], was: %s"
                % (self.MANUAL_DISTANCE_MIN, self.MANUAL_DISTANCE_MAX, distance)
            )
        self.call_action(
            "move",
            [
                {
                    "piid": 1,
                    "value": "0",
                },
                {
                    "piid": 2,
                    "value": f"{distance}",
                },
            ],
        )

    @command(
        click.argument("rotatation", default=90, type=int),
    )
    def rotate(self, rotatation: int) -> None:
        """Rotate vacuum."""
        if (
            rotatation < self.MANUAL_ROTATION_MIN
            or rotatation > self.MANUAL_ROTATION_MAX
        ):
            raise DeviceException(
                "Given rotation is invalid, should be [%s, %s], was %s"
                % (self.MANUAL_ROTATION_MIN, self.MANUAL_ROTATION_MAX, rotatation)
            )
        self.call_action(
            "move",
            [
                {
                    "piid": 1,
                    "value": f"{rotatation}",
                },
                {
                    "piid": 2,
                    "value": "0",
                },
            ],
        )

    @command(
        click.argument("url", type=str),
        click.argument("md5sum", type=str, required=False),
        click.argument("size", type=int, default=0),
        click.argument("voice_id", type=str, default="CP"),
    )
    def set_voice(self, url: str, md5sum: str, size: int, voice_id: str):
        """Upload voice package.

        :param str url: URL or path to language pack
        :param str md5sum: MD5 hash for file if URL used
        :param int size: File size in bytes if URL used
        :param str voice_id: In original it is country code for the selected
        voice pack. You can put here what you like, I guess it doesn't matter (default: CP - Custom Packet)
        """
        local_url = None
        server = None
        if url.startswith("http"):
            if md5sum is None or size == 0:
                click.echo(
                    "You need to pass md5 and file size when using URL for updating."
                )
                return
            local_url = url
        else:
            server = OneShotServer(file=url)
            local_url = server.url()
            md5sum = server.md5
            size = len(server.payload)

            t = threading.Thread(target=server.serve_once)
            t.start()
            click.echo(f"Hosting file at {local_url}")

        params = [
            {"piid": 3, "value": voice_id},
            {"piid": 4, "value": local_url},
            {"piid": 5, "value": md5sum},
            {"piid": 6, "value": size},
        ]
        result_status = self.call_action("set_voice", params=params)
        if result_status["code"] == 0:
            click.echo("Installation complete!")

        return result_status
