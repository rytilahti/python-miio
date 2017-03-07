# -*- coding: UTF-8 -*#
import datetime


def pretty_area(x):
    return int(x) / 1000000


def pretty_seconds(x):
    return datetime.timedelta(seconds=x)


def pretty_time(x):
    return datetime.datetime.fromtimestamp(x)


class VacuumStatus:
    """Container for status reports from the vacuum."""
    def __init__(self, data):
        # {'result': [{'state': 8, 'dnd_enabled': 1, 'clean_time': 0,
        #  'msg_ver': 4, 'map_present': 1, 'error_code': 0, 'in_cleaning': 0,
        #  'clean_area': 0, 'battery': 100, 'fan_power': 20, 'msg_seq': 320}], 'id': 1}
        self.data = data

    @property
    def state_code(self):
        return self.data["state"]

    @property
    def state(self):
        states = {
            1: 'Unknown 1',
            2: 'Unknown (unplugged charger?)',
            3: 'Unknown 3',
            5: 'Cleaning',
            6: 'Returning home',
            8: 'Charging',
            10: 'Paused',
            11: 'Spot cleaning',
            12: 'Unknown 12, error?!'
        }
        return states[int(self.state_code)]

    @property
    def error_code(self):
        return int(self.data["error_code"])

    @property
    def error(self):
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
        return error_codes[self.error_code]

    @property
    def battery(self):
        return self.data["battery"]

    @property
    def fanspeed(self):
        return self.data["fan_power"]

    @property
    def clean_time(self):
        return pretty_seconds(self.data["clean_time"])

    @property
    def clean_area(self):
        return pretty_area(self.data["clean_area"])

    @property
    def dnd(self):
        return self.data["dnd_enabled"]

    @property
    def map(self):
        return self.data["map_present"]

    @property
    def in_cleaning(self):
        return self.data["in_cleaning"]

    def __str__(self):
        s = "[%s, %s] " % (self.state, self.error)
        s += "[BAT: %s, FAN: %s%%] " % (self.battery, self.fanspeed)
        s += "[CLEAN: %s m² in %s]" % (self.clean_area, self.clean_time)
        return s

class CleaningSummary:
    """Cleaning summary."""
    def __init__(self, data):
        # unknown, unknown2, amount of cleans
        # [ list, of, ids ]
        # { "result": [ 174145, 2410150000, 82,
        # [ 1488240000, 1488153600, 1488067200, 1487980800, 1487894400, 1487808000, 1487548800 ] ], "id": 1 }
        self.data = data

    @property
    def count(self):
        return self.data[2]

    @property
    def ids(self):
        return self.data[3]

    def __str__(self):
        return "[SUMMARY: %s times, ids: %s]" % (self.count, self.ids)


class CleaningDetails:
    """Cleaning details."""
    def __init__(self, data):
        # start, end, duration, area, unk, complete
        # { "result": [ [ 1488347071, 1488347123, 16, 0, 0, 0 ] ], "id": 1 }
        self.data = data

    @property
    def start(self):
        return pretty_time(self.data[0])

    @property
    def end(self):
        return pretty_time(self.data[1])

    @property
    def duration(self):
        return pretty_seconds(self.data[2])

    @property
    def area(self):
        return pretty_area(self.data[3])

    @property
    def unknown(self):
        return self.data[4]

    @property
    def complete(self):
        return self.data[5] == 1


class ConsumableStatus:
    """Container for consumable status information."""
    def __init__(self, data):
        # {'id': 1, 'result': [{'filter_work_time': 32454,
        #  'sensor_dirty_time': 3798,
        # 'side_brush_work_time': 32454,
        #  'main_brush_work_time': 32454}]}
        self.data = data

    @property
    def main_brush(self):
        return pretty_seconds(self.data["main_brush_work_time"])

    @property
    def side_brush(self):
        return pretty_seconds(self.data["side_brush_work_time"])

    @property
    def filter(self):
        return pretty_seconds(self.data["filter_work_time"])

    @property
    def sensor_dirty(self):
        return pretty_seconds(self.data["sensor_dirty_time"])

    def __str__(self):
        return "main: %s, side: %s, filter: %s, sensor dirty: %s" % (
            self.main_brush, self.side_brush, self.filter, self.sensor_dirty)


class Timer:
    def __init__(self, data):
        # id / timestamp, enabled, ['<cron string>', ['command', 'params']
        # [['1488667794112', 'off', ['49 22 * * 6', ['start_clean', '']]],
        #  ['1488667777661', 'off', ['49 21 * * 3,4,5,6', ['start_clean', '']]],
        self.data = data

    @property
    def id(self):
        return int(self.data[0])

    @property
    def ts(self):
        """Pretty id presentation as time."""
        return pretty_time(int(self.data[0]) / 1000)

    @property
    def enabled(self):
        return self.data[1] == 'on'

    @property
    def cron(self):
        return self.data[2][0]


    @property
    def action(self):
        return self.data[2][1]