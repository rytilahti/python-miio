from unittest import TestCase
from miio import AirConditioningCompanion
from miio.airconditioningcompanion import OperationMode, FanSpeed
from .dummies import DummyDevice
import pytest


class DummyAirConditioningCompanion(DummyDevice, AirConditioningCompanion):
    def __init__(self, *args, **kwargs):
        self.state = ['010500978022222102', '010201190280222221', '2']

        self.return_values = {
            'get_model_and_state': self._get_state
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def airconditioningcompanion(request):
    request.cls.device = DummyAirConditioningCompanion()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("airconditioningcompanion")
class TestAirConditioningCompanion(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def state(self):
        return self.device.status()

    def test_status(self):
        self.device._reset_state()

        assert self.is_on() is False
        assert self.state().ac_power == '2'
        assert self.state().ac_model == '0180222221'
        assert self.state().temperature == 25
        assert self.state().sweep_mode is False
        assert self.state().fan_speed == FanSpeed.Low
        assert self.state().mode == OperationMode.Auto

    def test_status_without_power_consume_rate(self):
        del self.device.state["power_consume_rate"]

        assert self.state().load_power is None
