from unittest import TestCase

import pytest

from miio.toiletlid import (
    Toiletlid,
    ToiletlidStatus,
    AmbientLightColor,
    MODEL_TOILETLID_V1,
)
from .dummies import DummyDevice

"""
Response instance
>> status

Work: False
State: 1
Ambient Light: Yellow
Filter remaining: 100%
Filter remaining time: 180
"""


class DummyToiletlidV1(DummyDevice, Toiletlid):
    def __init__(self, *args, **kwargs):
        self.model = MODEL_TOILETLID_V1
        self.state = {
            "is_on": False,
            "work_state": 1,
            "ambient_light": "Yellow",
            "filter_use_flux": "100",
            "filter_use_time": "180",
        }

        self.return_values = {
            "get_prop": self._get_state,
            "nozzle_clean": lambda x: self._set_state("work_state", [97]),
            "set_aled_v_of_uid": self.set_aled_v_of_uid,
            "get_aled_v_of_uid": self.get_aled_v_of_uid,
        }
        super().__init__(args, kwargs)

    def set_aled_v_of_uid(self, x):
        uid, color = x
        return self._set_state("ambient_light", [AmbientLightColor(color).name])

    def get_aled_v_of_uid(self, uid):
        color = self._get_state(["ambient_light"])
        if not AmbientLightColor._member_map_.get(color[0]):
            raise ValueError(color)
        return AmbientLightColor._member_map_.get(color[0]).value


@pytest.fixture(scope="class")
def toiletlidv1(request):
    request.cls.device = DummyToiletlidV1()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("toiletlidv1")
class TestToiletlidV1(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def state(self):
        return self.device.status()

    def test_status(self):
        self.device._reset_state()

        assert repr(self.state()) == repr(ToiletlidStatus(self.device.start_state))

        assert self.is_on() is False
        assert self.state().work_state == self.device.start_state["work_state"]
        assert self.state().ambient_light == self.device.start_state["ambient_light"]
        assert (
            self.state().filter_use_percentage
            == "%s%%" % self.device.start_state["filter_use_flux"]
        )
        assert (
            self.state().filter_remaining_time
            == self.device.start_state["filter_use_time"]
        )

    def test_set_ambient_light(self):
        for value, enum in AmbientLightColor._member_map_.items():
            self.device.set_ambient_light(enum)
            assert self.device.status().ambient_light == value

    def test_nozzle_clean(self):
        self.device.nozzle_clean()
        assert self.is_on() is True
        self.device._reset_state()
