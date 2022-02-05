from collections import OrderedDict
from unittest import TestCase

import pytest

from miio import AirHumidifierJsq,AirHumidifierJsq002
from miio.airhumidifier import AirHumidifierException
from miio.airhumidifier_jsq import (
    AVAILABLE_PROPERTIES,
    MODEL_HUMIDIFIER_JSQ001,
    AirHumidifierStatus,
    LedBrightness,
    OperationMode,
    MODEL_HUMIDIFIER_JSQ002,
    AirHumidifierStatusJsq002,
    OperationModeJsq002,
    LedBrightnessJsq002
)

from .dummies import DummyDevice


class DummyAirHumidifierJsq001(DummyDevice, AirHumidifierJsq):
    def __init__(self, *args, **kwargs):
        self._model = MODEL_HUMIDIFIER_JSQ001

        self.dummy_device_info = {
            "life": 575661,
            "token": "68ffffffffffffffffffffffffffffff",
            "mac": "78:11:FF:FF:FF:FF",
            "fw_ver": "1.3.9",
            "hw_ver": "ESP8266",
            "uid": "1111111111",
            "model": self.model,
            "mcu_fw_ver": "0001",
            "wifi_fw_ver": "1.5.0-dev(7efd021)",
            "ap": {"rssi": -71, "ssid": "ap", "bssid": "FF:FF:FF:FF:FF:FF"},
            "netif": {
                "gw": "192.168.0.1",
                "localIp": "192.168.0.25",
                "mask": "255.255.255.0",
            },
            "mmfree": 228248,
        }

        self.device_info = None

        self.state = OrderedDict(
            (
                ("temperature", 24),
                ("humidity", 29),
                ("mode", 3),
                ("buzzer", 1),
                ("child_lock", 1),
                ("led_brightness", 2),
                ("power", 1),
                ("no_water", 1),
                ("lid_opened", 1),
            )
        )
        self.start_state = self.state.copy()

        self.return_values = {
            "get_props": self._get_state,
            "set_start": lambda x: self._set_state("power", x),
            "set_mode": lambda x: self._set_state("mode", x),
            "set_brightness": lambda x: self._set_state("led_brightness", x),
            "set_buzzer": lambda x: self._set_state("buzzer", x),
            "set_lock": lambda x: self._set_state("child_lock", x),
            "miIO.info": self._get_device_info,
        }

        super().__init__(args, kwargs)

    def _get_device_info(self, _):
        """Return dummy device info."""
        return self.dummy_device_info

    def _get_state(self, props):
        """Return wanted properties."""
        return list(self.state.values())


class DummyAirHumidifierJsq002(DummyDevice, AirHumidifierJsq002):
    def _set_state_by_key(self, key, value):
        self._set_state(
            self._available_properties.index(key),
            value
        )

    def _get_state_by_key(self, key):
        return self.state[self._available_properties.index(key)]

    def __init__(self, *args, **kwargs):
        self._model = MODEL_HUMIDIFIER_JSQ002

        self.dummy_device_info = {
            "fw_ver": "1.4.0",
            "hw_ver": "ESP8266",
        }

        self.start_state = [1, 2, 36, 2, 46, 4, 1, 1, 1, 50, 51, 0]
        self.state = self.start_state.copy()

        # Mocks for `device.send("cmd_name", args)` commands:
        self._available_properties = AVAILABLE_PROPERTIES[self._model]

        self.return_values = {
            "get_props": self._get_state,
            "on_off": lambda x: self._set_state_by_key("power", x),
            "set_gear": lambda x: self._set_state_by_key("mode", x),
            "set_led": lambda x: self._set_state_by_key("led_brightness", x),
            "warm_on": lambda x: self._set_state_by_key("heat", x),
            "buzzer_on": lambda x: self._set_state_by_key("buzzer", x),
            "set_lock": lambda x: self._set_state_by_key("child_lock", x),
            "set_temp": lambda x: self._set_state_by_key("target_temperature", x),
            "set_humidity": lambda x: self._set_state_by_key("target_humidity", x),
            # "corrected_water": ?
            # "rst_clean": ?
            "miIO.info": self._get_device_info,
        }

        super().__init__(args, kwargs)

    def _get_state(self, props):
        """Mocks device `get_props` command """
        return self.state

    def _get_device_info(self, _):
        """Return dummy device info."""
        return self.dummy_device_info


@pytest.fixture(scope="class")
def airhumidifier_jsq001(request):
    request.cls.device = DummyAirHumidifierJsq001()


