import logging
from datetime import timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    from pydantic.v1 import BaseModel, Field, PrivateAttr, root_validator
except ImportError:
    from pydantic import BaseModel, Field, PrivateAttr, root_validator

from .descriptors import (
    AccessFlags,
    ActionDescriptor,
    EnumDescriptor,
    PropertyDescriptor,
    RangeDescriptor,
)

_LOGGER = logging.getLogger(__name__)


class URN(BaseModel):
    """Parsed type URN.

    The expected format is urn:<namespace>:<type>:<name>:<id>:<model>:<version>.
    All extraneous parts are stored inside *unexpected*.
    """

    namespace: str
    type: str
    name: str
    internal_id: str
    model: str
    version: int
    unexpected: Optional[List[str]]

    parent_urn: Optional["URN"] = Field(None, repr=False)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str) or ":" not in v:
            raise TypeError("invalid type")

        _, namespace, type, name, id_, model, version, *unexpected = v.split(":")

        return cls(
            namespace=namespace,
            type=type,
            name=name,
            internal_id=id_,
            model=model,
            version=version,
            unexpected=unexpected if unexpected else None,
        )

    @property
    def urn_string(self) -> str:
        """Return string presentation of the URN."""
        urn = f"urn:{self.namespace}:{self.type}:{self.name}:{self.internal_id}:{self.model}:{self.version}"
        if self.unexpected is not None:
            urn = f"{urn}:{':'.join(self.unexpected)}"
        return urn

    def __repr__(self):
        return f"<URN {self.urn_string} parent:{self.parent_urn}>"


class MiotFormat(type):
    """Custom type to convert textual presentation to python type."""

    @classmethod
    def __get_validators__(cls):
        yield cls.convert_type

    @classmethod
    def convert_type(cls, input: str):
        if input.startswith("uint") or input.startswith("int"):
            return int
        type_map = {
            "bool": bool,
            "string": str,
            "float": float,
            "none": None,
        }
        return type_map[input]


class MiotEnumValue(BaseModel):
    """Enum value for miot."""

    description: str
    value: int

    @root_validator
    def description_from_value(cls, values):
        """If description is empty, use the value instead."""
        if not values["description"]:
            values["description"] = str(values["value"])
        return values

    class Config:
        extra = "forbid"


class MiotBaseModel(BaseModel):
    """Base model for all other miot models."""

    urn: URN = Field(alias="type")
    description: str

    extras: Dict = Field(default_factory=dict, repr=False)
    service: Optional["MiotService"] = None  # backref to containing service

    def fill_from_parent(self, service: "MiotService"):
        """Fill some information from the parent service."""
        # TODO: this could be done using a validator
        self.service = service
        self.urn.parent_urn = service.urn

    @property
    def siid(self) -> Optional[int]:
        """Return siid."""
        if self.service is not None:
            return self.service.siid

        return None

    @property
    def plain_name(self) -> str:
        """Return plain name."""
        return self.urn.name

    @property
    def name(self) -> str:
        """Return combined name of the service and the action."""
        if self.service is not None and self.urn.name is not None:
            return f"{self.service.name}:{self.urn.name}"  # type: ignore
        return "unitialized"

    @property
    def normalized_name(self) -> str:
        """Return a normalized name.

        This returns a normalized :meth:`name` that can be used as a python identifier,
        currently meaning that ':' and '-' are replaced with '_'.
        """
        return self.name.replace(":", "_").replace("-", "_")


class MiotAction(MiotBaseModel):
    """Action presentation for miot."""

    aiid: int = Field(alias="iid")

    inputs: Any = Field(alias="in")
    outputs: Any = Field(alias="out")

    def fill_from_parent(self, service: "MiotService"):
        """Overridden to convert inputs and outputs to property references."""
        super().fill_from_parent(service)
        self.inputs = [service.get_property_by_id(piid) for piid in self.inputs]
        self.outputs = [service.get_property_by_id(piid) for piid in self.outputs]

    def get_descriptor(self):
        """Create a descriptor based on the property information."""
        id_ = self.name

        extras = self.extras
        extras["urn"] = self.urn
        extras["siid"] = self.siid
        extras["aiid"] = self.aiid
        extras["miot_action"] = self

        inputs = self.inputs
        if inputs:
            # TODO: this is just temporarily here, pending refactoring the descriptor creation into the model
            inputs = [prop.get_descriptor() for prop in self.inputs]

        return ActionDescriptor(
            id=id_,
            name=self.description,
            inputs=inputs,
            extras=extras,
        )

    class Config:
        extra = "forbid"


