from unittest import TestCase
from miio import ChuangmiIr
from miio.chuangmi_ir import ChuangmiIrException
import pytest
import base64

PROSONIC_POWER_ON = 'Z6VPAAUCAABgAgAAxQYAAOUIAACUEQAAqyIAADSeAABwdQEAAAAAAAA' \
                    'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABFEBAQEBAQEBAgICAgIC' \
                    'AgEBAgECAQEBAQIBAgECAgICBgNXA1cDUA'


class DummyChuangmiIr(ChuangmiIr):
    def __init__(self, *args, **kwargs):
        self.return_values = {
            'miIO.ir_learn': lambda x: True,
            'miIO.ir_read': lambda x: True,
            'miIO.ir_play': lambda x: self._ir_play_input_validation,
        }
        self.start_state = self.state.copy()

    def send(self, command: str, parameters=None, retry_count=3):
        """Overridden send() to return values from `self.return_values`."""
        return self.return_values[command](parameters)

    def _reset_state(self):
        """Revert back to the original state."""
        self.state = self.start_state.copy()

    @staticmethod
    def _ir_play_input_validation(self, props):
        try:
            base64.b64decode(props['code'])
            return True
        except TypeError:
            return False


@pytest.fixture(scope="class")
def chuangmiir(request):
    request.cls.device = DummyChuangmiIr()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("chuangmiir")
class TestChuangmiIr(TestCase):
    def test_learn(self):
        assert self.device.learn() is True
        assert self.device.learn(30) is True

        with pytest.raises(ChuangmiIrException):
            self.device.learn(-1)

        with pytest.raises(ChuangmiIrException):
            self.device.learn(1000001)

    def test_read(self):
        assert self.device.read() is True
        assert self.device.read(30) is True

        with pytest.raises(ChuangmiIrException):
            self.device.read(-1)

        with pytest.raises(ChuangmiIrException):
            self.device.read(1000001)

    def test_play(self):
        assert self.device.send(PROSONIC_POWER_ON) is True
        assert self.device.send(PROSONIC_POWER_ON, 19200) is True
