from datetime import timedelta

import pytest

from miio.identifiers import VacuumState
from miio.tests.dummies import DummyDevice

from ..viomivacuum import (
    SUPPORTED_MODELS,
    ViomiBinType,
    ViomiCarpetTurbo,
    ViomiConsumableStatus,
    ViomiEdgeState,
    ViomiLanguage,
    ViomiMode,
    ViomiRoutePattern,
    ViomiVacuum,
    ViomiVacuumSpeed,
    ViomiVacuumState,
    ViomiWaterGrade,
    _get_rooms_from_schedules,
)

# Example v8 state from the ViomiVacuumStatus docstring
_INITIAL_STATE = {
    "battary_life": 100,
    "box_type": 2,
    "err_state": 2105,
    "has_map": 1,
    "has_newmap": 0,
    "hw_info": "1.0.1",
    "is_charge": 0,
    "is_mop": 0,
    "is_work": 1,
    "light_state": 0,
    "mode": 0,
    "mop_type": 0,
    "order_time": "0",
    "remember_map": 1,
    "repeat_state": 0,
    "run_state": 5,
    "s_area": 1.2,
    "s_time": 0,
    "start_time": 0,
    "suction_grade": 0,
    "sw_info": "3.5.8_0021",
    "v_state": 10,
    "water_grade": 11,
    "zone_data": "0",
}

_CONSUMABLE_DATA = [17, 17, 17, 17]

_DND_DATA = [1, 22, 0, 8, 0]

_MAP_LIST = [
    {"name": "Downstairs", "id": 1598622255, "cur": True},
    {"name": "Upstairs", "id": 1599508355, "cur": False},
]

_POSITIONS = [1.0, 2.0, 3.0, 4, 5.0, 6.0, 7.0, 8]


class DummyViomiVacuum(DummyDevice, ViomiVacuum):
    def __init__(self, *args, **kwargs):
        self._model = "viomi.vacuum.v8"
        self._cache = {"edge_state": None, "rooms": {}, "maps": {}}
        self.state = _INITIAL_STATE.copy()
        self.return_values = {
            "get_prop": self._get_state,
            "get_consumables": lambda _: list(_CONSUMABLE_DATA),
            "get_notdisturb": lambda _: list(_DND_DATA),
            "set_charge": lambda x: None,
            "set_mode_withroom": lambda x: None,
            "set_mode": lambda x: self._set_state("mode", x),
            "set_mop": lambda x: self._set_state("is_mop", x),
            "set_suction": lambda x: self._set_state("suction_grade", x),
            "set_repeat": lambda x: self._set_state("repeat_state", x),
            "set_moproute": lambda x: self._set_state("mop_route", x),
            "set_notdisturb": lambda x: None,
            "set_voice": lambda x: None,
            "set_remember": lambda x: self._set_state("remember_map", x),
            "set_light": lambda x: self._set_state("light_state", x),
            "set_language": lambda x: None,
            "set_carpetturbo": lambda x: None,
            "set_direction": lambda x: None,
            "set_resetpos": lambda x: None,
            "get_map": lambda _: list(_MAP_LIST),
            "set_map": lambda x: None,
            "del_map": lambda x: None,
            "rename_map": lambda x: None,
            "get_ordertime": lambda _: [
                "1_0_32_0_0_0_1_1_11_0_1594139992_2_11_room1_13_room2"
            ],
            "get_curpos": lambda _: list(_POSITIONS),
        }
        super().__init__(args, kwargs)


@pytest.fixture
def dev(request):
    return DummyViomiVacuum()