@pytest.fixture(scope="class")
def airhumidifier_jsq002(request):
    request.cls.device = DummyAirHumidifierJsq002()


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class AirHumidifierJsqTestCase(TestCase):
    def state(self):
        return self.device.status()

    def _is_on(self):
        return self.device.status().is_on

    def do_test_on_off_property(self, setter_name, getter_name):
        def prop_value():
            return getattr(self.device.status(), getter_name)

        prop_fun = getattr(self.device, setter_name)
        prop_fun(True)
        assert prop_value() is True

        prop_fun(False)
        assert prop_value() is False

        # if user uses wrong type for buzzer value
        prop_fun(1)
        assert prop_value() is True

        prop_fun(0)
        assert prop_value() is False

        prop_fun("not_empty_str")
        assert prop_value() is True

        prop_fun("on")
        assert prop_value() is True

        # all string values are considered to by True, even "off"
        prop_fun("off")
        assert prop_value() is True

        prop_fun("")
        assert prop_value() is False


@pytest.mark.usefixtures("airhumidifier_jsq001")
class TestAirHumidifierJsq001(AirHumidifierJsqTestCase):
    def test_on(self):
        self.device.off()  # ensure off
        assert self._is_on() is False

        self.device.on()
        assert self._is_on() is True

    def test_off(self):
        self.device.on()  # ensure on
        assert self._is_on() is True

        self.device.off()
        assert self._is_on() is False

    def test_status(self):
        self.device._reset_state()

        assert repr(self.state()) == repr(AirHumidifierStatus(self.device.start_state))

        assert self.state().temperature == self.device.start_state["temperature"]
        assert self.state().humidity == self.device.start_state["humidity"]
        assert self.state().mode == OperationMode(self.device.start_state["mode"])
        assert self.state().buzzer == (self.device.start_state["buzzer"] == 1)
        assert self.state().child_lock == (self.device.start_state["child_lock"] == 1)
        assert self.state().led_brightness == LedBrightness(
            self.device.start_state["led_brightness"]
        )
        assert self._is_on() is True
        assert self.state().no_water == (self.device.start_state["no_water"] == 1)
        assert self.state().lid_opened == (self.device.start_state["lid_opened"] == 1)

    def test_status_wrong_input(self):
        def mode():
            return self.device.status().mode

        def led_brightness():
            return self.device.status().led_brightness

        self.device._reset_state()

        self.device.state["mode"] = 10
        assert mode() == OperationMode.Intelligent

        self.device.state["mode"] = "smth"
        assert mode() == OperationMode.Intelligent

        self.device.state["led_brightness"] = 10
        assert led_brightness() == LedBrightness.Off

        self.device.state["led_brightness"] = "smth"
        assert led_brightness() == LedBrightness.Off

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Intelligent)
        assert mode() == OperationMode.Intelligent

        self.device.set_mode(OperationMode.Level1)
        assert mode() == OperationMode.Level1

        self.device.set_mode(OperationMode.Level4)
        assert mode() == OperationMode.Level4

    def test_set_mode_wrong_input(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Level3)
        assert mode() == OperationMode.Level3

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_mode(Bunch(value=10))
        assert str(excinfo.value) == "10 is not a valid OperationMode value"
        assert mode() == OperationMode.Level3

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_mode(Bunch(value=-1))
        assert str(excinfo.value) == "-1 is not a valid OperationMode value"
        assert mode() == OperationMode.Level3

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_mode(Bunch(value="smth"))
        assert str(excinfo.value) == "smth is not a valid OperationMode value"
        assert mode() == OperationMode.Level3

    def test_set_led_brightness(self):
        def led_brightness():
            return self.device.status().led_brightness

        self.device.set_led_brightness(LedBrightness.Off)
        assert led_brightness() == LedBrightness.Off

        self.device.set_led_brightness(LedBrightness.Low)
        assert led_brightness() == LedBrightness.Low

        self.device.set_led_brightness(LedBrightness.High)
        assert led_brightness() == LedBrightness.High

    def test_set_led_brightness_wrong_input(self):
        def led_brightness():
            return self.device.status().led_brightness

        self.device.set_led_brightness(LedBrightness.Low)
        assert led_brightness() == LedBrightness.Low

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_led_brightness(Bunch(value=10))
        assert str(excinfo.value) == "10 is not a valid LedBrightness value"
        assert led_brightness() == LedBrightness.Low

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_led_brightness(Bunch(value=-10))
        assert str(excinfo.value) == "-10 is not a valid LedBrightness value"
        assert led_brightness() == LedBrightness.Low

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_led_brightness(Bunch(value="smth"))
        assert str(excinfo.value) == "smth is not a valid LedBrightness value"
        assert led_brightness() == LedBrightness.Low

    def test_set_led(self):
        def led_brightness():
            return self.device.status().led_brightness

        self.device.set_led(True)
        assert led_brightness() == LedBrightness.High

        self.device.set_led(False)
        assert led_brightness() == LedBrightness.Off

    def test_set_buzzer(self):
        self.do_test_on_off_property("set_buzzer", "buzzer")

    def test_status_without_temperature(self):
        self.device._reset_state()
        self.device.state["temperature"] = None

        assert self.state().temperature is None

    def test_status_without_led_brightness(self):
        self.device._reset_state()
        self.device.state["led_brightness"] = None

        assert self.state().led_brightness is LedBrightness.Off

    def test_status_without_mode(self):
        self.device._reset_state()
        self.device.state["mode"] = None

        assert self.state().mode is OperationMode.Intelligent

    def test_set_child_lock(self):
        self.do_test_on_off_property("set_child_lock", "child_lock")


