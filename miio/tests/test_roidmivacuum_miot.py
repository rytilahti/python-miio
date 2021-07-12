from datetime import timedelta
from unittest import TestCase

import pytest

from miio import RoidmiVacuumMiot
from miio.roidmivacuum_miot import (
    ChargingState,
    FanSpeed,
    PathMode,
    RoidmiState,
    SweepMode,
    SweepType,
    WaterLevel,
)
from miio.vacuumcontainers import DNDStatus

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "auto_boost": 1,
    "battery_level": 42,
    "main_brush_life_level": 85,
    "side_brushes_life_level": 57,
    "sensor_dirty_remaning_level": 60,
    "main_brush_left_minutes": 235,
    "side_brushes_left_minutes": 187,
    "sensor_dirty_time_left_minutes": 1096,
    "charging_state": ChargingState.Charging,
    "fanspeed_mode": FanSpeed.FullSpeed,
    "current_audio": "girl_en",
    "clean_area": 27,
    "error_code": 0,
    "state": RoidmiState.Paused.value,
    "double_clean": 0,
    "filter_left_minutes": 154,
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
    "timing": '{"time":[[32400,1,3,0,[1,2,3,4,5],0,[12,10],null],[57600,0,1,2,[1,2,3,4,5,6,0],2,[],null]],"tz":2,"tzs":7200}',
    "path_mode": PathMode.Normal,
    "work_station_freq": 1,
    # "uid": "12345678",
    "volume": 4,
    "water_level": WaterLevel.Mop,
    "total_clean_time_sec": 321456,
    "total_clean_areas": 345678,
    "clean_counts": 987,
    "clean_time_sec": 32,
}


class DummyRoidmiVacuumMiot(DummyMiotDevice, RoidmiVacuumMiot):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def dummyroidmivacuum(request):
    request.cls.device = DummyRoidmiVacuumMiot()


