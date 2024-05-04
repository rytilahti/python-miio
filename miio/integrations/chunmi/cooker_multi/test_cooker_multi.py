from unittest import TestCase

import pytest

from miio.tests.dummies import DummyDevice

from .cooker_multi import MultiCooker, OperationMode

COOKING_PROFILES = {
    "Fine rice": "02010000000001e101000000000000800101050814000000002091827d7800050091822d781c0a0091823c781c1e0091ff827820ffff91828278000500ffff8278ffffff91828278000d00ff828778ff000091827d7800000091827d7800ffff91826078ff0100490366780701086c0078090301af540266780801086c00780a02023c5701667b0e010a71007a0d02ffff5701667b0f010a73007d0d032005000000000000000000000000000000cf53",
    "Quick rice": "02010100000002e100280000000000800101050614000000002091827d7800000091823c7820000091823c781c1e0091ff827820ffff91828278000500ffff8278ffffff91828278000d00ff828778ff000082827d7800000091827d7800ffff91826078ff0164490366780701086c007409030200540266780801086c00760a0202785701667b0e010a7100780a02ffff5701667b0f010a73007b0a032005000000000000000000000000000000ddba",
    "Congee": "02010200000003e2011e0400002800800101050614000000002091827d7800000091827d7800000091827d78001e0091ff877820ffff91827d78001e0091ff8278ffffff91828278001e0091828278060f0091827d7804000091827d7800000091827d780001f54e0255261802062a0482030002eb4e0255261802062a04820300032d4e0252261802062c04820501ffff4e0152241802062c0482050120000000000000000000000000000000009ce2",
    "Keep warm": "020103000000040c00001800000100800100000000000000002091827d7800000091827d7800000091827d78000000915a7d7820000091827d7800000091826e78ff000091827d7800000091826e7810000091826e7810000091827d7800000091827d780000a082007882140010871478030000eb820078821400108714780300012d8200788214001087147a0501ffff8200788214001087147d0501200000000000000000000000000000000090e5",
}

TEST_CASES = {
    # Fine rice; Schedule 75; auto-keep-warm True
    "test_case_0": {
        "expected_profile": "02010000000001e1010000000000818f0101050814000000002091827d7800050091822d781c0a0091823c781c1e0091ff827820ffff91828278000500ffff8278ffffff91828278000d00ff828778ff000091827d7800000091827d7800ffff91826078ff0100490366780701086c0078090301af540266780801086c00780a02023c5701667b0e010a71007a0d02ffff5701667b0f010a73007d0d032005000000000000000000000000000000b557",
        "cooker_state": {
            "status": 4,
            "phase": 0,
            "menu": "0000000000000000000000000000000000000001",
            "t_cook": 60,
            "t_left": 3600,
            "t_pre": 75,
            "t_kw": 0,
            "taste": 8,
            "temp": 24,
            "rice": 261,
            "favs": "00000afe",
            "akw": 1,
            "t_start": 0,
            "t_finish": 0,
            "version": 13,
            "setting": 0,
            "code": 0,
            "en_warm": 9,
            "t_congee": 90,
            "t_love": 60,
            "boil": 0,
        },
    },
    # Fine rice; Schedule 75; auto-keep-warm False
    "test_case_1": {
        "expected_profile": "02010000000001e1010000000000810f0101050814000000002091827d7800050091822d781c0a0091823c781c1e0091ff827820ffff91828278000500ffff8278ffffff91828278000d00ff828778ff000091827d7800000091827d7800ffff91826078ff0100490366780701086c0078090301af540266780801086c00780a02023c5701667b0e010a71007a0d02ffff5701667b0f010a73007d0d03200500000000000000000000000000000049ee",
        "cooker_state": {
            "status": 4,
            "phase": 0,
            "menu": "0000000000000000000000000000000000000001",
            "t_cook": 60,
            "t_left": 3600,
            "t_pre": 75,
            "t_kw": 0,
            "taste": 8,
            "temp": 24,
            "rice": 261,
            "favs": "00000afe",
            "akw": 2,
            "t_start": 0,
            "t_finish": 0,
            "version": 13,
            "setting": 0,
            "code": 0,
            "en_warm": 8,
            "t_congee": 90,
            "t_love": 60,
            "boil": 0,
        },
    },
    # Quick rice; Schedule 75; auto-keep-warm False
    "test_case_2": {
        "expected_profile": "02010100000002e1002800000000810f0101050614000000002091827d7800000091823c7820000091823c781c1e0091ff827820ffff91828278000500ffff8278ffffff91828278000d00ff828778ff000082827d7800000091827d7800ffff91826078ff0164490366780701086c007409030200540266780801086c00760a0202785701667b0e010a7100780a02ffff5701667b0f010a73007b0a0320050000000000000000000000000000005b07",
        "cooker_state": {
            "status": 4,
            "phase": 0,
            "menu": "0101000000000000000000000000000000000002",
            "t_cook": 40,
            "t_left": 2400,
            "t_pre": 75,
            "t_kw": 0,
            "taste": 6,
            "temp": 24,
            "rice": 261,
            "favs": "00000afe",
            "akw": 2,
            "t_start": 0,
            "t_finish": 0,
            "version": 13,
            "setting": 0,
            "code": 0,
            "en_warm": 8,
            "t_congee": 90,
            "t_love": 60,
            "boil": 0,
        },
    },
    # Congee; auto-keep-warm False
    "test_case_3": {
        "expected_profile": "02010200000003e2011e0400002800000101050614000000002091827d7800000091827d7800000091827d78001e0091ff877820ffff91827d78001e0091ff8278ffffff91828278001e0091828278060f0091827d7804000091827d7800000091827d780001f54e0255261802062a0482030002eb4e0255261802062a04820300032d4e0252261802062c04820501ffff4e0152241802062c048205012000000000000000000000000000000000605b",
        "cooker_state": {
            "status": 2,
            "phase": 0,
            "menu": "0202000000000000000000000000000000000003",
            "t_cook": 90,
            "t_left": 5396,
            "t_pre": 75,
            "t_kw": 0,
            "taste": 6,
            "temp": 24,
            "rice": 261,
            "favs": "00000afe",
            "akw": 2,
            "t_start": 0,
            "t_finish": 0,
            "version": 13,
            "setting": 0,
            "code": 0,
            "en_warm": 8,
            "t_congee": 90,
            "t_love": 60,
            "boil": 0,
        },
    },
    # Keep warm; Duration 55
    "test_case_4": {
        "expected_profile": "020103000000040c00371800000100800100000000000000002091827d7800000091827d7800000091827d78000000915a7d7820000091827d7800000091826e78ff000091827d7800000091826e7810000091826e7810000091827d7800000091827d780000a082007882140010871478030000eb820078821400108714780300012d8200788214001087147a0501ffff8200788214001087147d050120000000000000000000000000000000001ab9",
        "cooker_state": {
            "status": 2,
            "phase": 0,
            "menu": "0303000000000000000000000000000000000004",
            "t_cook": 55,
            "t_left": 5,
            "t_pre": 75,
            "t_kw": 0,
            "taste": 0,
            "temp": 24,
            "rice": 0,
            "favs": "00000afe",
            "akw": 1,
            "t_start": 0,
            "t_finish": 0,
            "version": 13,
            "setting": 0,
            "code": 0,
            "en_warm": 8,
            "t_congee": 90,
            "t_love": 60,
            "boil": 0,
        },
    },
}

