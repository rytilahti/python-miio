from unittest import TestCase

import pytest

from miio import YeelightDualControlModule
from miio.yeelight_dual_switch import Switch, YeelightDualControlModuleException

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "switch_1_state": True,
    "switch_1_default_state": True,
    "switch_1_off_delay": 300,
    "switch_2_state": False,
    "switch_2_default_state": False,
    "switch_2_off_delay": 0,
    "interlock": False,
    "flex_mode": True,
    "rc_list": "[{'mac':'9db0eb4124f8','evtid':4097,'pid':339,'beaconkey':'3691bc0679eef9596bb63abf'}]",
}


class DummyYeelightDualControlModule(DummyMiotDevice, YeelightDualControlModule):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
        }
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def switch(request):
    request.cls.device = DummyYeelightDualControlModule()


@pytest.mark.usefixtures("switch")
class TestYeelightDualControlModule(TestCase):
    def test_1_on(self):
        self.device.off(Switch.First)  # ensure off
        assert self.device.status().switch_1_state is False

        self.device.on(Switch.First)
        assert self.device.status().switch_1_state is True

    def test_2_on(self):
        self.device.off(Switch.Second)  # ensure off
        assert self.device.status().switch_2_state is False

        self.device.on(Switch.Second)
        assert self.device.status().switch_2_state is True

    def test_1_off(self):
        self.device.on(Switch.First)  # ensure on
        assert self.device.status().switch_1_state is True

        self.device.off(Switch.First)
        assert self.device.status().switch_1_state is False

    def test_2_off(self):
        self.device.on(Switch.Second)  # ensure on
        assert self.device.status().switch_2_state is True

        self.device.off(Switch.Second)
        assert self.device.status().switch_2_state is False

    def test_status(self):
        status = self.device.status()

        assert status.switch_1_state is _INITIAL_STATE["switch_1_state"]
        assert status.switch_1_off_delay == _INITIAL_STATE["switch_1_off_delay"]
        assert status.switch_1_default_state == _INITIAL_STATE["switch_1_default_state"]
        assert status.switch_1_state is _INITIAL_STATE["switch_1_state"]
        assert status.switch_1_off_delay == _INITIAL_STATE["switch_1_off_delay"]
        assert status.switch_1_default_state == _INITIAL_STATE["switch_1_default_state"]
        assert status.interlock == _INITIAL_STATE["interlock"]
        assert status.flex_mode == _INITIAL_STATE["flex_mode"]
        assert status.rc_list == _INITIAL_STATE["rc_list"]

    def test_set_switch_off_delay(self):
        self.device.set_switch_off_delay(300, Switch.First)
        assert self.device.status().switch_1_off_delay == 300
        self.device.set_switch_off_delay(200, Switch.Second)
        assert self.device.status().switch_2_off_delay == 200

        with pytest.raises(YeelightDualControlModuleException):
            self.device.set_switch_off_delay(-2, Switch.First)

        with pytest.raises(YeelightDualControlModuleException):
            self.device.set_switch_off_delay(43300, Switch.Second)
