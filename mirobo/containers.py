# -*- coding: UTF-8 -*#
from datetime import datetime, timedelta
from typing import Any, Dict, List


def pretty_area(x: float) -> float:
    return int(x) / 1000000


def pretty_seconds(x: int) -> timedelta:
    return timedelta(seconds=x)


def pretty_time(x: int) -> datetime:
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


class PlugStatus:
    """Container for status reports from the plug."""
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def temperature(self) -> float:
        return self.data["temperature"]

    @property
    def current(self) -> float:
        return self.data["current"]

    def __str__(self) -> str:
        s = "<PlugStatus power=%s, temperature=%s, current=%s>" % \
            (self.power,
             self.temperature,
             self.current)
        return s


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
        return int(self.data["state"])

    @property
    def state(self) -> str:
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
        return int(self.data["error_code"])

    @property
    def error(self) -> str:
        return error_codes[self.error_code]

    @property
    def battery(self) -> int:
        return int(self.data["battery"])

    @property
    def fanspeed(self) -> int:
        return int(self.data["fan_power"])

    @property
    def clean_time(self) -> timedelta:
        return pretty_seconds(self.data["clean_time"])

    @property
    def clean_area(self) -> float:
        return pretty_area(self.data["clean_area"])

    @property
    def dnd(self) -> bool:
        return bool(self.data["dnd_enabled"])

    @property
    def map(self) -> bool:
        return bool(self.data["map_present"])

    @property
    def in_cleaning(self) -> bool:
        return bool(self.data["in_cleaning"])

    @property
    def is_on(self) -> bool:
        return self.state_code == 5

    @property
    def got_error(self) -> bool:
        return self.state_code == 12

    def __str__(self) -> str:
        s = "<VacuumStatus state=%s, error=%s " % (self.state, self.error)
        s += "bat=%s%%, fan=%s%% " % (self.battery, self.fanspeed)
        s += "cleaned %s m² in %s>" % (self.clean_area, self.clean_time)
        return s


class CleaningSummary:
    """Cleaning summary."""
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
        return pretty_seconds(self.data[0])

    @property
    def total_area(self) -> float:
        return pretty_area(self.data[1])

    @property
    def count(self) -> int:
        return int(self.data[2])

    @property
    def ids(self) -> List[int]:
        return list(self.data[3])

    def __str__(self) -> str:
        return "<CleaningSummary: %s times, total time: %s, total area: %s, ids: %s>" % (  # noqa: E501
            self.count,
            self.total_duration,
            self.total_area,
            self.ids)


class CleaningDetails:
    """Cleaning details."""
    def __init__(self, data: List[Any]) -> None:
        # start, end, duration, area, unk, complete
        # { "result": [ [ 1488347071, 1488347123, 16, 0, 0, 0 ] ], "id": 1 }
        self.data = data

    @property
    def start(self) -> datetime:
        return pretty_time(self.data[0])

    @property
    def end(self) -> datetime:
        return pretty_time(self.data[1])

    @property
    def duration(self) -> timedelta:
        return pretty_seconds(self.data[2])

    @property
    def area(self) -> float:
        return pretty_area(self.data[3])

    @property
    def error(self) -> str:
        return error_codes[self.data[4]]

    @property
    def complete(self) -> bool:
        return bool(self.data[5] == 1)

    def __str__(self) -> str:
        return "<CleaningDetails: %s (duration: %s, done: %s), area: %s>" % (
            self.start, self.duration, self.complete, self.area
        )


class ConsumableStatus:
    """Container for consumable status information."""
    def __init__(self, data: Dict[str, Any]) -> None:
        # {'id': 1, 'result': [{'filter_work_time': 32454,
        #  'sensor_dirty_time': 3798,
        # 'side_brush_work_time': 32454,
        #  'main_brush_work_time': 32454}]}
        self.data = data
        self.main_brush_total = timedelta(hours=300)
        self.side_brush_total = timedelta(hours=200)
        self.filter_total = timedelta(hours=150)

    @property
    def main_brush(self) -> timedelta:
        return pretty_seconds(self.data["main_brush_work_time"])

    @property
    def main_brush_left(self) -> timedelta:
        return self.main_brush_total - self.main_brush

    @property
    def side_brush(self) -> timedelta:
        return pretty_seconds(self.data["side_brush_work_time"])

    @property
    def side_brush_left(self) -> timedelta:
        return self.side_brush_total - self.side_brush

    @property
    def filter(self) -> timedelta:
        return pretty_seconds(self.data["filter_work_time"])

    @property
    def filter_left(self) -> timedelta:
        return self.filter_total - self.filter

    @property
    def sensor_dirty(self) -> timedelta:
        return pretty_seconds(self.data["sensor_dirty_time"])

    def __str__(self) -> str:
        return "<ConsumableStatus main: %s, side: %s, filter: %s, sensor dirty: %s>" % (  # noqa: E501
            self.main_brush, self.side_brush, self.filter, self.sensor_dirty)


class Timer:
    def __init__(self, data: List[Any]) -> None:
        # id / timestamp, enabled, ['<cron string>', ['command', 'params']
        # [['1488667794112', 'off', ['49 22 * * 6', ['start_clean', '']]],
        #  ['1488667777661', 'off', ['49 21 * * 3,4,5,6', ['start_clean', '']]
        # ],
        self.data = data

    @property
    def id(self) -> int:
        return int(self.data[0])

    @property
    def ts(self) -> datetime:
        """Pretty id presentation as time."""
        return pretty_time(int(self.data[0] / 1000))

    @property
    def enabled(self) -> bool:
        return bool(self.data[1] == 'on')

    @property
    def cron(self) -> str:
        return str(self.data[2][0])

    @property
    def action(self) -> str:
        return str(self.data[2][1])
