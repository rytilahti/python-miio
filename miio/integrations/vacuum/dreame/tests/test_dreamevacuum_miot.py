from unittest import TestCase

import pytest

from miio import DreameVacuum
from miio.tests.dummies import DummyMiotDevice

from ..dreamevacuum_miot import (
    DREAME_1C,
    DREAME_F9,
    MIOT_MAPPING,
    ChargingState,
    CleaningModeDreame1C,
    CleaningModeDreameF9,
    DeviceStatus,
    FaultStatus,
    OperatingMode,
    WaterFlow,
)

_INITIAL_STATE_1C = {
    "battery_level": 42,
    "charging_state": 1,
    "device_fault": 0,
    "device_status": 3,
    "brush_left_time": 235,
    "brush_life_level": 85,
    "filter_life_level": 66,
    "filter_left_time": 154,
    "brush_left_time2": 187,
    "brush_life_level2": 57,
    "operating_mode": 2,
    "cleaning_mode": 2,
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
    "timezone": "Europe/London",
    "cleaning_time": 10,
    "cleaning_area": 20,
    "first_clean_time": 1640854830,
    "total_clean_time": 1000,
    "total_clean_times": 15,
    "total_clean_area": 500,
}


_INITIAL_STATE_F9 = {
    "battery_level": 42,
    "charging_state": 1,
    "device_fault": 0,
    "device_status": 3,
    "brush_left_time": 235,
    "brush_life_level": 85,
    "filter_life_level": 66,
    "filter_left_time": 154,
    "brush_left_time2": 187,
    "brush_life_level2": 57,
    "operating_mode": 2,
    "cleaning_mode": 1,
    "delete_timer": 12,
    "timer_enable": "false",
    "start_time": "22:00",
    "stop_time": "8:00",
    "map_view": "tmp",
    "frame_info": 3,
    "volume": 4,
    "voice_package": "DE",
    "water_flow": 2,
    "water_box_carriage_status": 1,
    "timezone": "Europe/London",
    "cleaning_time": 10,
    "cleaning_area": 20,
    "first_clean_time": 1640854830,
    "total_clean_time": 1000,
    "total_clean_times": 15,
    "total_clean_area": 500,
}


class DummyDreame1CVacuumMiot(DummyMiotDevice, DreameVacuum):
    def __init__(self, *args, **kwargs):
        self._model = DREAME_1C
        self.state = _INITIAL_STATE_1C
        super().__init__(*args, **kwargs)


class DummyDreameF9VacuumMiot(DummyMiotDevice, DreameVacuum):
    def __init__(self, *args, **kwargs):
        self._model = DREAME_F9
        self.state = _INITIAL_STATE_F9
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def dummydreame1cvacuum(request):
    request.cls.device = DummyDreame1CVacuumMiot()


@pytest.fixture(scope="function")
def dummydreamef9vacuum(request):
    request.cls.device = DummyDreameF9VacuumMiot()


@pytest.mark.usefixtures("dummydreame1cvacuum")
class TestDreame1CVacuum(TestCase):
    def test_status(self):
        status = self.device.status()
        assert status.battery_level == _INITIAL_STATE_1C["battery_level"]
        assert status.brush_left_time == _INITIAL_STATE_1C["brush_left_time"]
        assert status.brush_left_time2 == _INITIAL_STATE_1C["brush_left_time2"]
        assert status.brush_life_level2 == _INITIAL_STATE_1C["brush_life_level2"]
        assert status.brush_life_level == _INITIAL_STATE_1C["brush_life_level"]
        assert status.filter_left_time == _INITIAL_STATE_1C["filter_left_time"]
        assert status.filter_life_level == _INITIAL_STATE_1C["filter_life_level"]
        assert status.timezone == _INITIAL_STATE_1C["timezone"]
        assert status.cleaning_time == _INITIAL_STATE_1C["cleaning_time"]
        assert status.cleaning_area == _INITIAL_STATE_1C["cleaning_area"]
        assert status.first_clean_time == _INITIAL_STATE_1C["first_clean_time"]
        assert status.total_clean_time == _INITIAL_STATE_1C["total_clean_time"]
        assert status.total_clean_times == _INITIAL_STATE_1C["total_clean_times"]
        assert status.total_clean_area == _INITIAL_STATE_1C["total_clean_area"]

        assert status.device_fault == FaultStatus(_INITIAL_STATE_1C["device_fault"])
        assert repr(status.device_fault) == repr(
            FaultStatus(_INITIAL_STATE_1C["device_fault"])
        )
        assert status.charging_state == ChargingState(
            _INITIAL_STATE_1C["charging_state"]
        )
        assert repr(status.charging_state) == repr(
            ChargingState(_INITIAL_STATE_1C["charging_state"])
        )
        assert status.operating_mode == OperatingMode(
            _INITIAL_STATE_1C["operating_mode"]
        )
        assert repr(status.operating_mode) == repr(
            OperatingMode(_INITIAL_STATE_1C["operating_mode"])
        )
        assert status.cleaning_mode == CleaningModeDreame1C(
            _INITIAL_STATE_1C["cleaning_mode"]
        )
        assert repr(status.cleaning_mode) == repr(
            CleaningModeDreame1C(_INITIAL_STATE_1C["cleaning_mode"])
        )
        assert status.device_status == DeviceStatus(_INITIAL_STATE_1C["device_status"])
        assert repr(status.device_status) == repr(
            DeviceStatus(_INITIAL_STATE_1C["device_status"])
        )
        assert status.life_sieve == _INITIAL_STATE_1C["life_sieve"]
        assert status.life_brush_side == _INITIAL_STATE_1C["life_brush_side"]
        assert status.life_brush_main == _INITIAL_STATE_1C["life_brush_main"]
        assert status.timer_enable == _INITIAL_STATE_1C["timer_enable"]
        assert status.start_time == _INITIAL_STATE_1C["start_time"]
        assert status.stop_time == _INITIAL_STATE_1C["stop_time"]
        assert status.map_view == _INITIAL_STATE_1C["map_view"]
        assert status.volume == _INITIAL_STATE_1C["volume"]
        assert status.voice_package == _INITIAL_STATE_1C["voice_package"]

    def test_fanspeed_presets(self):
        presets = self.device.fan_speed_presets()
        for item in CleaningModeDreame1C:
            assert item.name in presets
            assert presets[item.name] == item.value

    def test_fan_speed(self):
        value = self.device.fan_speed()
        assert value == {"Medium": 2}

    def test_set_fan_speed_preset(self):
        for speed in self.device.fan_speed_presets().values():
            self.device.set_fan_speed_preset(speed)


