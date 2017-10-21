from unittest import TestCase
import pytest
from .dummies import DummyDevice
import datetime
from miio import Vacuum, VacuumStatus, VacuumException


class DummyVacuum(DummyDevice, Vacuum):
    STATE_CHARGING = 8
    STATE_CLEANING = 5
    STATE_IDLE = 3
    STATE_HOME = 6
    STATE_SPOT = 11
    STATE_ERROR = 12
    STATE_PAUSED = 10
    STATE_MANUAL = 7
    def __init__(self, *args, **kwargs):
        self.state = {
            'state': 8,
            'dnd_enabled': 1,
            'clean_time': 0,
            'msg_ver': 4,
            'map_present': 1,
            'error_code': 0,
            'in_cleaning': 0,
            'clean_area': 0,
            'battery': 100,
            'fan_power': 20,
            'msg_seq': 320
        }

        self.return_values = {
            'get_status': self.vacuum_state,
            'app_start': lambda x: self.change_mode("start"),
            'app_stop': lambda x: self.change_mode("stop"),
            'app_pause': lambda x: self.change_mode("home"),
            'app_spot': lambda x: self.change_mode("spot"),
            'app_charge': lambda x: self.change_mode("charge")
        }

        super().__init__(args, kwargs)

    def change_mode(self, new_mode):
        if new_mode == "spot":
            self.state["state"] = DummyVacuum.STATE_SPOT
        elif new_mode == "home":
            self.state["state"] = DummyVacuum.STATE_HOME
        elif new_mode == "start":
            self.state["state"] = DummyVacuum.STATE_CLEANING
        elif new_mode == "stop":
            self.state["state"] = DummyVacuum.STATE_IDLE
        elif new_mode == "charge":
            self.state["state"] = DummyVacuum.STATE_CHARGING

    def vacuum_state(self, _):
        return [self.state]


@pytest.fixture(scope="class")
def dummyvacuum(request):
    request.cls.device = DummyVacuum()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("dummyvacuum")
class TestVacuum(TestCase):
    def status(self):
        return self.device.status()

    def test_status(self):
        self.device._reset_state()
        status = self.status()
        assert status.is_on is False
        assert status.dnd is True
        assert status.clean_time == datetime.timedelta()
        assert status.error_code == 0
        assert status.error == "No error"
        assert status.fanspeed == self.device.start_state["fan_power"]
        assert status.battery == self.device.start_state["battery"]

    def test_status_with_errors(self):
        errors = {5: "Clean main brush",
                  19: "Unpowered charging station"}

        for errcode, error in errors.items():
            self.device.state["state"] = self.device.STATE_ERROR
            self.device.state["error_code"] = errcode
            assert self.status().is_on is False
            assert self.status().got_error is True
            assert self.status().error_code == errcode
            assert self.status().error == error

    def test_start_and_stop(self):
        assert self.status().is_on is False
        self.device.start()
        assert self.status().is_on is True
        assert self.status().state_code == self.device.STATE_CLEANING
        self.device.stop()
        assert self.status().is_on is False

    def test_spot(self):
        assert self.status().is_on is False
        self.device.spot()
        assert self.status().is_on is True
        assert self.status().state_code == self.device.STATE_SPOT
        self.device.stop()
        assert self.status().is_on is False

    def test_pause(self):
        self.device.start()
        assert self.status().is_on is True
        self.device.pause()
        assert self.status().state_code == self.device.STATE_PAUSED

    def test_home(self):
        self.device.start()
        assert self.status().is_on is True
        self.device.home()
        assert self.status().state_code == self.device.STATE_HOME
        self.device.change_mode(self.device.STATE_CHARGING)

    def test_manual_control(self):
        self.fail()

    @pytest.mark.skip("unknown handling")
    def test_log_upload(self):
        self.fail()

    def test_consumable_status(self):
        self.fail()

    @pytest.mark.skip("consumable reset is not implemented")
    def test_consumable_reset(self):
        self.fail()

    def test_map(self):
        self.fail()

    def test_clean_history(self):
        self.fail()

    def test_clean_details(self):
        self.fail()

    def test_find(self):
        self.fail()

    def test_timer(self):
        self.fail()

    def test_dnd(self):
        self.fail()

    def test_fan_speed(self):
        self.fail()

    def test_sound_info(self):
        self.fail()

    def test_serial_number(self):
        self.fail()

    def test_timezone(self):
        self.fail()

    def test_raw_command(self):
        self.fail()
