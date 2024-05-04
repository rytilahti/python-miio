import pytest

from miio.tests.dummies import DummyMiotDevice

from .. import AirHumidifierMiotCA6
from ..airhumidifier_miot import LedBrightness, OperationModeCA6, OperationStatusCA6

_INITIAL_STATE = {
    "power": True,
    "fault": 0,
    "mode": 0,
    "target_humidity": 40,
    "water_level": 1,
    "dry": True,
    "status": 2,
    "temperature": 19,
    "humidity": 51,
    "buzzer": False,
    "led_brightness": 2,
    "child_lock": False,
    "actual_speed": 1100,
    "clean_mode": False,
    "self_clean_percent": 0,
    "pump_state": False,
    "pump_cnt": 1000,
}


class DummyAirHumidifierMiotCA6(DummyMiotDevice, AirHumidifierMiotCA6):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_speed": lambda x: self._set_state("speed_level", x),
            "set_target_humidity": lambda x: self._set_state("target_humidity", x),
            "set_mode": lambda x: self._set_state("mode", x),
            "set_led_brightness": lambda x: self._set_state("led_brightness", x),
            "set_buzzer": lambda x: self._set_state("buzzer", x),
            "set_child_lock": lambda x: self._set_state("child_lock", x),
            "set_dry": lambda x: self._set_state("dry", x),
            "set_clean_mode": lambda x: self._set_state("clean_mode", x),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture()
def dev(request):
    yield DummyAirHumidifierMiotCA6()


def test_on(dev):
    dev.off()  # ensure off
    assert dev.status().is_on is False

    dev.on()
    assert dev.status().is_on is True


def test_off(dev):
    dev.on()  # ensure on
    assert dev.status().is_on is True

    dev.off()
    assert dev.status().is_on is False


def test_status(dev):
    status = dev.status()
    assert status.is_on is _INITIAL_STATE["power"]
    assert status.error == _INITIAL_STATE["fault"]
    assert status.mode == OperationModeCA6(_INITIAL_STATE["mode"])
    assert status.target_humidity == _INITIAL_STATE["target_humidity"]
    assert status.water_level == {0: 0, 1: 50, 2: 100}.get(
        int(_INITIAL_STATE["water_level"])
    )
    assert status.dry == _INITIAL_STATE["dry"]
    assert status.temperature == _INITIAL_STATE["temperature"]
    assert status.humidity == _INITIAL_STATE["humidity"]
    assert status.buzzer == _INITIAL_STATE["buzzer"]
    assert status.led_brightness == LedBrightness(_INITIAL_STATE["led_brightness"])
    assert status.child_lock == _INITIAL_STATE["child_lock"]
    assert status.actual_speed == _INITIAL_STATE["actual_speed"]
    assert status.actual_speed == _INITIAL_STATE["actual_speed"]
    assert status.clean_mode == _INITIAL_STATE["clean_mode"]
    assert status.self_clean_percent == _INITIAL_STATE["self_clean_percent"]
    assert status.pump_state == _INITIAL_STATE["pump_state"]
    assert status.pump_cnt == _INITIAL_STATE["pump_cnt"]


def test_set_target_humidity(dev):
    def target_humidity():
        return dev.status().target_humidity

    dev.set_target_humidity(30)
    assert target_humidity() == 30
    dev.set_target_humidity(60)
    assert target_humidity() == 60

    with pytest.raises(ValueError):
        dev.set_target_humidity(29)

    with pytest.raises(ValueError):
        dev.set_target_humidity(61)


def test_set_mode(dev):
    def mode():
        return dev.status().mode

    dev.set_mode(OperationModeCA6.Auto)
    assert mode() == OperationModeCA6.Auto

    dev.set_mode(OperationModeCA6.Fav)
    assert mode() == OperationModeCA6.Fav

    dev.set_mode(OperationModeCA6.Sleep)
    assert mode() == OperationModeCA6.Sleep


def test_set_led_brightness(dev):
    def led_brightness():
        return dev.status().led_brightness

    dev.set_led_brightness(LedBrightness.Bright)
    assert led_brightness() == LedBrightness.Bright

    dev.set_led_brightness(LedBrightness.Dim)
    assert led_brightness() == LedBrightness.Dim

    dev.set_led_brightness(LedBrightness.Off)
    assert led_brightness() == LedBrightness.Off


def test_set_buzzer(dev):
    def buzzer():
        return dev.status().buzzer

    dev.set_buzzer(True)
    assert buzzer() is True

    dev.set_buzzer(False)
    assert buzzer() is False


def test_set_child_lock(dev):
    def child_lock():
        return dev.status().child_lock

    dev.set_child_lock(True)
    assert child_lock() is True

    dev.set_child_lock(False)
    assert child_lock() is False


def test_set_dry(dev):
    def dry():
        return dev.status().dry

    dev.set_dry(True)
    assert dry() is True

    dev.set_dry(False)
    assert dry() is False


def test_set_clean_mode(dev):
    def clean_mode():
        return dev.status().clean_mode

    dev.set_clean_mode(True)
    assert clean_mode() is True

    dev.set_clean_mode(False)
    assert clean_mode() is False


@pytest.mark.parametrize("given,expected", [(0, 0), (1, 50), (2, 100)])
def test_water_level(dev, given, expected):
    dev.set_property("water_level", given)
    assert dev.status().water_level == expected


def test_op_status(dev):
    def op_status():
        return dev.status().status

    dev.set_property("status", OperationStatusCA6.Close)
    assert op_status() == OperationStatusCA6.Close

    dev.set_property("status", OperationStatusCA6.Work)
    assert op_status() == OperationStatusCA6.Work

    dev.set_property("status", OperationStatusCA6.Dry)
    assert op_status() == OperationStatusCA6.Dry

    dev.set_property("status", OperationStatusCA6.Clean)
    assert op_status() == OperationStatusCA6.Clean