class MiotAccess(Enum):
    Read = "read"
    Write = "write"
    Notify = "notify"


class MiotProperty(MiotBaseModel):
    """Property presentation for miot."""

    piid: int = Field(alias="iid")

    format: MiotFormat
    access: List[MiotAccess] = Field(default=["read"])
    unit: Optional[str] = None

    range: Optional[List[int]] = Field(alias="value-range")
    choices: Optional[List[MiotEnumValue]] = Field(alias="value-list")
    gatt_access: Optional[List[Any]] = Field(alias="gatt-access")

    # TODO: currently just used to pass the data for miiocli
    #       there must be a better way to do this..
    value: Optional[Any] = None

    @property
    def pretty_value(self):
        value = self.value

        if self.choices is not None:
            # TODO: find a nicer way to get the choice by value
            selected = next(c.description for c in self.choices if c.value == value)
            current = f"{selected} (value: {value})"
            return current

        if self.format == bool:
            return bool(value)

        unit_map = {
            "none": "",
            "percentage": "%",
            "minutes": timedelta(minutes=1),
            "hours": timedelta(hours=1),
            "days": timedelta(days=1),
        }

        unit = unit_map.get(self.unit)
        if isinstance(unit, timedelta):
            value = value * unit
        else:
            value = f"{value} {unit}"

        return value

    @property
    def pretty_access(self):
        """Return pretty-printable access."""
        acc = ""
        if MiotAccess.Read in self.access:
            acc += "R"
        if MiotAccess.Write in self.access:
            acc += "W"
        # Just for completeness, as notifications are not supported
        # if MiotAccess.Notify in self.access:
        #    acc += "N"

        return acc

    @property
    def pretty_input_constraints(self) -> str:
        """Return input constraints for writable settings."""
        out = ""
        if self.choices is not None:
            out += (
                "choices: "
                + ", ".join([f"{c.description} ({c.value})" for c in self.choices])
                + ""
            )
        if self.range is not None:
            out += f"min: {self.range[0]}, max: {self.range[1]}, step: {self.range[2]}"

        return out

    def get_descriptor(self) -> PropertyDescriptor:
        """Create a descriptor based on the property information."""
        # TODO: initialize inside __init__?
        extras = self.extras
        extras["urn"] = self.urn
        extras["siid"] = self.siid
        extras["piid"] = self.piid
        extras["miot_property"] = self

        desc: PropertyDescriptor

        # Handle ranged properties
        if self.range is not None:
            desc = self._create_range_descriptor()

        # Handle enums
        elif self.choices is not None:
            desc = self._create_enum_descriptor()

        else:
            desc = self._create_regular_descriptor()

        return desc

    def _miot_access_list_to_access(self, access_list: List[MiotAccess]) -> AccessFlags:
        """Convert miot access list to property access list."""
        access = AccessFlags(0)
        if MiotAccess.Read in access_list:
            access |= AccessFlags.Read
        if MiotAccess.Write in access_list:
            access |= AccessFlags.Write

        return access

    def _create_enum_descriptor(self) -> EnumDescriptor:
        """Create a descriptor for enum-based property."""
        try:
            choices = Enum(
                self.description, {c.description: c.value for c in self.choices}
            )
            _LOGGER.debug("Created enum %s", choices)
        except ValueError as ex:
            _LOGGER.error("Unable to create enum for %s: %s", self, ex)
            raise

        desc = EnumDescriptor(
            id=self.name,
            name=self.description,
            status_attribute=self.normalized_name,
            unit=self.unit,
            choices=choices,
            extras=self.extras,
            type=self.format,
            access=self._miot_access_list_to_access(self.access),
        )

        return desc

    def _create_range_descriptor(
        self,
    ) -> RangeDescriptor:
        """Create a descriptor for range-based property."""
        if self.range is None:
            raise ValueError("Range is None")
        desc = RangeDescriptor(
            id=self.name,
            name=self.description,
            status_attribute=self.normalized_name,
            min_value=self.range[0],
            max_value=self.range[1],
            step=self.range[2],
            unit=self.unit,
            extras=self.extras,
            type=self.format,
            access=self._miot_access_list_to_access(self.access),
        )

        return desc

    def _create_regular_descriptor(self) -> PropertyDescriptor:
        """Create boolean setting descriptor."""
        return PropertyDescriptor(
            id=self.name,
            name=self.description,
            status_attribute=self.normalized_name,
            type=self.format,
            extras=self.extras,
            access=self._miot_access_list_to_access(self.access),
        )

    class Config:
        extra = "forbid"


