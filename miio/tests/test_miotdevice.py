from unittest.mock import ANY

import pytest

from miio import Huizuo, MiotDevice
from miio.integrations.genericmiot.genericmiot import GenericMiot
from miio.miot_device import MiotValueType, _filter_request_fields

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
    device._model = "test.model"
    module_mocker.patch.object(device, "send")
    return device


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
    _ = dev.set_property_by(siid, piid, value, value_type=value_type)

    if value_type is not None:
        value = value_type.value(value)

    dev.send.assert_called_with(
        "set_properties",
        [{"did": f"set-{siid}-{piid}", "siid": siid, "piid": piid, "value": value}],
    )


def test_set_property_by_name(dev):
    siid = 1
    piid = 1
    value = 1
    _ = dev.set_property_by(siid, piid, value, name="test-name")

    dev.send.assert_called_with(
        "set_properties",
        [{"did": "test-name", "siid": siid, "piid": piid, "value": value}],
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
        ("some.model", {"x": {"y": 1}}, ""),
        ("unknown.model", {"x": {"y": 1}}, "Unable to find mapping"),
    ],
)
def test_get_mapping(dev, caplog, model, expected_mapping, expected_log):
    """Test _get_mapping logic for fallbacks."""
    dev._mappings["some.model"] = {"x": {"y": 1}}
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
    if cls == GenericMiot:
        pytest.skip("Skipping genericmiot as it provides no mapping")

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
    assert cls.supported_models == list(cls._mappings.keys())
    if cls == GenericMiot:
        pytest.skip("Skipping genericmiot as it uses supported_models for now")

    # make sure that that _supported_models is not defined
    assert not cls._supported_models


def test_call_action_from_mapping(dev):
    dev._mappings["test.model"] = {"test_action": {"siid": 1, "aiid": 1}}

    dev.call_action_from_mapping("test_action")


@pytest.mark.parametrize(
    "props,included_in_request",
    [
        ({"access": ["read"]}, True),  # read only
        ({"access": ["read", "write"]}, True),  # read-write
        ({}, True),  # not defined
        ({"access": ["write"]}, False),  # write-only
        ({"aiid": "1"}, False),  # action
    ],
    ids=["read-only", "read-write", "access-not-defined", "write-only", "action"],
)
def test_get_properties_for_mapping_readables(mocker, dev, props, included_in_request):
    base_props = {"readable_property": {"siid": 1, "piid": 1}}
    base_request = [{"did": k, **v} for k, v in base_props.items()]
    dev._mappings["test.model"] = mapping = {
        **base_props,
        "property_under_test": {"siid": 1, "piid": 2, **props},
    }
    expected_request = [
        {"did": k, **_filter_request_fields(v)} for k, v in mapping.items()
    ]

    req = mocker.patch.object(dev, "get_properties")
    dev.get_properties_for_mapping()

    try:
        req.assert_called_with(
            expected_request, property_getter=ANY, max_properties=ANY
        )
    except AssertionError:
        if included_in_request:
            raise AssertionError("Required property was not requested")
        else:
            try:
                req.assert_called_with(
                    base_request, property_getter=ANY, max_properties=ANY
                )
            except AssertionError as ex:
                raise AssertionError("Tried to read unreadable property") from ex
