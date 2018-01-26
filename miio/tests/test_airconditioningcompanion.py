import string
from unittest import TestCase
from miio import AirConditioningCompanion
from miio.airconditioningcompanion import OperationMode, FanSpeed, Power, \
    SwingMode, STORAGE_SLOT_ID
import pytest


class DummyAirConditioningCompanion(AirConditioningCompanion):
    def __init__(self, *args, **kwargs):
        self.state = ['010500978022222102', '010201190280222221', '2']

        self.return_values = {
            'get_model_and_state': self._get_state,
            'start_ir_learn': lambda x: True,
            'end_ir_learn': lambda x: True,
            'get_ir_learn_result': lambda x: True,
            'send_ir_code': lambda x: True,
            'send_cmd': self._send_cmd_input_validation,
        }
        self.start_state = self.state.copy()

    def send(self, command: str, parameters=None, retry_count=3):
        """Overridden send() to return values from `self.return_values`."""
        return self.return_values[command](parameters)

    def _reset_state(self):
        """Revert back to the original state."""
        self.state = self.start_state.copy()

    def _get_state(self, props):
        """Return the requested data"""
        return self.state

    def _send_cmd_input_validation(self, props):
        return all(c in string.hexdigits for c in props[0])


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
        assert self.state().air_condition_power == '2'
        assert self.state().air_condition_model == '0180222221'
        assert self.state().temperature == 25
        assert self.state().swing_mode is False
        assert self.state().fan_speed == FanSpeed.Low
        assert self.state().mode == OperationMode.Auto

    def test_status_without_temperature(self):
        self.device._reset_state()
        self.device.state[1] = None
        assert self.state().temperature is None

    def test_status_without_mode(self):
        self.device._reset_state()
        self.device.state[1] = None
        assert self.state().mode is None

    def test_status_without_fan_speed(self):
        self.device._reset_state()
        self.device.state[1] = None
        assert self.state().fan_speed is None

    def test_learn(self):
        assert self.device.learn(STORAGE_SLOT_ID) is True
        assert self.device.learn() is True

    def test_learn_result(self):
        assert self.device.learn_result() is True

    def test_learn_stop(self):
        assert self.device.learn_stop(STORAGE_SLOT_ID) is True
        assert self.device.learn_stop() is True

    def test_send_ir_code(self):
        assert self.device.send_ir_code('0000000') is True

    def test_send_command(self):
        assert self.device.send_command('0000000') is True

    def test_send_configuration(self):
        def send_configuration_known_aircondition():
            return self.device.send_configuration(
                '0100010727',
                Power.On,
                OperationMode.Auto,
                22.5,
                FanSpeed.Low,
                SwingMode.On)

        def send_configuration_known_aircondition_turn_off():
            return self.device.send_configuration(
                '0100010727',
                Power.Off,
                OperationMode.Auto,
                22.5,
                FanSpeed.Low,
                SwingMode.On)

        def send_configuration_unknown_aircondition():
            return self.device.send_configuration(
                '01000fffff',
                Power.On,
                OperationMode.Auto,
                22.5,
                FanSpeed.Low,
                SwingMode.On)

        assert send_configuration_known_aircondition() is True
        assert send_configuration_known_aircondition_turn_off() is True
        assert send_configuration_unknown_aircondition() is True