DEFAULT_STATE = {
    "status": 1,  # Waiting
    "phase": 0,  # Current cooking phase: Unknown / No stage
    "menu": "0000000000000000000000000000000000000001",  # Menu: Fine Rice
    "t_cook": 60,  # Total cooking time for the menu
    "t_left": 3600,  # Remaining cooking time for the menu
    "t_pre": 0,  # Remaining pre cooking time
    "t_kw": 0,  # Keep warm time after finish cooking the menu
    "taste": 8,  # Taste setting
    "temp": 24,  # Current temperature
    "rice": 261,  # Rice setting
    "favs": "00000afe",  # Current favorite menu configured
    "akw": 0,  # Keep warm enabled
    "t_start": 0,
    "t_finish": 0,
    "version": 13,
    "setting": 0,
    "code": 0,
    "en_warm": 15,
    "t_congee": 90,
    "t_love": 60,
    "boil": 0,
}


class DummyMultiCooker(DummyDevice, MultiCooker):
    def __init__(self, *args, **kwargs):
        self.state = DEFAULT_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_start": lambda x: self.set_start(x),
            "cancel_cooking": lambda _: self.cancel_cooking(),
        }
        super().__init__(args, kwargs)

    def set_start(self, profile):
        state = DEFAULT_STATE

        for test_case in TEST_CASES:
            if profile == [TEST_CASES[test_case]["expected_profile"]]:
                state = TEST_CASES[test_case]["cooker_state"]

        for prop in state:
            self._set_state(prop, [state[prop]])

    def cancel_cooking(self):
        for prop in DEFAULT_STATE:
            self._set_state(prop, [DEFAULT_STATE[prop]])


@pytest.fixture(scope="class")
def multicooker(request):
    request.cls.device = DummyMultiCooker()


@pytest.mark.usefixtures("multicooker")
class TestMultiCooker(TestCase):
    def test_case_0(self):
        self.device.start(COOKING_PROFILES["Fine rice"], None, 75, True)
        status = self.device.status()
        assert status.mode == OperationMode.PreCook
        assert status.menu == "Fine Rice"
        assert status.delay_remaining == 75 - 60
        assert status.remaining == 75
        assert status.keep_warm is True
        self.device.stop()

    def test_case_1(self):
        self.device.start(COOKING_PROFILES["Fine rice"], None, 75, False)
        status = self.device.status()
        assert status.mode == OperationMode.PreCook
        assert status.menu == "Fine Rice"
        assert status.delay_remaining == 75 - 60
        assert status.remaining == 75
        assert status.keep_warm is False
        self.device.stop()

    def test_case_2(self):
        self.device.start(COOKING_PROFILES["Quick rice"], None, 75, False)
        status = self.device.status()
        assert status.mode == OperationMode.PreCook
        assert status.menu == "Quick Rice"
        assert status.delay_remaining == 75 - 40
        assert status.remaining == 75
        assert status.keep_warm is False
        self.device.stop()

    def test_case_3(self):
        self.device.start(COOKING_PROFILES["Congee"], None, None, False)
        status = self.device.status()
        assert status.mode == OperationMode.Running
        assert status.menu == "Congee"
        assert status.keep_warm is False
        self.device.stop()

    def test_case_4(self):
        self.device.start(COOKING_PROFILES["Keep warm"], 55, None, None)
        status = self.device.status()
        assert status.mode == OperationMode.Running
        assert status.menu == "Keep warm"
        assert status.duration == 55
        self.device.stop()
