"""Tests for miot model parsing."""

import pytest
from pydantic import BaseModel

from miio.miot_models import (
    URN,
    MiotAction,
    MiotEnumValue,
    MiotEvent,
    MiotFormat,
    MiotProperty,
    MiotService,
)


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

    data = f'{{"format": "{format}"}}'
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


def test_urn():
    """Test the parsing of URN strings."""
    urn_string = "urn:namespace:type:name:41414141:dummy.model:1"
    example_urn = f'{{"urn": "{urn_string}"}}'

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
    assert prop.access == ["read"]
    assert prop.description == "Device Manufacturer"

    assert prop.plain_name == "manufacturer"


@pytest.mark.xfail(reason="not implemented")
def test_property_pretty_value():
    """Test the pretty value conversions."""
    raise NotImplementedError()
