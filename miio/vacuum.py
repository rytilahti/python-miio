import logging
import math
import time
from typing import List
import enum
import datetime
import pytz

from .vacuumcontainers import (VacuumStatus, ConsumableStatus, DNDStatus,
                               CleaningSummary, CleaningDetails, Timer,
                               SoundStatus, SoundInstallStatus)
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class VacuumException(DeviceException):
    pass


class TimerState(enum.Enum):
    On = "on"
    Off = "off"


class Consumable(enum.Enum):
    MainBrush = "main_brush_work_time"
    SideBrush = "side_brush_work_time"
    Filter = "filter_work_time"
    SensorDirty = "sensor_dirty_time"


class Vacuum(Device):
    """Main class representing the vacuum."""

    def __init__(self, ip: str, token: str = None, start_id: int = 0,
                 debug: int = 0) -> None:
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

    def manual_control_once(
            self, rotation: int, velocity: float, duration: int=1500):
        """Starts the remote control mode and executes
        the action once before deactivating the mode."""
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

    def manual_control(self, rotation: int, velocity: float,
                       duration: int=1500):
        """Give a command over manual control interface."""
        if rotation < -180 or rotation > 180:
            raise DeviceException("Given rotation is invalid, should "
                                  "be ]-180, 180[, was %s" % rotation)
        if velocity < -0.3 or velocity > 0.3:
            raise DeviceException("Given velocity is invalid, should "
                                  "be ]-0.3, 0.3[, was: %s" % velocity)

        self.manual_seqnum += 1
        params = {"omega": round(math.radians(rotation), 1),
                  "velocity": velocity,
                  "duration": duration,
                  "seqnum": self.manual_seqnum}

        self.send("app_rc_move", [params])

    def status(self) -> VacuumStatus:
        """Return status of the vacuum."""
        return VacuumStatus(self.send("get_status")[0])

    def enable_log_upload(self):
        raise NotImplementedError("unknown parameters")
        # return self.send("enable_log_upload")

    def log_upload_status(self):
        # {"result": [{"log_upload_status": 7}], "id": 1}
        return self.send("get_log_upload_status")

    def consumable_status(self) -> ConsumableStatus:
        """Return information about consumables."""
        return ConsumableStatus(self.send("get_consumable")[0])

    def consumable_reset(self, consumable: Consumable):
        """Reset consumable information."""
        return self.send("reset_consumable", [consumable.value])

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

    def add_timer(self, cron: str, command: str, parameters: str):
        """Add a timer.

        :param cron: schedule in cron format
        :param command: ignored by the vacuum.
        :param parameters: ignored by the vacuum."""
        import time
        ts = int(round(time.time() * 1000))
        return self.send("set_timer", [
            [str(ts), [cron, [command, parameters]]]
        ])

    def delete_timer(self, timer_id: int):
        """Delete a timer with given ID.

        :param int timer_id: Timer ID"""
        return self.send("del_timer", [str(timer_id)])

    def update_timer(self, timer_id: int, mode: TimerState):
        """Update a timer with given ID.

        :param int timer_id: Timer ID
        :param TimerStae mode: either On or Off"""
        if mode != TimerState.On and mode != TimerState.Off:
            raise DeviceException("Only 'On' or 'Off' are  allowed")
        return self.send("upd_timer", [str(timer_id), mode.value])

    def dnd_status(self):
        """Returns do-not-disturb status."""
        # {'result': [{'enabled': 1, 'start_minute': 0, 'end_minute': 0,
        #  'start_hour': 22, 'end_hour': 8}], 'id': 1}
        return DNDStatus(self.send("get_dnd_timer")[0])

    def set_dnd(self, start_hr: int, start_min: int,
                end_hr: int, end_min: int):
        """Set do-not-disturb.

        :param int start_hr: Start hour
        :param int start_min: Start minute
        :param int end_hr: End hour
        :param int end_min: End minute"""
        return self.send("set_dnd_timer",
                         [start_hr, start_min, end_hr, end_min])

    def disable_dnd(self):
        """Disable do-not-disturb."""
        return self.send("close_dnd_timer", [""])

    def set_fan_speed(self, speed: int):
        """Set fan speed.

        :param int speed: Fan speed to set"""
        # speed = [38, 60 or 77]
        return self.send("set_custom_mode", [speed])

    def fan_speed(self):
        """Return fan speed."""
        return self.send("get_custom_mode")[0]

    def sound_info(self):
        """Get voice settings."""
        return SoundStatus(self.send("get_current_sound")[0])

    def install_sound(self, url: str, md5sum: str, sound_id: int):
        """Install sound from the given url."""
        payload = {
            "url": url,
            "md5": md5sum,
            "sid": int(sound_id),
        }
        return SoundInstallStatus(self.send("dnld_install_sound", payload)[0])

    def sound_install_progress(self):
        """Get sound installation progress."""
        return SoundInstallStatus(self.send("get_sound_progress")[0])

    def sound_volume(self) -> int:
        """Get sound volume."""
        return self.send("get_sound_volume")[0]

    def set_sound_volume(self, vol: int):
        """Set sound volume [0-100]."""
        return self.send("change_sound_volume", [vol])

    def test_sound_volume(self):
        """Test current sound volume."""
        return self.send("test_sound_volume")

    def serial_number(self):
        """Get serial number."""
        return self.send("get_serial_number")[0]["serial_number"]

    def timezone(self):
        """Get the timezone."""
        return self.send("get_timezone")[0]

    def set_timezone(self, new_zone):
        """Set the timezone."""
        return self.send("set_timezone", [new_zone])[0] == 'ok'

    def configure_wifi(self, ssid, password, uid=0, timezone=None):
        """Configure the wifi settings."""
        extra_params = {}
        if timezone is not None:
            now = datetime.datetime.now(pytz.timezone(timezone))
            offset_as_float = now.utcoffset().total_seconds() / 60 / 60
            extra_params["tz"] = timezone
            extra_params["gmt_offset"] = offset_as_float

        return super().configure_wifi(ssid, password, uid, extra_params)

    def raw_command(self, cmd, params):
        """Send a raw command to the robot."""
        return self.send(cmd, params)
