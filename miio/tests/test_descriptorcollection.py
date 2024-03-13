import pytest

from miio import (
    AccessFlags,
    ActionDescriptor,
    DescriptorCollection,
    Device,
    DeviceStatus,
    EnumDescriptor,
    PropertyDescriptor,
    RangeDescriptor,
    ValidSettingRange,
)
from miio.devicestatus import sensor, setting


def test_descriptors_from_device_object(dummy_device):
    """Test descriptor collection from device class."""

    coll = DescriptorCollection(device=dummy_device)
    coll.descriptors_from_object(dummy_device)
    assert len(coll) == 1
    assert isinstance(coll["test"], ActionDescriptor)


def test_descriptors_from_status_object(dummy_device):
    coll = DescriptorCollection(device=dummy_device)

    class TestStatus(DeviceStatus):
        @sensor(id="test", name="test sensor")
        def test_sensor(self):
            pass

        @setting(id="test-setting", name="test setting", setter=lambda _: _)
        def test_setting(self):
            pass

    status = TestStatus()
    coll.descriptors_from_object(status)
    assert len(coll) == 2
    assert isinstance(coll["test"], PropertyDescriptor)
    assert isinstance(coll["test-setting"], PropertyDescriptor)
    assert coll["test-setting"].access & AccessFlags.Write


@pytest.mark.parametrize(
    "cls, params",
    [
        pytest.param(ActionDescriptor, {"method": lambda _: _}, id="action"),
        pytest.param(PropertyDescriptor, {"status_attribute": "foo"}),
    ],
)
def test_add_descriptor(dummy_device: Device, cls, params):
    """Test that adding a descriptor works."""
    coll: DescriptorCollection = DescriptorCollection(device=dummy_device)
    coll.add_descriptor(cls(id="id", name="test name", **params))
    assert len(coll) == 1
    assert coll["id"] is not None


def test_handle_action_descriptor(mocker, dummy_device):
    coll = DescriptorCollection(device=dummy_device)
    invalid_desc = ActionDescriptor(id="action", name="test name")
    with pytest.raises(ValueError, match="Neither method or method_name was defined"):
        coll.add_descriptor(invalid_desc)

    mocker.patch.object(dummy_device, "existing_method", create=True)

    # Test method name binding
    act_with_method_name = ActionDescriptor(
        id="with-method-name", name="with-method-name", method_name="existing_method"
    )
    coll.add_descriptor(act_with_method_name)
    assert act_with_method_name.method is not None

    # Test non-existing method
    act_with_method_name_missing = ActionDescriptor(
        id="with-method-name-missing",
        name="with-method-name-missing",
        method_name="nonexisting_method",
    )
    with pytest.raises(AttributeError):
        coll.add_descriptor(act_with_method_name_missing)


def test_handle_writable_property_descriptor(mocker, dummy_device):
    coll = DescriptorCollection(device=dummy_device)
    data = {
        "name": "",
        "status_attribute": "",
        "access": AccessFlags.Write,
    }
    invalid = PropertyDescriptor(id="missing_setter", **data)
    with pytest.raises(ValueError, match="Neither setter or setter_name was defined"):
        coll.add_descriptor(invalid)

    mocker.patch.object(dummy_device, "existing_method", create=True)

    # Test name binding
    setter_name_desc = PropertyDescriptor(
        **data, id="setter_name", setter_name="existing_method"
    )
    coll.add_descriptor(setter_name_desc)
    assert setter_name_desc.setter is not None

    with pytest.raises(AttributeError):
        coll.add_descriptor(
            PropertyDescriptor(
                **data, id="missing_setter", setter_name="non_existing_setter"
            )
        )


def test_handle_enum_constraints(dummy_device, mocker):
    coll = DescriptorCollection(device=dummy_device)

    data = {
        "name": "enum",
        "status_attribute": "attr",
    }

    mocker.patch.object(dummy_device, "choices_attr", create=True)

    # Check that error is raised if choices are missing
    invalid = EnumDescriptor(id="missing", **data)
    with pytest.raises(
        ValueError, match="Neither choices nor choices_attribute was defined"
    ):
        coll.add_descriptor(invalid)

    # Check that binding works
    choices_attribute = EnumDescriptor(
        id="with_choices_attr", choices_attribute="choices_attr", **data
    )
    coll.add_descriptor(choices_attribute)
    assert len(coll) == 1
    assert coll["with_choices_attr"].choices is not None


def test_handle_range_constraints(dummy_device, mocker):
    coll = DescriptorCollection(device=dummy_device)

    data = {
        "name": "name",
        "status_attribute": "attr",
        "min_value": 0,
        "max_value": 100,
        "step": 1,
    }

    # Check regular descriptor
    desc = RangeDescriptor(id="regular", **data)
    coll.add_descriptor(desc)
    assert coll["regular"].max_value == 100

    mocker.patch.object(
        dummy_device, "range", create=True, new=ValidSettingRange(-1, 1000, 10)
    )
    range_attr = RangeDescriptor(id="range_attribute", range_attribute="range", **data)
    coll.add_descriptor(range_attr)

    assert coll["range_attribute"].min_value == -1
    assert coll["range_attribute"].max_value == 1000
    assert coll["range_attribute"].step == 10


def test_duplicate_identifiers(dummy_device):
    coll = DescriptorCollection(device=dummy_device)
    for i in range(3):
        coll.add_descriptor(
            ActionDescriptor(id="action", name=f"action {i}", method=lambda _: _)
        )

    assert coll["action"]
    assert coll["action-2"]
    assert coll["action-3"]
