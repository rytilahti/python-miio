from unittest import TestCase

import pytest

from miio import DreameVacuumMiot
from miio.dreamevacuum_miot import (
    ChargingState,
    CleaningMode,
    DeviceStatus,
    FaultStatus,
    OperatingMode,
)

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "battery_level": 42,
    "charging_state": ChargingState.Charging,
    "device_fault": FaultStatus.NoFaults,
    "device_status": DeviceStatus.Paused,
    "brush_left_time": 235,
    "brush_life_level": 85,
    "filter_life_level": 66,
    "filter_left_time": 154,
    "brush_left_time2": 187,
    "brush_life_level2": 57,
    "operating_mode": OperatingMode.Cleaning,
    "cleaning_mode": CleaningMode.Medium,
    "delete_timer": 12,
    "life_sieve": "9000-9000",
    "life_brush_side": "12000-12000",
    "life_brush_main": "18000-18000",
    "timer_enable": "false",
    "start_time": "22:00",
    "stop_time": "8:00",
    "deg": 5,
    "speed": 5,
    "map_view": "tmp",
    "frame_info": 3,
    "volume": 4,
    "voice_package": "DE",
}


class DummyDreameVacuumMiot(DummyMiotDevice, DreameVacuumMiot):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def dummydreamevacuum(request):
    request.cls.device = DummyDreameVacuumMiot()


@pytest.mark.usefixtures("dummydreamevacuum")
class TestDreameVacuum(TestCase):
    def test_status(self):
        status = self.device.status()
        assert status.battery_level == _INITIAL_STATE["battery_level"]
        assert status.brush_left_time == _INITIAL_STATE["brush_left_time"]
        assert status.brush_left_time2 == _INITIAL_STATE["brush_left_time2"]
        assert status.brush_life_level2 == _INITIAL_STATE["brush_life_level2"]
        assert status.brush_life_level == _INITIAL_STATE["brush_life_level"]
        assert status.filter_left_time == _INITIAL_STATE["filter_left_time"]
        assert status.filter_life_level == _INITIAL_STATE["filter_life_level"]
        assert status.device_fault == FaultStatus(_INITIAL_STATE["device_fault"])
        assert repr(status.device_fault) == repr(
            FaultStatus(_INITIAL_STATE["device_fault"])
        )
        assert status.charging_state == ChargingState(_INITIAL_STATE["charging_state"])
        assert repr(status.charging_state) == repr(
            ChargingState(_INITIAL_STATE["charging_state"])
        )
        assert status.operating_mode == OperatingMode(_INITIAL_STATE["operating_mode"])
        assert repr(status.operating_mode) == repr(
            OperatingMode(_INITIAL_STATE["operating_mode"])
        )
        assert status.cleaning_mode == CleaningMode(_INITIAL_STATE["cleaning_mode"])
        assert repr(status.cleaning_mode) == repr(
            CleaningMode(_INITIAL_STATE["cleaning_mode"])
        )
        assert status.device_status == DeviceStatus(_INITIAL_STATE["device_status"])
        assert repr(status.device_status) == repr(
            DeviceStatus(_INITIAL_STATE["device_status"])
        )
        assert status.life_sieve == _INITIAL_STATE["life_sieve"]
        assert status.life_brush_side == _INITIAL_STATE["life_brush_side"]
        assert status.life_brush_main == _INITIAL_STATE["life_brush_main"]
        assert status.timer_enable == _INITIAL_STATE["timer_enable"]
        assert status.start_time == _INITIAL_STATE["start_time"]
        assert status.stop_time == _INITIAL_STATE["stop_time"]
        assert status.map_view == _INITIAL_STATE["map_view"]
        assert status.volume == _INITIAL_STATE["volume"]
        assert status.voice_package == _INITIAL_STATE["voice_package"]
