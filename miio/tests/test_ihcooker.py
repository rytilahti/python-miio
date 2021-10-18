import string
from unittest import TestCase

import pytest

from miio import IHCooker, ihcooker

# V2 state from @aquarat
# ['running', '01484f54504f540000000000000000000000000000000000000000000000000001', '00306300b9', '0200013b00000000', '000a1404', '0000000100000002000000030000000400000005000000000000000000000000', '01', '0000ea4a6330303400'
from ..ihcooker import StageMode
from .dummies import DummyDevice

# V1 state from @EUA
# ['waiting', '02537465616d2f626f696c000000000002', '0013000000', '0100010000000000', '001b0a04', '00000001000000020000000300000004000000050000a4e000000dcc00000000', '00', '0000e60a0017130f00']


class DummyIHCookerV2(DummyDevice, IHCooker):
    def __init__(self, *args, **kwargs):
        self._model = ihcooker.MODEL_EXP1

        self.state = [
            "running",
            "08526963650000000000000000000000000000000000000000000000000000001e",
            "033c14083c",
            "000f000400000000",
            "000d1404",
            "0000000100000002000000030000000400000005000000180000001a0000001e",
            "01",
            "0306eb0a001d3c3c00",
        ]
        self.return_values = {
            "get_prop": self._get_state,
            "set_start": lambda profile: self._validate_profile(profile[0]),
            "set_menu1": lambda profile: self._validate_profile(profile[0]),
        }
        super().__init__(args, kwargs)

    def _get_state(self, vars):
        """Return wanted properties."""
        assert vars == ["all"], "Only get_props all is supported"
        return self.state

    @staticmethod
    def _validate_profile(profile):
        """Validates if profile is a valid string."""
        assert all(c in string.hexdigits for c in profile) and len(profile) == 358


class DummyIHCookerV1(DummyIHCookerV2):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self._model = ihcooker.MODEL_V1

        self.state = [
            "waiting",
            "02537465616d2f626f696c000000000002",
            "0013000000",
            "0100010000000000",
            "001b0a04",
            "00000001000000020000000300000004000000050000a4e000000dcc00000000",
            "00",
            "0000e60a0017130f00",
        ]


@pytest.fixture(scope="class")
def ihcooker_exp1(request):
    request.cls.device = DummyIHCookerV2()


@pytest.fixture(scope="class")
def ihcooker_v1(request):
    request.cls.device = DummyIHCookerV1()