@pytest.mark.usefixtures("dummyroidmivacuum")
class TestRoidmiVacuum(TestCase):
    def test_vacuum_status(self):
        status = self.device.status()
        assert status.carpet_mode == _INITIAL_STATE["auto_boost"]
        assert status.battery == _INITIAL_STATE["battery_level"]
        assert status.charging_state == ChargingState(_INITIAL_STATE["charging_state"])
        assert status.fan_speed == FanSpeed(_INITIAL_STATE["fanspeed_mode"])
        assert status.current_audio == _INITIAL_STATE["current_audio"]
        assert status.clean_area == _INITIAL_STATE["clean_area"]
        assert status.clean_time.total_seconds() == _INITIAL_STATE["clean_time_sec"]
        assert status.error_code == _INITIAL_STATE["error_code"]
        assert status.error == "NoFaults"
        assert status.state == RoidmiState(_INITIAL_STATE["state"])
        assert status.double_clean == _INITIAL_STATE["double_clean"]
        assert str(status.dnd_status) == str(
            status._parse_forbid_mode(_INITIAL_STATE["forbid_mode"])
        )
        assert status.led == _INITIAL_STATE["led_switch"]
        assert status.is_lidar_collision_sensor == _INITIAL_STATE["lidar_collision"]
        assert status.is_mop_attached == _INITIAL_STATE["mop_present"]
        assert status.is_muted == _INITIAL_STATE["mute"]
        assert status.station_key == _INITIAL_STATE["station_key"]
        assert status.station_led == _INITIAL_STATE["station_led"]
        assert status.sweep_mode == SweepMode(_INITIAL_STATE["sweep_mode"])
        assert status.sweep_type == SweepType(_INITIAL_STATE["sweep_type"])
        assert status.timing == _INITIAL_STATE["timing"]
        assert status.path_mode == PathMode(_INITIAL_STATE["path_mode"])
        assert status.dust_collection_frequency == _INITIAL_STATE["work_station_freq"]
        assert status.volume == _INITIAL_STATE["volume"]
        assert status.water_level == WaterLevel(_INITIAL_STATE["water_level"])

        assert status.is_paused is True
        assert status.is_on is False
        assert status.got_error is False

    def test_cleaning_summary(self):
        status = self.device.cleaning_summary()
        assert (
            status.total_duration.total_seconds()
            == _INITIAL_STATE["total_clean_time_sec"]
        )
        assert status.total_area == _INITIAL_STATE["total_clean_areas"]
        assert status.count == _INITIAL_STATE["clean_counts"]

    def test_consumable_status(self):
        status = self.device.consumable_status()
        assert (
            status.main_brush_left.total_seconds() / 60
            == _INITIAL_STATE["main_brush_left_minutes"]
        )
        assert (
            status.side_brush_left.total_seconds() / 60
            == _INITIAL_STATE["side_brushes_left_minutes"]
        )
        assert (
            status.sensor_dirty_left.total_seconds() / 60
            == _INITIAL_STATE["sensor_dirty_time_left_minutes"]
        )
        assert status.main_brush == status._calcUsageTime(
            status.main_brush_left, _INITIAL_STATE["main_brush_life_level"]
        )
        assert status.side_brush == status._calcUsageTime(
            status.side_brush_left, _INITIAL_STATE["side_brushes_life_level"]
        )
        assert status.sensor_dirty == status._calcUsageTime(
            status.sensor_dirty_left, _INITIAL_STATE["sensor_dirty_remaning_level"]
        )
        assert (
            status.filter_left.total_seconds() / 60
            == _INITIAL_STATE["filter_left_minutes"]
        )
        assert status.filter == status._calcUsageTime(
            status.filter_left, _INITIAL_STATE["filter_life_level"]
        )

    def test__calcUsageTime(self):
        status = self.device.consumable_status()
        orig_time = timedelta(minutes=500)
        remaning_level = 30
        remaning_time = orig_time * 0.30
        used_time = orig_time - remaning_time
        assert used_time == status._calcUsageTime(remaning_time, remaning_level)

    def test_parse_forbid_mode(self):
        status = self.device.status()
        value = '{"time":[75600,21600,1],"tz":2,"tzs":7200}'
        expected_value = DNDStatus(
            dict(
                enabled=True,
                start_hour=21,
                start_minute=0,
                end_hour=6,
                end_minute=0,
            )
        )
        assert str(status._parse_forbid_mode(value)) == str(expected_value)

    def test_parse_forbid_mode2(self):
        status = self.device.status()
        value = '{"time":[82080,33300,0],"tz":3,"tzs":10800}'
        expected_value = DNDStatus(
            dict(
                enabled=False,
                start_hour=22,
                start_minute=48,
                end_hour=9,
                end_minute=15,
            )
        )
        assert str(status._parse_forbid_mode(value)) == str(expected_value)


class DummyRoidmiVacuumMiot2(DummyMiotDevice, RoidmiVacuumMiot):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.state["charging_state"] = -10
        self.state["fanspeed_mode"] = -11
        self.state["state"] = -12
        self.state["sweep_mode"] = -13
        self.state["sweep_type"] = -14
        self.state["path_mode"] = -15
        self.state["water_level"] = -16
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def dummyroidmivacuum2(request):
    request.cls.device = DummyRoidmiVacuumMiot2()


@pytest.mark.usefixtures("dummyroidmivacuum2")
class TestRoidmiVacuum2(TestCase):
    def test_vacuum_status_unexpected_values(self):
        status = self.device.status()
        assert status.charging_state == ChargingState.Unknown
        assert status.fan_speed == FanSpeed.Unknown
        assert status.state == RoidmiState.Unknown
        assert status.sweep_mode == SweepMode.Unknown
        assert status.sweep_type == SweepType.Unknown
        assert status.path_mode == PathMode.Unknown
        assert status.water_level == WaterLevel.Unknown
