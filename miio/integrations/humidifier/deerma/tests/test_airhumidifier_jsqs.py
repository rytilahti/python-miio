import pytest

from miio import AirHumidifierJsqs
from miio.tests.dummies import DummyMiotDevice

from ..airhumidifier_jsqs import OperationMode

_INITIAL_STATE = {
    "power": True,
    "fault": 0,
    "mode": 4,
    "target_humidity": 60,
    "temperature": 21.6,
    "relative_humidity": 62,
    "buzzer": False,
    "led_light": True,
    "water_shortage_fault": False,
    "tank_filed": False,
    "overwet_protect": True,
}


class DummyAirHumidifierJsqs(DummyMiotDevice, AirHumidifierJsqs):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_target_humidity": lambda x: self._set_state("target_humidity", x),
            "set_mode": lambda x: self._set_state("mode", x),
            "set_led_light": lambda x: self._set_state("led_light", x),
            "set_buzzer": lambda x: self._set_state("buzzer", x),
            "set_overwet_protect": lambda x: self._set_state("overwet_protect", x),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture()
def dev(request):
    yield DummyAirHumidifierJsqs()


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
    assert status.mode == OperationMode(_INITIAL_STATE["mode"])
    assert status.target_humidity == _INITIAL_STATE["target_humidity"]
    assert status.temperature == _INITIAL_STATE["temperature"]
    assert status.relative_humidity == _INITIAL_STATE["relative_humidity"]
    assert status.buzzer == _INITIAL_STATE["buzzer"]
    assert status.led_light == _INITIAL_STATE["led_light"]
    assert status.water_shortage_fault == _INITIAL_STATE["water_shortage_fault"]
    assert status.tank_filed == _INITIAL_STATE["tank_filed"]
    assert status.overwet_protect == _INITIAL_STATE["overwet_protect"]


def test_set_target_humidity(dev):
    def target_humidity():
        return dev.status().target_humidity

    dev.set_target_humidity(40)
    assert target_humidity() == 40
    dev.set_target_humidity(80)
    assert target_humidity() == 80

    with pytest.raises(ValueError):
        dev.set_target_humidity(39)

    with pytest.raises(ValueError):
        dev.set_target_humidity(81)


def test_set_mode(dev):
    def mode():
        return dev.status().mode

    dev.set_mode(OperationMode.Auto)
    assert mode() == OperationMode.Auto

    dev.set_mode(OperationMode.Low)
    assert mode() == OperationMode.Low

    dev.set_mode(OperationMode.Mid)
    assert mode() == OperationMode.Mid

    dev.set_mode(OperationMode.High)
    assert mode() == OperationMode.High


def test_set_led_light(dev):
    def led_light():
        return dev.status().led_light

    dev.set_light(True)
    assert led_light() is True

    dev.set_light(False)
    assert led_light() is False


def test_set_buzzer(dev):
    def buzzer():
        return dev.status().buzzer

    dev.set_buzzer(True)
    assert buzzer() is True

    dev.set_buzzer(False)
    assert buzzer() is False


def test_set_overwet_protect(dev):
    def overwet_protect():
        return dev.status().overwet_protect

    dev.set_overwet_protect(True)
    assert overwet_protect() is True

    dev.set_overwet_protect(False)
    assert overwet_protect() is False
