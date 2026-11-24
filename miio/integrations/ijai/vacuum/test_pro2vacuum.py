import datetime
import json
from unittest import TestCase

import pytest

from miio.exceptions import DeviceException
from miio.tests.dummies import DummyMiotDevice

from .pro2vacuum import (
    ERROR_CODES,
    MI_ROBOT_VACUUM_MOP_PRO_2,
    Consumable,
    DeviceState,
    Direction,
    DoorState,
    FanSpeedMode,
    MopRoute,
    Pro2Vacuum,
    SweepMode,
    SweepType,
    TankShake,
    WaterLevel,
)

_INITIAL_STATE_PRO2 = {
    "state": DeviceState.Mopping,
    "error_code": 2105,
    "sweep_mode": SweepMode.SweepAndMop,
    "sweep_type": SweepType.Floor,
    "battery": 42,
    "mop_state": False,
    "fan_speed": FanSpeedMode.EnergySaving,
    "water_level": WaterLevel.High,
    "side_brush_life_level": 93,
    "side_brush_time_left": 14,
    "main_brush_life_level": 87,
    "main_brush_time_left": 15,
    "filter_life_level": 88,
    "filter_time_left": 12,
    "mop_life_level": 85,
    "mop_time_left": 10,
    "current_language": "en_US",
    "clean_time": 5,
    "clean_area": 8,
    "repeat_state": 0,
    "door_state": 1,
    "mop_route": 1,
    "time_zone": 18000,
    "tank_shake": 1,
    "shake_shift": 2,
    "volume": 7,
    "dnd_enable": 1,
    "dnd_start_hour": 20,
    "dnd_start_minute": 30,
    "dnd_end_hour": 9,
    "dnd_end_minute": 0,
    # map service (siid=10)
    "current_map_id": 1700000002,
    "map_count": 2,
    "has_new_map": 0,
}

_MAP_LIST = [
    {"name": "Floor 1", "id": 1700000001, "cur": False},
    {"name": "Floor 2", "id": 1700000002, "cur": True},
]


class DummyPRO2Vacuum(DummyMiotDevice, Pro2Vacuum):
    def __init__(self, *args, **kwargs):
        self._model = MI_ROBOT_VACUUM_MOP_PRO_2
        self.state = dict(_INITIAL_STATE_PRO2)
        super().__init__(*args, **kwargs)

    def call_action_by(self, siid, aiid, params=None):
        if (siid, aiid) == (10, 1):  # get-map-list
            return {"code": 0, "out": [{"piid": 4, "value": json.dumps(_MAP_LIST)}]}
        return super().call_action_by(siid, aiid, params)


@pytest.fixture
def dummypro2vacuum(request):
    request.cls.device = DummyPRO2Vacuum()


