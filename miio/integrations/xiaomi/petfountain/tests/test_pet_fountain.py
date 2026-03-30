from datetime import time
from unittest import TestCase

import pytest

from miio.tests.dummies import DummyMiotDevice

from ..device import MODEL_XIAOMI_PET_WATERER_70M2, XiaomiPetFountain
from ..status import ChargingState, PetFountainMode, PetFountainStatus

_INITIAL_STATE = {
    "fault_code": 0,
    "status": 2,
    "mode": 1,
    "water_shortage": False,
    "water_interval": 25,
    "filter_life_remaining": 76,
    "filter_left_time": 23,
    "child_lock": False,
    "battery": 21,
    "charging_state": 0,
    "do_not_disturb": False,
    "low_battery": False,
    "usb_power": False,
    "dnd_start": 22 * 3600,
    "dnd_end": 8 * 3600 + 30 * 60,
    "pump_blocked": False,
}

_UNKNOWN_STATE = {
    "fault_code": None,
    "status": None,
    "mode": None,
    "water_shortage": None,
    "water_interval": None,
    "filter_life_remaining": None,
    "filter_left_time": None,
    "child_lock": None,
    "battery": None,
    "charging_state": None,
    "do_not_disturb": None,
    "low_battery": None,
    "usb_power": None,
    "dnd_start": None,
    "dnd_end": None,
    "pump_blocked": None,
}


class DummyXiaomiPetFountain(DummyMiotDevice, XiaomiPetFountain):
    def __init__(self, *args, **kwargs):
        self._model = MODEL_XIAOMI_PET_WATERER_70M2
        self.state = _INITIAL_STATE
        self.return_values = {
            "action": lambda payload: payload,
        }
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def petfountain(request):
    request.cls.device = DummyXiaomiPetFountain()


@pytest.mark.usefixtures("petfountain")
class TestXiaomiPetFountain(TestCase):
    def test_status(self):
        status = self.device.status()

        assert status.is_on is True
        assert status.fault_code == 0
        assert status.has_fault is False
        assert status.status == PetFountainStatus.Watering
        assert status.mode == PetFountainMode.Interval
        assert status.water_shortage is False
        assert status.water_interval == 25
        assert status.filter_life_remaining == 76
        assert status.filter_left_time == round(23 / 24, 2)
        assert status.child_lock is False
        assert status.battery == 21
        assert status.charging_state == ChargingState.NotCharging
        assert status.do_not_disturb is False
        assert status.low_battery is False
        assert status.usb_power is False
        assert status.dnd_start == time(22, 0)
        assert status.dnd_end == time(8, 30)
        assert status.pump_blocked is False

    def test_set_mode(self):
        self.device.set_mode(PetFountainMode.Auto)
        assert self.device.status().mode == PetFountainMode.Auto

        self.device.set_mode(PetFountainMode.Interval)
        assert self.device.status().mode == PetFountainMode.Interval

        self.device.set_mode(PetFountainMode.Continuous)
        assert self.device.status().mode == PetFountainMode.Continuous

    def test_set_water_interval(self):
        self.device.set_water_interval(45)
        assert self.device.status().water_interval == 45

        with pytest.raises(ValueError):
            self.device.set_water_interval(43)

    def test_set_child_lock(self):
        self.device.set_child_lock(True)
        assert self.device.status().child_lock is True

        self.device.set_child_lock(False)
        assert self.device.status().child_lock is False

    def test_set_do_not_disturb(self):
        self.device.set_do_not_disturb(True)
        assert self.device.status().do_not_disturb is True

        self.device.set_do_not_disturb(False)
        assert self.device.status().do_not_disturb is False

    def test_set_dnd_start(self):
        self.device.set_dnd_start(time(21, 15))
        assert self.device.status().dnd_start == time(21, 15)

    def test_set_dnd_end(self):
        self.device.set_dnd_end(time(7, 45))
        assert self.device.status().dnd_end == time(7, 45)

    def test_reset_filter_life(self):
        result = self.device.reset_filter_life()
        assert result["did"] == "call-3-1"

    def test_status_handles_missing_values(self):
        self.device.state = _UNKNOWN_STATE

        status = self.device.status()

        assert status.fault_code is None
        assert status.has_fault is False
        assert status.status is None
        assert status.mode is None
        assert status.water_shortage is None
        assert status.water_interval is None
        assert status.filter_life_remaining is None
        assert status.filter_left_time is None
        assert status.child_lock is None
        assert status.battery is None
        assert status.charging_state is None
        assert status.do_not_disturb is None
        assert status.low_battery is None
        assert status.usb_power is None
        assert status.dnd_start is None
        assert status.dnd_end is None
        assert status.pump_blocked is None
