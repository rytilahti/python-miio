import pytest

from miio import AirDehumidifierMiot
from miio.tests.dummies import DummyMiotDevice

from ..airdehumidifier_miot import FaultStatus, LedBrightness, OperationMode

_INITIAL_STATE = {
    "power": True,
    "fault": 0,
    "mode": 0,
    "target_humidity": 50,
    "relative_humidity": 62,
    "temperature": 21.6,
    "buzzer": False,
    "led": True,
    "led_brightness": 2,
    "child_lock": False,
    "dry_after_off": False,
    "dry_left_time": 0,
    "is_warming_up": False,
    "delay": False,
    "delay_time": 0,
    "delay_remain_time": 0,
}


class DummyAirDehumidifierMiot(DummyMiotDevice, AirDehumidifierMiot):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_target_humidity": lambda x: self._set_state("target_humidity", x),
            "set_mode": lambda x: self._set_state("mode", x),
            "set_led": lambda x: self._set_state("led", x),
            "set_led_brightness": lambda x: self._set_state("led_brightness", x),
            "set_buzzer": lambda x: self._set_state("buzzer", x),
            "set_child_lock": lambda x: self._set_state("child_lock", x),
            "set_dry_after_off": lambda x: self._set_state("dry_after_off", x),
            "set_delay": lambda x: self._set_state("delay", x),
            "set_delay_time": lambda x: self._set_state("delay_time", x),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture
def dev(request):
    return DummyAirDehumidifierMiot()


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
    assert status.fault == FaultStatus(_INITIAL_STATE["fault"])
    assert status.tank_full is False
    assert status.mode == OperationMode(_INITIAL_STATE["mode"])
    assert status.target_humidity == _INITIAL_STATE["target_humidity"]
    assert status.relative_humidity == _INITIAL_STATE["relative_humidity"]
    assert status.temperature == _INITIAL_STATE["temperature"]
    assert status.buzzer == _INITIAL_STATE["buzzer"]
    assert status.led == _INITIAL_STATE["led"]
    assert status.led_brightness == LedBrightness(_INITIAL_STATE["led_brightness"])
    assert status.child_lock == _INITIAL_STATE["child_lock"]
    assert status.dry_after_off == _INITIAL_STATE["dry_after_off"]
    assert status.dry_left_time == _INITIAL_STATE["dry_left_time"]
    assert status.is_warming_up == _INITIAL_STATE["is_warming_up"]
    assert status.delay == _INITIAL_STATE["delay"]
    assert status.delay_time == _INITIAL_STATE["delay_time"]
    assert status.delay_remain_time == _INITIAL_STATE["delay_remain_time"]


def test_tank_full(dev):
    dev.set_property("fault", FaultStatus.WaterFull.value)
    assert dev.status().fault is FaultStatus.WaterFull
    assert dev.status().tank_full is True


def test_set_target_humidity(dev):
    def target_humidity():
        return dev.status().target_humidity

    dev.set_target_humidity(40)
    assert target_humidity() == 40
    dev.set_target_humidity(70)
    assert target_humidity() == 70

    with pytest.raises(ValueError):
        dev.set_target_humidity(39)

    with pytest.raises(ValueError):
        dev.set_target_humidity(71)


def test_set_mode(dev):
    def mode():
        return dev.status().mode

    dev.set_mode(OperationMode.Smart)
    assert mode() == OperationMode.Smart

    dev.set_mode(OperationMode.Sleep)
    assert mode() == OperationMode.Sleep

    dev.set_mode(OperationMode.ClothesDrying)
    assert mode() == OperationMode.ClothesDrying


def test_set_led(dev):
    def led():
        return dev.status().led

    dev.set_led(True)
    assert led() is True

    dev.set_led(False)
    assert led() is False


def test_set_led_brightness(dev):
    def led_brightness():
        return dev.status().led_brightness

    dev.set_led_brightness(LedBrightness.Off)
    assert led_brightness() == LedBrightness.Off

    dev.set_led_brightness(LedBrightness.Dim)
    assert led_brightness() == LedBrightness.Dim

    dev.set_led_brightness(LedBrightness.Bright)
    assert led_brightness() == LedBrightness.Bright


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


def test_set_dry_after_off(dev):
    def dry_after_off():
        return dev.status().dry_after_off

    dev.set_dry_after_off(True)
    assert dry_after_off() is True

    dev.set_dry_after_off(False)
    assert dry_after_off() is False


def test_set_delay(dev):
    def delay():
        return dev.status().delay

    dev.set_delay(True)
    assert delay() is True

    dev.set_delay(False)
    assert delay() is False


def test_set_delay_time(dev):
    def delay_time():
        return dev.status().delay_time

    dev.set_delay_time(0)
    assert delay_time() == 0
    dev.set_delay_time(720)
    assert delay_time() == 720

    with pytest.raises(ValueError):
        dev.set_delay_time(-1)

    with pytest.raises(ValueError):
        dev.set_delay_time(721)
