# -*- coding: UTF-8 -*#
from datetime import datetime, timedelta, time
from enum import IntEnum
from typing import Any, Dict, List

from .utils import deprecated, pretty_time, pretty_seconds


def pretty_area(x: float) -> float:
    """Prettify area value."""
    return int(x) / 1000000


error_codes = {  # from vacuum_cleaner-EN.pdf
    0: "No error",
    1: "Laser distance sensor error",
    2: "Collision sensor error",
    3: "Wheels on top of void, move robot",
    4: "Clean hovering sensors, move robot",
    5: "Clean main brush",
    6: "Clean side brush",
    7: "Main wheel stuck?",
    8: "Device stuck, clean area",
    9: "Dust collector missing",
    10: "Clean filter",
    11: "Stuck in magnetic barrier",
    12: "Low battery",
    13: "Charging fault",
    14: "Battery fault",
    15: "Wall sensors dirty, wipe them",
    16: "Place me on flat surface",
    17: "Side brushes problem, reboot me",
    18: "Suction fan problem",
    19: "Unpowered charging station",
}


states = {
    1: 'Starting',
    2: 'Charger disconnected',
    3: 'Idle',
    4: 'Remote control active',
    5: 'Cleaning',
    6: 'Returning home',
    7: 'Manual mode',
    8: 'Charging',
    9: 'Charging problem',
    10: 'Paused',
    11: 'Spot cleaning',
    12: 'Error',
    13: 'Shutting down',
    14: 'Updating',
    15: 'Docking',
    16: 'Going to target',
    17: 'Zoned cleaning',
}


class VacuumError(IntEnum):
    """Enum representing an error."""

    Invalid = -1
    NoError = 0
    LaserDistanceError = 1
    CollisionSensorError = 2
    WheelsOnVoid = 3
    CleanHoverSensor = 4
    CleanMainBrush = 5
    CleanSideBrush = 6
    StuckMainWheel = 7
    DeviceStuck = 8
    DustBinMissing = 9
    CleanFilter = 10
    StuckMagneticBarrier = 11
    LowBattery = 12
    ChargingError = 13
    BatteryError = 14
    CleanWallSensors = 15
    NotOnFlatSurface = 16
    SideBrushError = 17
    SuctionFanError = 18
    ChargerNoPower = 19


class VacuumState(IntEnum):
    """Enum representing the vacuum state."""

    Invalid = -1
    Starting = 1
    ChargerDisconnected = 2
    Idle = 3
    RemoteControl = 4
    Cleaning = 5
    Returning = 6
    ManualMode = 7
    Charging = 8
    ChargingProblem = 9
    Paused = 10
    SpotClean = 11
    Error = 12
    ShuttingDown = 13
    Updating = 14
    Docking = 15
    GoingToTarget = 16
    ZoneClean = 17