@pytest.mark.usefixtures("dummypro2vacuum")
class TestPro2Vacuum(TestCase):
    def test_status(self):
        status = self.device.status()
        assert status.clean_time == datetime.timedelta(
            minutes=_INITIAL_STATE_PRO2["clean_time"]
        )
        assert status.battery == _INITIAL_STATE_PRO2["battery"]
        assert status.error_code == _INITIAL_STATE_PRO2["error_code"]
        assert status.error == ERROR_CODES[_INITIAL_STATE_PRO2["error_code"]]
        assert status.state == _INITIAL_STATE_PRO2["state"]
        assert status.fan_speed == _INITIAL_STATE_PRO2["fan_speed"]
        assert status.sweep_type == _INITIAL_STATE_PRO2["sweep_type"]
        assert status.sweep_mode == _INITIAL_STATE_PRO2["sweep_mode"]
        assert status.mop_state == _INITIAL_STATE_PRO2["mop_state"]
        assert status.water_level == _INITIAL_STATE_PRO2["water_level"]
        assert (
            status.main_brush_life_level == _INITIAL_STATE_PRO2["main_brush_life_level"]
        )
        assert status.main_brush_time_left == datetime.timedelta(
            hours=_INITIAL_STATE_PRO2["main_brush_time_left"]
        )
        assert (
            status.side_brush_life_level == _INITIAL_STATE_PRO2["side_brush_life_level"]
        )
        assert status.side_brush_time_left == datetime.timedelta(
            hours=_INITIAL_STATE_PRO2["side_brush_time_left"]
        )
        assert status.filter_life_level == _INITIAL_STATE_PRO2["filter_life_level"]
        assert status.filter_time_left == datetime.timedelta(
            hours=_INITIAL_STATE_PRO2["filter_time_left"]
        )
        assert status.mop_life_level == _INITIAL_STATE_PRO2["mop_life_level"]
        assert status.mop_time_left == datetime.timedelta(
            hours=_INITIAL_STATE_PRO2["mop_time_left"]
        )
        assert status.clean_area == _INITIAL_STATE_PRO2["clean_area"]
        assert status.clean_time == datetime.timedelta(
            minutes=_INITIAL_STATE_PRO2["clean_time"]
        )
        assert status.current_language == _INITIAL_STATE_PRO2["current_language"]

    def test_map_status(self):
        status = self.device.map_status()
        assert status.current_map_id == _INITIAL_STATE_PRO2["current_map_id"]
        assert status.map_count == _INITIAL_STATE_PRO2["map_count"]
        assert status.has_new_map is False

    def test_get_maps(self):
        maps = self.device.get_maps()
        assert maps == _MAP_LIST
        assert [m["id"] for m in maps if m["cur"]] == [
            _INITIAL_STATE_PRO2["current_map_id"]
        ]

    def _record_actions(self):
        calls = []
        self.device.call_action_by = lambda siid, aiid, params=None: calls.append(
            (siid, aiid, params)
        )
        return calls

    def test_start_modes(self):
        calls = self._record_actions()
        self.device.start_sweep()
        self.device.start_sweep_mop()
        self.device.start_mop()
        assert calls == [(2, 3, None), (2, 5, None), (2, 6, None)]

    def test_start_rooms(self):
        calls = self._record_actions()
        self.device.start_rooms([10, 12])
        assert calls == [(2, 7, [{"piid": 10, "value": "10,12"}])]

    def test_start_rooms_requires_rooms(self):
        calls = self._record_actions()
        with pytest.raises(ValueError):
            self.device.start_rooms([])
        assert calls == []

    def test_get_maps_unexpected_response(self):
        self.device.call_action_by = lambda *args, **kwargs: {"code": 0}
        with pytest.raises(DeviceException):
            self.device.get_maps()

    def test_fanspeed_presets(self):
        presets = self.device.fan_speed_presets()
        for item in FanSpeedMode:
            assert item.name in presets
            assert presets[item.name] == item.value

    def test_set_fan_speed_preset(self):
        for speed in self.device.fan_speed_presets().values():
            self.device.set_fan_speed_preset(speed)
            status = self.device.status()
            assert status.fan_speed == FanSpeedMode(speed)

    def test_set_fan_speed(self):
        for speed in self.device.fan_speed_presets().values():
            self.device.set_fan_speed(speed)
            status = self.device.status()
            assert status.fan_speed == FanSpeedMode(speed)

    def test_extended_status(self):
        status = self.device.status()
        assert status.repeat_state is False
        assert status.door_state == DoorState.DustBox
        assert status.mop_route == MopRoute.YStyle
        assert status.time_zone == 18000
        assert status.tank_shake is True
        assert status.shake_shift == TankShake.Medium
        assert status.volume == 7
        assert status.dnd_enabled is True
        assert status.dnd_start == datetime.time(20, 30)
        assert status.dnd_end == datetime.time(9, 0)

    def test_setters(self):
        self.device.set_sweep_mode(SweepMode.Mop)
        self.device.set_water_level(WaterLevel.Low)
        self.device.set_mop_route(MopRoute.BowStyle)
        self.device.set_repeat(True)
        self.device.set_tank_shake(False)
        self.device.set_tank_shake_level(TankShake.High)
        self.device.set_volume(3)
        status = self.device.status()
        assert status.sweep_mode == SweepMode.Mop
        assert status.water_level == WaterLevel.Low
        assert status.mop_route == MopRoute.BowStyle
        assert status.repeat_state is True
        assert status.tank_shake is False
        assert status.shake_shift == TankShake.High
        assert status.volume == 3

    def test_volume_out_of_range(self):
        # The CLI validates the range; the python API passes the value through.
        self.device.set_volume(10)
        assert self.device.status().volume == 10

    def test_locate_and_manual_control(self):
        calls = []
        self.device.set_property_by = lambda siid, piid, value, *a, **k: calls.append(
            (siid, piid, value)
        )
        self.device.locate()
        self.device.manual_control(Direction.Forward)
        self.device.manual_control(Direction.Exit)
        assert calls == [(4, 1, 1), (7, 16, 1), (7, 16, 10)]

    def test_reset_consumable(self):
        calls = self._record_actions()
        self.device.reset_consumable(Consumable.Filter)
        assert calls == [(7, 1, [{"piid": 17, "value": 3}])]

    def test_set_dnd(self):
        calls = self._record_actions()
        self.device.set_dnd(False, datetime.time(21, 15), datetime.time(7, 5))
        self.device.set_dnd(True)  # keeps the configured times
        assert calls == [
            (
                12,
                1,
                [
                    {"piid": 1, "value": 0},
                    {"piid": 2, "value": 21},
                    {"piid": 3, "value": 15},
                    {"piid": 4, "value": 7},
                    {"piid": 5, "value": 5},
                    {"piid": 6, "value": 18000},
                ],
            ),
            (
                12,
                1,
                [
                    {"piid": 1, "value": 1},
                    {"piid": 2, "value": 20},
                    {"piid": 3, "value": 30},
                    {"piid": 4, "value": 9},
                    {"piid": 5, "value": 0},
                    {"piid": 6, "value": 18000},
                ],
            ),
        ]
