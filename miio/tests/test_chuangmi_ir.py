from unittest import TestCase
from miio import ChuangmiIr
from miio.chuangmi_ir import ChuangmiIrException
from .dummies import DummyDevice
import pytest
import base64

PROSONIC_POWER_ON = 'Z6VPAAUCAABgAgAAxQYAAOUIAACUEQAAqyIAADSeAABwdQEAAAAAAAA' \
                    'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABFEBAQEBAQEBAgICAgIC' \
                    'AgEBAgECAQEBAQIBAgECAgICBgNXA1cDUA'

PROSONIC_POWER_ON_PROTON = '0000006C00220002015B00AD001600160016001600160016' \
                           '001600160016001600160016001600160016001600160041' \
                           '001600410016004100160041001600410016004100160041' \
                           '001600160016001600160041001600160016004100160016' \
                           '001600160016001600160016001600410016001600160041' \
                           '001600160016004100160041001600410016004100160623' \
                           '015B005700160E6E'

class DummyChuangmiIr(DummyDevice, ChuangmiIr):
    def __init__(self, *args, **kwargs):
        self.state = {}
        self.return_values = {
            'miIO.ir_learn': lambda x: True,
            'miIO.ir_read': lambda x: True,
            'miIO.ir_play': self._ir_play_input_validation,
        }
        super().__init__(args, kwargs)

    @staticmethod
    def _ir_play_input_validation(payload):
        try:
            base64.b64decode(payload['code'])
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
        assert self.device.play(PROSONIC_POWER_ON) is True
        assert self.device.play(PROSONIC_POWER_ON, 19200) is True

    def test_play_pronto(self):
        assert self.device.play_pronto(PROSONIC_POWER_ON_PROTON) is True
        assert self.device.play_pronto(PROSONIC_POWER_ON_PROTON, 0) is True
        assert self.device.play_pronto(PROSONIC_POWER_ON_PROTON, 1) is True

        with pytest.raises(ChuangmiIrException):
            self.device.play_pronto(PROSONIC_POWER_ON_PROTON, -1)