class VacuumStatus:
    """Container for status reports from the vacuum."""

    def __init__(self, data: Dict[str, Any]) -> None:
        # {'result': [{'state': 8, 'dnd_enabled': 1, 'clean_time': 0,
        #  'msg_ver': 4, 'map_present': 1, 'error_code': 0, 'in_cleaning': 0,
        #  'clean_area': 0, 'battery': 100, 'fan_power': 20, 'msg_seq': 320}],
        #  'id': 1}

        # v8 new items
        # clean_mode, begin_time, clean_trigger,
        # back_trigger, clean_strategy, and completed
        # TODO: create getters if wanted
        #
        # {"msg_ver":8,"msg_seq":60,"state":5,"battery":93,"clean_mode":0,
        # "fan_power":50,"error_code":0,"map_present":1,"in_cleaning":1,
        # "dnd_enabled":0,"begin_time":1534333389,"clean_time":21,
        # "clean_area":202500,"clean_trigger":2,"back_trigger":0,
        # "completed":0,"clean_strategy":1}
        self.data = data

    @property
    def state_code(self) -> int:
        """State code as returned by the device."""
        return int(self.data["state"])

    @property
    @deprecated("Use state_str for string presentation, "
                "this will return an enum in the future.")
    def state(self) -> str:
        """Human readable state description, see also :func:`state_code`."""
        return self.state_str

    @property
    def state_str(self) -> str:
        """Human readable state description.

        See also :func:`state_code`, :func:`state`, and :func:`state_enum`.
        """
        try:
            return states[int(self.state_code)]
        except KeyError:
            return "Definition missing for state %s" % self.state_code

    @property
    def state_enum(self) -> VacuumState:
        """Vacuum state as enum."""
        try:
            return VacuumState(self.state_code)
        except ValueError:
            return VacuumState(VacuumState.Invalid)

    @property
    def error_code(self) -> int:
        """Error code as returned by the device."""
        return int(self.data["error_code"])

    @property
    @deprecated("Use error_str for human readable, "
                "this will change in the future to return an enum.")
    def error(self):
        """Human readable error description, see also :func:`error_code`."""
        return self.error_str

    @property
    def error_str(self) -> str:
        """Human readable error description, see also :func:`error_code`."""
        try:
            return error_codes[self.error_code]
        except KeyError:
            return "Definition missing for error %s" % self.error_code

    @property
    def error_enum(self) -> VacuumError:
        """Return error as enum."""
        try:
            return VacuumError(self.error_code)
        except ValueError:
            return VacuumError(VacuumError.Invalid)

    @property
    def battery(self) -> int:
        """Remaining battery in percentage."""
        return int(self.data["battery"])

    @property
    def fanspeed(self) -> int:
        """Return current fan speed."""
        return int(self.data["fan_power"])

    @property
    def clean_time(self) -> timedelta:
        """Return time in cleaning.

        If cleaning is finished, returns the duration.
        """
        return pretty_seconds(self.data["clean_time"])

    @property
    def clean_area(self) -> float:
        """Return cleaned area in m2."""
        return pretty_area(self.data["clean_area"])

    @property
    @deprecated("Use vacuum's dnd_status() instead, which is more accurate")
    def dnd(self) -> bool:
        """Return DnD status.

        Use :func:`vacuum.dnd_status` instead of this.
        """
        return bool(self.data["dnd_enabled"])

    @property
    def map(self) -> bool:
        """Return the map token."""
        return bool(self.data["map_present"])

    @property
    @deprecated("See is_on")
    def in_cleaning(self) -> bool:
        """Return True if in cleaning.

        Please use :func:`is_on` instead of this.
        """
        return self.is_on
        # we are not using in_cleaning as it does not seem to work properly.
        # return bool(self.data["in_cleaning"])

    @property
    def is_on(self) -> bool:
        """Return True if device is currently cleaning.

        Either automatic, manual, spot, or zone.
        """
        return (self.state_enum == VacuumState.Cleaning or
                self.state_enum == VacuumState.ManualMode or
                self.state_enum == VacuumState.SpotClean or
                self.state_enum == VacuumState.ZoneClean)

    @property
    def got_error(self) -> bool:
        """Return True if an error has occured."""
        return self.error_code != 0

    def __repr__(self) -> str:
        s = "<VacuumStatus state=%s, error=%s " % (self.state, self.error)
        s += "bat=%s%%, fan=%s%% " % (self.battery, self.fanspeed)
        s += "cleaned %s m² in %s>" % (self.clean_area, self.clean_time)
        return s

    def __json__(self):
        return self.data


class CleaningSummary:
    """Contains summarized information about available cleaning runs."""

    def __init__(self, data: List[Any]) -> None:
        # total duration, total area, amount of cleans
        # [ list, of, ids ]
        # { "result": [ 174145, 2410150000, 82,
        # [ 1488240000, 1488153600, 1488067200, 1487980800,
        #  1487894400, 1487808000, 1487548800 ] ],
        #  "id": 1 }
        self.data = data

    @property
    def total_duration(self) -> timedelta:
        """Return total cleaning duration."""
        return pretty_seconds(self.data[0])

    @property
    def total_area(self) -> float:
        """Return total cleaned area."""
        return pretty_area(self.data[1])

    @property
    def count(self) -> int:
        """Return number of cleaning runs."""
        return int(self.data[2])

    @property
    def ids(self) -> List[int]:
        """Return a list of available cleaning IDs.

        See also :class:`CleaningDetails`.
        """
        return list(self.data[3])

    def __repr__(self) -> str:
        return "<CleaningSummary: %s times, total time: %s, total area: %s, ids: %s>" % (  # noqa: E501
            self.count,
            self.total_duration,
            self.total_area,
            self.ids)

    def __json__(self):
        return self.data


