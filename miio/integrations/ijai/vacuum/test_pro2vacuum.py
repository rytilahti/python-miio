import datetime
from unittest import TestCase

import pytest

from miio.tests.dummies import DummyMiotDevice

from .pro2vacuum import (
    ERROR_CODES,
    MI_ROBOT_VACUUM_MOP_PRO_2,
    DeviceState,
    FanSpeedMode,
    Pro2Vacuum,
    SweepMode,
    SweepType,
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
}


class DummyPRO2Vacuum(DummyMiotDevice, Pro2Vacuum):
    def __init__(self, *args, **kwargs):
        self._model = MI_ROBOT_VACUUM_MOP_PRO_2
        self.state = _INITIAL_STATE_PRO2
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
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