class TestViomiVacuumStatus:
    """Tests for ViomiVacuumStatus parsing."""

    def test_status_properties(self, dev):
        """Test that status returns correct values from v8 state."""
        status = dev.status()

        assert status.battery == 100
        assert status.bin_type == ViomiBinType.Water
        assert status.error_code == 2105
        assert status.has_map is True
        assert status.has_new_map is False
        assert status.hw_info == "1.0.1"
        assert status.charging is True  # is_charge=0 means charging
        assert status.clean_mode == ViomiMode.Vacuum
        assert status.is_on is False  # is_work=1 means not working (inverted)
        assert status.led_state is False
        assert status.edge_state == ViomiEdgeState.Off
        assert status.mop_attached is False
        assert status.remember_map is True
        assert status.repeat_cleaning is False
        assert status.state == ViomiVacuumState.Docked
        assert status.clean_area == 1.2
        assert status.clean_time == timedelta(seconds=0)
        assert status.fanspeed == ViomiVacuumSpeed.Silent
        assert status.water_grade == ViomiWaterGrade.Low
        assert status.sound_volume == 10
        assert status.order_time == "0"
        assert status.start_time == 0
        assert status.zone_data == "0"

    def test_vacuum_state_docked(self, dev):
        dev.state["run_state"] = 5
        status = dev.status()
        assert status.vacuum_state == VacuumState.Docked

    def test_vacuum_state_cleaning(self, dev):
        for run_state in [
            ViomiVacuumState.Cleaning,
            ViomiVacuumState.Mopping,
            ViomiVacuumState.VacuumingAndMopping,
        ]:
            dev.state["run_state"] = run_state.value
            status = dev.status()
            assert status.vacuum_state == VacuumState.Cleaning

    def test_vacuum_state_paused(self, dev):
        dev.state["run_state"] = ViomiVacuumState.Paused.value
        status = dev.status()
        assert status.vacuum_state == VacuumState.Paused

    def test_vacuum_state_returning(self, dev):
        dev.state["run_state"] = ViomiVacuumState.Returning.value
        status = dev.status()
        assert status.vacuum_state == VacuumState.Returning

    def test_vacuum_state_idle(self, dev):
        for run_state in [ViomiVacuumState.Idle, ViomiVacuumState.IdleNotDocked]:
            dev.state["run_state"] = run_state.value
            status = dev.status()
            assert status.vacuum_state == VacuumState.Idle

    def test_vacuum_state_error(self, dev):
        """Error codes between 1 and 1999 should map to Error state."""
        dev.state["err_state"] = 500
        status = dev.status()
        assert status.vacuum_state == VacuumState.Error
        assert status.error is not None

    def test_vacuum_state_non_error_high_code(self, dev):
        """Error codes >= 2000 are informational, not errors."""
        dev.state["err_state"] = 2105
        status = dev.status()
        assert status.vacuum_state != VacuumState.Error
        assert status.error is None

    def test_error_string(self, dev):
        dev.state["err_state"] = 500
        status = dev.status()
        assert status.error == "Radar timed out"

    def test_error_unknown_code(self, dev):
        dev.state["err_state"] = 999
        status = dev.status()
        assert "Unknown error" in status.error

    def test_unknown_run_state(self, dev):
        dev.state["run_state"] = 99
        status = dev.status()
        assert status.state == ViomiVacuumState.Unknown

    def test_clean_time_conversion(self, dev):
        dev.state["s_time"] = 30  # 30 minutes
        status = dev.status()
        assert status.clean_time == timedelta(minutes=30)

    def test_charging_inverted(self, dev):
        """is_charge=0 means charging, is_charge=1 means not charging."""
        dev.state["is_charge"] = 0
        assert dev.status().charging is True
        dev.state["is_charge"] = 1
        assert dev.status().charging is False

    def test_is_on_inverted(self, dev):
        """is_work=0 means working, is_work=1 means not working."""
        dev.state["is_work"] = 0
        assert dev.status().is_on is True
        dev.state["is_work"] = 1
        assert dev.status().is_on is False


