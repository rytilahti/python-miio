from datetime import timedelta
from unittest import TestCase

import pytest

from miio import Walkingpad
from miio.walkingpad import (
    OperationMode,
    OperationSensitivity,
    WalkingpadException,
    WalkingpadStatus,
)

from .dummies import DummyDevice


class DummyWalkingpad(DummyDevice, Walkingpad):
    def _get_state(self, props):
        """Return wanted properties."""

        # Overriding here to deal with case of 'all' being requested

        if props[0] == "all":
            return self.state[props[0]]

        return [self.state[x] for x in props if x in self.state]

    def _set_state(self, var, value):
        """Set a state of a variable, the value is expected to be an array with length
        of 1."""

        # Overriding here to deal with case of 'all' being set

        if var == "all":
            self.state[var] = value
        else:
            self.state[var] = value.pop(0)

    def __init__(self, *args, **kwargs):
        self.state = {
            "power": "on",
            "mode": OperationMode.Manual,
            "time": 1387,
            "step": 2117,
            "sensitivity": OperationSensitivity.Low,
            "dist": 1150,
            "sp": 3.15,
            "cal": 71710,
            "start_speed": 3.1,
            "all": [
                "mode:" + str(OperationMode.Manual.value),
                "time:1387",
                "sp:3.15",
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
                        "sp:" + str(x[0]),
                        "dist:1150",
                        "cal:71710",
                        "step:2117",
                    ],
                ),
                self._set_state("sp", x),
            ),
            "set_step": lambda x: self._set_state("step", x),
            "set_sensitivity": lambda x: self._set_state("sensitivity", x),
            "set_start_speed": lambda x: self._set_state("start_speed", x),
            "set_time": lambda x: self._set_state("time", x),
            "set_distance": lambda x: self._set_state("dist", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def walkingpad(request):
    request.cls.device = DummyWalkingpad()


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

        assert repr(self.state()) == repr(WalkingpadStatus(self.device.start_state))
        assert self.is_on() is True
        assert self.state().power == self.device.start_state["power"]
        assert self.state().mode == self.device.start_state["mode"]
        assert self.state().speed == self.device.start_state["sp"]
        assert self.state().step_count == self.device.start_state["step"]
        assert self.state().distance == self.device.start_state["dist"]
        assert self.state().sensitivity == self.device.start_state["sensitivity"]
        assert self.state().walking_time == timedelta(
            seconds=self.device.start_state["time"]
        )

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Auto)
        assert mode() == OperationMode.Auto

        self.device.set_mode(OperationMode.Manual)
        assert mode() == OperationMode.Manual

        with pytest.raises(WalkingpadException):
            self.device.set_mode(-1)

        with pytest.raises(WalkingpadException):
            self.device.set_mode(3)

        with pytest.raises(WalkingpadException):
            self.device.set_mode("blah")

    def test_set_speed(self):
        def speed():
            return self.device.status().speed

        self.device.on()
        self.device.set_speed(3.055)
        assert speed() == 3.055

        with pytest.raises(WalkingpadException):
            self.device.set_speed(7.6)

        with pytest.raises(WalkingpadException):
            self.device.set_speed(-1)

        with pytest.raises(WalkingpadException):
            self.device.set_speed("blah")

        with pytest.raises(WalkingpadException):
            self.device.off()
            self.device.set_speed(3.4)

    def test_set_start_speed(self):
        def speed():
            return self.device.status().start_speed

        self.device.on()

        self.device.set_start_speed(3.055)
        assert speed() == 3.055

        with pytest.raises(WalkingpadException):
            self.device.set_start_speed(7.6)

        with pytest.raises(WalkingpadException):
            self.device.set_start_speed(-1)

        with pytest.raises(WalkingpadException):
            self.device.set_start_speed("blah")

        with pytest.raises(WalkingpadException):
            self.device.off()
            self.device.set_start_speed(3.4)

    def test_set_sensitivity(self):
        def sensitivity():
            return self.device.status().sensitivity

        self.device.set_sensitivity(OperationSensitivity.High)
        assert sensitivity() == OperationSensitivity.High

        self.device.set_sensitivity(OperationSensitivity.Medium)
        assert sensitivity() == OperationSensitivity.Medium

        with pytest.raises(WalkingpadException):
            self.device.set_sensitivity(-1)

        with pytest.raises(WalkingpadException):
            self.device.set_sensitivity(99)

        with pytest.raises(WalkingpadException):
            self.device.set_sensitivity("blah")
