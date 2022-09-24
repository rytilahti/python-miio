import datetime
from unittest import TestCase

import pytest

from miio import Pro2Vacuum
from miio.tests.dummies import DummyDevice

from ..pro2vacuum import MI_ROBOT_VACUUM_MOP_PRO_2, Pro2Status

_INITIAL_STATE_PRO2 = {
    "state": 4,
    "error_code": 2105,
    "sweep_mode": 1,
    "sweep_type": 0,
    "battery": 42,
    "mop_state": 0,
    "fan_speed": 1,
    "water_level": 1,
    "side_brush_life_level": 93,
    "side_brush_time_left": 125,
    "main_brush_life_level": 87,
    "main_brush_time_left": 152,
    "filter_life_level": 88,
    "filter_time_left": 142,
    "mop_life_level": 85,
    "mop_time_left": 135,
    "current_language": "en_US",
    "clean_time": 9,
    "clean_area": 8,
}


class DummyPRO2Vacuum(DummyDevice, Pro2Vacuum):
    def __init__(self, *args, **kwargs):
        self._model = MI_ROBOT_VACUUM_MOP_PRO_2
        self.state = _INITIAL_STATE_PRO2
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="class")
def dummypro2vacuum(request):
    request.cls.device = DummyPRO2Vacuum()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("dummypro2vacuum")
class TestPro2Vacuum(TestCase):
    def status(self):
        return self.device.status()

    def test_status(self):
        self.device._reset_state()

        assert repr(self.status()) == repr(Pro2Status(self.device.start_state))

        status = self.status()
        assert status.clean_time == datetime.timedelta()
        assert status.error_code == 2105
        assert status.error == "Unknown error code: 2105"
        assert status.fan_speed == self.device.start_state["fan_speed"]
        assert status.battery == self.device.start_state["battery"]
        assert status.mop_state is False
