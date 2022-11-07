import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, PrivateAttr, root_validator

_LOGGER = logging.getLogger(__name__)


class URN(BaseModel):
    """Parsed type URN."""

    namespace: str
    type: str
    name: str
    internal_id: str
    model: str
    version: int

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str) or ":" not in v:
            raise TypeError("invalid type")

        _, namespace, type, name, id_, model, version = v.split(":")

        return cls(
            namespace=namespace,
            type=type,
            name=name,
            internal_id=id_,
            model=model,
            version=version,
        )

    def __repr__(self):
        return f"urn:{self.namespace}:{self.type}:{self.name}:{self.internal_id}:{self.model}:{self.version}"


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
        }
        return type_map[input]


class MiotEvent(BaseModel):
    """Presentation of miot event."""

    eiid: int = Field(alias="iid")
    urn: URN = Field(alias="type")
    description: str

    arguments: Any

    service: Optional["MiotService"] = None  # backref to containing service

    class Config:
        extra = "forbid"


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


class MiotAction(BaseModel):
    """Action presentation for miot."""

    aiid: int = Field(alias="iid")
    urn: URN = Field(alias="type")
    description: str

    inputs: Any = Field(alias="in")
    outputs: Any = Field(alias="out")

    extras: Dict = Field(default_factory=dict, repr=False)

    service: Optional["MiotService"] = None  # backref to containing service

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
        return f"{self.service.name}:{self.urn.name}"  # type: ignore

    class Config:
        extra = "forbid"


class MiotProperty(BaseModel):
    """Property presentation for miot."""

    piid: int = Field(alias="iid")
    urn: URN = Field(alias="type")
    description: str

    format: MiotFormat
    access: Any = Field(default=["read"])
    unit: Optional[str] = None

    range: Optional[List[int]] = Field(alias="value-range")
    choices: Optional[List[MiotEnumValue]] = Field(alias="value-list")

    extras: Dict[str, Any] = Field(default_factory=dict, repr=False)

    service: Optional["MiotService"] = None  # backref to containing service

    # TODO: currently just used to pass the data for miiocli
    #       there must be a better way to do this..
    value: Optional[Any] = None

    @property
    def siid(self) -> Optional[int]:
        """Return siid."""
        if self.service is not None:
            return self.service.siid

        return None

    @property
    def plain_name(self):
        """Return plain name."""
        return self.urn.name

    @property
    def name(self) -> str:
        """Return combined name of the service and the property."""
        return f"{self.service.name}:{self.urn.name}"  # type: ignore

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

    def __init__(self, *args, **kwargs):
        """Initialize a service.

        Overridden to propagate the siid to the children.
        """
        super().__init__(*args, **kwargs)

        for prop in self.properties:
            prop.service = self
        for act in self.actions:
            act.service = self
        for ev in self.events:
            ev.service = self

    @property
    def name(self) -> str:
        """Return service name."""
        return self.urn.name

    class Config:
        extra = "forbid"


class DeviceModel(BaseModel):
    """Device presentation for miot."""

    description: str
    urn: URN = Field(alias="type")
    services: List[MiotService] = Field(repr=False)

    # internal mappings to simplify accesses to a specific (siid, piid)
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
            self._properties_by_name[serv.name] = dict()
            self._properties_by_id[serv.siid] = dict()
            for prop in serv.properties:
                self._properties_by_name[serv.name][prop.plain_name] = prop
                self._properties_by_id[serv.siid][prop.piid] = prop

    @property
    def device_type(self) -> str:
        """Return device type as string."""
        return self.urn.type

    def get_property(self, service: str, prop_name: str) -> MiotProperty:
        """Return the property model for given service and property name."""
        return self._properties_by_name[service][prop_name]

    def get_property_by_siid_piid(self, siid: int, piid: int) -> MiotProperty:
        """Return the property model for given siid, piid."""
        return self._properties_by_id[siid][piid]

    class Config:
        extra = "forbid"
