from unittest import TestCase

import pytest

from miio import FanMiot, PropertyAdapter
from miio.fan_miot import (
    MODEL_FAN_P9,
    FanException,
    FanMiotDeviceAdapter,
    OperationMode,
)
from miio.miot_spec_v2 import DeviceSpec

from .dummies import DummyMiotV2Device


class TestFanMiotDeviceAdapter(TestCase):
    def test_check_validation(self):
        adapter = FanMiotDeviceAdapter(
            "fan-dmaker-p11-1.json",
            speed=PropertyAdapter("fan", "fan-level"),
            off_delay=PropertyAdapter("off-delay-time", "off-delay-time"),
            alarm=PropertyAdapter("alarm", "alarm"),
            brightness=PropertyAdapter("indicator-light", "on"),
            motor_control=PropertyAdapter("motor-controller", "motor-control"),
        )
        adapter.check_validation()


class DummyFanMiot(DummyMiotV2Device, FanMiot):
    def __init__(self, *args, **kwargs):
        self.model = MODEL_FAN_P9
        self.adapter = self.get_adapter()
        self.spec = self.adapter.spec
        self.state = {
            "fan.on": True,
            "fan.mode": 0,
            "fan.speed-level": 35,
            "fan.horizontal-swing": False,
            "fan.horizontal-angle": 140,
            "fan.off-delay-time": 0,
            "fan.brightness": True,
            "fan.alarm": False,
            "physical-controls-locked": False,
        }
        self.return_values = {
            "get_prop": self._get_state,
            "fan.on": lambda x: self._set_state("power", x),
            "fan.mode": lambda x: self._set_state("mode", x),
            "fan.speed-level": lambda x: self._set_state("fan_speed", x),
            "fan.horizontal-swing": lambda x: self._set_state("swing_mode", x),
            "fan.horizontal-angle": lambda x: self._set_state("swing_mode_angle", x),
            "fan.off-delay-time": lambda x: self._set_state("power_off_time", x),
            "fan.brightness": lambda x: self._set_state("light", x),
            "fan.alarm": lambda x: self._set_state("buzzer", x),
            "physical-controls-locked": lambda x: self._set_state("child_lock", x),
            "motor-control": lambda x: True,
        }
        super().__init__(args, kwargs)

    def get_adapter(self):
        return FanMiotDeviceAdapter(
            spec_file_name="fan-dmaker-p9-1.json",
            spec=DeviceSpec.from_json(
                '{"type":"urn:miot-spec-v2:device:fan:0000A005:dmaker-p9:1","description":"Fan","services":[{"iid":1,"type":"urn:miot-spec-v2:service:device-information:00007801:dmaker-p9:1","description":"Device Information","properties":[{"iid":1,"type":"urn:miot-spec-v2:property:manufacturer:00000001:dmaker-p9:1","description":"Device Manufacturer","format":"string","access":["read"]},{"iid":2,"type":"urn:miot-spec-v2:property:model:00000002:dmaker-p9:1","description":"Device Model","format":"string","access":["read"]},{"iid":3,"type":"urn:miot-spec-v2:property:serial-number:00000003:dmaker-p9:1","description":"Device Serial Number","format":"string","access":["read"]},{"iid":4,"type":"urn:miot-spec-v2:property:firmware-revision:00000005:dmaker-p9:1","description":"Current Firmware Version","format":"string","access":["read"]}]},{"iid":2,"type":"urn:miot-spec-v2:service:fan:00007808:dmaker-p9:1","description":"Fan","properties":[{"iid":1,"type":"urn:miot-spec-v2:property:on:00000006:dmaker-p9:1","description":"Switch Status","format":"bool","access":["read","write","notify"]},{"iid":2,"type":"urn:miot-spec-v2:property:fan-level:00000016:dmaker-p9:1","description":"Fan Level","format":"uint8","access":["read","write","notify"],"unit":"none","value-list":[{"value":1,"description":"Level1"},{"value":2,"description":"Level2"},{"value":3,"description":"Level3"},{"value":4,"description":"Level4"}]},{"iid":4,"type":"urn:miot-spec-v2:property:mode:00000008:dmaker-p9:1","description":"Mode","format":"uint8","access":["read","write","notify"],"unit":"none","value-list":[{"value":0,"description":"Straight Wind"},{"value":1,"description":"Natural Wind"},{"value":2,"description":"Sleep"}]},{"iid":5,"type":"urn:miot-spec-v2:property:horizontal-swing:00000017:dmaker-p9:1","description":"Horizontal Swing","format":"bool","access":["read","write","notify"],"unit":"none"},{"iid":6,"type":"urn:miot-spec-v2:property:horizontal-angle:00000019:dmaker-p9:1","description":"Horizontal Angle","format":"uint16","access":["read","write","notify"],"unit":"none","value-list":[{"value":30,"description":"30"},{"value":60,"description":"60"},{"value":90,"description":"90"},{"value":120,"description":"120"},{"value":150,"description":"150"}]},{"iid":7,"type":"urn:miot-spec-v2:property:alarm:00000012:dmaker-p9:1","description":"Alarm","format":"bool","access":["read","write","notify"]},{"iid":8,"type":"urn:miot-spec-v2:property:off-delay-time:00000054:dmaker-p9:1","description":"Power Off Delay Time","format":"uint32","access":["read","write","notify"],"unit":"minutes","value-range":[0,480,1]},{"iid":9,"type":"urn:miot-spec-v2:property:brightness:0000000D:dmaker-p9:1","description":"Brightness","format":"bool","access":["read","write","notify"],"unit":"none"},{"iid":10,"type":"urn:miot-spec-v2:property:motor-control:00000038:dmaker-p9:1","description":"Motor Control","format":"uint8","access":["write"],"unit":"none","value-list":[{"value":0,"description":"None"},{"value":1,"description":"Left"},{"value":2,"description":"Right"}]},{"iid":11,"type":"urn:miot-spec-v2:property:speed-level:00000023:dmaker-p9:1","description":"Speed Level","format":"uint8","access":["read","write","notify"],"unit":"none","value-range":[1,100,1]}],"actions":[{"iid":1,"type":"urn:miot-spec-v2:action:toggle:00002811:dmaker-p9:1","description":"Toggle","in":[],"out":[]}]},{"iid":3,"type":"urn:miot-spec-v2:service:physical-controls-locked:00007807:dmaker-p9:1","description":"Physical Control Locked","properties":[{"iid":1,"type":"urn:miot-spec-v2:property:physical-controls-locked:0000001D:dmaker-p9:1","description":"Physical Control Locked","format":"bool","access":["read","write","notify"]}]}]}'
            ),
        )


