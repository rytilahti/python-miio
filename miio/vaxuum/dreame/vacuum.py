from typing import Optional, Union

import click
from miio.click_common import command
from miio.miot_device import MiotDevice, MiotMapping

import miio.vaxuum.base as basevacuum
from miio.vaxuum.base import BaseVacuum

from .containers import FanSpeed, VacuumState, ChargeStatus


_MAPPING: MiotMapping = {
    "battery_level": {"siid": 2, "piid": 1},
    "charging_state": {"siid": 2, "piid": 2},
    "device_fault": {"siid": 3, "piid": 1},
    "status": {"siid": 3, "piid": 2},

    "main_brush_left_time": {"siid": 26, "piid": 1},
    "main_brush_life_level": {"siid": 26, "piid": 2},
    "filter_life_level": {"siid": 27, "piid": 1},
    "filter_left_time": {"siid": 27, "piid": 2},
    "side_brush_left_time": {"siid": 28, "piid": 1},
    "side_brush_life_level": {"siid": 28, "piid": 2},

    "operating_mode": {"siid": 18, "piid": 1},
    "timer": {"siid": 18, "piid": 2},
    "area": {"siid": 18, "piid": 3},
    "fan_speed": {"siid": 18, "piid": 6},

    "delete_timer": {"siid": 18, "piid": 8, "access": ["write"]},

    "last_clean": {"siid": 18, "piid": 13},
    "total_clean_count": {"siid": 18, "piid": 14},
    "total_area": {"siid": 18, "piid": 15},

    "water_level": {"siid": 18, "piid": 20},

    "life_sieve": {"siid": 19, "piid": 1},
    "life_brush_side": {"siid": 19, "piid": 2},
    "life_brush_main": {"siid": 19, "piid": 3},

    "dnd_enabled": {"siid": 20, "piid": 1},
    "dnd_start_time": {"siid": 20, "piid": 2},
    "dnd_stop_time": {"siid": 20, "piid": 3},

    "remote_deg": {"siid": 21, "piid": 1, "access": ["write"]},
    "remote_speed": {"siid": 21, "piid": 2, "access": ["write"]},

    "map_view": {"siid": 23, "piid": 1},

    "audio_volume": {"siid": 24, "piid": 1},
    "audio_voice_package_id": {"siid": 24, "piid": 3},
}


class DreameStatus(basevacuum.VacuumStatus):
    def __init__(self, data):
        self.data = data

        self._battery_level = data.get('battery_level', 0)
        self._fan_speed = FanSpeed(data.get('fan_speed', 0))
        self._state = VacuumState(data.get('status', 0))
        self._charge_status = ChargeStatus(data.get('charging_state', 0))
        self._device_fault = data.get('device_fault', 0)

    @property
    def state(self) -> basevacuum.VacuumState:
        """Get current state """
        return self._state.as_base()

    @property
    def charge_status(self) -> basevacuum.ChargeStatus:
        """Get battery status """
        return self._charge_status.as_base()

    @property
    def battery_level(self) -> int:
        """Get battery percentage """
        return self._battery_level

    @property
    def fan_speed(self) -> basevacuum.FanSpeed:
        """ get current fan speed """
        return self._fan_speed.as_base()

    @property
    def cleaning_type(self) -> basevacuum.CleaningType:
        """ get current cleaning type """
        return basevacuum.CleaningType.UNKNOWN

    @property
    def error(self) -> Optional[str]:
        """ get current error, if any """
        if self._device_fault == 0:
            return None
        return str(self._device_fault)


class DreameVacuum(MiotDevice, BaseVacuum):
    """Support for dreame vacuum (1C STYTJ01ZHM, dreame.vacuum.mc1808)."""
    mapping = _MAPPING

    devices = [
        'dreame.vacuum.mc1808',
    ]

    def _call_action(self, siid, aiid, params=None):
        # {"did":"<mydeviceID>","siid":18,"aiid":1,"in":[{"piid":1,"value":2}]
        if params is None:
            params = []
        payload = {
            "did": f"call-{siid}-{aiid}",
            "siid": siid,
            "aiid": aiid,
            "in": params,
        }
        return self.send("action", payload)

    @command()
    def start(self):
        """Start cleaning"""
        payload = [{"piid": 1, "value": 2}]
        return self._call_action(18, 1, payload)

    @command()
    def stop(self):
        """Stop cleaning"""
        self._call_action(18, 2)

    @command()
    def pause(self):
        """Pause cleaning"""
        self._call_action(3, 2)

    @command()
    def resume(self):
        """Resume current cleaning process or start new process"""
        self._call_action(3, 1)

    @command(click.argument("speed", type=int))
    def set_fan_speed(self, speed: Union[int, basevacuum.FanSpeed]):
        """Set fan speed
        See .status for getting current speed

        :param speed: pass int for raw model-dependent value, or VacuumSpeed for common preset
        """
        if isinstance(speed, basevacuum.FanSpeed):
            speed = FanSpeed.from_base(speed).value
        elif isinstance(speed, FanSpeed):
            speed = speed.value

        return self.set_property(fan_speed=speed)

    @command()
    def return_to_dock(self):
        """Stop cleaning and return to dock."""
        return self._call_action(2, 1)

    @command()
    def status(self) -> DreameStatus:
        """Return current status of Vacuum"""
        return DreameStatus({
            prop["did"]: prop["value"] if prop["code"] == 0 else None
            for prop in self.get_properties_for_mapping(max_properties=14)
        })

    @command()
    def find(self):
        """Locate the vacuum """
        return self._call_action(17, 1)