@pytest.mark.usefixtures("airhumidifier_jsq002")
class TestAirHumidifierJsq002(AirHumidifierJsqTestCase):
    def test_status(self):
        self.device._reset_state()

        state: AirHumidifierStatusJsq002 = self.state()
        properties = AVAILABLE_PROPERTIES[MODEL_HUMIDIFIER_JSQ002]
        assert repr(state) == repr(AirHumidifierStatusJsq002({
            k: v for k, v in zip(properties, self.device.start_state)
        }))

        assert state.data['power'] == 1
        assert self._is_on() is True

        assert state.data['mode'] == 2
        assert state.mode == OperationModeJsq002.Level2

        assert state.data['humidity'] == 36
        assert state.humidity == 36

        assert state.data['led_brightness'] == 2
        assert state.led_brightness == LedBrightnessJsq002.Low

        assert state.data['temperature'] == 46
        assert state.temperature == 26

        assert state.data['water_level'] == 4
        assert state.water_level == 4

        assert state.data['heat'] == 1
        assert state.heater is True

        assert state.data['buzzer'] == 1
        assert state.buzzer is True

        assert state.data['child_lock'] == 1
        assert state.child_lock is True

        assert state.data['target_temperature'] == 50
        assert state.water_target_temperature == 50

        assert state.data['target_humidity'] == 51
        assert state.target_humidity == 51

        assert state.data['reserved'] == 0

    def test_on(self):
        self.device.off()  # ensure off
        assert self._is_on() is False

        self.device.on()
        assert self._is_on() is True

    def test_off(self):
        self.device.on()  # ensure on
        assert self._is_on() is True

        self.device.off()
        assert self._is_on() is False

    def test_status_wrong_input(self):
        def mode():
            return self.device.status().mode

        def set_mock_state_mode(new_mode):
            self.device._set_state_by_key("mode", [new_mode])

        def set_mock_state_brightness(new_val):
            self.device._set_state_by_key("led_brightness", [new_val])

        def led_brightness():
            return self.device.status().led_brightness

        def water_level():
            return self.device.status().water_level

        def set_mock_water_level(new_val):
            self.device._set_state_by_key("water_level", [new_val])

        self.device._reset_state()

        set_mock_state_mode(10)
        assert mode() == OperationModeJsq002.Level1

        set_mock_state_mode(10)
        assert mode() == OperationModeJsq002.Level1

        set_mock_state_brightness(10)
        assert led_brightness() == LedBrightnessJsq002.Off

        set_mock_state_brightness("smth")
        assert led_brightness() == LedBrightnessJsq002.Off

        set_mock_water_level(10)
        assert water_level() == 5

        set_mock_water_level("smth")
        assert water_level() == 5

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationModeJsq002.Level1)
        assert mode() == OperationModeJsq002.Level1

        self.device.set_mode(OperationModeJsq002.Level2)
        assert mode() == OperationModeJsq002.Level2

        self.device.set_mode(OperationModeJsq002.Level3)
        assert mode() == OperationModeJsq002.Level3

    def test_set_mode_wrong_input(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationModeJsq002.Level3)
        assert mode() == OperationModeJsq002.Level3

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_mode(Bunch(value=10))
        assert str(excinfo.value) == "10 is not a valid OperationModeJsq2 value"
        assert mode() == OperationModeJsq002.Level3

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_mode(Bunch(value=-1))
        assert str(excinfo.value) == "-1 is not a valid OperationModeJsq2 value"
        assert mode() == OperationModeJsq002.Level3

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_mode(Bunch(value="smth"))
        assert str(excinfo.value) == "smth is not a valid OperationModeJsq2 value"
        assert mode() == OperationModeJsq002.Level3

    def test_set_led_brightness(self):
        def led_brightness():
            return self.device.status().led_brightness

        self.device.set_led_brightness(LedBrightnessJsq002.Off)
        assert led_brightness() == LedBrightnessJsq002.Off

        self.device.set_led_brightness(LedBrightnessJsq002.Low)
        assert led_brightness() == LedBrightnessJsq002.Low

        self.device.set_led_brightness(LedBrightnessJsq002.High)
        assert led_brightness() == LedBrightnessJsq002.High

    def test_set_led_brightness_wrong_input(self):
        def led_brightness():
            return self.device.status().led_brightness

        self.device.set_led_brightness(LedBrightnessJsq002.Low)
        assert led_brightness() == LedBrightnessJsq002.Low

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_led_brightness(Bunch(value=10))
        assert str(excinfo.value) == "10 is not a valid LedBrightnessJsq2 value"
        assert led_brightness() == LedBrightnessJsq002.Low

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_led_brightness(Bunch(value=-10))
        assert str(excinfo.value) == "-10 is not a valid LedBrightnessJsq2 value"
        assert led_brightness() == LedBrightnessJsq002.Low

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_led_brightness(Bunch(value="smth"))
        assert str(excinfo.value) == "smth is not a valid LedBrightnessJsq2 value"
        assert led_brightness() == LedBrightnessJsq002.Low

    def test_set_led(self):
        def led_brightness():
            return self.device.status().led_brightness

        self.device.set_led(True)
        assert led_brightness() == LedBrightnessJsq002.High

        self.device.set_led(False)
        assert led_brightness() == LedBrightnessJsq002.Off

    def test_no_water(self):
        def set_mock_water_level(new_val):
            self.device._set_state_by_key("water_level", [new_val])

        def no_water():
            return self.device.status().no_water

        set_mock_water_level(1)
        assert no_water() is False

        set_mock_water_level(0)
        assert no_water() is True

        set_mock_water_level(6)
        assert no_water() is False

    def test_set_heater(self):
        self.do_test_on_off_property("set_heater", "heater")

    def test_set_buzzer(self):
        self.do_test_on_off_property("set_buzzer", "buzzer")

    def test_set_child_lock(self):
        self.do_test_on_off_property("set_child_lock", "child_lock")

    def test_set_target_temperature(self):
        def water_target_temp():
            return self.device.status().water_target_temperature

        self.device.set_target_temperature(30)
        assert water_target_temp() == 30

        self.device.set_target_temperature(31)
        assert water_target_temp() == 31

        self.device.set_target_temperature(59)
        assert water_target_temp() == 59

        self.device.set_target_temperature(60)
        assert water_target_temp() == 60

    def test_set_target_temperature_wrong_input(self):
        def water_target_temp():
            return self.device.status().water_target_temperature

        self.device.set_target_temperature(40)
        assert water_target_temp() == 40

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_target_temperature(29)
        assert str(excinfo.value) == "Invalid water target temperature, should be in [30..60]. But was: 29"
        assert water_target_temp() == 40

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_target_temperature(61)
        assert str(excinfo.value) == "Invalid water target temperature, should be in [30..60]. But was: 61"
        assert water_target_temp() == 40

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_target_temperature(-10)
        assert str(excinfo.value) == "Invalid water target temperature, should be in [30..60]. But was: -10"
        assert water_target_temp() == 40

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_target_temperature("smth")
        assert str(excinfo.value) == "Invalid water target temperature, should be in [30..60]. But was: smth"
        assert water_target_temp() == 40

    def test_set_target_humidity(self):
        def target_humidity():
            return self.device.status().target_humidity

        self.device.set_target_humidity(0)
        assert target_humidity() == 0

        self.device.set_target_humidity(31)
        assert target_humidity() == 31

        self.device.set_target_humidity(99)
        assert target_humidity() == 99

        # self.device.set_target_humidity(160)
        # assert target_humidity() == 160

    def test_set_target_humidity_wrong_input(self):
        def target_humidity():
            return self.device.status().target_humidity

        self.device.set_target_humidity(40)
        assert target_humidity() == 40

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_target_humidity(-10)
        assert str(excinfo.value) == "Invalid target humidity, should be in [0..99]. But was: -10"
        assert target_humidity() == 40

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_target_humidity(100)
        assert str(excinfo.value) == "Invalid target humidity, should be in [0..99]. But was: 100"
        assert target_humidity() == 40

        with pytest.raises(AirHumidifierException) as excinfo:
            self.device.set_target_humidity("smth")
        assert str(excinfo.value) == "Invalid target humidity, should be in [0..99]. But was: smth"
        assert target_humidity() == 40

    # def test_status_without_temperature(self):
    #     self.device._reset_state()
    #     self.device.state["temperature"] = None
    #
    #     assert self.state().temperature is None
    #
    # def test_status_without_led_brightness(self):
    #     self.device._reset_state()
    #     self.device.state["led_brightness"] = None
    #
    #     assert self.state().led_brightness is LedBrightness.Off
    #
    # def test_status_without_mode(self):
    #     self.device._reset_state()
    #     self.device.state["mode"] = None
    #
    #     assert self.state().mode is OperationMode.Intelligent
    #
