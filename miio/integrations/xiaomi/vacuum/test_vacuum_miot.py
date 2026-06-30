from datetime import timedelta
from unittest import TestCase

import pytest

from miio import XiaomiVacuumE101GB
from miio.tests.dummies import DummyMiotDevice

from .vacuum_miot import (
    XIAOMI_VACUUM_E101GB,
    Consumable,
    FanSpeed,
    VacuumStatus,
    WaterLevel,
)

_INITIAL_STATE = {
    "status": 9,
    "fault": 100008,
    "battery_level": 100,
    "mode": 2,
    "water_level": 1,
    "mop_status": False,
    "zone_ids": "",
    "room_information": (
        '{"rooms":[{"id":3,"name":""},{"id":4,"name":""}],"map_uid":2}'
    ),
    "cleaning_area": 700,
    "cleaning_time": 540,
    "main_brush_life_level": 97,
    "main_brush_left_time": 290,
    "side_brush_life_level": 96,
    "side_brush_left_time": 280,
    "filter_life_level": 94,
    "filter_left_time": 260,
}


class DummyXiaomiVacuumE101GB(DummyMiotDevice, XiaomiVacuumE101GB):
    def __init__(self, *args, **kwargs):
        self._model = XIAOMI_VACUUM_E101GB
        self.state = _INITIAL_STATE
        self.return_values = {
            "action": lambda x: x,
            "set_properties": lambda x: x,
        }
        super().__init__(*args, **kwargs)


class DummyXiaomiVacuumE101GBDeviceDid(DummyXiaomiVacuumE101GB):
    def get_properties(
        self, properties, *, property_getter="get_prop", max_properties=None
    ):
        response = []
        for prop in properties:
            key = prop["did"]
            response.append(
                {
                    "did": "1171712073",
                    "siid": prop["siid"],
                    "piid": prop["piid"],
                    "code": 0,
                    "value": _INITIAL_STATE[key],
                }
            )
        return response


class DummyXiaomiVacuumE101GBUnexpected(DummyXiaomiVacuumE101GB):
    def get_properties(
        self, properties, *, property_getter="get_prop", max_properties=None
    ):
        return [
            {
                "did": None,
                "code": 0,
                "value": 123,
            }
        ]


class DummyXiaomiVacuumE101GBEmptyRoomInfo(DummyXiaomiVacuumE101GB):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = {
            prop["did"]: prop["value"]
            for prop in self.state
            if prop["did"] != "room_information"
        }
        self.state["room_information"] = ""
        self.state = [{"did": k, "value": v, "code": 0} for k, v in self.state.items()]


@pytest.fixture(scope="function")
def dummy_xiaomi_vacuum(request):
    request.cls.device = DummyXiaomiVacuumE101GB()


@pytest.mark.usefixtures("dummy_xiaomi_vacuum")
class TestXiaomiVacuumE101GB(TestCase):
    def test_status(self):
        status = self.device.status()
        assert status.status == VacuumStatus.Charged
        assert status.error_code == _INITIAL_STATE["fault"]
        assert status.battery == _INITIAL_STATE["battery_level"]
        assert status.fan_speed == FanSpeed.Basic
        assert status.water_level == WaterLevel.Level1
        assert status.mop_status is False
        assert status.cleaning_area == _INITIAL_STATE["cleaning_area"]
        assert status.cleaning_time == timedelta(
            seconds=_INITIAL_STATE["cleaning_time"]
        )
        assert status.main_brush_life_level == _INITIAL_STATE["main_brush_life_level"]
        assert status.main_brush_left_time == timedelta(
            hours=_INITIAL_STATE["main_brush_left_time"]
        )
        assert status.side_brush_life_level == _INITIAL_STATE["side_brush_life_level"]
        assert status.side_brush_left_time == timedelta(
            hours=_INITIAL_STATE["side_brush_left_time"]
        )
        assert status.filter_life_level == _INITIAL_STATE["filter_life_level"]
        assert status.filter_left_time == timedelta(
            hours=_INITIAL_STATE["filter_left_time"]
        )

    def test_fan_speed_presets(self):
        presets = self.device.fan_speed_presets()
        for item in FanSpeed:
            assert presets[item.name] == item.value

    def test_set_fan_speed(self):
        self.device.set_fan_speed(FanSpeed.Strong)
        assert self.device.status().fan_speed == FanSpeed.Strong

    def test_set_fan_speed_preset(self):
        self.device.set_fan_speed_preset(FanSpeed.FullSpeed.value)
        assert self.device.status().fan_speed == FanSpeed.FullSpeed

        with pytest.raises(ValueError):
            self.device.set_fan_speed_preset(99)

    def test_set_water_level(self):
        self.device.set_water_level(WaterLevel.Level3)
        assert self.device.status().water_level == WaterLevel.Level3

    def test_action_payloads(self):
        assert self.device.start()["aiid"] == 1
        assert self.device.stop()["aiid"] == 2
        assert self.device.home()["aiid"] == 3
        assert self.device.pause()["aiid"] == 7
        assert self.device.resume()["aiid"] == 8
        assert self.device.find()["siid"] == 6

    def test_room_and_zone_payloads(self):
        room = self.device.start_room_sweep("12,13")
        assert room["aiid"] == 16
        assert room["in"] == [{"piid": 15, "value": "12,13"}]

        zone = self.device.start_zone_sweep("1,2,3,4")
        assert zone["aiid"] == 37
        assert zone["in"] == [{"piid": 12, "value": "1,2,3,4"}]

    def test_consumable_resets(self):
        assert self.device.reset_main_brush_life()["siid"] == 12
        assert self.device.reset_side_brush_life()["siid"] == 13
        assert self.device.reset_filter_life()["siid"] == 14
        assert self.device.consumable_reset(Consumable.Filter)["siid"] == 14

    def test_room_helpers(self):
        assert self.device.zone_ids() == ""
        assert self.device.room_information()["map_uid"] == 2
        assert self.device.room_ids() == [3, 4]

    def test_room_information_empty(self):
        assert DummyXiaomiVacuumE101GBEmptyRoomInfo().room_information() == {}

    def test_get_room_configs(self):
        payload = self.device.get_room_configs("3,4")
        assert payload["aiid"] == 11
        assert payload["in"] == [{"piid": 15, "value": "3,4"}]

    def test_get_zone_configs(self):
        payload = self.device.get_zone_configs("1,2")
        assert payload["aiid"] == 10
        assert payload["in"] == [{"piid": 12, "value": "1,2"}]

    def test_consumable_resets_all_variants(self):
        assert self.device.consumable_reset(Consumable.MainBrush)["siid"] == 12
        assert self.device.consumable_reset(Consumable.SideBrush)["siid"] == 13
        assert self.device.consumable_reset(Consumable.Filter)["siid"] == 14

    def test_water_level_presets(self):
        presets = self.device.water_level_presets()
        for item in WaterLevel:
            assert presets[item.name] == item.value


def test_xiaomi_vacuum_model():
    XiaomiVacuumE101GB(model=XIAOMI_VACUUM_E101GB)


def test_status_maps_response_without_request_did():
    status = DummyXiaomiVacuumE101GBDeviceDid().status()
    assert status.status == VacuumStatus.Charged
    assert status.battery == 100


def test_status_ignores_unexpected_property_response():
    assert (
        DummyXiaomiVacuumE101GBUnexpected()._get_properties_for_keys(["status"]) == {}
    )
