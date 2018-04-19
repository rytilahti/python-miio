from unittest import TestCase

import pytest

from miio import PhilipsEyecare
from miio.philips_eyecare import PhilipsEyecareStatus, PhilipsEyecareException
from .dummies import DummyDevice


class DummyPhilipsEyecare(DummyDevice, PhilipsEyecare):
    def __init__(self, *args, **kwargs):
        self.state = {
            'power': 'on',
            'bright': 100,
            'notifystatus': 'off',
            'ambstatus': 'off',
            'ambvalue': 100,
            'eyecare': 'on',
            'scene_num': 3,
            'bls': 'on',
            'dvalue': 0,
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
            'set_eyecare': lambda x: self._set_state("eyecare", x),
            'set_bright': lambda x: self._set_state("bright", x),
            'set_user_scene': lambda x: self._set_state("scene_num", x),
            'delay_off': lambda x: self._set_state("dvalue", x),
            'enable_bl': lambda x: self._set_state("bls", x),
            'set_notifyuser': lambda x: self._set_state("notifystatus", x),
            'enable_amb': lambda x: self._set_state("ambstatus", x),
            'set_amb_bright': lambda x: self._set_state("ambvalue", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def philips_eyecare(request):
    request.cls.device = DummyPhilipsEyecare()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("philips_eyecare")
class TestPhilipsEyecare(TestCase):
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

        assert repr(self.state()) == repr(PhilipsEyecareStatus(self.device.start_state))

        assert self.is_on() is True
        assert self.state().brightness == self.device.start_state["bright"]
        assert self.state().reminder is (self.device.start_state["notifystatus"] == 'on')
        assert self.state().ambient is (self.device.start_state["ambstatus"] == 'on')
        assert self.state().ambient_brightness == self.device.start_state["ambvalue"]
        assert self.state().eyecare is (self.device.start_state["eyecare"] == 'on')
        assert self.state().scene == self.device.start_state["scene_num"]
        assert self.state().smart_night_light is (self.device.start_state["bls"] == 'on')
        assert self.state().delay_off_countdown == self.device.start_state["dvalue"]

    def test_eyecare(self):
        def eyecare():
            return self.device.status().eyecare

        self.device.eyecare_on()
        assert eyecare() is True
        self.device.eyecare_off()
        assert eyecare() is False

    def test_set_brightness(self):
        def brightness():
            return self.device.status().brightness

        self.device.set_brightness(1)
        assert brightness() == 1
        self.device.set_brightness(50)
        assert brightness() == 50
        self.device.set_brightness(100)

        with pytest.raises(PhilipsEyecareException):
            self.device.set_brightness(-1)

        with pytest.raises(PhilipsEyecareException):
            self.device.set_brightness(0)

        with pytest.raises(PhilipsEyecareException):
            self.device.set_brightness(101)

    def test_set_scene(self):
        def scene():
            return self.device.status().scene

        self.device.set_scene(1)
        assert scene() == 1
        self.device.set_scene(2)
        assert scene() == 2

        with pytest.raises(PhilipsEyecareException):
            self.device.set_scene(-1)

        with pytest.raises(PhilipsEyecareException):
            self.device.set_scene(0)

        with pytest.raises(PhilipsEyecareException):
            self.device.set_scene(5)

    def test_delay_off(self):
        def delay_off_countdown():
            return self.device.status().delay_off_countdown

        self.device.delay_off(1)
        assert delay_off_countdown() == 1
        self.device.delay_off(100)
        assert delay_off_countdown() == 100
        self.device.delay_off(200)
        assert delay_off_countdown() == 200

        with pytest.raises(PhilipsEyecareException):
            self.device.delay_off(-1)

    def test_smart_night_light(self):
        def smart_night_light():
            return self.device.status().smart_night_light

        self.device.smart_night_light_on()
        assert smart_night_light() is True
        self.device.smart_night_light_off()
        assert smart_night_light() is False

    def test_reminder(self):
        def reminder():
            return self.device.status().reminder

        self.device.reminder_on()
        assert reminder() is True
        self.device.reminder_off()
        assert reminder() is False

    def test_ambient(self):
        def ambient():
            return self.device.status().ambient

        self.device.ambient_on()
        assert ambient() is True
        self.device.ambient_off()
        assert ambient() is False

    def test_set_ambient_brightness(self):
        def ambient_brightness():
            return self.device.status().ambient_brightness

        self.device.set_ambient_brightness(1)
        assert ambient_brightness() == 1
        self.device.set_ambient_brightness(50)
        assert ambient_brightness() == 50
        self.device.set_ambient_brightness(100)

        with pytest.raises(PhilipsEyecareException):
            self.device.set_ambient_brightness(-1)

        with pytest.raises(PhilipsEyecareException):
            self.device.set_ambient_brightness(0)

        with pytest.raises(PhilipsEyecareException):
            self.device.set_ambient_brightness(101)
