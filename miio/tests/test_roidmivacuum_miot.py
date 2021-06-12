from unittest import TestCase

import pytest

from miio import RoidmiVacuumMiot
from miio.roidmivacuum_miot import (
    ChargingState,
    CleaningMode,
    DeviceStatus,
    FaultStatus,
    PathMode,
    SweepMode,
    SweepType,
    WaterLevel,
)

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "auto_boost": 1,
    "battery_level": 42,
    "brush_life_level": 85,
    "brush_life_level2": 57,
    "brush_life_level3": 60,
    "brush_left_time": 235,
    "brush_left_time2": 187,
    "brush_left_time3": 1096,
    "charging_state": ChargingState.Charging,
    "cleaning_mode": CleaningMode.FullSpeed,
    "current_audio": "girl_en",
    "clean_area": 27,
    "clean_counts": 778,
    "device_fault": FaultStatus.NoFaults,
    "device_status": DeviceStatus.Paused,
    "double_clean": 0,
    "edge_sweep": 0,
    "filter_left_time": 154,
    "filter_life_level": 66,
    "forbid_mode": '{"time":[75600,21600,1],"tz":2,"tzs":7200}',
    "led_switch": 0,
    "lidar_collision": 1,
    "mop_present": 1,
    "mute": 0,
    "station_key": 0,
    "station_led": 0,
    # "station_type": {"siid": 8, "piid": 29}, # uint32
    # "switch_status": {"siid": 2, "piid": 10},
    "sweep_mode": SweepMode.Smart,
    "sweep_type": SweepType.MopAndSweep,
    "timing": '{"tz":2,"tzs":7200}',
    "path_mode": PathMode.Normal,
    "progress": 57,
    "work_station_freq": 1,
    # "uid": "12345678",
    # "voice_conf": {"siid": 8, "piid": 30},
    "volume": 4,
    "water_level": WaterLevel.Mop,
    # "siid8_13": {"siid": 8, "piid": 13}, # no-name: (uint32, unit: seconds) (acc: ['read', 'notify'])
    # "siid8_14": {"siid": 8, "piid": 14}, # no-name: (uint32, unit: none) (acc: ['read', 'notify'])
    # "siid8_19": {"siid": 8, "piid": 19}, # no-name: (uint32, unit: seconds) (acc: ['read', 'notify'])
}


class DummyRoidmiVacuumMiot(DummyMiotDevice, RoidmiVacuumMiot):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def dummyroidmivacuum(request):
    request.cls.device = DummyRoidmiVacuumMiot()


def assertEnum(a, b):
    assert a == b
    assert repr(a) == repr(b)


@pytest.mark.usefixtures("dummyroidmivacuum")
class TestRoidmiVacuum(TestCase):
    def test_status(self):
        status = self.device.status()
        assert status.auto_boost == _INITIAL_STATE["auto_boost"]
        assert status.battery_level == _INITIAL_STATE["battery_level"]
        assert status.brush_left_time == _INITIAL_STATE["brush_left_time"]
        assert status.brush_left_time2 == _INITIAL_STATE["brush_left_time2"]
        assert status.brush_left_time3 == _INITIAL_STATE["brush_left_time3"]
        assert status.brush_life_level == _INITIAL_STATE["brush_life_level"]
        assert status.brush_life_level2 == _INITIAL_STATE["brush_life_level2"]
        assert status.brush_life_level3 == _INITIAL_STATE["brush_life_level3"]
        assertEnum(
            status.charging_state, ChargingState(_INITIAL_STATE["charging_state"])
        )
        assertEnum(status.cleaning_mode, CleaningMode(_INITIAL_STATE["cleaning_mode"]))
        assert status.current_audio == _INITIAL_STATE["current_audio"]
        assert status.clean_area == _INITIAL_STATE["clean_area"]
        assert status.clean_counts == _INITIAL_STATE["clean_counts"]
        assertEnum(status.device_fault, FaultStatus(_INITIAL_STATE["device_fault"]))
        assertEnum(status.device_status, DeviceStatus(_INITIAL_STATE["device_status"]))
        assert status.double_clean == _INITIAL_STATE["double_clean"]
        assert status.edge_sweep == _INITIAL_STATE["edge_sweep"]
        assert status.filter_left_time == _INITIAL_STATE["filter_left_time"]
        assert status.filter_life_level == _INITIAL_STATE["filter_life_level"]
        assert status.forbid_mode == status.parseForbidMode(
            _INITIAL_STATE["forbid_mode"]
        )
        assert status.led_switch == _INITIAL_STATE["led_switch"]
        assert status.lidar_collision == _INITIAL_STATE["lidar_collision"]
        assert status.mop_present == _INITIAL_STATE["mop_present"]
        assert status.mute == _INITIAL_STATE["mute"]
        assert status.station_key == _INITIAL_STATE["station_key"]
        assert status.station_led == _INITIAL_STATE["station_led"]
        assertEnum(status.sweep_mode, SweepMode(_INITIAL_STATE["sweep_mode"]))
        assertEnum(status.sweep_type, SweepType(_INITIAL_STATE["sweep_type"]))
        assert status.timing == _INITIAL_STATE["timing"]
        assertEnum(status.path_mode, PathMode(_INITIAL_STATE["path_mode"]))
        assert status.progress == _INITIAL_STATE["progress"]
        assert status.work_station_freq == _INITIAL_STATE["work_station_freq"]
        assert status.volume == _INITIAL_STATE["volume"]
        assertEnum(status.water_level, WaterLevel(_INITIAL_STATE["water_level"]))

    def test_parseForbidMode(self):
        status = self.device.status()
        value = '{"time":[75600,21600,1],"tz":2,"tzs":7200}'
        expected_value = '{"enabled": true, "begin": "21:00", "end": "6:00", "tz": 2}'
        assert status.parseForbidMode(value) == expected_value

    def test_parseForbidMode2(self):
        status = self.device.status()
        value = '{"time":[82080,33300,0],"tz":3,"tzs":10800}'
        expected_value = '{"enabled": false, "begin": "22:48", "end": "9:15", "tz": 3}'
        assert status.parseForbidMode(value) == expected_value
