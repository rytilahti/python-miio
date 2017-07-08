import logging
import math
import time
from typing import List

from .containers import (VacuumStatus, ConsumableStatus,
                         CleaningSummary, CleaningDetails, Timer)
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class VacuumException(DeviceException):
    pass


class Vacuum(Device):
    """Main class representing the vacuum."""

    def __init__(self, ip: str, token: str, start_id: int = 0, debug: int = 0) -> None:
        super().__init__(ip, token, start_id, debug)
        self.manual_seqnum = -1

    def start(self):
        """Start cleaning."""
        return self.send("app_start")

    def stop(self):
        """Stop cleaning."""
        return self.send("app_stop")

    def spot(self):
        """Start spot cleaning."""
        return self.send("app_spot")

    def pause(self):
        """Pause cleaning."""
        return self.send("app_pause")

    def home(self):
        """Stop cleaning and return home."""
        self.send("app_stop")
        return self.send("app_charge")

    def manual_start(self):
        """Start manual control mode."""
        self.manual_seqnum = 0
        return self.send("app_rc_start")

    def manual_stop(self):
        """Stop manual control mode."""
        self.manual_seqnum = 0
        return self.send("app_rc_end")

    def manual_control_once(self, rotation: int, velocity: float, duration: int=1500):
        """Starts the remote control mode and executes the action once before deactivating the mode."""
        number_of_tries = 3
        self.manual_start()
        while number_of_tries > 0:
            if self.status().state_code == 7:
                time.sleep(5)
                self.manual_control(rotation, velocity, duration)
                time.sleep(5)
                return self.manual_stop()

            time.sleep(2)
            number_of_tries -= 1

    def manual_control(self, rotation: int, velocity: float, duration: int=1500):
        """Give a command over manual control interface."""
        if rotation <= -180 or rotation >= 180:
            raise DeviceException("Given rotation is invalid, should be ]-3.1,3.1[, was %s" % rotation)
        if velocity <= -0.3 or velocity >= 0.3:
            raise DeviceException("Given velocity is invalid, should be ]-0.3, 0.3[, was: %s" % velocity)


        self.manual_seqnum += 1
        params = {"omega": round(math.radians(rotation), 1),
                  "velocity": velocity,
                  "duration": duration,
                  "seqnum": self.manual_seqnum}

        self.send("app_rc_move", [params])

    def status(self) -> VacuumStatus:
        """Return status of the vacuum."""
        return VacuumStatus(self.send("get_status")[0])

    def log_upload_status(self):
        # {"result": [{"log_upload_status": 7}], "id": 1}
        return self.send("get_log_upload_status")

    def consumable_status(self) -> ConsumableStatus:
        """Return information about consumables."""
        return ConsumableStatus(self.send("get_consumable")[0])

    def map(self):
        """Return map token."""
        # returns ['retry'] without internet
        return self.send("get_map_v1")

    def clean_history(self) -> CleaningSummary:
        """Return generic cleaning history."""
        return CleaningSummary(self.send("get_clean_summary"))

    def clean_details(self, id_: int) -> List[CleaningDetails]:
        """Return details about specific cleaning."""
        details = self.send("get_clean_record", [id_])

        res = list()
        for rec in details:
            res.append(CleaningDetails(rec))

        return res

    def find(self):
        """Find the robot."""
        return self.send("find_me", [""])

    def timer(self) -> List[Timer]:
        """Return a list of timers."""
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
        """Returns do-not-disturb status."""
        # {'result': [{'enabled': 1, 'start_minute': 0, 'end_minute': 0,
        #  'start_hour': 22, 'end_hour': 8}], 'id': 1}
        return self.send("get_dnd_timer")

    def set_dnd(self, start_hr: int, start_min: int,
                end_hr: int, end_min: int):
        """Set do-not-disturb."""
        return self.send("set_dnd_timer",
                         [start_hr, start_min, end_hr, end_min])

    def disable_dnd(self):
        """Disable do-not-disturb."""
        return self.send("close_dnd_timer", [""])

    def set_fan_speed(self, speed: int):
        """Set fan speed."""
        # speed = [38, 60 or 77]
        return self.send("set_custom_mode", [speed])

    def fan_speed(self):
        """Return fan speed."""
        return self.send("get_custom_mode")[0]

    def raw_command(self, cmd, params):
        """Send a raw command to the robot."""
        return self.send(cmd, params)
