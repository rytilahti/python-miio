# -*- coding: UTF-8 -*#
from datetime import datetime, timedelta, time
from typing import Any, Dict, List
import warnings
import functools
import inspect


def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    From https://stackoverflow.com/a/40301488
    """

    string_types = (type(b''), type(u''))
    if isinstance(reason, string_types):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(
                    fmt1.format(name=func1.__name__, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2
                )
                warnings.simplefilter('default', DeprecationWarning)
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(
                fmt2.format(name=func2.__name__),
                category=DeprecationWarning,
                stacklevel=2
            )
            warnings.simplefilter('default', DeprecationWarning)
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))


def pretty_area(x: float) -> float:
    return int(x) / 1000000


def pretty_seconds(x: float) -> timedelta:
    return timedelta(seconds=x)


def pretty_time(x: float) -> datetime:
    return datetime.fromtimestamp(x)


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


class VacuumStatus:
    """Container for status reports from the vacuum."""
    def __init__(self, data: Dict[str, Any]) -> None:
        # {'result': [{'state': 8, 'dnd_enabled': 1, 'clean_time': 0,
        #  'msg_ver': 4, 'map_present': 1, 'error_code': 0, 'in_cleaning': 0,
        #  'clean_area': 0, 'battery': 100, 'fan_power': 20, 'msg_seq': 320}],
        #  'id': 1}
        self.data = data

    @property
    def state_code(self) -> int:
        """State code as returned by the device."""
        return int(self.data["state"])

    @property
    def state(self) -> str:
        """Human readable state description, see also :func:`state_code`."""
        states = {
            1: 'Unknown 1',
            2: 'Charger disconnected',
            3: 'Idle',
            4: 'Unknown 4',
            5: 'Cleaning',
            6: 'Returning home',
            7: 'Manual mode',
            8: 'Charging',
            9: 'Unknown 9',
            10: 'Paused',
            11: 'Spot cleaning',
            12: 'Error',
            13: 'Unknown 13',
            14: 'Updating',
        }
        return states[int(self.state_code)]

    @property
    def error_code(self) -> int:
        """Error code as returned by the device."""
        return int(self.data["error_code"])

    @property
    def error(self) -> str:
        """Human readable error description, see also :func:`error_code`."""
        return error_codes[self.error_code]

    @property
    def battery(self) -> int:
        """Remaining battery in percentage. """
        return int(self.data["battery"])

    @property
    def fanspeed(self) -> int:
        """Current fan speed."""
        return int(self.data["fan_power"])

    @property
    def clean_time(self) -> timedelta:
        """Time used for cleaning (if finished, shows how long it took)."""
        return pretty_seconds(self.data["clean_time"])

    @property
    def clean_area(self) -> float:
        """Cleaned area in m2."""
        return pretty_area(self.data["clean_area"])

    @property
    @deprecated("Use vacuum's dnd_status() instead, which is more accurate")
    def dnd(self) -> bool:
        """DnD status. Use :func:`vacuum.dnd_status` instead of this."""
        return bool(self.data["dnd_enabled"])

    @property
    def map(self) -> bool:
        """Map token."""
        return bool(self.data["map_present"])

    @property
    @deprecated("See is_on")
    def in_cleaning(self) -> bool:
        """True if currently cleaning. Please use :func:`is_on` instead of this."""
        return self.is_on
        # we are not using in_cleaning as it does not seem to work properly.
        # return bool(self.data["in_cleaning"])

    @property
    def is_on(self) -> bool:
        """True if device is currently cleaning (either automatic, manual or spot)."""
        return self.state_code == 5 or \
               self.state_code == 7 or \
               self.state_code == 11

    @property
    def got_error(self) -> bool:
        """True if an error has occured."""
        return self.state_code == 12

    def __repr__(self) -> str:
        s = "<VacuumStatus state=%s, error=%s " % (self.state, self.error)
        s += "bat=%s%%, fan=%s%% " % (self.battery, self.fanspeed)
        s += "cleaned %s m² in %s>" % (self.clean_area, self.clean_time)
        return s


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
        """Total cleaning duration."""
        return pretty_seconds(self.data[0])

    @property
    def total_area(self) -> float:
        """Total cleaned area."""
        return pretty_area(self.data[1])

    @property
    def count(self) -> int:
        """Number of cleaning runs."""
        return int(self.data[2])

    @property
    def ids(self) -> List[int]:
        """A list of available cleaning IDs, see also :class:`CleaningDetails`."""
        return list(self.data[3])

    def __repr__(self) -> str:
        return "<CleaningSummary: %s times, total time: %s, total area: %s, ids: %s>" % (  # noqa: E501
            self.count,
            self.total_duration,
            self.total_area,
            self.ids)


class CleaningDetails:
    """Contains details about a specific cleaning run."""
    def __init__(self, data: List[Any]) -> None:
        # start, end, duration, area, unk, complete
        # { "result": [ [ 1488347071, 1488347123, 16, 0, 0, 0 ] ], "id": 1 }
        self.data = data

    @property
    def start(self) -> datetime:
        """When cleaning was started."""
        return pretty_time(self.data[0])

    @property
    def end(self) -> datetime:
        """When cleaning was finished."""
        return pretty_time(self.data[1])

    @property
    def duration(self) -> timedelta:
        """Total duration of the cleaning run."""
        return pretty_seconds(self.data[2])

    @property
    def area(self) -> float:
        """Total cleaned area."""
        return pretty_area(self.data[3])

    @property
    def error_code(self) -> int:
        """Error code."""
        return int(self.data[4])

    @property
    def error(self) -> str:
        """Error state of this cleaning run."""
        return error_codes[self.data[4]]

    @property
    def complete(self) -> bool:
        """Return True if the cleaning run was complete (e.g. without errors), see also :func:`error`."""
        return bool(self.data[5] == 1)

    def __repr__(self) -> str:
        return "<CleaningDetails: %s (duration: %s, done: %s), area: %s>" % (
            self.start, self.duration, self.complete, self.area
        )


class ConsumableStatus:
    """Container for consumable status information,
    including information about brushes and duration until they should be changed.
    The methods returning time left are based on the following lifetimes:

    - Sensor cleanup time: XXX FIXME
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
        """Main brush usage time."""
        return pretty_seconds(self.data["main_brush_work_time"])

    @property
    def main_brush_left(self) -> timedelta:
        """How long until the main brush should be changed."""
        return self.main_brush_total - self.main_brush

    @property
    def side_brush(self) -> timedelta:
        """Side brush usage time."""
        return pretty_seconds(self.data["side_brush_work_time"])

    @property
    def side_brush_left(self) -> timedelta:
        """How long until the side brush should be changed."""
        return self.side_brush_total - self.side_brush

    @property
    def filter(self) -> timedelta:
        """Filter usage time."""
        return pretty_seconds(self.data["filter_work_time"])

    @property
    def filter_left(self) -> timedelta:
        """How long until the filter should be changed."""
        return self.filter_total - self.filter

    @property
    def sensor_dirty(self) -> timedelta:
        """Return ``sensor_dirty_time``"""
        return pretty_seconds(self.data["sensor_dirty_time"])

    @property
    def sensor_dirty_left(self) -> timedelta:
        return self.sensor_dirty_total - self.sensor_dirty

    def __repr__(self) -> str:
        return "<ConsumableStatus main: %s, side: %s, filter: %s, sensor dirty: %s>" % (  # noqa: E501
            self.main_brush, self.side_brush, self.filter, self.sensor_dirty)