class TestViomiVacuumActions:
    """Tests for ViomiVacuum commands."""

    def test_home(self, dev):
        dev.home()

    def test_start(self, dev):
        dev.start()

    def test_pause(self, dev):
        dev.pause()

    def test_stop(self, dev):
        dev.stop()

    def test_find(self, dev):
        dev.find()

    def test_set_fan_speed(self, dev):
        for speed in ViomiVacuumSpeed:
            dev.set_fan_speed(speed)
            assert dev.state["suction_grade"] == speed.value

    def test_fan_speed_presets(self, dev):
        presets = dev.fan_speed_presets()
        assert isinstance(presets, dict)
        assert "Silent" in presets
        assert "Standard" in presets
        assert "Medium" in presets
        assert "Turbo" in presets

    def test_set_fan_speed_preset(self, dev):
        dev.set_fan_speed_preset(0)  # Silent
        assert dev.state["suction_grade"] == 0
        dev.set_fan_speed_preset(3)  # Turbo
        assert dev.state["suction_grade"] == 3

    def test_set_fan_speed_preset_invalid(self, dev):
        with pytest.raises(ValueError):
            dev.set_fan_speed_preset(99)

    def test_set_water_grade(self, dev):
        for grade in ViomiWaterGrade:
            dev.set_water_grade(grade)
            assert dev.state["suction_grade"] == grade.value

    def test_clean_mode(self, dev):
        for mode in ViomiMode:
            dev.clean_mode(mode)
            assert dev.state["is_mop"] == mode.value

    def test_set_edge(self, dev):
        for state in ViomiEdgeState:
            dev.set_edge(state)
            assert dev.state["mode"] == state.value

    def test_set_repeat_cleaning(self, dev):
        dev.set_repeat_cleaning(True)
        assert dev.state["repeat_state"] == 1
        dev.set_repeat_cleaning(False)
        assert dev.state["repeat_state"] == 0

    def test_set_route_pattern(self, dev):
        dev.set_route_pattern(ViomiRoutePattern.S)
        assert dev.state.get("mop_route") == 0
        dev.set_route_pattern(ViomiRoutePattern.Y)
        assert dev.state.get("mop_route") == 1

    def test_set_sound_volume(self, dev):
        dev.set_sound_volume(5)

    def test_set_sound_volume_invalid(self, dev):
        with pytest.raises(ValueError):
            dev.set_sound_volume(-1)
        with pytest.raises(ValueError):
            dev.set_sound_volume(11)

    def test_set_remember_map(self, dev):
        dev.set_remember_map(True)
        assert dev.state["remember_map"] == 1
        dev.set_remember_map(False)
        assert dev.state["remember_map"] == 0

    def test_led(self, dev):
        dev.led(True)
        assert dev.state["light_state"] is True
        dev.led(False)
        assert dev.state["light_state"] is False

    def test_set_language(self, dev):
        dev.set_language(ViomiLanguage.EN)

    def test_carpet_mode(self, dev):
        dev.carpet_mode(ViomiCarpetTurbo.Turbo)


class TestViomiVacuumDND:
    """Tests for DND functionality."""

    def test_dnd_status(self, dev):
        dnd = dev.dnd_status()
        assert dnd.enabled is True
        assert dnd.start.hour == 22
        assert dnd.start.minute == 0
        assert dnd.end.hour == 8
        assert dnd.end.minute == 0

    def test_set_dnd(self, dev):
        dev.set_dnd(disable=False, start_hr=22, start_min=0, end_hr=7, end_min=0)

    def test_set_dnd_disable(self, dev):
        dev.set_dnd(disable=True, start_hr=0, start_min=0, end_hr=0, end_min=0)


class TestViomiVacuumConsumables:
    """Tests for consumable status."""

    def test_consumable_status(self, dev):
        consumables = dev.consumable_status()
        assert isinstance(consumables, ViomiConsumableStatus)
        assert consumables.main_brush == timedelta(hours=17)
        assert consumables.side_brush == timedelta(hours=17)
        assert consumables.filter == timedelta(hours=17)
        assert consumables.mop == timedelta(hours=17)

    def test_consumable_remaining(self, dev):
        consumables = dev.consumable_status()
        assert consumables.main_brush_left == timedelta(hours=360) - timedelta(hours=17)
        assert consumables.side_brush_left == timedelta(hours=180) - timedelta(hours=17)
        assert consumables.filter_left == timedelta(hours=180) - timedelta(hours=17)
        assert consumables.mop_left == timedelta(hours=180) - timedelta(hours=17)

    def test_consumable_sensor_dirty_zero(self, dev):
        """Viomi doesn't have sensor_dirty, returns zero."""
        consumables = dev.consumable_status()
        assert consumables.sensor_dirty == timedelta(seconds=0)
        assert consumables.sensor_dirty_left == timedelta(seconds=0)


class TestViomiVacuumMaps:
    """Tests for map operations."""

    def test_get_maps(self, dev):
        maps = dev.get_maps()
        assert len(maps) == 2
        assert maps[0]["name"] == "Downstairs"
        assert maps[1]["name"] == "Upstairs"

    def test_set_map(self, dev):
        dev.set_map(1598622255)

    def test_set_map_invalid(self, dev):
        with pytest.raises(ValueError):
            dev.set_map(9999)

    def test_delete_map(self, dev):
        dev.delete_map(1598622255)

    def test_delete_map_invalid(self, dev):
        with pytest.raises(ValueError):
            dev.delete_map(9999)

    def test_rename_map(self, dev):
        dev.rename_map(1598622255, "NewName")

    def test_rename_map_invalid(self, dev):
        with pytest.raises(ValueError):
            dev.rename_map(9999, "NewName")


