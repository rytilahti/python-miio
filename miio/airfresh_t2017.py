import enum
import logging
from collections import defaultdict
from typing import Any, Dict, Optional

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_AIRFRESH_A1 = "dmaker.airfresh.a1"
MODEL_AIRFRESH_T2017 = "dmaker.airfresh.t2017"

AVAILABLE_PROPERTIES_COMMON = [
    "power",
    "mode",
    "pm25",
    "co2",
    "temperature_outside",
    "favourite_speed",
    "control_speed",
    "ptc_on",
    "ptc_status",
    "child_lock",
    "sound",
    "display",
]

AVAILABLE_PROPERTIES = {
    MODEL_AIRFRESH_T2017: AVAILABLE_PROPERTIES_COMMON
    + [
        "filter_intermediate",
        "filter_inter_day",
        "filter_efficient",
        "filter_effi_day",
        "ptc_level",
        "screen_direction",
    ],
    MODEL_AIRFRESH_A1: AVAILABLE_PROPERTIES_COMMON
    + [
        "filter_rate",
        "filter_day",
    ],
}


class AirFreshException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Off = "off"
    Auto = "auto"
    Sleep = "sleep"
    Favorite = "favourite"


class PtcLevel(enum.Enum):
    Low = "low"
    Medium = "medium"
    High = "high"


class DisplayOrientation(enum.Enum):
    Portrait = "forward"
    LandscapeLeft = "left"
    LandscapeRight = "right"


class AirFreshStatus(DeviceStatus):
    """Container for status reports from the air fresh t2017."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Air Fresh A1 (dmaker.airfresh.a1):
        {
            'power': True,
            'mode': 'auto',
            'pm25': 2,
            'co2': 554,
            'temperature_outside': 12,
            'favourite_speed': 150,
            'control_speed': 60,
            'filter_rate': 45,
            'filter_day': 81,
            'ptc_on': False,
            'ptc_status': False,
            'child_lock': False,
            'sound': False,
            'display': False,
        }

        Response of a Air Fresh T2017 (dmaker.airfresh.t2017):

        {
            'power': True,
            'mode': 'favourite',
            'pm25': 1,
            'co2': 550,
            'temperature_outside': 24,
            'favourite_speed': 241,
            'control_speed': 241,
            'filter_intermediate': 100,
            'filter_inter_day': 90,
            'filter_efficient': 100,
            'filter_effi_day': 180,
            'ptc_on': False,
            'ptc_level': 'low',
            'ptc_status': False,
            'child_lock': False,
            'sound': True,
            'display': False,
            'screen_direction': 'forward',
        }
        """

        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.data["power"] else "off"

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.data["power"]

    @property
    def mode(self) -> OperationMode:
        """Current operation mode."""
        return OperationMode(self.data["mode"])

    @property
    def pm25(self) -> int:
        """Fine particulate patter (PM2.5)."""
        return self.data["pm25"]

    @property
    def co2(self) -> int:
        """Carbon dioxide."""
        return self.data["co2"]

    @property
    def temperature(self) -> int:
        """Current temperature in degree celsions."""
        return self.data["temperature_outside"]

    @property
    def favorite_speed(self) -> int:
        """Favorite speed."""
        return self.data["favourite_speed"]

    @property
    def control_speed(self) -> int:
        """Control speed."""
        return self.data["control_speed"]

    @property
    def dust_filter_life_remaining(self) -> Optional[int]:
        """Remaining dust filter life in percent."""
        return self.data.get("filter_intermediate", self.data.get("filter_rate"))

    @property
    def dust_filter_life_remaining_days(self) -> Optional[int]:
        """Remaining dust filter life in days."""
        return self.data.get("filter_inter_day", self.data.get("filter_day"))

    @property
    def upper_filter_life_remaining(self) -> Optional[int]:
        """Remaining upper filter life in percent."""
        return self.data.get("filter_efficient")

    @property
    def upper_filter_life_remaining_days(self) -> Optional[int]:
        """Remaining upper filter life in days."""
        return self.data.get("filter_effi_day")

    @property
    def ptc(self) -> bool:
        """Return True if PTC is on."""
        return self.data["ptc_on"]

    @property
    def ptc_level(self) -> Optional[PtcLevel]:
        """PTC level."""
        try:
            return PtcLevel(self.data["ptc_level"])
        except (KeyError, ValueError):
            return None

    @property
    def ptc_status(self) -> bool:
        """Return true if PTC status is on."""
        return self.data["ptc_status"]

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"]

    @property
    def buzzer(self) -> bool:
        """Return True if sound is on."""
        return self.data["sound"]

    @property
    def display(self) -> bool:
        """Return True if the display is on."""
        return self.data["display"]

    @property
    def display_orientation(self) -> Optional[DisplayOrientation]:
        """Display orientation."""
        try:
            return DisplayOrientation(self.data["screen_direction"])
        except (KeyError, ValueError):
            return None


