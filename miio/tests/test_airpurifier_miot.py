from unittest import TestCase

import pytest

from miio import AirPurifierMiot
from miio.airfilter_util import FilterType
from miio.airpurifier_miot import AirPurifierMiotException, LedBrightness, OperationMode

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "power": True,
    "aqi": 10,
    "average_aqi": 8,
    "humidity": 62,
    "temperature": 18.599999,
    "fan_level": 2,
    "mode": 0,
    "led": True,
    "led_brightness": 1,
    "buzzer": False,
    "buzzer_volume": 0,
    "child_lock": False,
    "favorite_level": 10,
    "filter_life_remaining": 80,
    "filter_hours_used": 682,
    "use_time": 2457000,
    "purify_volume": 25262,
    "motor_speed": 354,
    "filter_rfid_product_id": "0:0:41:30",
    "filter_rfid_tag": "10:20:30:40:50:60:7",
    "button_pressed": "power",
}


class DummyAirPurifierMiot(DummyMiotDevice, AirPurifierMiot):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_mode": lambda x: self._set_state("mode", x),
            "set_led": lambda x: self._set_state("led", x),
            "set_buzzer": lambda x: self._set_state("buzzer", x),
            "set_child_lock": lambda x: self._set_state("child_lock", x),
            "set_level_favorite": lambda x: self._set_state("favorite_level", x),
            "set_led_b": lambda x: self._set_state("led_b", x),
            "set_volume": lambda x: self._set_state("volume", x),
            "set_act_sleep": lambda x: self._set_state("act_sleep", x),
            "reset_filter1": lambda x: (
                self._set_state("f1_hour_used", [0]),
                self._set_state("filter1_life", [100]),
            ),
            "set_act_det": lambda x: self._set_state("act_det", x),
            "set_app_extra": lambda x: self._set_state("app_extra", x),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def airpurifier(request):
    request.cls.device = DummyAirPurifierMiot()


@pytest.mark.usefixtures("airpurifier")
class TestAirPurifier(TestCase):
    def test_on(self):
        self.device.off()  # ensure off
        assert self.device.status().is_on is False

        self.device.on()
        assert self.device.status().is_on is True

    def test_off(self):
        self.device.on()  # ensure on
        assert self.device.status().is_on is True

        self.device.off()
        assert self.device.status().is_on is False

    def test_status(self):
        status = self.device.status()
        assert status.is_on is _INITIAL_STATE["power"]
        assert status.aqi == _INITIAL_STATE["aqi"]
        assert status.average_aqi == _INITIAL_STATE["average_aqi"]
        assert status.humidity == _INITIAL_STATE["humidity"]
        assert status.temperature == 18.6
        assert status.fan_level == _INITIAL_STATE["fan_level"]
        assert status.mode == OperationMode(_INITIAL_STATE["mode"])
        assert status.led == _INITIAL_STATE["led"]
        assert status.led_brightness == LedBrightness(_INITIAL_STATE["led_brightness"])
        assert status.buzzer == _INITIAL_STATE["buzzer"]
        assert status.child_lock == _INITIAL_STATE["child_lock"]
        assert status.favorite_level == _INITIAL_STATE["favorite_level"]
        assert status.filter_life_remaining == _INITIAL_STATE["filter_life_remaining"]
        assert status.filter_hours_used == _INITIAL_STATE["filter_hours_used"]
        assert status.use_time == _INITIAL_STATE["use_time"]
        assert status.purify_volume == _INITIAL_STATE["purify_volume"]
        assert status.motor_speed == _INITIAL_STATE["motor_speed"]
        assert status.filter_rfid_product_id == _INITIAL_STATE["filter_rfid_product_id"]
        assert status.filter_type == FilterType.AntiBacterial

    def test_set_fan_level(self):
        def fan_level():
            return self.device.status().fan_level

        self.device.set_fan_level(1)
        assert fan_level() == 1
        self.device.set_fan_level(2)
        assert fan_level() == 2
        self.device.set_fan_level(3)
        assert fan_level() == 3

        with pytest.raises(AirPurifierMiotException):
            self.device.set_fan_level(0)

        with pytest.raises(AirPurifierMiotException):
            self.device.set_fan_level(4)

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Auto)
        assert mode() == OperationMode.Auto

        self.device.set_mode(OperationMode.Silent)
        assert mode() == OperationMode.Silent

        self.device.set_mode(OperationMode.Favorite)
        assert mode() == OperationMode.Favorite

        self.device.set_mode(OperationMode.Fan)
        assert mode() == OperationMode.Fan

    def test_set_favorite_level(self):
        def favorite_level():
            return self.device.status().favorite_level

        self.device.set_favorite_level(0)
        assert favorite_level() == 0
        self.device.set_favorite_level(6)
        assert favorite_level() == 6
        self.device.set_favorite_level(14)
        assert favorite_level() == 14

        with pytest.raises(AirPurifierMiotException):
            self.device.set_favorite_level(-1)

        with pytest.raises(AirPurifierMiotException):
            self.device.set_favorite_level(15)

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
