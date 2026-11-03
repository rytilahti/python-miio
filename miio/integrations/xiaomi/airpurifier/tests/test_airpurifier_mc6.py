import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from miio import DeviceException, DeviceFactory
from miio.integrations.xiaomi.airpurifier import AirPurifierMC6
from miio.integrations.xiaomi.airpurifier.airpurifier_mc6 import (
    MODEL,
    OperationMode,
    ScreenBrightness,
)


@pytest.fixture
def dev():
    return AirPurifierMC6("192.0.2.1", "0" * 32, model=MODEL)


@pytest.fixture
def replies():
    # Sanitized local get_properties readings from MC6 firmware 1.0.5.
    return json.loads(Path(__file__).with_name("mc6_status.json").read_text())


def test_factory():
    assert DeviceFactory.class_for_model(MODEL) is AirPurifierMC6
    assert isinstance(
        DeviceFactory.create("192.0.2.1", "0" * 32, model=MODEL), AirPurifierMC6
    )


def test_recorded_status(dev, replies):
    by_pair = {(r["siid"], r["piid"]): r for r in replies}

    def respond(method, params):
        assert method == "get_properties"
        assert len(params) <= 5
        return [by_pair[p["siid"], p["piid"]] for p in params]

    dev.send = Mock(side_effect=respond)
    status = dev.status()
    assert status.is_on is True
    assert status.mode is OperationMode.Auto
    assert status.favorite_level == 9
    assert status.aqi == 3
    assert status.pm1 == 1
    assert status.humidity == 42
    assert status.temperature == 22.5
    assert status.screen_brightness is ScreenBrightness.Mid
    assert status.motor_target_speed == 400
    assert status.motor_speed == 404
    assert dev.send.call_count == 5


def test_missing_optional_readings_and_unknown_mode(dev):
    dev.get_properties_for_mapping = Mock(
        return_value=[
            {"siid": 2, "piid": 1, "code": 0, "value": True},
            {"siid": 2, "piid": 3, "code": 0, "value": 6},
            {"siid": 3, "piid": 4, "code": -4004},
        ]
    )
    status = dev.status()
    assert status.mode is None
    assert status.aqi is None
    assert status.screen_brightness is None


def test_failed_power_read(dev):
    dev.get_properties_for_mapping = Mock(return_value=[])
    with pytest.raises(DeviceException):
        dev.status()


@pytest.mark.parametrize(
    ("method", "value", "key", "pair", "wire"),
    [
        ("set_mode", OperationMode.Auto, "mode", (2, 3), 0),
        ("set_mode", OperationMode.Sleep, "mode", (2, 3), 3),
        ("set_mode", OperationMode.Favorite, "mode", (2, 3), 5),
        ("set_screen_brightness", ScreenBrightness.Mid, "screen_brightness", (6, 2), 2),
        ("set_fan_level", 2, "fan_level", (2, 4), 2),
        ("set_favorite_level", 9, "favorite_level", (9, 1), 9),
        ("set_favorite_level", 0, "favorite_level", (9, 1), 0),
        ("set_screen", False, "screen", (6, 1), False),
        ("set_uv", True, "uv", (2, 6), True),
        ("set_anion", False, "anion", (2, 5), False),
        ("set_buzzer", False, "buzzer", (7, 1), False),
        ("set_child_lock", True, "child_lock", (8, 1), True),
    ],
)
def test_command_encoding(dev, method, value, key, pair, wire):
    dev.send = Mock(return_value=[{"siid": pair[0], "piid": pair[1], "code": 0}])
    getattr(dev, method)(value)
    dev.send.assert_called_once_with(
        "set_properties",
        [{"did": key, "siid": pair[0], "piid": pair[1], "value": wire}],
    )


@pytest.mark.parametrize(
    ("method", "value"),
    [
        ("set_mode", 0),
        ("set_mode", ScreenBrightness.Dim),
        ("set_screen_brightness", 0),
        ("set_favorite_level", -1),
        ("set_favorite_level", 10),
        ("set_favorite_level", 1.5),
        ("set_favorite_level", True),
        ("set_fan_level", 3),
        ("set_screen", 1),
    ],
)
def test_invalid_commands_do_not_send(dev, method, value):
    dev.send = Mock()
    with pytest.raises(ValueError):
        getattr(dev, method)(value)
    dev.send.assert_not_called()


@pytest.mark.parametrize(
    "response",
    [
        None,
        [],
        [{"siid": 2, "piid": 1, "code": -4004}],
        [{"siid": 2, "piid": 3, "code": 0}],
    ],
)
def test_rejected_or_mismatched_command(dev, response):
    dev.send = Mock(return_value=response)
    with pytest.raises(DeviceException):
        dev.on()


@pytest.mark.parametrize(("method", "value"), [("on", True), ("off", False)])
def test_power_commands(dev, method, value):
    dev.send = Mock(return_value=[{"siid": 2, "piid": 1, "code": 0}])
    getattr(dev, method)()
    dev.send.assert_called_once_with(
        "set_properties", [{"did": "power", "siid": 2, "piid": 1, "value": value}]
    )