class CleaningDetails:
    """Contains details about a specific cleaning run."""

    def __init__(self, data: List[Any]) -> None:
        # start, end, duration, area, unk, complete
        # { "result": [ [ 1488347071, 1488347123, 16, 0, 0, 0 ] ], "id": 1 }
        self.data = data

    @property
    def start(self) -> datetime:
        """Return when cleaning was started."""
        return pretty_time(self.data[0])

    @property
    def end(self) -> datetime:
        """Return when cleaning was finished."""
        return pretty_time(self.data[1])

    @property
    def duration(self) -> timedelta:
        """Return total duration of the cleaning run."""
        return pretty_seconds(self.data[2])

    @property
    def area(self) -> float:
        """Return cleaned area."""
        return pretty_area(self.data[3])

    @property
    def error_code(self) -> int:
        """Return error code of the cleaning run."""
        return int(self.data[4])

    @property
    def error(self) -> str:
        """Return error state of the cleaning run."""
        return error_codes[self.data[4]]

    @property
    def complete(self) -> bool:
        """Return True if the cleaning run was complete without errors.

        see also :func:`error`.
        """
        return bool(self.data[5] == 1)

    def __repr__(self) -> str:
        return "<CleaningDetails: %s (duration: %s, done: %s), area: %s>" % (
            self.start, self.duration, self.complete, self.area
        )

    def __json__(self):
        return self.data


