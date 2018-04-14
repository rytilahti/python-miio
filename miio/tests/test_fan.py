from unittest import TestCase

import pytest

from miio import Fan
from miio.fan import (MoveDirection, LedBrightness, FanStatus, FanException,
                      MODEL_FAN_V2, MODEL_FAN_V3, )
from .dummies import DummyDevice


class DummyFanV2(DummyDevice, Fan):
    def __init__(self, *args, **kwargs):
        self.model = MODEL_FAN_V2
        # This example response is just a guess. Please update!
        self.state = {
            'temp_dec': 232,
            'humidity': 46,
            'angle': 118,
            'speed': 298,
            'poweroff_time': 0,
            'power': 'on',
            'ac_power': 'off',
            'battery': 98,
            'angle_enable': 'off',
            'speed_level': 1,
            'natural_level': 0,
            'child_lock': 'off',
            'buzzer': 'on',
            'led_b': 1,
            'led': None,
            'natural_enable': None,
            'use_time': 0,
            'bat_charge': 'complete',
            'bat_state': None,
            'button_pressed': 'speed'
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def fanv2(request):
    request.cls.device = DummyFanV2()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("fanv2")
class TestFanV2(TestCase):
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

        assert repr(self.state()) == repr(FanStatus(self.device.start_state))

        assert self.is_on() is True
        assert self.state().temperature == self.device.start_state["temp_dec"] / 10.0
        assert self.state().humidity == self.device.start_state["humidity"]
        assert self.state().angle == self.device.start_state["angle"]
        assert self.state().speed == self.device.start_state["speed"]
        assert self.state().delay_off_countdown == self.device.start_state["poweroff_time"]
        assert self.state().ac_power is (self.device.start_state["ac_power"] == 'on')
        assert self.state().battery == self.device.start_state["battery"]
        assert self.state().oscillate is (self.device.start_state["angle_enable"] == 'on')
        assert self.state().direct_speed == self.device.start_state["speed_level"]
        assert self.state().natural_speed == self.device.start_state["natural_level"]
        assert self.state().child_lock is (self.device.start_state["child_lock"] == 'on')
        assert self.state().buzzer is (self.device.start_state["buzzer"] == 'on')
        assert self.state().led_brightness == LedBrightness(self.device.start_state["led_b"])
        assert self.state().led == self.device.start_state["led"]
        assert self.state().use_time == self.device.start_state["use_time"]
        assert self.state().battery_charge == self.device.start_state["bat_charge"]
        assert self.state().battery_state == self.device.start_state["bat_state"]
        assert self.state().button_pressed == self.device.start_state["button_pressed"]

class DummyFanV3(DummyDevice, Fan):
    def __init__(self, *args, **kwargs):
        self.model = MODEL_FAN_V3
        self.state = {
            'temp_dec': 232,
            'humidity': 46,
            'angle': 118,
            'speed': 298,
            'poweroff_time': 0,
            'power': 'on',
            'ac_power': 'off',
            'battery': 98,
            'angle_enable': 'off',
            'speed_level': 1,
            'natural_level': 0,
            'child_lock': 'off',
            'buzzer': 'on',
            'led_b': 1,
            'led': None,
            'natural_enable': None,
            'use_time': 0,
            'bat_charge': 'complete',
            'bat_state': None,
            'button_pressed': 'speed'
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def fanv3(request):
    request.cls.device = DummyFanV3()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("fanv3")
class TestFanV3(TestCase):
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

        assert repr(self.state()) == repr(FanStatus(self.device.start_state))

        assert self.is_on() is True
        assert self.state().temperature == self.device.start_state["temp_dec"] / 10.0
        assert self.state().humidity == self.device.start_state["humidity"]
        assert self.state().angle == self.device.start_state["angle"]
        assert self.state().speed == self.device.start_state["speed"]
        assert self.state().delay_off_countdown == self.device.start_state["poweroff_time"]
        assert self.state().ac_power is (self.device.start_state["ac_power"] == 'on')
        assert self.state().battery == self.device.start_state["battery"]
        assert self.state().oscillate is (self.device.start_state["angle_enable"] == 'on')
        assert self.state().direct_speed == self.device.start_state["speed_level"]
        assert self.state().natural_speed == self.device.start_state["natural_level"]
        assert self.state().child_lock is (self.device.start_state["child_lock"] == 'on')
        assert self.state().buzzer is (self.device.start_state["buzzer"] == 'on')
        assert self.state().led_brightness == LedBrightness(self.device.start_state["led_b"])
        assert self.state().led == self.device.start_state["led"]
        assert self.state().use_time == self.device.start_state["use_time"]
        assert self.state().battery_charge == self.device.start_state["bat_charge"]
        assert self.state().battery_state == self.device.start_state["bat_state"]
        assert self.state().button_pressed == self.device.start_state["button_pressed"]
