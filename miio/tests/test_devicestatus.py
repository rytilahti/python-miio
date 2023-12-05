import re
from enum import Enum

import pytest

from miio import DeviceStatus
from miio.descriptors import EnumDescriptor, RangeDescriptor, ValidSettingRange
from miio.devicestatus import sensor, setting


def test_multiple():
    class MultipleProperties(DeviceStatus):
        @property
        def first(self):
            return "first"

        @property
        def second(self):
            return "second"

    assert (
        repr(MultipleProperties()) == "<MultipleProperties first=first second=second>"
    )


def test_empty():
    class EmptyStatus(DeviceStatus):
        pass

    assert repr(EmptyStatus() == "<EmptyStatus>")


def test_exception():
    class StatusWithException(DeviceStatus):
        @property
        def raise_exception(self):
            raise Exception("test")

    assert (
        repr(StatusWithException()) == "<StatusWithException raise_exception=Exception>"
    )


def test_inheritance():
    class Parent(DeviceStatus):
        @property
        def from_parent(self):
            return True

    class Child(Parent):
        @property
        def from_child(self):
            return True

    assert repr(Child()) == "<Child from_child=True from_parent=True>"


def test_list():
    class List(DeviceStatus):
        @property
        def return_list(self):
            return [0, 1, 2]

    assert repr(List()) == "<List return_list=[0, 1, 2]>"


def test_none():
    class NoneStatus(DeviceStatus):
        @property
        def return_none(self):
            return None

    assert repr(NoneStatus()) == "<NoneStatus return_none=None>"


def test_get_attribute():
    """Make sure that __get_attribute__ works as expected."""

    class TestStatus(DeviceStatus):
        @property
        def existing_attribute(self):
            return None

    status = TestStatus()
    with pytest.raises(AttributeError):
        _ = status.__missing_attribute

    with pytest.raises(AttributeError):
        _ = status.__missing_dunder__

    assert status.existing_attribute is None


def test_sensor_decorator():
    class DecoratedProps(DeviceStatus):
        @property
        @sensor(name="Voltage", unit="V")
        def all_kwargs(self):
            pass

        @property
        @sensor(name="Only name")
        def only_name(self):
            pass

        @property
        @sensor(name="", unknown_kwarg="123")
        def unknown(self):
            pass

    status = DecoratedProps()
    descs = status.descriptors()
    assert len(descs) == 3

    all_kwargs = descs["all_kwargs"]
    assert all_kwargs.name == "Voltage"
    assert all_kwargs.unit == "V"

    assert descs["only_name"].name == "Only name"

    assert "unknown_kwarg" in descs["unknown"].extras


def test_setting_decorator_number(dummy_device, mocker):
    """Tests for setting decorator with numbers."""

    class Settings(DeviceStatus):
        @property
        @setting(
            id="level",
            name="Level",
            unit="something",
            setter_name="set_level",
            min_value=0,
            max_value=2,
        )
        def level(self) -> int:
            return 1

    # Patch status to return our class
    status = mocker.patch.object(dummy_device, "status", return_value=Settings())
    status.__annotations__ = {}
    status.__annotations__["return"] = Settings
    # Patch to create a new setter as defined in the status class
    setter = mocker.patch.object(dummy_device, "set_level", create=True)

    settings = dummy_device.settings()
    assert len(settings) == 1

    desc = settings["level"]
    assert isinstance(desc, RangeDescriptor)

    assert getattr(dummy_device.status(), desc.status_attribute) == 1

    assert desc.name == "Level"
    assert desc.min_value == 0
    assert desc.max_value == 2
    assert desc.step == 1

    settings["level"].setter(1)
    setter.assert_called_with(1)


def test_setting_decorator_number_range_attribute(mocker, dummy_device):
    """Tests for setting decorator with range_attribute.

    This makes sure the range_attribute overrides {min,max}_value and step.
    """

    class Settings(DeviceStatus):
        @property
        @setting(
            id="level",
            name="Level",
            unit="something",
            setter_name="set_level",
            min_value=0,
            max_value=2,
            step=1,
            range_attribute="valid_range",
        )
        def level(self) -> int:
            return 1

    # Patch status to return our class
    status = mocker.patch.object(dummy_device, "status", return_value=Settings())
    status.__annotations__ = {}
    status.__annotations__["return"] = Settings

    mocker.patch.object(
        dummy_device, "valid_range", create=True, new=ValidSettingRange(1, 100, 2)
    )
    # Patch to create a new setter as defined in the status class
    setter = mocker.patch.object(dummy_device, "set_level", create=True)

    settings = dummy_device.settings()
    assert len(settings) == 1

    desc = settings["level"]
    assert isinstance(desc, RangeDescriptor)

    assert getattr(dummy_device.status(), desc.status_attribute) == 1

    assert desc.name == "Level"
    assert desc.min_value == 1
    assert desc.max_value == 100
    assert desc.step == 2

    settings["level"].setter(50)
    setter.assert_called_with(50)


def test_setting_decorator_enum(dummy_device, mocker):
    """Tests for setting decorator with enums."""

    class TestEnum(Enum):
        First = 1
        Second = 2

    class Settings(DeviceStatus):
        @property
        @setting(
            id="level",
            name="Level",
            unit="something",
            setter_name="set_level",
            choices=TestEnum,
        )
        def level(self) -> TestEnum:
            return TestEnum.First

    # Patch status to return our class
    status = mocker.patch.object(dummy_device, "status", return_value=Settings())
    status.__annotations__ = {}
    status.__annotations__["return"] = Settings
    # Patch to create a new setter as defined in the status class
    setter = mocker.patch.object(dummy_device, "set_level", create=True)

    settings = dummy_device.settings()
    assert len(settings) == 1

    desc = settings["level"]
    assert isinstance(desc, EnumDescriptor)
    assert getattr(dummy_device.status(), desc.status_attribute) == TestEnum.First

    assert desc.name == "Level"
    assert len(desc.choices) == 2

    settings["level"].setter(TestEnum.Second)
    setter.assert_called_with(TestEnum.Second)


def test_embed():
    class MainStatus(DeviceStatus):
        @property
        @sensor("main_sensor")
        def main_sensor(self):
            return "main"

    class SubStatus(DeviceStatus):
        @property
        @sensor("sub_sensor")
        def sub_sensor(self):
            return "sub"

    main = MainStatus()
    assert len(main.descriptors()) == 1

    sub = SubStatus()
    main.embed("SubStatus", sub)
    sensors = main.descriptors()
    assert len(sensors) == 2
    assert sub._parent == main

    assert getattr(main, sensors["main_sensor"].status_attribute) == "main"
    assert getattr(main, sensors["SubStatus__sub_sensor"].status_attribute) == "sub"

    with pytest.raises(KeyError):
        main.descriptors()["nonexisting_sensor"]

    assert (
        repr(main)
        == "<MainStatus main_sensor=main SubStatus=<SubStatus sub_sensor=sub>>"
    )

    # Test attribute access to the sub status
    assert isinstance(main.SubStatus, SubStatus)

    # Test that __dir__ is implemented correctly
    assert "SubStatus" in dir(main)
    assert "SubStatus__sub_sensor" in dir(main)


def test_cli_output(dummy_status):
    """Test the cli output string."""

    expected_regex = [
        "r-- sensor_without_unit (.+?): 1",
        "r-- sensor_with_unit (.+?): 2 V",
        r"rw- setting_without_unit (.+?): 3",
        r"rw- setting_with_unit (.+?): 4 V",
    ]

    for idx, line in enumerate(dummy_status.__cli_output__.splitlines()):
        assert re.match(expected_regex[idx], line) is not None
