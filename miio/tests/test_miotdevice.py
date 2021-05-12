import pytest

from miio import DeviceException, MiotDevice
from miio.miot_device import MiotValueType


@pytest.fixture(scope="module")
def dev(module_mocker):
    DUMMY_MAPPING = {}
    device = MiotDevice(
        "127.0.0.1", "68ffffffffffffffffffffffffffffff", mapping=DUMMY_MAPPING
    )
    module_mocker.patch.object(device, "send")
    return device


def test_missing_mapping():
    """Make sure ctor raises exception if neither class nor parameter defines the
    mapping."""
    with pytest.raises(DeviceException):
        _ = MiotDevice("127.0.0.1", "68ffffffffffffffffffffffffffffff")


def test_ctor_mapping():
    """Make sure the constructor accepts the mapping parameter."""
    test_mapping = {}
    dev2 = MiotDevice(
        "127.0.0.1", "68ffffffffffffffffffffffffffffff", mapping=test_mapping
    )
    assert dev2.mapping == test_mapping


def test_get_property_by(dev):
    siid = 1
    piid = 2
    _ = dev.get_property_by(siid, piid)

    dev.send.assert_called_with(
        "get_properties", [{"did": f"{siid}-{piid}", "siid": siid, "piid": piid}]
    )


@pytest.mark.parametrize(
    "value_type,value",
    [
        (None, 1),
        (MiotValueType.Int, "1"),
        (MiotValueType.Float, "1.2"),
        (MiotValueType.Str, "str"),
        (MiotValueType.Bool, "1"),
    ],
)
def test_set_property_by(dev, value_type, value):
    siid = 1
    piid = 1
    _ = dev.set_property_by(siid, piid, value, value_type)

    if value_type is not None:
        value = value_type.value(value)

    dev.send.assert_called_with(
        "set_properties",
        [{"did": f"set-{siid}-{piid}", "siid": siid, "piid": piid, "value": value}],
    )


def test_call_action_by(dev):
    siid = 1
    aiid = 1

    _ = dev.call_action_by(siid, aiid)
    dev.send.assert_called_with(
        "action",
        {
            "did": f"call-{siid}-{aiid}",
            "siid": siid,
            "aiid": aiid,
            "in": [],
        },
    )

    params = {"test_param": 1}
    _ = dev.call_action_by(siid, aiid, params)
    dev.send.assert_called_with(
        "action",
        {
            "did": f"call-{siid}-{aiid}",
            "siid": siid,
            "aiid": aiid,
            "in": params,
        },
    )
