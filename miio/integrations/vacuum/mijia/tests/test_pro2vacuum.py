import datetime
from unittest import TestCase

import pytest

from miio import Pro2Vacuum
from miio.tests.dummies import DummyMiotDevice

from ..pro2vacuum import (
    MI_ROBOT_VACUUM_MOP_PRO_2,
    DeviceState,
    FanSpeedMode,
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
    "water_level": WaterLevel.Medium,
    "side_brush_life_level": 93,
    "side_brush_time_left": datetime.timedelta(hours=14),
    "main_brush_life_level": 87,
    "main_brush_time_left": datetime.timedelta(hours=15),
    "filter_life_level": 88,
    "filter_time_left": datetime.timedelta(hours=12),
    "mop_life_level": 85,
    "mop_time_left": datetime.timedelta(hours=10),
    "current_language": "en_US",
    "clean_time": 5,
    "clean_area": 8,
}


class DummyPRO2Vacuum(DummyMiotDevice, Pro2Vacuum):
    def __init__(self, *args, **kwargs):
        self._model = MI_ROBOT_VACUUM_MOP_PRO_2
        self.state = _INITIAL_STATE_PRO2
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="class")
def dummypro2vacuum(request):
    request.cls.device = DummyPRO2Vacuum()


@pytest.mark.usefixtures("dummypro2vacuum")
class TestPro2Vacuum(TestCase):
    def test_status(self):
        status = self.device.status()
        assert status.clean_time == datetime.timedelta(
            minutes=_INITIAL_STATE_PRO2["clean_time"]
        )
        assert status.error_code == _INITIAL_STATE_PRO2["error_code"]
        assert status.error == "Unknown error code: 2105"
        assert status.fan_speed == _INITIAL_STATE_PRO2["fan_speed"]
        assert status.battery == _INITIAL_STATE_PRO2["battery"]
        assert status.mop_state == _INITIAL_STATE_PRO2["mop_state"]
