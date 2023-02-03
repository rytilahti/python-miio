import datetime
from unittest import TestCase
from unittest.mock import patch

import pytest

from miio import DeviceError, RoborockVacuum, UnsupportedFeatureException
from miio.tests.dummies import DummyDevice, DummyMiIOProtocol

from ..updatehelper import UpdateHelper
from ..vacuum import (
    ROCKROBO_Q7_MAX,
    ROCKROBO_S7,
    CarpetCleaningMode,
    MopIntensity,
    MopMode,
    WaterFlow,
)
from ..vacuumcontainers import VacuumStatus


class DummyRoborockProtocol(DummyMiIOProtocol):
    """Roborock-specific dummy protocol handler.

    The vacuum reports 'unknown_method' instead of device error for unknown commands.
    """

    def send(self, command: str, parameters=None, retry_count=3, extra_parameters=None):
        """Overridden send() to return values from `self.return_values`."""
        try:
            return super().send(command, parameters, retry_count, extra_parameters)
        except DeviceError:
            return "unknown_method"


class DummyVacuum(DummyDevice, RoborockVacuum):
    STATE_CHARGING = 8
    STATE_CLEANING = 5
    STATE_ZONED_CLEAN = 9
    STATE_IDLE = 3
    STATE_HOME = 6
    STATE_SPOT = 11
    STATE_GOTO = 4
    STATE_ERROR = 12
    STATE_PAUSED = 10
    STATE_MANUAL = 7

    def __init__(self, *args, **kwargs):
        self._model = "missing.model.vacuum"
        self.state = {
            "state": 8,
            "dnd_enabled": 1,
            "clean_time": 0,
            "msg_ver": 4,
            "map_present": 1,
            "error_code": 0,
            "in_cleaning": 0,
            "clean_area": 0,
            "battery": 100,
            "fan_power": 20,
            "msg_seq": 320,
            "water_box_status": 1,
        }
        self._maps = None
        self._map_enum_cache = None
        self._status_helper = UpdateHelper(self.vacuum_status)
        self.dummies = {
            "consumables": [
                {
                    "filter_work_time": 32454,
                    "sensor_dirty_time": 3798,
                    "side_brush_work_time": 32454,
                    "main_brush_work_time": 32454,
                    "strainer_work_times": 44,
                    "cleaning_brush_work_times": 44,
                }
            ],
            "clean_summary": [
                174145,
                2410150000,
                82,
                [
                    1488240000,
                    1488153600,
                    1488067200,
                    1487980800,
                    1487894400,
                    1487808000,
                    1487548800,
                ],
            ],
            "dnd_timer": [
                {
                    "enabled": 1,
                    "start_minute": 0,
                    "end_minute": 0,
                    "start_hour": 22,
                    "end_hour": 8,
                }
            ],
            "multi_maps": [
                {
                    "max_multi_map": 4,
                    "max_bak_map": 1,
                    "multi_map_count": 3,
                    "map_info": [
                        {
                            "mapFlag": 0,
                            "add_time": 1664448893,
                            "length": 10,
                            "name": "Downstairs",
                            "bak_maps": [{"mapFlag": 4, "add_time": 1663577737}],
                        },
                        {
                            "mapFlag": 1,
                            "add_time": 1663580330,
                            "length": 8,
                            "name": "Upstairs",
                            "bak_maps": [{"mapFlag": 5, "add_time": 1663577752}],
                        },
                        {
                            "mapFlag": 2,
                            "add_time": 1663580384,
                            "length": 5,
                            "name": "Attic",
                            "bak_maps": [{"mapFlag": 6, "add_time": 1663577765}],
                        },
                    ],
                }
            ],
            "water_box_custom_mode": [202],
        }

        self.return_values = {
            "get_status": lambda x: [self.state],
            "get_consumable": lambda x: self.dummies["consumables"],
            "get_clean_summary": lambda x: self.dummies["clean_summary"],
            "app_start": lambda x: self.change_mode("start"),
            "app_stop": lambda x: self.change_mode("stop"),
            "app_pause": lambda x: self.change_mode("pause"),
            "app_spot": lambda x: self.change_mode("spot"),
            "app_goto_target": lambda x: self.change_mode("goto"),
            "app_zoned_clean": lambda x: self.change_mode("zoned clean"),
            "app_charge": lambda x: self.change_mode("charge"),
            "miIO.info": "dummy info",
            "get_clean_record": lambda x: [[1488347071, 1488347123, 16, 0, 0, 0]],
            "get_dnd_timer": lambda x: self.dummies["dnd_timer"],
            "get_multi_maps_list": lambda x: self.dummies["multi_maps"],
            "get_water_box_custom_mode": lambda x: self.dummies[
                "water_box_custom_mode"
            ],
            "set_water_box_custom_mode": self.set_water_box_custom_mode_callback,
        }

        super().__init__(args, kwargs)
        self._protocol = DummyRoborockProtocol(self)

    def set_water_box_custom_mode_callback(self, parameters):
        assert parameters == self.dummies["water_box_custom_mode"]
        return self.dummies["water_box_custom_mode"]

    def change_mode(self, new_mode):
        if new_mode == "spot":
            self.state["state"] = DummyVacuum.STATE_SPOT
        elif new_mode == "home":
            self.state["state"] = DummyVacuum.STATE_HOME
        elif new_mode == "pause":
            self.state["state"] = DummyVacuum.STATE_PAUSED
        elif new_mode == "start":
            self.state["state"] = DummyVacuum.STATE_CLEANING
        elif new_mode == "stop":
            self.state["state"] = DummyVacuum.STATE_IDLE
        elif new_mode == "goto":
            self.state["state"] = DummyVacuum.STATE_GOTO
        elif new_mode == "zoned clean":
            self.state["state"] = DummyVacuum.STATE_ZONED_CLEAN
        elif new_mode == "charge":
            self.state["state"] = DummyVacuum.STATE_CHARGING


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

        assert repr(self.status()) == repr(VacuumStatus(self.device.start_state))

        status = self.status()
        assert status.is_on is False
        assert status.clean_time == datetime.timedelta()
        assert status.error_code == 0
        assert status.error == "No error"
        assert status.fanspeed == self.device.start_state["fan_power"]
        assert status.battery == self.device.start_state["battery"]
        assert status.is_water_box_attached is True

    def test_status_with_errors(self):
        errors = {5: "Clean main brush", 19: "Unpowered charging station"}

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
        assert self.status().state_code == self.device.STATE_CHARGING
        # TODO pause here and update to idle/charging and assert for that?
        # Another option is to mock that app_stop mode is entered before
        # the charging is activated.

    def test_goto(self):
        self.device.start()
        assert self.status().is_on is True
        self.device.goto(24000, 24000)
        assert self.status().state_code == self.device.STATE_GOTO

    def test_zoned_clean(self):
        self.device.start()
        assert self.status().is_on is True
        self.device.zoned_clean(
            [[25000, 25000, 25500, 25500, 3], [23000, 23000, 22500, 22500, 1]]
        )
        assert self.status().state_code == self.device.STATE_ZONED_CLEAN

    def test_timezone(self):
        with patch.object(
            self.device,
            "send",
            return_value=[
                {"olson": "Europe/Berlin", "posix": "CET-1CEST,M3.5.0,M10.5.0/3"}
            ],
        ):
            assert self.device.timezone() == "Europe/Berlin"

        with patch.object(self.device, "send", return_value=["Europe/Berlin"]):
            assert self.device.timezone() == "Europe/Berlin"

        with patch.object(self.device, "send", return_value=0):
            assert self.device.timezone() == "UTC"

    def test_history(self):
        with patch.object(
            self.device,
            "send",
            return_value=[
                174145,
                2410150000,
                82,
                [
                    1488240000,
                    1488153600,
                    1488067200,
                    1487980800,
                    1487894400,
                    1487808000,
                    1487548800,
                ],
            ],
        ):
            assert self.device.clean_history().total_duration == datetime.timedelta(
                days=2, seconds=1345
            )

            assert self.device.clean_history().dust_collection_count is None

            assert self.device.clean_history().ids[0] == 1488240000

    def test_history_dict(self):
        with patch.object(
            self.device,
            "send",
            return_value={
                "clean_time": 174145,
                "clean_area": 2410150000,
                "clean_count": 82,
                "dust_collection_count": 5,
                "records": [
                    1488240000,
                    1488153600,
                    1488067200,
                    1487980800,
                    1487894400,
                    1487808000,
                    1487548800,
                ],
            },
        ):
            assert self.device.clean_history().total_duration == datetime.timedelta(
                days=2, seconds=1345
            )

            assert self.device.clean_history().dust_collection_count == 5

            assert self.device.clean_history().ids[0] == 1488240000

    def test_history_details(self):
        with patch.object(
            self.device,
            "send",
            return_value=[[1488347071, 1488347123, 16, 0, 0, 0]],
        ):
            assert self.device.clean_details(123123).duration == datetime.timedelta(
                seconds=16
            )

    def test_history_details_dict(self):
        with patch.object(
            self.device,
            "send",
            return_value=[
                {
                    "begin": 1616757243,
                    "end": 1616758193,
                    "duration": 950,
                    "area": 10852500,
                    "error": 0,
                    "complete": 1,
                    "start_type": 2,
                    "clean_type": 1,
                    "finish_reason": 52,
                    "dust_collection_status": 0,
                }
            ],
        ):
            assert self.device.clean_details(123123).duration == datetime.timedelta(
                seconds=950
            )

    def test_history_empty(self):
        with patch.object(
            self.device,
            "send",
            return_value={
                "clean_time": 174145,
                "clean_area": 2410150000,
                "clean_count": 82,
                "dust_collection_count": 5,
            },
        ):
            assert self.device.clean_history().total_duration == datetime.timedelta(
                days=2, seconds=1345
            )

            assert len(self.device.clean_history().ids) == 0

    def test_get_maps_dict(self):
        MAP_LIST = [
            {
                "mapFlag": 0,
                "add_time": 1664448893,
                "length": 10,
                "name": "Downstairs",
                "bak_maps": [{"mapFlag": 4, "add_time": 1663577737}],
            },
            {
                "mapFlag": 1,
                "add_time": 1663580330,
                "length": 8,
                "name": "Upstairs",
                "bak_maps": [{"mapFlag": 5, "add_time": 1663577752}],
            },
            {
                "mapFlag": 2,
                "add_time": 1663580384,
                "length": 5,
                "name": "Attic",
                "bak_maps": [{"mapFlag": 6, "add_time": 1663577765}],
            },
        ]

        with patch.object(
            self.device,
            "send",
            return_value=[
                {
                    "max_multi_map": 4,
                    "max_bak_map": 1,
                    "multi_map_count": 3,
                    "map_info": MAP_LIST,
                }
            ],
        ):
            maps = self.device.get_maps()

        assert maps.map_count == 3
        assert maps.map_id_list == [0, 1, 2]
        assert maps.map_list == MAP_LIST
        assert maps.map_name_dict == {"Downstairs": 0, "Upstairs": 1, "Attic": 2}

    def test_info_no_cloud(self):
        """Test the info functionality for non-cloud connected device."""
        from miio.exceptions import DeviceInfoUnavailableException

        with patch(
            "miio.Device._fetch_info", side_effect=DeviceInfoUnavailableException()
        ):
            assert self.device.info().model == "rockrobo.vacuum.v1"

    def test_carpet_cleaning_mode(self):
        assert self.device.carpet_cleaning_mode() is None

        with patch.object(self.device, "send", return_value=[{"carpet_clean_mode": 0}]):
            assert self.device.carpet_cleaning_mode() == CarpetCleaningMode.Avoid

        with patch.object(self.device, "send", return_value="unknown_method"):
            assert self.device.carpet_cleaning_mode() is None

        with patch.object(self.device, "send", return_value=["ok"]) as mock_method:
            assert self.device.set_carpet_cleaning_mode(CarpetCleaningMode.Rise) is True
            mock_method.assert_called_once_with(
                "set_carpet_clean_mode", {"carpet_clean_mode": 1}
            )

    def test_mop_mode(self):
        with patch.object(self.device, "send", return_value=["ok"]) as mock_method:
            assert self.device.set_mop_mode(MopMode.Deep) is True
            mock_method.assert_called_once_with("set_mop_mode", [301])

        with patch.object(self.device, "send", return_value=[300]):
            assert self.device.mop_mode() == MopMode.Standard

        with patch.object(self.device, "send", return_value=[32453]):
            assert self.device.mop_mode() is None

    def test_mop_intensity_model_check(self):
        """Test Roborock S7 check when getting mop intensity."""
        with pytest.raises(UnsupportedFeatureException):
            self.device.mop_intensity()

    def test_set_mop_intensity_model_check(self):
        """Test Roborock S7 check when setting mop intensity."""
        with pytest.raises(UnsupportedFeatureException):
            self.device.set_mop_intensity(MopIntensity.Intense)

    def test_strainer_cleaned_count(self):
        """Test getting strainer cleaned count."""
        assert self.device.consumable_status().strainer_cleaned_count == 44

    def test_cleaning_brush_cleaned_count(self):
        """Test getting cleaning brush cleaned count."""
        assert self.device.consumable_status().cleaning_brush_cleaned_count == 44

    def test_mop_dryer_model_check(self):
        """Test Roborock S7 check when getting mop dryer status."""
        with pytest.raises(UnsupportedFeatureException):
            self.device.mop_dryer_settings()

    def test_set_mop_dryer_enabled_model_check(self):
        """Test Roborock S7 check when setting mop dryer enabled."""
        with pytest.raises(UnsupportedFeatureException):
            self.device.set_mop_dryer_enabled(enabled=True)

    def test_set_mop_dryer_dry_time_model_check(self):
        """Test Roborock S7 check when setting mop dryer dry time."""
        with pytest.raises(UnsupportedFeatureException):
            self.device.set_mop_dryer_dry_time(dry_time_seconds=10800)

    def test_start_mop_drying_model_check(self):
        """Test Roborock S7 check when starting mop drying."""
        with pytest.raises(UnsupportedFeatureException):
            self.device.start_mop_drying()

    def test_stop_mop_drying_model_check(self):
        """Test Roborock S7 check when stopping mop drying."""
        with pytest.raises(UnsupportedFeatureException):
            self.device.stop_mop_drying()

    def test_waterflow(self):
        assert self.device.waterflow() == WaterFlow.High

    def test_set_waterflow(self):
        self.device.set_waterflow(WaterFlow.High)


