"""Tests for miot model parsing."""

import json
from pathlib import Path

import pytest

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

from miio.descriptors import (
    AccessFlags,
    EnumDescriptor,
    PropertyConstraint,
    PropertyDescriptor,
    RangeDescriptor,
)
from miio.miot_models import (
    URN,
    MiotAccess,
    MiotAction,
    MiotEnumValue,
    MiotEvent,
    MiotFormat,
    MiotProperty,
    MiotService,
)


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    file = Path(__file__).parent.absolute() / "fixtures" / "miot" / filename
    with file.open() as f:
        return json.load(f)


DUMMY_SERVICE = """
    {
        "iid": 1,
        "description": "test service",
        "type": "urn:miot-spec-v2:service:device-information:00000001:dummy:1",
        "properties": [
        {
            "iid": 4,
            "type": "urn:miot-spec-v2:property:firmware-revision:00000005:dummy:1",
            "description": "Current Firmware Version",
            "format": "string",
            "access": [
              "read"
            ]
        }
        ],
        "actions": [
        {
            "iid": 1,
            "type": "urn:miot-spec-v2:action:start-sweep:00000004:dummy:1",
            "description": "Start Sweep",
            "in": [],
            "out": []
        }
        ],
        "events": [
        {
            "iid": 1,
            "type": "urn:miot-spec-v2:event:low-battery:00000003:dummy:1",
            "description": "Low Battery",
            "arguments": []
        }
        ]
    }
"""


def test_enum():
    """Test that enum parsing works."""
    data = """
    {
        "value": 1,
        "description": "dummy"
    }"""
    en = MiotEnumValue.parse_raw(data)
    assert en.value == 1
    assert en.description == "dummy"


def test_enum_missing_description():
    """Test that missing description gets replaced by the value."""
    data = '{"value": 1, "description": ""}'
    en = MiotEnumValue.parse_raw(data)
    assert en.value == 1
    assert en.description == "1"


TYPES_FOR_FORMAT = [
    ("bool", bool),
    ("string", str),
    ("float", float),
    ("uint8", int),
    ("uint16", int),
    ("uint32", int),
    ("int8", int),
    ("int16", int),
    ("int32", int),
]


@pytest.mark.parametrize("format,expected_type", TYPES_FOR_FORMAT)
def test_format(format, expected_type):
    class Wrapper(BaseModel):
        """Need to wrap as plain string is not valid json."""

        format: MiotFormat

    data = f'{{"format": "{format}"}}'  # noqa: B028
    f = Wrapper.parse_raw(data)
    assert f.format == expected_type


def test_action():
    """Test the public properties of action."""
    simple_action = """
    {
        "iid": 1,
        "type": "urn:miot-spec-v2:action:dummy-action:0000001:dummy:1",
        "description": "Description",
        "in": [],
        "out": []
    }"""
    act = MiotAction.parse_raw(simple_action)
    assert act.aiid == 1
    assert act.urn.type == "action"
    assert act.description == "Description"
    assert act.inputs == []
    assert act.outputs == []

    assert act.plain_name == "dummy-action"


@pytest.mark.parametrize(
    ("urn_string", "unexpected"),
    [
        pytest.param(
            "urn:namespace:type:name:41414141:dummy.model:1", None, id="regular_urn"
        ),
        pytest.param(
            "urn:namespace:type:name:41414141:dummy.model:1:unexpected",
            ["unexpected"],
            id="unexpected_component",
        ),
        pytest.param(
            "urn:namespace:type:name:41414141:dummy.model:1:unexpected:unexpected2",
            ["unexpected", "unexpected2"],
            id="multiple_unexpected_components",
        ),
    ],
)
def test_urn(urn_string, unexpected):
    """Test the parsing of URN strings."""
    example_urn = f'{{"urn": "{urn_string}"}}'  # noqa: B028

    class Wrapper(BaseModel):
        """Need to wrap as plain string is not valid json."""

        urn: URN

    wrapper = Wrapper.parse_raw(example_urn)
    urn = wrapper.urn
    assert urn.namespace == "namespace"
    assert urn.type == "type"
    assert urn.name == "name"
    assert urn.internal_id == "41414141"
    assert urn.model == "dummy.model"
    assert urn.version == 1
    assert urn.unexpected == unexpected

    # Check that the serialization works
    assert urn.urn_string == urn_string
    assert repr(urn) == f"<URN {urn_string} parent:None>"


