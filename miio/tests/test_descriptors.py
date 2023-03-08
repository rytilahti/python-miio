from enum import Enum

import pytest

from miio.descriptors import (
    AccessFlags,
    ActionDescriptor,
    Descriptor,
    EnumDescriptor,
    PropertyConstraint,
    PropertyDescriptor,
)

COMMON_FIELDS = {
    "id": "test",
    "name": "Test",
    "type": int,
    "status_attribute": "test",
    "unit": "unit",
    "extras": {"test": "test"},
}


def test_accessflags():
    """Test that accessflags str representation is correct."""
    assert str(AccessFlags(AccessFlags.Read)) == "r--"
    assert str(AccessFlags(AccessFlags.Write)) == "-w-"
    assert str(AccessFlags(AccessFlags.Execute)) == "--x"
    assert str(AccessFlags(AccessFlags.Read | AccessFlags.Write)) == "rw-"


@pytest.mark.parametrize(
    ("class_", "access"),
    [
        pytest.param(Descriptor, AccessFlags(0), id="base class (no access)"),
        pytest.param(ActionDescriptor, AccessFlags.Execute, id="action (execute)"),
        pytest.param(
            PropertyDescriptor, AccessFlags.Read, id="regular property (read)"
        ),
    ],
)
def test_descriptor(class_, access):
    """Test that the common descriptor has the expected API."""
    desc = class_(**COMMON_FIELDS)
    assert desc.id == "test"
    assert desc.name == "Test"
    assert desc.type == int
    assert desc.status_attribute == "test"
    assert desc.extras == {"test": "test"}
    assert desc.access == access

    # TODO: test for cli output in the derived classes
    assert hasattr(desc, "__cli_output__")


def test_actiondescriptor():
    """Test that an action descriptor has the expected API."""
    desc = ActionDescriptor(id="test", name="Test", extras={"test": "test"})
    assert desc.id == "test"
    assert desc.name == "Test"
    assert desc.method_name is None
    assert desc.type is None
    assert desc.status_attribute is None
    assert desc.inputs is None
    assert desc.extras == {"test": "test"}
    assert desc.access == AccessFlags.Execute


def test_propertydescriptor():
    """Test that a property descriptor has the expected API."""
    desc = PropertyDescriptor(
        id="test",
        name="Test",
        type=int,
        status_attribute="test",
        unit="unit",
        extras={"test": "test"},
    )
    assert desc.id == "test"
    assert desc.name == "Test"
    assert desc.type == int
    assert desc.status_attribute == "test"
    assert desc.unit == "unit"
    assert desc.extras == {"test": "test"}
    assert desc.access == AccessFlags.Read


def test_enumdescriptor():
    """Test that an enum descriptor has the expected API."""

    class TestChoices(Enum):
        One = 1
        Two = 2

    desc = EnumDescriptor(**COMMON_FIELDS, choices=TestChoices)
    assert desc.id == "test"
    assert desc.name == "Test"
    assert desc.type == int
    assert desc.status_attribute == "test"
    assert desc.unit == "unit"
    assert desc.extras == {"test": "test"}
    assert desc.access == AccessFlags.Read
    assert desc.constraint == PropertyConstraint.Choice
    assert desc.choices == TestChoices