class DNDStatus:
    """A container for the do-not-disturb status."""
    def __init__(self, data: Dict[str, Any]):
        # {'end_minute': 0, 'enabled': 1, 'start_minute': 0,
        #  'start_hour': 22, 'end_hour': 8}
        self.data = data

    @property
    def enabled(self) -> bool:
        """True if DnD is enabled."""
        return bool(self.data["enabled"])

    @property
    def start(self) -> time:
        """Start time of DnD."""
        return time(hour=self.data["start_hour"],
                    minute=self.data["start_minute"])

    @property
    def end(self) -> time:
        """End time of DnD."""
        return time(hour=self.data["end_hour"],
                    minute=self.data["end_minute"])

    def __repr__(self):
        return "<DNDStatus enabled: %s - between %s and %s>" % (
            self.enabled,
            self.start,
            self.end)


class Timer:
    """A container for scheduling.
    The timers are accessed using an integer ID, which is based on the unix
    timestamp of the creation time."""
    def __init__(self, data: List[Any]) -> None:
        # id / timestamp, enabled, ['<cron string>', ['command', 'params']
        # [['1488667794112', 'off', ['49 22 * * 6', ['start_clean', '']]],
        #  ['1488667777661', 'off', ['49 21 * * 3,4,5,6', ['start_clean', '']]
        # ],
        self.data = data

    @property
    def id(self) -> int:
        """ID which can be used to point to this timer."""
        return int(self.data[0])

    @property
    def ts(self) -> datetime:
        """Pretty-printed ID (timestamp) presentation as time."""
        return pretty_time(int(self.data[0]) / 1000)

    @property
    def enabled(self) -> bool:
        """True if the timer is active."""
        return bool(self.data[1] == 'on')

    @property
    def cron(self) -> str:
        """Cron-formated timer string."""
        return str(self.data[2][0])

    @property
    def action(self) -> str:
        """The action to be taken on the given time.
        Note, this seems to be always 'start'."""
        return str(self.data[2][1])

    def __repr__(self) -> str:
        return "<Timer %s: %s - enabled: %s - cron: %s>" % (self.id, self.ts, self.enabled, self.cron)