class TestViomiVacuumRooms:
    """Tests for room extraction."""

    def test_get_rooms_from_schedules(self):
        schedules = ["1_0_32_0_0_0_1_1_11_0_1594139992_2_11_room1_13_room2"]
        found, rooms = _get_rooms_from_schedules(schedules)
        assert found is True
        assert rooms == {"11": "room1", "13": "room2"}

    def test_get_rooms_from_schedules_not_found(self):
        """Schedules that don't match the 00:00 inactive pattern."""
        schedules = ["1_1_32_12_30_0_1_1_11_0_1594139992_2_11_room1_13_room2"]
        found, rooms = _get_rooms_from_schedules(schedules)
        assert found is False
        assert rooms == {}

    def test_get_rooms_from_schedules_multiple(self):
        schedules = [
            "1_0_32_0_0_0_1_1_11_0_1594139992_2_11_room1_13_room2",
            "2_0_32_0_0_0_1_1_11_0_1594139992_1_15_room3",
        ]
        found, rooms = _get_rooms_from_schedules(schedules)
        assert found is True
        assert "11" in rooms
        assert "13" in rooms
        assert "15" in rooms

    def test_get_rooms(self, dev):
        rooms = dev.get_rooms()
        assert "11" in rooms
        assert rooms["11"] == "room1"
        assert rooms["13"] == "room2"

    def test_get_rooms_cached(self, dev):
        """Second call should use cache."""
        rooms1 = dev.get_rooms()
        rooms2 = dev.get_rooms()
        assert rooms1 == rooms2


class TestViomiVacuumPositions:
    """Tests for position tracking."""

    def test_get_positions(self, dev):
        positions = dev.get_positions()
        assert len(positions) == 2
        assert positions[0].pos_x == 1.0
        assert positions[0].pos_y == 2.0
        assert positions[0].phi == 3.0
        assert positions[0].update == 4

    def test_get_positions_with_multiplicator(self, dev):
        positions = dev.get_positions(plan_multiplicator=2)
        assert positions[0].pos_x == 2.0
        assert positions[0].pos_y == 4.0

    def test_get_current_position(self, dev):
        pos = dev.get_current_position()
        assert pos is not None
        assert pos.pos_x == 5.0
        assert pos.pos_y == 6.0

    def test_get_current_position_empty(self, dev):
        dev.return_values["get_curpos"] = lambda _: []
        pos = dev.get_current_position()
        assert pos is None

    def test_position_equality(self, dev):
        positions = dev.get_positions()
        assert positions[0] != positions[1]

    def test_position_repr(self, dev):
        positions = dev.get_positions()
        repr_str = repr(positions[0])
        assert "ViomiPositionPoint" in repr_str
        assert "1.0" in repr_str

    def test_position_image_coords(self, dev):
        positions = dev.get_positions()
        pos = positions[0]
        assert pos.image_pos_x(offset=0.5, img_center=100) == 1.0 - 0.5 + 100
        assert pos.image_pos_y(offset=0.5, img_center=100) == 2.0 - 0.5 + 100


class TestViomiVacuumSupportedModels:
    """Tests for model registration."""

    def test_supported_models(self):
        assert "viomi.vacuum.v6" in SUPPORTED_MODELS
        assert "viomi.vacuum.v7" in SUPPORTED_MODELS
        assert "viomi.vacuum.v8" in SUPPORTED_MODELS
        assert "viomi.vacuum.v10" in SUPPORTED_MODELS
        assert "viomi.vacuum.v13" in SUPPORTED_MODELS

    def test_scheduled_cleanup_not_implemented(self, dev):
        with pytest.raises(NotImplementedError):
            dev.get_scheduled_cleanup()

    def test_add_timer_not_implemented(self, dev):
        with pytest.raises(NotImplementedError):
            dev.add_timer()

    def test_delete_timer_not_implemented(self, dev):
        with pytest.raises(NotImplementedError):
            dev.delete_timer()