@pytest.mark.usefixtures("ihcooker_exp1")
class TestIHCookerV2(TestCase):
    def state(self):
        return self.device.status()

    def test_recipe(self):
        recipe = {}
        self.device.start(recipe)

    def test_set_menu(self):
        recipe = {}
        self.device.set_menu(recipe, 1)

    def test_start_temp(self):
        self.device.start_temp(temperature=30, minutes=30)

    def test_construct(self):
        recipe = (
            "030405546573740a52656369706500000000000000000000000000000000000000000003ea0000000"
            "000000000000100008005323c111113028006333d121012188007343e130f11000000f93e00141400"
            "0000f93e001414000000f93e001414000000f93e001414000000f93e001414000000f93e001414000"
            "000f93e001414000000f93e001414000000f93e001414000000f93e001414000000f93e0014140000"
            "00f93e001414000000000000000000df87"
        )

        res = ihcooker.profile_v2.parse(bytes.fromhex(recipe))
        self.assertEqual(ihcooker.profile_v2.parse(ihcooker.profile_v2.build(res)), res)
        self.assertEqual(len(ihcooker.profile_v2.build(res)), len(recipe) // 2)
        self.assertEqual(str(ihcooker.profile_v2.build(res).hex()), recipe)

    def test_phases(self):
        profile = dict(
            device_version=4,
            duration_minutes=115,
            recipe_id=1002,
            recipe_name="Test Recipe",
            menu_location=5,
            menu_settings=dict(save_recipe=True),
            stages=[
                dict(
                    mode=StageMode.FireMode,
                    temp_target=60,
                    temp_threshold=50,
                    minutes=115,
                    power=17,
                    fire_on=19,
                    fire_off=17,
                ),
                dict(
                    mode=StageMode.TemperatureMode,
                    temp_target=61,
                    temp_threshold=51,
                    minutes=6,
                    power=18,
                    fire_on=18,
                    fire_off=16,
                ),
                dict(
                    mode=StageMode.TempAutoBigPot,
                    temp_target=62,
                    temp_threshold=52,
                    minutes=7,
                    power=19,
                    fire_on=17,
                    fire_off=15,
                ),
                dict(
                    mode=StageMode.TempAutoBigPot,
                    temp_target=62,
                    temp_threshold=52,
                    minutes=7,
                    power=19,
                    fire_on=17,
                    fire_off=15,
                ),
            ],
            crc=0,
        )

        bytes_recipe = ihcooker.profile_v2.build(profile)
        hex_recipe = bytes_recipe.hex()
        self.assertEqual(
            "030405546573740a52656369706500000000000000000000000000000000000000000003ea8001370000000000000100008137323c111113028006333d121012188007343e130f11188007343e130f11008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d14140000000000000000000a6b",
            hex_recipe,
        )
        self.assertEqual(
            hex_recipe,
            ihcooker.profile_v2.build(ihcooker.profile_v2.parse(bytes_recipe)).hex(),
        )
        self.assertEqual(115, ihcooker.profile_v2.parse(bytes_recipe).duration_minutes)

    def test_crc(self):
        recipe = {}
        self.device.start(recipe)

    def test_mode(self):
        self.assertEqual(ihcooker.OperationMode.Running, self.state().mode)

    def test_temperature(self):
        self.assertEqual(60, self.state().temperature)

    def test_target_temp(self):
        self.assertEqual(60, self.state().target_temp)

    def test_menu_text(self):
        self.assertEqual("Rice", self.state().recipe_name)

    def test_recipe_id(self):
        self.assertEqual(30, self.state().recipe_id)

    def test_stage(self):
        self.assertEqual(3, self.state().stage)

    def test_stage_mode(self):
        self.assertEqual(8, self.state().stage_mode)


@pytest.mark.usefixtures("ihcooker_v1")
class TestIHCookerv1(TestCase):
    def state(self):
        return self.device.status()

    def test_recipe(self):
        recipe = {}
        self.device.start(recipe)

    def test_set_menu(self):
        recipe = {}
        self.device.set_menu(recipe, 1)

    def test_start_temp(self):
        self.device.start_temp(temperature=30, minutes=30)

    def test_construct(self):
        recipe = "030405546573740a52656369706500000000000000000000000000000000000000000000000000000000000000000100008005323c111113028006333d121012188007343e130f11000000f93e001414000000f93e001414000000f93e001414000000f93e001414000000f93e001414000000f93e001414000000f93e001414000000f93e001414000000f93e001414000000f93e001414000000f93e000000000000000000000000000000000000000071ba"
        res = ihcooker.profile_v1.parse(bytes.fromhex(recipe))
        self.assertEqual(len(ihcooker.profile_v1.build(res)), len(recipe) // 2)
        self.assertEqual(str(ihcooker.profile_v1.build(res).hex()), recipe)

    def test_phases(self):
        profile = dict(
            device_version=4,
            duration_minutes=115,
            recipe_id=1002,
            recipe_name="Test Recipe",
            menu_location=5,
            menu_settings=dict(save_recipe=True),
            stages=[
                dict(
                    mode=StageMode.FireMode,
                    temp_target=60,
                    temp_threshold=50,
                    minutes=115,
                    power=17,
                    fire_on=19,
                    fire_off=17,
                ),
                dict(
                    mode=StageMode.TemperatureMode,
                    temp_target=61,
                    temp_threshold=51,
                    minutes=6,
                    power=18,
                    fire_on=18,
                    fire_off=16,
                ),
                dict(
                    mode=StageMode.TempAutoBigPot,
                    temp_target=62,
                    temp_threshold=52,
                    minutes=7,
                    power=19,
                    fire_on=17,
                    fire_off=15,
                ),
                dict(
                    mode=StageMode.TempAutoBigPot,
                    temp_target=62,
                    temp_threshold=52,
                    minutes=7,
                    power=19,
                    fire_on=17,
                    fire_off=15,
                ),
            ],
            crc=0,
        )

        bytes_recipe = ihcooker.profile_v1.build(profile)
        hex_recipe = bytes_recipe.hex()
        self.assertEqual(
            "030405546573740a526563697065000000000003ea8001370000000000000100000000000000008137323c111113028006333d121012188007343e130f11188007343e130f11008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d1414008000f9e52d14140000000000000000000000000000000000000005ce",
            hex_recipe,
        )
        self.assertEqual(
            hex_recipe,
            ihcooker.profile_v1.build(ihcooker.profile_v1.parse(bytes_recipe)).hex(),
        )

    def test_mode(self):
        self.assertEqual(ihcooker.OperationMode.Waiting, self.state().mode)

    def test_temperature(self):
        self.assertEqual(19, self.state().temperature)

    def test_target_temp(self):
        self.assertEqual(0, self.state().target_temp)

    def test_menu_text(self):
        self.assertEqual("Steam/boil", self.state().recipe_name)

    def test_recipe_id(self):
        self.assertEqual(2, self.state().recipe_id)

    def test_stage(self):
        self.assertEqual(0, self.state().stage)

    def test_stage_mode(self):
        self.assertEqual(0, self.state().stage_mode)
