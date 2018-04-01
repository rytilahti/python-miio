from unittest import TestCase

import pytest

from miio import WaterPurifier
from miio.waterpurifier import WaterPurifierStatus
from .dummies import DummyDevice


class DummyWaterPurifier(DummyDevice, WaterPurifier):
    def __init__(self, *args, **kwargs):
        self.state = {
            'power': 'on',
            'mode': 'unknown',
            'tds': 'unknown',
            'filter1_life': -1,
            'filter1_state': -1,
            'filter_life': -1,
            'filter_state': -1,
            'life': -1,
            'state': -1,
            'level': 'unknown',
            'volume': 'unknown',
            'filter': 'unknown',
            'usage': 'unknown',
            'temperature': 'unknown',
            'uv_life': -1,
            'uv_state': -1,
            'elecval_state': 'unknown'

        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def waterpurifier(request):
    request.cls.device = DummyWaterPurifier()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("waterpurifier")
class TestWaterPurifier(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def state(self):
        return self.device.status()

    def test_on(self):
        self.device.off()  # ensure off
        assert self.is_on() is False

        self.device.on()
        assert self.is_on() is True

    def test_off(self):
        self.device.on()  # ensure on
        assert self.is_on() is True

        self.device.off()
        assert self.is_on() is False

    def test_status(self):
        self.device._reset_state()

        assert repr(self.state()) == repr(WaterPurifierStatus(self.device.start_state))

        assert self.is_on() is True
