import datetime
import enum
import json
import logging
import math
import os
import pathlib
import time
from typing import List, Optional, Union

import click
import pytz
from appdirs import user_cache_dir

from .click_common import (
    DeviceGroup, command, GlobalContextObject, LiteralParamType
)
from .device import Device, DeviceException
from .vacuumcontainers import (VacuumStatus, ConsumableStatus, DNDStatus,
                               CleaningSummary, CleaningDetails, Timer,
                               SoundStatus, SoundInstallStatus, CarpetModeStatus)

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

    @command()
    def start(self):
        """Start cleaning."""
        return self.send("app_start")

    @command()
    def stop(self):
        """Stop cleaning.

        Note, prefer 'pause' instead of this for wider support.
        Some newer vacuum models do not support this command.
        """
        return self.send("app_stop")

    @command()
    def spot(self):
        """Start spot cleaning."""
        return self.send("app_spot")

    @command()
    def pause(self):
        """Pause cleaning."""
        return self.send("app_pause")

    @command()
    def home(self):
        """Stop cleaning and return home."""
        self.send("app_pause")
        return self.send("app_charge")

    @command(
        click.argument("x_coord", type=int),
        click.argument("y_coord", type=int),
    )
    def goto(self, x_coord: int, y_coord: int):
        """Go to specific target.
        :param int x_coord: x coordinate
        :param int y_coord: y coordinate"""
        return self.send("app_goto_target", [x_coord, y_coord])

    @command(
        click.argument("zones", type=LiteralParamType(), required=True),
    )
    def zoned_clean(self, zones: List):
        """Clean zones.
        :param List zones: List of zones to clean: [[x1,y1,x2,y2, iterations],[x1,y1,x2,y2, iterations]]"""
        return self.send("app_zoned_clean", zones)

    @command()
    def manual_start(self):
        """Start manual control mode."""
        self.manual_seqnum = 0
        return self.send("app_rc_start")

    @command()
    def manual_stop(self):
        """Stop manual control mode."""
        self.manual_seqnum = 0
        return self.send("app_rc_end")

    @command(
        click.argument("rotation", type=int),
        click.argument("velocity", type=float),
        click.argument("duration", type=int, required=False, default=1500)
    )
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

    @command(
        click.argument("rotation", type=int),
        click.argument("velocity", type=float),
        click.argument("duration", type=int, required=False, default=1500)
    )
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

    @command()
    def status(self) -> VacuumStatus:
        """Return status of the vacuum."""
        return VacuumStatus(self.send("get_status")[0])

    def enable_log_upload(self):
        raise NotImplementedError("unknown parameters")
        # return self.send("enable_log_upload")

    @command()
    def log_upload_status(self):
        # {"result": [{"log_upload_status": 7}], "id": 1}
        return self.send("get_log_upload_status")

    @command()
    def consumable_status(self) -> ConsumableStatus:
        """Return information about consumables."""
        return ConsumableStatus(self.send("get_consumable")[0])

    @command(
        click.argument("consumable", type=Consumable),
    )
    def consumable_reset(self, consumable: Consumable):
        """Reset consumable information."""
        return self.send("reset_consumable", [consumable.value])

    @command()
    def map(self):
        """Return map token."""
        # returns ['retry'] without internet
        return self.send("get_map_v1")

    @command()
    def clean_history(self) -> CleaningSummary:
        """Return generic cleaning history."""
        return CleaningSummary(self.send("get_clean_summary"))

    @command()
    def last_clean_details(self) -> CleaningDetails:
        """Return details from the last cleaning."""
        last_clean_id = self.clean_history().ids.pop(0)
        return self.clean_details(last_clean_id, return_list=False)

    @command(
        click.argument("id_", type=int, metavar="ID"),
        click.argument("return_list", type=bool, default=False)
    )
    def clean_details(self, id_: int, return_list=True) -> Union[
            List[CleaningDetails],
            Optional[CleaningDetails]]:
        """Return details about specific cleaning."""
        details = self.send("get_clean_record", [id_])

        if not details:
            _LOGGER.warning("No cleaning record found for id %s" % id_)
            return None

        if return_list:
            _LOGGER.warning("This method will be returning the details "
                            "without wrapping them into a list in the "
                            "near future. The current behavior can be "
                            "kept by passing return_list=True and this "
                            "warning will be removed when the default gets "
                            "changed.")
            return [CleaningDetails(entry) for entry in details]

        if len(details) > 1:
            _LOGGER.warning("Got multiple clean details, returning the first")

        res = CleaningDetails(details.pop())
        return res

    @command()
    def find(self):
        """Find the robot."""
        return self.send("find_me", [""])

    @command()
    def timer(self) -> List[Timer]:
        """Return a list of timers."""
        timers = list()
        for rec in self.send("get_timer", [""]):
            timers.append(Timer(rec))

        return timers

    @command(
        click.argument("cron"),
        click.argument("command", required=False, default=""),
        click.argument("parameters", required=False, default=""),
    )
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

    @command(
        click.argument("timer_id", type=int),
    )
    def delete_timer(self, timer_id: int):
        """Delete a timer with given ID.

        :param int timer_id: Timer ID"""
        return self.send("del_timer", [str(timer_id)])

    @command(
        click.argument("timer_id", type=int),
        click.argument("mode", type=TimerState),
    )
    def update_timer(self, timer_id: int, mode: TimerState):
        """Update a timer with given ID.

        :param int timer_id: Timer ID
        :param TimerStae mode: either On or Off"""
        if mode != TimerState.On and mode != TimerState.Off:
            raise DeviceException("Only 'On' or 'Off' are  allowed")
        return self.send("upd_timer", [str(timer_id), mode.value])

    @command()
    def dnd_status(self):
        """Returns do-not-disturb status."""
        # {'result': [{'enabled': 1, 'start_minute': 0, 'end_minute': 0,
        #  'start_hour': 22, 'end_hour': 8}], 'id': 1}
        return DNDStatus(self.send("get_dnd_timer")[0])

    @command(
        click.argument("start_hr", type=int),
        click.argument("start_min", type=int),
        click.argument("end_hr", type=int),
        click.argument("end_min", type=int),
    )
    def set_dnd(self, start_hr: int, start_min: int,
                end_hr: int, end_min: int):
        """Set do-not-disturb.

        :param int start_hr: Start hour
        :param int start_min: Start minute
        :param int end_hr: End hour
        :param int end_min: End minute"""
        return self.send("set_dnd_timer",
                         [start_hr, start_min, end_hr, end_min])

    @command()
    def disable_dnd(self):
        """Disable do-not-disturb."""
        return self.send("close_dnd_timer", [""])

    @command(
        click.argument("speed", type=int),
    )
    def set_fan_speed(self, speed: int):
        """Set fan speed.

        :param int speed: Fan speed to set"""
        # speed = [38, 60 or 77]
        return self.send("set_custom_mode", [speed])

    @command()
    def fan_speed(self):
        """Return fan speed."""
        return self.send("get_custom_mode")[0]

    @command()
    def sound_info(self):
        """Get voice settings."""
        return SoundStatus(self.send("get_current_sound")[0])

    @command(
        click.argument("url"),
        click.argument("md5sum"),
        click.argument("sound_id", type=int),
    )
    def install_sound(self, url: str, md5sum: str, sound_id: int):
        """Install sound from the given url."""
        payload = {
            "url": url,
            "md5": md5sum,
            "sid": int(sound_id),
        }
        return SoundInstallStatus(self.send("dnld_install_sound", payload)[0])

    @command()
    def sound_install_progress(self):
        """Get sound installation progress."""
        return SoundInstallStatus(self.send("get_sound_progress")[0])

    @command()
    def sound_volume(self) -> int:
        """Get sound volume."""
        return self.send("get_sound_volume")[0]

    @command(
        click.argument("vol", type=int),
    )
    def set_sound_volume(self, vol: int):
        """Set sound volume [0-100]."""
        return self.send("change_sound_volume", [vol])

    @command()
    def test_sound_volume(self):
        """Test current sound volume."""
        return self.send("test_sound_volume")

    @command()
    def serial_number(self):
        """Get serial number."""
        serial = self.send("get_serial_number")
        if isinstance(serial, list):
            return serial[0]["serial_number"]
        return serial

    @command()
    def locale(self):
        """Return locale information."""
        return self.send("app_get_locale")

    @command()
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

    @command()
    def carpet_mode(self):
        """Get carpet mode settings"""
        return CarpetModeStatus(self.send("get_carpet_mode")[0])

    @command(
        click.argument("enabled", required=True, type=bool),
        click.argument("stall_time", required=False, default=10, type=int),
        click.argument("low", required=False, default=400, type=int),
        click.argument("high", required=False, default=500, type=int),
        click.argument("integral", required=False, default=450, type=int)
    )
    def set_carpet_mode(self, enabled: bool, stall_time: int = 10,
                        low: int = 400, high: int = 500, integral: int = 450):
        """Set the carpet mode."""
        click.echo("Setting carpet mode: %s" % enabled)
        data = {
            'enable': int(enabled),
            'stall_time': stall_time,
            'current_low': low,
            'current_high': high,
            'current_integral': integral,
        }
        return self.send("set_carpet_mode", [data])[0] == 'ok'

    @classmethod
    def get_device_group(cls):

        @click.pass_context
        def callback(ctx, *args, id_file, **kwargs):
            gco = ctx.find_object(GlobalContextObject)
            if gco:
                kwargs['debug'] = gco.debug

            start_id = manual_seq = 0
            try:
                with open(id_file, 'r') as f:
                    x = json.load(f)
                    start_id = x.get("seq", 0)
                    manual_seq = x.get("manual_seq", 0)
                    _LOGGER.debug("Read stored sequence ids: %s", x)
            except (FileNotFoundError, TypeError, ValueError):
                pass

            ctx.obj = cls(*args, start_id=start_id, **kwargs)
            ctx.obj.manual_seqnum = manual_seq

        dg = DeviceGroup(cls, params=DeviceGroup.DEFAULT_PARAMS + [
            click.Option(
                ['--id-file'], type=click.Path(dir_okay=False, writable=True),
                default=os.path.join(
                    user_cache_dir('python-miio'),
                    'python-mirobo.seq'
                )
            ),
        ], callback=callback)

        @dg.resultcallback()
        @dg.device_pass
        def cleanup(vac: Vacuum, *args, **kwargs):
            if vac.ip is None:  # dummy Device for discovery, skip teardown
                return
            id_file = kwargs['id_file']
            seqs = {'seq': vac.raw_id, 'manual_seq': vac.manual_seqnum}
            _LOGGER.debug("Writing %s to %s", seqs, id_file)
            path_obj = pathlib.Path(id_file)
            cache_dir = path_obj.parents[0]
            try:
                cache_dir.mkdir(parents=True)
            except FileExistsError:
                pass  # after dropping py3.4 support, use exist_ok for mkdir
            with open(id_file, 'w') as f:
                json.dump(seqs, f)

        return dg