class AirFreshA1(Device):
    """Main class representing the air fresh a1."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_AIRFRESH_A1,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_AIRFRESH_A1

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "PM2.5: {result.pm25}\n"
            "CO2: {result.co2}\n"
            "Temperature: {result.temperature}\n"
            "Favorite speed: {result.favorite_speed}\n"
            "Control speed: {result.control_speed}\n"
            "Dust filter life: {result.dust_filter_life_remaining} %, "
            "{result.dust_filter_life_remaining_days} days\n"
            "PTC: {result.ptc}\n"
            "PTC status: {result.ptc_status}\n"
            "Child lock: {result.child_lock}\n"
            "Buzzer: {result.buzzer}\n"
            "Display: {result.display}\n",
        )
    )
    def status(self) -> AirFreshStatus:
        """Retrieve properties."""

        properties = AVAILABLE_PROPERTIES[self.model]
        values = self.get_properties(properties, max_properties=15)

        return AirFreshStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", [True])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", [False])

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.send("set_mode", [mode.value])

    @command(
        click.argument("display", type=bool),
        default_output=format_output(
            lambda led: "Turning on display" if led else "Turning off display"
        ),
    )
    def set_display(self, display: bool):
        """Turn led on/off."""
        return self.send("set_display", [display])

    @command(
        click.argument("ptc", type=bool),
        default_output=format_output(
            lambda ptc: "Turning on ptc" if ptc else "Turning off ptc"
        ),
    )
    def set_ptc(self, ptc: bool):
        """Turn ptc on/off."""
        return self.send("set_ptc_on", [ptc])

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set sound on/off."""
        return self.send("set_sound", [buzzer])

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        return self.send("set_child_lock", [lock])

    @command(default_output=format_output("Resetting dust filter"))
    def reset_dust_filter(self):
        """Resets filter lifetime of the dust filter."""
        return self.send("set_filter_rate", [100])

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting favorite speed to {speed}"),
    )
    def set_favorite_speed(self, speed: int):
        """Sets the fan speed in favorite mode."""
        if speed < 0 or speed > 150:
            raise AirFreshException("Invalid favorite speed: %s" % speed)

        return self.send("set_favourite_speed", [speed])

    @command()
    def set_ptc_timer(self):
        """
        value = time.index + '-' +
            time.hexSum + '-' +
            time.startTime + '-' +
            time.ptcTimer.endTime + '-' +
            time.level + '-' +
            time.status;
        return self.send("set_ptc_timer", [value])
        """
        raise NotImplementedError()

    @command()
    def get_ptc_timer(self):
        """Returns a list of PTC timers.

        Response unknown.
        """
        return self.send("get_ptc_timer")

    @command()
    def get_timer(self):
        """Response unknown."""
        return self.send("get_timer")


class AirFreshT2017(AirFreshA1):
    """Main class representing the air fresh t2017."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_AIRFRESH_T2017,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_AIRFRESH_T2017

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "PM2.5: {result.pm25}\n"
            "CO2: {result.co2}\n"
            "Temperature: {result.temperature}\n"
            "Favorite speed: {result.favorite_speed}\n"
            "Control speed: {result.control_speed}\n"
            "Dust filter life: {result.dust_filter_life_remaining} %, "
            "{result.dust_filter_life_remaining_days} days\n"
            "Upper filter life remaining: {result.upper_filter_life_remaining} %, "
            "{result.upper_filter_life_remaining_days} days\n"
            "PTC: {result.ptc}\n"
            "PTC level: {result.ptc_level}\n"
            "PTC status: {result.ptc_status}\n"
            "Child lock: {result.child_lock}\n"
            "Buzzer: {result.buzzer}\n"
            "Display: {result.display}\n"
            "Display orientation: {result.display_orientation}\n",
        )
    )
    def status(self) -> AirFreshStatus:
        """Retrieve properties."""

        return super().status()

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting favorite speed to {speed}"),
    )
    def set_favorite_speed(self, speed: int):
        """Sets the fan speed in favorite mode."""
        if speed < 60 or speed > 300:
            raise AirFreshException("Invalid favorite speed: %s" % speed)

        return self.send("set_favourite_speed", [speed])

    @command(default_output=format_output("Resetting dust filter"))
    def reset_dust_filter(self):
        """Resets filter lifetime of the dust filter."""
        return self.send("set_filter_reset", ["intermediate"])

    @command(default_output=format_output("Resetting upper filter"))
    def reset_upper_filter(self):
        """Resets filter lifetime of the upper filter."""
        return self.send("set_filter_reset", ["efficient"])

    @command(
        click.argument("orientation", type=EnumType(DisplayOrientation)),
        default_output=format_output("Setting orientation to '{orientation.value}'"),
    )
    def set_display_orientation(self, orientation: DisplayOrientation):
        """Set display orientation."""
        return self.send("set_screen_direction", [orientation.value])

    @command(
        click.argument("level", type=EnumType(PtcLevel)),
        default_output=format_output("Setting ptc level to '{level.value}'"),
    )
    def set_ptc_level(self, level: PtcLevel):
        """Set PTC level."""
        return self.send("set_ptc_level", [level.value])
