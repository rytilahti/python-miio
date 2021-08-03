from unittest import TestCase

import pytest

from miio import G1Vacuum
from miio.g1vacuum import (
    G1ChargeState,
    G1FanSpeed,
    G1State,
    G1Status,
    G1VacuumMode,
    G1MopState,
    G1WaterLevel,
)

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "battery_level": 42,
    "charge_state": G1ChargeState.Charging,
    "error_code": 0,
    "state": G1State.Paused,
    "fan_speed": G1FanSpeed.Medium,
    "operating_mode": G1VacuumMode.GlobalClean,
    "mop_state": G1MopState.Off,
    "water_level": G1WaterLevel.Level1,
    "fan_speed": G1FanSpeed.Medium,
    "main_brush_time_left": 235,
    "main_brush_life_level": 85,
    "filter_life_level": 66,
    "filter_left_time": 154,
    "side_brush_life_left": 187,
    "side_brush_life_level": 57,
    "clean_area": 12,
    "clean_time": 17,
    "total_clean_area": 0,
    "total_clean_time": 0,
    "total_clean_count": 0,
 }

class DummyG1Vacuum(DummyMiotDevice, G1Vacuum):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def dummyg1vacuum(request):
    request.cls.device = DummyG1Vacuum()


@pytest.mark.usefixtures("dummyg1vacuum")
class TestG1Vacuum(TestCase):
    def test_status(self):
        status = self.device.status()
        assert status.battery == _INITIAL_STATE["battery"]
        assert status.error_code == _INITIAL_STATE["error_code"]
        assert status.main_brush_time_left == _INITIAL_STATE["main_brush_time_left"]
        assert status.side_brush_life_left == _INITIAL_STATE["side_brush_life_left"]
        assert status.side_brush_life_level == _INITIAL_STATE["side_brush_life_level"]
        assert status.main_brush_time_level == _INITIAL_STATE["main_brush_time_level"]
        assert status.filter_left_time == _INITIAL_STATE["filter_left_time"]
        assert status.filter_life_level == _INITIAL_STATE["filter_life_level"]
        assert status.clean_area == _INITIAL_STATE["clean_area"]
        assert status.clean_time == _INITIAL_STATE["clean_time"]
        assert status.total_clean_area == _INITIAL_STATE["total_clean_area"]
        assert status.total_clean_time == _INITIAL_STATE["total_clean_time"]
        assert status.total_clean_count == _INITIAL_STATE["total_clean_count"]
        assert status.charge_state == ChargingState(_INITIAL_STATE["charge_state"])
        assert repr(status.charge_state) == repr(
            ChargingState(_INITIAL_STATE["charge_state"])
        )
        assert status.fan_speed == G1FanSpeed(_INITIAL_STATE["fan_speed"])
        assert repr(status.fan_speed) == repr(
            G1FanSpeed(_INITIAL_STATE["fan_speed"])
        )
        assert status.state == G1State(_INITIAL_STATE["state"])
        assert repr(status.state) == repr(
            G1State(_INITIAL_STATE["state"])
        )
        assert status.operating_mode == G1VacuumMode(_INITIAL_STATE["operating_mode"])
        assert repr(status.operating_mode) == repr(
            G1VacuumMode(_INITIAL_STATE["operating_mode"])
        )
        assert status.mop_state == G1MopState(_INITIAL_STATE["mop_state"])
        assert repr(status.mop_state) == repr(
            G1MopState(_INITIAL_STATE["mop_state"])
        )
        assert status.water_level == G1WaterLevel(_INITIAL_STATE["water_level"])
        assert repr(status.water_level) == repr(
            G1WaterLevel(_INITIAL_STATE["water_level"])
        )