from unittest import TestCase

import pytest

from miio import AirPurifier
from miio.airpurifier import (OperationMode, LedBrightness, FilterType,
                              SleepMode, AirPurifierStatus,
                              AirPurifierException, )
from .dummies import DummyDevice


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
            'motor2_speed': 800,
            'purify_volume': 25262,
            'f1_hour': 3500,
            'led': 'off',
            'led_b': 2,
            'bright': 83,
            'buzzer': 'off',
            'child_lock': 'off',
            'volume': 50,
            'rfid_product_id': '0:0:41:30',
            'rfid_tag': '10:20:30:40:50:60:7',
            'act_sleep': 'close',
            'sleep_mode': 'idle',
            'sleep_time': 83890,
            'sleep_data_num': 22,
            'app_extra': 1,
            'act_det': 'off',
            'button_pressed': 'power',
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
            'set_volume': lambda x: self._set_state("volume", x),
            'set_act_sleep': lambda x: self._set_state("act_sleep", x),
            'reset_filter1': lambda x: (
                self._set_state('f1_hour_used', [0]),
                self._set_state('filter1_life', [100])
            ),
            'set_act_det': lambda x: self._set_state("act_det", x),
            'set_app_extra': lambda x: self._set_state("app_extra", x),
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

        assert repr(self.state()) == repr(AirPurifierStatus(self.device.start_state))

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
        assert self.state().motor2_speed == self.device.start_state["motor2_speed"]
        assert self.state().purify_volume == self.device.start_state["purify_volume"]
        assert self.state().led == (self.device.start_state["led"] == 'on')
        assert self.state().led_brightness == LedBrightness(self.device.start_state["led_b"])
        assert self.state().buzzer == (self.device.start_state["buzzer"] == 'on')
        assert self.state().child_lock == (self.device.start_state["child_lock"] == 'on')
        assert self.state().illuminance == self.device.start_state["bright"]
        assert self.state().volume == self.device.start_state["volume"]
        assert self.state().filter_rfid_product_id == self.device.start_state["rfid_product_id"]
        assert self.state().sleep_mode == SleepMode(self.device.start_state["sleep_mode"])
        assert self.state().sleep_time == self.device.start_state["sleep_time"]
        assert self.state().sleep_mode_learn_count == self.device.start_state["sleep_data_num"]
        assert self.state().extra_features == self.device.start_state["app_extra"]
        assert self.state().turbo_mode_supported == (self.device.start_state["app_extra"] == 1)
        assert self.state().auto_detect == (self.device.start_state["act_det"] == 'on')
        assert self.state().button_pressed == self.device.start_state["button_pressed"]

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
        assert favorite_level() == 10

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

    def test_set_volume(self):
        def volume():
            return self.device.status().volume

        self.device.set_volume(0)
        assert volume() == 0
        self.device.set_volume(35)
        assert volume() == 35
        self.device.set_volume(100)
        assert volume() == 100

        with pytest.raises(AirPurifierException):
            self.device.set_volume(-1)

        with pytest.raises(AirPurifierException):
            self.device.set_volume(101)

    def test_set_learn_mode(self):
        def learn_mode():
            return self.device.status().learn_mode

        self.device.set_learn_mode(True)
        assert learn_mode() is True

        self.device.set_learn_mode(False)
        assert learn_mode() is False

    def test_set_auto_detect(self):
        def auto_detect():
            return self.device.status().auto_detect

        self.device.set_auto_detect(True)
        assert auto_detect() is True

        self.device.set_auto_detect(False)
        assert auto_detect() is False

    def test_set_extra_features(self):
        def extra_features():
            return self.device.status().extra_features

        self.device.set_extra_features(0)
        assert extra_features() == 0
        self.device.set_extra_features(1)
        assert extra_features() == 1
        self.device.set_extra_features(2)
        assert extra_features() == 2

        with pytest.raises(AirPurifierException):
            self.device.set_extra_features(-1)

    def test_reset_filter(self):
        def filter_hours_used():
            return self.device.status().filter_hours_used

        def filter_life_remaining():
            return self.device.status().filter_life_remaining

        self.device._reset_state()
        assert filter_hours_used() != 0
        assert filter_life_remaining() != 100
        self.device.reset_filter()
        assert filter_hours_used() == 0
        assert filter_life_remaining() == 100

    def test_status_without_volume(self):
        self.device._reset_state()

        # The Air Purifier 2 doesn't support volume
        self.device.state["volume"] = None
        assert self.state().volume is None

    def test_status_without_led_brightness(self):
        self.device._reset_state()

        # The Air Purifier Pro doesn't support LED brightness
        self.device.state["led_b"] = None
        assert self.state().led_brightness is None

    def test_status_unknown_led_brightness(self):
        self.device._reset_state()

        # The Air Purifier V3 returns a led brightness of 10 f.e.
        self.device.state["led_b"] = 10
        assert self.state().led_brightness is None

    def test_status_without_temperature(self):
        self.device._reset_state()
        self.device.state["temp_dec"] = None
        assert self.state().temperature is None

    def test_status_without_illuminance(self):
        self.device._reset_state()
        # The Air Purifier 2 doesn't provide illuminance
        self.device.state["bright"] = None
        assert self.state().illuminance is None

    def test_status_without_buzzer(self):
        self.device._reset_state()
        # The Air Purifier Pro doesn't provide the buzzer property
        self.device.state["buzzer"] = None
        assert self.state().buzzer is None

    def test_status_without_motor2_speed(self):
        self.device._reset_state()
        # The Air Purifier Pro doesn't provide the buzzer property
        self.device.state["motor2_speed"] = None
        assert self.state().motor2_speed is None

    def test_status_without_filter_rfid_tag(self):
        self.device._reset_state()
        self.device.state["rfid_tag"] = None
        assert self.state().filter_rfid_tag is None
        assert self.state().filter_type is None

    def test_status_with_filter_rfid_tag_zeros(self):
        self.device._reset_state()
        self.device.state["rfid_tag"] = '0:0:0:0:0:0:0'
        assert self.state().filter_type is FilterType.Unknown

    def test_status_without_filter_rfid_product_id(self):
        self.device._reset_state()
        self.device.state["rfid_product_id"] = None
        assert self.state().filter_type is FilterType.Regular

    def test_status_filter_rfid_product_ids(self):
        self.device._reset_state()
        self.device.state["rfid_product_id"] = '0:0:30:31'
        assert self.state().filter_type is FilterType.AntiFormaldehyde
        self.device.state["rfid_product_id"] = '0:0:30:32'
        assert self.state().filter_type is FilterType.Regular
        self.device.state["rfid_product_id"] = '0:0:41:30'
        assert self.state().filter_type is FilterType.AntiBacterial

    def test_status_without_sleep_mode(self):
        self.device._reset_state()
        self.device.state["sleep_mode"] = None
        assert self.state().sleep_mode is None

    def test_status_without_app_extra(self):
        self.device._reset_state()
        self.device.state["app_extra"] = None
        assert self.state().extra_features is None
        assert self.state().turbo_mode_supported is None

    def test_status_without_auto_detect(self):
        self.device._reset_state()
        self.device.state["act_det"] = None
        assert self.state().auto_detect is None