class MiotEvent(MiotBaseModel):
    """Presentation of miot event."""

    eiid: int = Field(alias="iid")
    arguments: Any

    class Config:
        extra = "forbid"


class MiotService(BaseModel):
    """Service presentation for miot."""

    siid: int = Field(alias="iid")
    urn: URN = Field(alias="type")
    description: str

    properties: List[MiotProperty] = Field(default_factory=list, repr=False)
    events: List[MiotEvent] = Field(default_factory=list, repr=False)
    actions: List[MiotAction] = Field(default_factory=list, repr=False)

    _property_by_id: Dict[int, MiotProperty] = PrivateAttr(default_factory=dict)
    _action_by_id: Dict[int, MiotAction] = PrivateAttr(default_factory=dict)

    def __init__(self, *args, **kwargs):
        """Initialize a service.

        Overridden to propagate the service to the children.
        """
        super().__init__(*args, **kwargs)

        for prop in self.properties:
            self._property_by_id[prop.piid] = prop
            prop.fill_from_parent(self)
        for act in self.actions:
            self._action_by_id[act.aiid] = act
            act.fill_from_parent(self)
        for ev in self.events:
            ev.fill_from_parent(self)

    def get_property_by_id(self, piid):
        """Return property by id."""
        return self._property_by_id[piid]

    def get_action_by_id(self, aiid):
        """Return action by id."""
        return self._action_by_id[aiid]

    @property
    def name(self) -> str:
        """Return service name."""
        return self.urn.name

    @property
    def normalized_name(self) -> str:
        """Return normalized service name.

        This returns a normalized :meth:`name` that can be used as a python identifier,
        currently meaning that ':' and '-' are replaced with '_'.
        """
        return self.urn.name.replace(":", "_").replace("-", "_")

    class Config:
        extra = "forbid"


class DeviceModel(BaseModel):
    """Device presentation for miot."""

    description: str
    urn: URN = Field(alias="type")
    services: List[MiotService] = Field(repr=False)

    # internal mappings to simplify accesses
    _services_by_id: Dict[int, MiotService] = PrivateAttr(default_factory=dict)
    _properties_by_id: Dict[int, Dict[int, MiotProperty]] = PrivateAttr(
        default_factory=dict
    )
    _properties_by_name: Dict[str, Dict[str, MiotProperty]] = PrivateAttr(
        default_factory=dict
    )

    def __init__(self, *args, **kwargs):
        """Presentation of a miot device model scehma.

        Overridden to implement internal (siid, piid) mapping.
        """
        super().__init__(*args, **kwargs)
        for serv in self.services:
            self._services_by_id[serv.siid] = serv
            self._properties_by_name[serv.name] = dict()
            self._properties_by_id[serv.siid] = dict()
            for prop in serv.properties:
                self._properties_by_name[serv.name][prop.plain_name] = prop
                self._properties_by_id[serv.siid][prop.piid] = prop

    @property
    def device_type(self) -> str:
        """Return device type as string."""
        return self.urn.type

    def get_service_by_siid(self, siid: int) -> MiotService:
        """Return the service for given siid."""
        return self._services_by_id[siid]

    def get_property(self, service: str, prop_name: str) -> MiotProperty:
        """Return the property model for given service and property name."""
        return self._properties_by_name[service][prop_name]

    def get_property_by_siid_piid(self, siid: int, piid: int) -> MiotProperty:
        """Return the property model for given siid, piid."""
        return self._properties_by_id[siid][piid]

    class Config:
        extra = "forbid"