@pytest.mark.usefixtures("dummydreamef9vacuum")
class TestDreameF9Vacuum(TestCase):
    def test_status(self):
        status = self.device.status()
        assert status.battery_level == _INITIAL_STATE_F9["battery_level"]
        assert status.brush_left_time == _INITIAL_STATE_F9["brush_left_time"]
        assert status.brush_left_time2 == _INITIAL_STATE_F9["brush_left_time2"]
        assert status.brush_life_level2 == _INITIAL_STATE_F9["brush_life_level2"]
        assert status.brush_life_level == _INITIAL_STATE_F9["brush_life_level"]
        assert status.filter_left_time == _INITIAL_STATE_F9["filter_left_time"]
        assert status.filter_life_level == _INITIAL_STATE_F9["filter_life_level"]
        assert status.water_flow == WaterFlow(_INITIAL_STATE_F9["water_flow"])
        assert status.timezone == _INITIAL_STATE_F9["timezone"]
        assert status.cleaning_time == _INITIAL_STATE_1C["cleaning_time"]
        assert status.cleaning_area == _INITIAL_STATE_1C["cleaning_area"]
        assert status.first_clean_time == _INITIAL_STATE_1C["first_clean_time"]
        assert status.total_clean_time == _INITIAL_STATE_1C["total_clean_time"]
        assert status.total_clean_times == _INITIAL_STATE_1C["total_clean_times"]
        assert status.total_clean_area == _INITIAL_STATE_1C["total_clean_area"]
        assert status.is_water_box_carriage_attached
        assert status.device_fault == FaultStatus(_INITIAL_STATE_F9["device_fault"])
        assert repr(status.device_fault) == repr(
            FaultStatus(_INITIAL_STATE_F9["device_fault"])
        )
        assert status.charging_state == ChargingState(
            _INITIAL_STATE_F9["charging_state"]
        )
        assert repr(status.charging_state) == repr(
            ChargingState(_INITIAL_STATE_F9["charging_state"])
        )
        assert status.operating_mode == OperatingMode(
            _INITIAL_STATE_F9["operating_mode"]
        )
        assert repr(status.operating_mode) == repr(
            OperatingMode(_INITIAL_STATE_F9["operating_mode"])
        )
        assert status.cleaning_mode == CleaningModeDreameF9(
            _INITIAL_STATE_F9["cleaning_mode"]
        )
        assert repr(status.cleaning_mode) == repr(
            CleaningModeDreameF9(_INITIAL_STATE_F9["cleaning_mode"])
        )
        assert status.device_status == DeviceStatus(_INITIAL_STATE_F9["device_status"])
        assert repr(status.device_status) == repr(
            DeviceStatus(_INITIAL_STATE_F9["device_status"])
        )
        assert status.timer_enable == _INITIAL_STATE_F9["timer_enable"]
        assert status.start_time == _INITIAL_STATE_F9["start_time"]
        assert status.stop_time == _INITIAL_STATE_F9["stop_time"]
        assert status.map_view == _INITIAL_STATE_F9["map_view"]
        assert status.volume == _INITIAL_STATE_F9["volume"]
        assert status.voice_package == _INITIAL_STATE_F9["voice_package"]

    def test_fanspeed_presets(self):
        presets = self.device.fan_speed_presets()
        for item in CleaningModeDreameF9:
            assert item.name in presets
            assert presets[item.name] == item.value

    def test_fan_speed(self):
        value = self.device.fan_speed()
        assert value == {"Standart": 1}

    def test_waterflow_presets(self):
        presets = self.device.waterflow_presets()
        for item in WaterFlow:
            assert item.name in presets
            assert presets[item.name] == item.value

    def test_waterflow(self):
        value = self.device.waterflow()
        assert value == {"Medium": 2}


@pytest.mark.parametrize("model", MIOT_MAPPING.keys())
def test_dreame_models(model: str):
    DreameVacuum(model=model)


def test_invalid_dreame_model():
    vac = DreameVacuum(model="model.invalid")
    fp = vac.fan_speed_presets()
    assert fp == {}
