from unittest import TestCase
from miio import AirHumidifier
from miio.airhumidifier import OperationMode, LedBrightness, AirHumidifierException
from .dummies import DummyDevice
import pytest


class DummyAirHumidifier(DummyDevice, AirHumidifier):
    def __init__(self, *args, **kwargs):
        self.state = {
            'power': 'on',
            'mode': 'medium',
            'temp_dec': 294,
            'humidity': 33,
            'buzzer': 'off',
            'led_b': 2,
            'child_lock': 'on',
            'limit_hum': 40,
            'trans_level': 85,
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
            'set_mode': lambda x: self._set_state("mode", x),
            'set_led_b': lambda x: self._set_state("led_b", x),
            'set_buzzer': lambda x: self._set_state("buzzer", x),
            'set_child_lock': lambda x: self._set_state("child_lock", x),
            'set_limit_hum': lambda x: self._set_state("limit_hum", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def airhumidifier(request):
    request.cls.device = DummyAirHumidifier()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("airhumidifier")
class TestAirHumidifier(TestCase):
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
        assert self.state().temperature == self.device.start_state["temp_dec"] / 10.0
        assert self.state().humidity == self.device.start_state["humidity"]
        assert self.state().mode == OperationMode(self.device.start_state["mode"])
        assert self.state().led_brightness == LedBrightness(self.device.start_state["led_b"])
        assert self.state().buzzer == (self.device.start_state["buzzer"] == 'on')
        assert self.state().child_lock == (self.device.start_state["child_lock"] == 'on')
        assert self.state().target_humidity == self.device.start_state["limit_hum"]
        assert self.state().trans_level == self.device.start_state["trans_level"]

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Silent)
        assert mode() == OperationMode.Silent

        self.device.set_mode(OperationMode.Medium)
        assert mode() == OperationMode.Medium

        self.device.set_mode(OperationMode.High)
        assert mode() == OperationMode.High

    def test_set_led_brightness(self):
        def led_brightness():
            return self.device.status().led_brightness

        self.device.set_led_brightness(LedBrightness.Bright)
        assert led_brightness() == LedBrightness.Bright

        self.device.set_led_brightness(LedBrightness.Dim)
        assert led_brightness() == LedBrightness.Dim

        self.device.set_led_brightness(LedBrightness.Off)
        assert led_brightness() == LedBrightness.Off

    def test_set_buzzer(self):
        def buzzer():
            return self.device.status().buzzer

        self.device.set_buzzer(True)
        assert buzzer() is True

        self.device.set_buzzer(False)
        assert buzzer() is False

    def test_status_without_temperature(self):
        self.device._reset_state()
        self.device.state["temp_dec"] = None

        assert self.state().temperature is None

    def test_status_without_led_brightness(self):
        self.device._reset_state()
        self.device.state["led_b"] = None

        assert self.state().led_brightness is None

    def test_set_target_humidity(self):
        def target_humidity():
            return self.device.status().target_humidity

        self.device.set_target_humidity(30)
        assert target_humidity() == 30
        self.device.set_target_humidity(60)
        assert target_humidity() == 60
        self.device.set_target_humidity(80)
        assert target_humidity() == 80

        with pytest.raises(AirHumidifierException):
            self.device.set_target_humidity(-1)

        with pytest.raises(AirHumidifierException):
            self.device.set_target_humidity(20)

        with pytest.raises(AirHumidifierException):
            self.device.set_target_humidity(90)

        with pytest.raises(AirHumidifierException):
            self.device.set_target_humidity(110)

    def test_set_child_lock(self):
        def child_lock():
            return self.device.status().child_lock

        self.device.set_child_lock(True)
        assert child_lock() is True

        self.device.set_child_lock(False)
        assert child_lock() is False
