from unittest import TestCase

import pytest

from miio import Walkingpad
from miio.walkingpad import WalkingpadException, WalkingpadStatus

from .dummies import DummyDevice


class DummyWalkingpad(DummyDevice, Walkingpad):
    def __init__(self, *args, **kwargs):
        self.state = {
            "power": "on",
            "mode": 1,
            "time": 1387,
            "step": 2117,
            "dist": 1150,
            "sp": 3.05,
            "cal": 71710,
            "all": [
                "mode:1",
                "time:1387",
                "sp:3.05",
                "dist:1150",
                "cal:71710",
                "step:2117",
            ],
        }
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_mode": lambda x: self._set_state("mode", x),
            "set_speed": lambda x: (
                self._set_state(
                    "all",
                    [
                        "mode:1",
                        "time:1387",
                        "sp:" + str(x),
                        "dist:1150",
                        "cal:71710",
                        "step:2117",
                    ],
                ),
                self._set_state("sp", x),
            ),
            "set_step": lambda x: self._set_state("step", x),
            "set_time": lambda x: self._set_state("time", x),
            "set_distance": lambda x: self._set_state("dist", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def walkingpad(request):
    request.cls.device = DummyWalkingpad()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("walkingpad")
class TestWalkingpad(TestCase):
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

        # Because we get a set of status values from the walkingpad via 'all' the dummy device doesnt work for testing.
        # TODO Need to figure out how to test this properly.

        assert repr(self.state()) == repr(WalkingpadStatus(self.device.start_state))

        assert self.is_on() is True
        assert self.state().power == self.device.start_state["power"]
        assert self.state().mode == self.device.start_state["mode"]
        # assert self.state().speed == self.device.start_state["speed"]
        # assert self.state().step == self.device.start_state["step"]
        # assert self.state().distance == self.device.start_state["dist"]
        # assert self.state().time == self.device.start_state["time"]

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(1)
        assert mode() == 1

        self.device.set_mode(0)
        assert mode() == 0

        with pytest.raises(WalkingpadException):
            self.device.set_mode(-1)

        with pytest.raises(WalkingpadException):
            self.device.set_mode(3)

        with pytest.raises(WalkingpadException):
            self.device.set_mode("blah")