class ConsumableStatus:
    """Container for consumable status information.

    This includes information about brushes and sensors,
    and provides also helpers to return time remaining for maintenance.

    The methods returning time left are based on the following lifetimes:
    - Sensor cleanup time: 30 hours
    - Main brush: 300 hours
    - Side brush: 200 hours
    - Filter: 150 hours
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        # {'id': 1, 'result': [{'filter_work_time': 32454,
        #  'sensor_dirty_time': 3798,
        # 'side_brush_work_time': 32454,
        #  'main_brush_work_time': 32454}]}
        self.data = data
        self.main_brush_total = timedelta(hours=300)
        self.side_brush_total = timedelta(hours=200)
        self.filter_total = timedelta(hours=150)
        self.sensor_dirty_total = timedelta(hours=30)

    @property
    def main_brush(self) -> timedelta:
        """Return main brush usage time."""
        return pretty_seconds(self.data["main_brush_work_time"])

    @property
    def main_brush_left(self) -> timedelta:
        """Return time remaining until the main brush should be replaced."""
        return self.main_brush_total - self.main_brush

    @property
    def side_brush(self) -> timedelta:
        """Return side brush usage time."""
        return pretty_seconds(self.data["side_brush_work_time"])

    @property
    def side_brush_left(self) -> timedelta:
        """Return time remaining until the side brush should be replaced."""
        return self.side_brush_total - self.side_brush

    @property
    def filter(self) -> timedelta:
        """Return filter usage time."""
        return pretty_seconds(self.data["filter_work_time"])

    @property
    def filter_left(self) -> timedelta:
        """Return time remaining until the filter should be replaced."""
        return self.filter_total - self.filter

    @property
    def sensor_dirty(self) -> timedelta:
        """Return time since sensor cleaning."""
        return pretty_seconds(self.data["sensor_dirty_time"])

    @property
    def sensor_dirty_left(self) -> timedelta:
        """Return time remaining until the sensors should be cleaned."""
        return self.sensor_dirty_total - self.sensor_dirty

    def __repr__(self) -> str:
        return "<ConsumableStatus main: %s, side: %s, filter: %s, sensor dirty: %s>" % (  # noqa: E501
            self.main_brush, self.side_brush, self.filter, self.sensor_dirty)

    def __json__(self):
        return self.data


class DNDStatus:
    """A container for the do-not-disturb status."""

    def __init__(self, data: Dict[str, Any]):
        # {'end_minute': 0, 'enabled': 1, 'start_minute': 0,
        #  'start_hour': 22, 'end_hour': 8}
        self.data = data

    @property
    def enabled(self) -> bool:
        """Return True if DnD is enabled."""
        return bool(self.data["enabled"])

    @property
    def start(self) -> time:
        """Return the start time of DnD."""
        return time(hour=self.data["start_hour"],
                    minute=self.data["start_minute"])

    @property
    def end(self) -> time:
        """Return the end time of DnD."""
        return time(hour=self.data["end_hour"],
                    minute=self.data["end_minute"])

    def __repr__(self):
        return "<DNDStatus enabled: %s - between %s and %s>" % (
            self.enabled,
            self.start,
            self.end)

    def __json__(self):
        return self.data


class Timer:
    """A container for scheduling.

    The timers are accessed using an integer ID, which is based on the unix
    timestamp of the creation time.
    """

    def __init__(self, data: List[Any]) -> None:
        # id / timestamp, enabled, ['<cron string>', ['command', 'params']
        # [['1488667794112', 'off', ['49 22 * * 6', ['start_clean', '']]],
        #  ['1488667777661', 'off', ['49 21 * * 3,4,5,6', ['start_clean', '']]
        # ],
        self.data = data

    @property
    def id(self) -> int:
        """Return the ID of this timer."""
        return int(self.data[0])

    @property
    def ts(self) -> datetime:
        """Return the creation time of the timer."""
        return pretty_time(int(self.data[0]) / 1000)

    @property
    def enabled(self) -> bool:
        """Return True if the timer is active."""
        return bool(self.data[1] == 'on')

    @property
    def cron(self) -> str:
        """Return cron-formated timer string."""
        return str(self.data[2][0])

    @property
    def action(self) -> str:
        """Return the action to be executed by the timer.

        Note, this seems to be always 'start'.
        """
        return str(self.data[2][1])

    def __repr__(self) -> str:
        return "<Timer %s: %s - enabled: %s - cron: %s>" % (self.id, self.ts,
                                                            self.enabled, self.cron)

    def __json__(self):
        return self.data


class SoundStatus:
    """Container for sound status."""

    def __init__(self, data):
        # {'sid_in_progress': 0, 'sid_in_use': 1004}
        self.data = data

    @property
    def current(self):
        """Return the ID of currently used sound pack."""
        return self.data['sid_in_use']

    @property
    def being_installed(self):
        """Return True if a sound pack is being installed."""
        return self.data['sid_in_progress']

    def __repr__(self):
        return "<SoundStatus current: %s installing: %s>" % (
            self.current,
            self.being_installed)

    def __json__(self):
        return self.data


class SoundInstallState(IntEnum):
    """Enum for sound install states."""

    Unknown = 0
    Downloading = 1
    Installing = 2
    Installed = 3
    Error = 4


class SoundInstallStatus:
    """Container for sound installation status."""

    def __init__(self, data):
        # {'progress': 0, 'sid_in_progress': 0, 'state': 0, 'error': 0}
        # error 0 = no error
        # error 1 = unknown 1
        # error 2 = download error
        # error 3 = checksum error
        # error 4 = unknown 4
        self.data = data

    @property
    def state(self) -> SoundInstallState:
        """Return the installation state."""
        return SoundInstallState(self.data['state'])

    @property
    def progress(self) -> int:
        """Return the install progress in percentage."""
        return self.data['progress']

    @property
    def sid(self) -> int:
        """Return the Sound ID currently being installed."""
        # this is missing on install confirmation, so let's use get
        return self.data.get('sid_in_progress', None)

    @property
    def error(self) -> int:
        """Return the error code.

        0 is no error, other values unknown.
        """
        return self.data['error']

    @property
    def is_installing(self) -> bool:
        """Return True if install is in progress."""
        return (self.state == SoundInstallState.Downloading or
                self.state == SoundInstallState.Installing)

    @property
    def is_errored(self) -> bool:
        """Return True if an error has occured, use `error` to access it."""
        return self.state == SoundInstallState.Error

    def __repr__(self) -> str:
        return "<SoundInstallStatus sid: %s (state: %s, error: %s)" \
               " - progress: %s>" % (self.sid, self.state,
                                     self.error, self.progress)

    def __json__(self):
        return self.data


class CarpetModeStatus:
    """Container for carpet mode status."""

    def __init__(self, data):
        # {'current_high': 500, 'enable': 1, 'current_integral': 450,
        #  'current_low': 400, 'stall_time': 10}
        self.data = data

    @property
    def enabled(self) -> bool:
        """Return True if carpet mode is enabled."""
        return self.data['enable'] == 1

    @property
    def stall_time(self) -> int:
        return self.data['stall_time']

    @property
    def current_low(self) -> int:
        return self.data['current_low']

    @property
    def current_high(self) -> int:
        return self.data['current_high']

    @property
    def current_integral(self) -> int:
        return self.data['current_integral']

    def __repr__(self):
        return "<CarpetModeStatus enabled=%s, " \
               "stall_time: %s, " \
               "current (low, high, integral): (%s, %s, %s)>" % (self.enabled,
                                                                 self.stall_time,
                                                                 self.current_low,
                                                                 self.current_high,
                                                                 self.current_integral)

    def __json__(self):
        return self.data