def test_service():
    data = """
    {
        "iid": 1,
        "description": "test service",
        "type": "urn:miot-spec-v2:service:device-information:00000001:dummy:1"
    }
    """
    serv = MiotService.parse_raw(data)
    assert serv.siid == 1
    assert serv.urn.type == "service"
    assert serv.actions == []
    assert serv.properties == []
    assert serv.events == []


@pytest.mark.parametrize("entity_type", ["actions", "properties", "events"])
def test_service_back_references(entity_type):
    """Check that backrefs are created correctly for properties, actions, and events."""
    serv = MiotService.parse_raw(DUMMY_SERVICE)
    assert serv.siid == 1
    assert serv.urn.type == "service"

    entities = getattr(serv, entity_type)
    assert len(entities) == 1
    entity_to_test = entities[0]

    assert entity_to_test.service.siid == serv.siid


@pytest.mark.parametrize("entity_type", ["actions", "properties", "events"])
def test_entity_names(entity_type):
    """Check that entity name consists of service name and entity's plain name."""
    serv = MiotService.parse_raw(DUMMY_SERVICE)

    entities = getattr(serv, entity_type)
    assert len(entities) == 1
    entity_to_test = entities[0]
    plain_name = entity_to_test.plain_name

    assert entity_to_test.name == f"{serv.name}:{plain_name}"

    def _normalize_name(x):
        return x.replace("-", "_").replace(":", "_")

    # normalized_name should be a valid python identifier based on the normalized service name and normalized plain name
    assert (
        entity_to_test.normalized_name
        == f"{_normalize_name(serv.name)}_{_normalize_name(plain_name)}"
    )
    assert entity_to_test.normalized_name.isidentifier() is True


def test_event():
    data = '{"iid": 1, "type": "urn:spect:event:example_event:00000001:dummymodel:1", "description": "dummy", "arguments": []}'
    ev = MiotEvent.parse_raw(data)
    assert ev.eiid == 1
    assert ev.urn.type == "event"
    assert ev.description == "dummy"
    assert ev.arguments == []


def test_property():
    data = """
    {
        "iid": 1,
        "type": "urn:miot-spec-v2:property:manufacturer:00000001:dummy:1",
        "description": "Device Manufacturer",
        "format": "string",
        "access": [
          "read"
        ]
    }
    """
    prop: MiotProperty = MiotProperty.parse_raw(data)
    assert prop.piid == 1
    assert prop.urn.type == "property"
    assert prop.format == str
    assert prop.access == [MiotAccess.Read]
    assert prop.description == "Device Manufacturer"

    assert prop.plain_name == "manufacturer"


@pytest.mark.parametrize(
    ("read_only", "access"),
    [
        (True, AccessFlags.Read),
        (False, AccessFlags.Read | AccessFlags.Write),
    ],
)
def test_get_descriptor_bool_property(read_only, access):
    """Test that boolean property creates a sensor."""
    boolean_prop = load_fixture("boolean_property.json")
    if read_only:
        boolean_prop["access"].remove("write")

    prop = MiotProperty.parse_obj(boolean_prop)
    desc = prop.get_descriptor()

    assert desc.type == bool
    assert desc.access == access

    if read_only:
        assert desc.access ^ AccessFlags.Write


@pytest.mark.parametrize(
    ("read_only", "expected"),
    [(True, PropertyDescriptor), (False, RangeDescriptor)],
)
def test_get_descriptor_ranged_property(read_only, expected):
    """Test value-range descriptors."""
    ranged_prop = load_fixture("ranged_property.json")
    if read_only:
        ranged_prop["access"].remove("write")

    prop = MiotProperty.parse_obj(ranged_prop)
    desc = prop.get_descriptor()

    assert isinstance(desc, expected)
    assert desc.type == int
    if not read_only:
        assert desc.constraint == PropertyConstraint.Range


@pytest.mark.parametrize(
    ("read_only", "expected"),
    [(True, PropertyDescriptor), (False, EnumDescriptor)],
)
def test_get_descriptor_enum_property(read_only, expected):
    """Test enum descriptors."""
    enum_prop = load_fixture("enum_property.json")
    if read_only:
        enum_prop["access"].remove("write")

    prop = MiotProperty.parse_obj(enum_prop)
    desc = prop.get_descriptor()

    assert isinstance(desc, expected)
    assert desc.type == int
    if not read_only:
        assert desc.constraint == PropertyConstraint.Choice


@pytest.mark.xfail(reason="not implemented")
def test_property_pretty_value():
    """Test the pretty value conversions."""
    raise NotImplementedError()
