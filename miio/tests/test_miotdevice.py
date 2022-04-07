import pytest

from miio import Huizuo, MiotDevice
from miio.miot_device import MiotValueType

MIOT_DEVICES = MiotDevice.__subclasses__()
# TODO: huizuo needs to be refactored to use _mappings,
# until then, just disable the tests on it.
MIOT_DEVICES.remove(Huizuo)  # type: ignore


@pytest.fixture(scope="module")
def dev(module_mocker):
    DUMMY_MAPPING = {}
    device = MiotDevice(
        "127.0.0.1", "68ffffffffffffffffffffffffffffff", mapping=DUMMY_MAPPING
    )
    module_mocker.patch.object(device, "send")
    return device


def test_missing_mapping(caplog):
    """Make sure ctor raises exception if neither class nor parameter defines the
    mapping."""
    _ = MiotDevice("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    assert "Neither the class nor the parameter defines the mapping" in caplog.text


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


@pytest.mark.parametrize(
    "model,expected_mapping,expected_log",
    [
        ("some_model", {"x": {"y": 1}}, ""),
        ("unknown_model", {"x": {"y": 1}}, "Unable to find mapping"),
    ],
)
def test_get_mapping(dev, caplog, model, expected_mapping, expected_log):
    """Test _get_mapping logic for fallbacks."""
    dev._mappings["some_model"] = {"x": {"y": 1}}
    dev._model = model
    assert dev._get_mapping() == expected_mapping

    assert expected_log in caplog.text


def test_get_mapping_backwards_compat(dev):
    """Test that the backwards compat works."""
    # as dev is mocked on module level, need to empty manually
    dev._mappings = {}
    assert dev._get_mapping() == {}


@pytest.mark.parametrize("cls", MIOT_DEVICES)
def test_mapping_deprecation(cls):
    """Check that deprecated mapping is not used."""
    # TODO: this can be removed in the future.
    assert not hasattr(cls, "mapping")


@pytest.mark.parametrize("cls", MIOT_DEVICES)
def test_mapping_structure(cls):
    """Check that mappings are structured correctly."""
    assert cls._mappings

    model, contents = next(iter(cls._mappings.items()))

    # model must contain a dot
    assert "." in model

    method, piid_siid = next(iter(contents.items()))
    assert isinstance(method, str)

    # mapping should be a dict with piid, siid
    assert "piid" in piid_siid
    assert "siid" in piid_siid


@pytest.mark.parametrize("cls", MIOT_DEVICES)
def test_supported_models(cls):
    assert cls.supported_models == cls._mappings.keys()

    # make sure that that _supported_models is not defined
    assert not cls._supported_models
