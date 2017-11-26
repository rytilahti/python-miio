from unittest import TestCase
from miio import AirPurifier
from miio.airpurifier import OperationMode, LedBrightness, AirPurifierException
from .dummies import DummyDevice
import pytest


class DummyAirPurifier(DummyDevice, AirPurifier):
    def __init__(self, *args, **kwargs):
        self.state = {
            'power': 'on',
            'aqi': 10,
            'average_aqi': 8,
            'humidity': 62,
            'temp_dec': 186,
            'mode': 'auto',
            'favorite_level': 10,
            'filter1_life': 80,
            'f1_hour_used': 682,
            'use_time': 2457000,
            'motor1_speed': 354,
            'purify_volume': 25262,
            'f1_hour': 3500,
            'led': 'off',
            'led_b': 2,
            'bright': None,
            'buzzer': 'off',
            'child_lock': 'off'
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
            'set_mode': lambda x: self._set_state("mode", x),
            'set_led': lambda x: self._set_state("led", x),
            'set_buzzer': lambda x: self._set_state("buzzer", x),
            'set_child_lock': lambda x: self._set_state("child_lock", x),
            'set_level_favorite':
                lambda x: self._set_state("favorite_level", x),
            'set_led_b': lambda x: self._set_state("led_b", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def airpurifier(request):
    request.cls.device = DummyAirPurifier()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("airpurifier")
class TestAirPurifier(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def state(self):
        return self.device.status()

    def test_on(self):
        self.device.off()  # ensure off

        start_state = self.is_on()
        assert start_state is False

        self.device.on()
        assert self.is_on() is True

    def test_off(self):
        self.device.on()  # ensure on

        assert self.is_on() is True
        self.device.off()
        assert self.is_on() is False

    def test_status(self):
        self.device._reset_state()

        assert self.is_on() is True
        assert self.state().aqi == self.device.start_state["aqi"]
        assert self.state().average_aqi == self.device.start_state["average_aqi"]
        assert self.state().temperature == self.device.start_state["temp_dec"] / 10.0
        assert self.state().humidity == self.device.start_state["humidity"]
        assert self.state().mode == OperationMode(self.device.start_state["mode"])
        assert self.state().favorite_level == self.device.start_state["favorite_level"]
        assert self.state().filter_life_remaining == self.device.start_state["filter1_life"]
        assert self.state().filter_hours_used == self.device.start_state["f1_hour_used"]
        assert self.state().use_time == self.device.start_state["use_time"]
        assert self.state().motor_speed == self.device.start_state["motor1_speed"]
        assert self.state().purify_volume == self.device.start_state["purify_volume"]

        assert self.state().led == (self.device.start_state["led"] == 'on')
        assert self.state().led_brightness == LedBrightness(self.device.start_state["led_b"])
        assert self.state().buzzer == (self.device.start_state["buzzer"] == 'on')
        assert self.state().child_lock == (self.device.start_state["child_lock"] == 'on')

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Silent)
        assert mode() == OperationMode.Silent

        self.device.set_mode(OperationMode.Auto)
        assert mode() == OperationMode.Auto

        self.device.set_mode(OperationMode.Favorite)
        assert mode() == OperationMode.Favorite

        self.device.set_mode(OperationMode.Idle)
        assert mode() == OperationMode.Idle

    def test_set_favorite_level(self):
        def favorite_level():
            return self.device.status().favorite_level

        self.device.set_favorite_level(0)
        assert favorite_level() == 0
        self.device.set_favorite_level(6)
        assert favorite_level() == 6
        self.device.set_favorite_level(10)

        with pytest.raises(AirPurifierException):
            self.device.set_favorite_level(-1)

        with pytest.raises(AirPurifierException):
            self.device.set_favorite_level(17)

    def test_set_led_brightness(self):
        def led_brightness():
            return self.device.status().led_brightness

        self.device.set_led_brightness(LedBrightness.Bright)
        assert led_brightness() == LedBrightness.Bright

        self.device.set_led_brightness(LedBrightness.Dim)
        assert led_brightness() == LedBrightness.Dim

        self.device.set_led_brightness(LedBrightness.Off)
        assert led_brightness() == LedBrightness.Off

    def test_set_led(self):
        def led():
            return self.device.status().led

        # The LED brightness of a Air Purifier Pro cannot be set so far.
        self.device.set_led(True)
        assert led() is True

        self.device.set_led(False)
        assert led() is False

    def test_set_buzzer(self):
        def buzzer():
            return self.device.status().buzzer

        self.device.set_buzzer(True)
        assert buzzer() is True

        self.device.set_buzzer(False)
        assert buzzer() is False

    def test_set_child_lock(self):
        def child_lock():
            return self.device.status().child_lock

        self.device.set_child_lock(True)
        assert child_lock() is True

        self.device.set_child_lock(False)
        assert child_lock() is False

    def test_status_without_led_b_and_with_bright(self):
        self.device._reset_state()

        self.device.state["bright"] = self.device.state["led_b"]
        del self.device.state["led_b"]

        assert self.state().led_brightness == \
               LedBrightness(self.device.start_state["led_b"])

    def test_status_without_led_brightness_at_all(self):
        self.device._reset_state()

        self.device.state["led_b"] = None
        self.device.state["bright"] = None
        assert self.state().led_brightness is None

    def test_status_without_temperature(self):
        self.device._reset_state()
        self.device.state["temp_dec"] = None

        assert self.state().temperature is None