@pytest.fixture(scope="class")
def fanmiot(request):
    request.cls.device = DummyFanMiot()


@pytest.mark.usefixtures("fanmiot")
class TestFanMiot(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def state(self):
        return self.device.status()

    def test_on(self):
        self.device.off()  # ensure off
        assert self.is_on() is False

        self.device.on()
        assert self.is_on() is True

    def test_off(self):
        self.device.on()  # ensure on
        assert self.is_on() is True

        self.device.off()
        assert self.is_on() is False

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Normal)
        assert mode() == OperationMode.Normal

        self.device.set_mode(OperationMode.Nature)
        assert mode() == OperationMode.Nature

    def test_set_speed(self):
        def speed():
            return self.device.status().speed

        self.device.set_speed(0)
        assert speed() == 0
        self.device.set_speed(1)
        assert speed() == 1
        self.device.set_speed(100)
        assert speed() == 100

        with pytest.raises(FanException):
            self.device.set_speed(-1)

        with pytest.raises(FanException):
            self.device.set_speed(101)

    def test_set_angle(self):
        def angle():
            return self.device.status().angle

        self.device.set_angle(30)
        assert angle() == 30
        self.device.set_angle(60)
        assert angle() == 60
        self.device.set_angle(90)
        assert angle() == 90
        self.device.set_angle(120)
        assert angle() == 120
        self.device.set_angle(140)
        assert angle() == 140

        with pytest.raises(FanException):
            self.device.set_angle(-1)

        with pytest.raises(FanException):
            self.device.set_angle(1)

        with pytest.raises(FanException):
            self.device.set_angle(31)

        with pytest.raises(FanException):
            self.device.set_angle(141)

    def test_set_oscillate(self):
        def oscillate():
            return self.device.status().oscillate

        self.device.set_oscillate(True)
        assert oscillate() is True

        self.device.set_oscillate(False)
        assert oscillate() is False

    def test_set_led(self):
        def led():
            return self.device.status().led

        self.device.set_led(True)
        assert led() is True

        self.device.set_led(False)
        assert led() is False

    def test_set_buzzer(self):
        def buzzer():
            return self.device.status().buzzer

        self.device.set_buzzer(True)
        assert buzzer() is True

        self.device.set_buzzer(False)
        assert buzzer() is False

    def test_set_child_lock(self):
        def child_lock():
            return self.device.status().child_lock

        self.device.set_child_lock(True)
        assert child_lock() is True

        self.device.set_child_lock(False)
        assert child_lock() is False

    def test_delay_off(self):
        def delay_off_countdown():
            return self.device.status().delay_off_countdown

        self.device.delay_off(100)
        assert delay_off_countdown() == 100
        self.device.delay_off(200)
        assert delay_off_countdown() == 200
        self.device.delay_off(0)
        assert delay_off_countdown() == 0

        with pytest.raises(FanException):
            self.device.delay_off(-1)
