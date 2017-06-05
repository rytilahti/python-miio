import logging

from . import (VacuumStatus, ConsumableStatus,
                    CleaningSummary, CleaningDetails, Timer)
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

class VacuumException(DeviceException):
    pass

class Vacuum(Device):
    """Main class representing the vacuum."""

    def start(self):
        return self.send("app_start")

    def stop(self):
        return self.send("app_stop")

    def spot(self):
        return self.send("app_spot")

    def pause(self):
        return self.send("app_pause")

    def home(self):
        self.send("app_stop")
        return self.send("app_charge")

    def status(self):
        return VacuumStatus(self.send("get_status")[0])

    def log_upload_status(self):
        # {"result": [{"log_upload_status": 7}], "id": 1}
        return self.send("get_log_upload_status")

    def consumable_status(self):
        return ConsumableStatus(self.send("get_consumable")[0])

    def map(self):
        # returns ['retry'] without internet
        return self.send("get_map_v1")

    def clean_history(self):
        return CleaningSummary(self.send("get_clean_summary"))

    def clean_details(self, id_):
        details = self.send("get_clean_record", [id_])

        res = list()
        for rec in details:
            res.append(CleaningDetails(rec))

        return res

    def find(self):
        return self.send("find_me", [""])

    def timer(self):
        timers = list()
        for rec in self.send("get_timer", [""]):
            timers.append(Timer(rec))

        return timers

    def set_timer(self, details):
        # how to create timers/change values?
        # ['ts', 'on'] to enable
        raise NotImplementedError()
        return self.send("upd_timer", ["ts", "on"])

    def dnd_status(self):
        # {'result': [{'enabled': 1, 'start_minute': 0, 'end_minute': 0,
        #  'start_hour': 22, 'end_hour': 8}], 'id': 1}
        return self.send("get_dnd_timer")

    def set_dnd(self, start_hr, start_min, end_hr, end_min):
        return self.send("set_dnd_timer",
                         [start_hr, start_min, end_hr, end_min])

    def disable_dnd(self):
        return self.send("close_dnd_timer", [""])

    def set_fan_speed(self, speed):
        # speed = [38, 60 or 77]
        return self.send("set_custom_mode", [speed])

    def fan_speed(self):
        return self.send("get_custom_mode")[0]

    def raw_command(self, cmd, params):
        return self.send(cmd, params)