class DummyVacuumS7(DummyVacuum):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        self._model = ROCKROBO_S7
        self.state = {
            **self.state,
            **{
                "dry_status": 1,
                "rdt": 3600,
            },
        }
        self.dummies["water_box_custom_mode"] = [203]
        self.return_values = {
            **self.return_values,
            **{
                "app_get_dryer_setting": lambda x: {
                    "status": 1,
                    "on": {
                        "cliff_on": 1,
                        "cliff_off": 1,
                        "count": 10,
                        "dry_time": 10800,
                    },
                    "off": {"cliff_on": 2, "cliff_off": 1, "count": 10},
                },
                "app_set_dryer_setting": lambda x: ["ok"],
                "app_set_dryer_status": lambda x: ["ok"],
            },
        }


@pytest.fixture(scope="class")
def dummyvacuums7(request):
    request.cls.device = DummyVacuumS7()


@pytest.mark.usefixtures("dummyvacuums7")
class TestVacuumS7(TestCase):
    def test_mop_intensity(self):
        """Test getting mop intensity."""
        assert self.device.mop_intensity() == MopIntensity.Intense

    def test_set_mop_intensity(self):
        """Test setting mop intensity."""
        assert self.device.set_mop_intensity(MopIntensity.Intense)

    def test_mop_dryer_settings(self):
        """Test getting mop dryer settings."""
        assert self.device.mop_dryer_settings().enabled

    def test_mop_dryer_is_drying(self):
        """Test getting mop dryer status."""
        assert self.device.status().is_mop_drying

    def test_mop_dryer_remaining_seconds(self):
        """Test getting mop dryer remaining seconds."""
        assert self.device.status().mop_dryer_remaining_seconds == datetime.timedelta(
            seconds=3600
        )

    def test_set_mop_dryer_enabled_model_check(self):
        """Test setting mop dryer enabled."""
        with patch.object(self.device, "send", return_value=["ok"]) as mock_method:
            assert self.device.set_mop_dryer_enabled(enabled=False)
            mock_method.assert_called_once_with("app_set_dryer_setting", {"status": 0})

    def test_set_mop_dryer_dry_time_model_check(self):
        """Test setting mop dryer dry time."""
        with patch.object(self.device, "send", return_value=["ok"]) as mock_method:
            assert self.device.set_mop_dryer_dry_time(dry_time_seconds=14400)
            mock_method.assert_called_once_with(
                "app_set_dryer_setting", {"on": {"dry_time": 14400}}
            )

    def test_start_mop_drying_model_check(self):
        """Test starting mop drying."""
        assert self.device.start_mop_drying()

    def test_stop_mop_drying_model_check(self):
        """Test stopping mop drying."""
        assert self.device.stop_mop_drying()


class DummyVacuumQ7Max(DummyVacuum):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        self._model = ROCKROBO_Q7_MAX
        self.dummies["water_box_custom_mode"] = {
            "water_box_mode": 202,
            "distance_off": 205,
        }


@pytest.fixture(scope="class")
def dummyvacuumq7max(request):
    request.cls.device = DummyVacuumQ7Max()


@pytest.mark.usefixtures("dummyvacuumq7max")
class TestVacuumQ7Max(TestCase):
    def test_waterflow(self):
        assert self.device.waterflow() == WaterFlow.High

    def test_set_waterflow(self):
        self.device.set_waterflow(WaterFlow.High)
