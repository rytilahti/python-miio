"""
miot specification v2 parser. pls refer https://iot.mi.com/new/doc/standard/miot-spec/spec
"""

import enum
from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin, config


class SpecificationType(enum.Enum):
    Template = "template"
    Property = "property"
    Action = "action"
    Event = "event"
    Service = "service"
    Device = "device"


class Access(enum.Enum):
    Read = "read"
    Write = "write"
    Notify = "notify"


class UrnExpression:
    namespace: str
    type: SpecificationType
    name: str
    value: str
    vendor_product: str
    version: int

    def __init__(self, expression):
        # <URN> ::= "urn:"<namespace>":"<type>":"<name>":"<value>[":"<vendor-product>":"<version>]
        fields = expression.split(":")
        if len(fields) < 5:
            raise ValueError("Invalid urn expression: {0}".format(expression))
        assert fields[0] == "urn"
        self.namespace = fields[1]
        self.type = SpecificationType(fields[2])
        self.name = fields[3]
        self.value = fields[4]
        if len(fields) == 7:
            self.vendor_product = fields[5]
            self.version = int(fields[6])

    def __repr__(self):
        return f"urn:{self.namespace}:{self.type.value}:{self.value}:{self.vendor_product}:{self.version}"

    def __str__(self):
        return self.__repr__()


@dataclass
class Property(DataClassJsonMixin):
    iid: int
    type: UrnExpression
    description: str
    format: str
    access: List[Access]
    unit: Optional[str] = None
    value_list: List = field(
        default_factory=list, metadata=config(field_name="value-list")
    )
    value_range: Optional[List] = field(
        default=None, metadata=config(field_name="value-range")
    )

    def __init__(
        self, iid, type, description, format, access, unit, value_list, value_range
    ):
        self.iid = iid
        self.type = UrnExpression(type)
        self.description = description
        self.format = format
        self.access = [Access(a) for a in access]
        self.unit = unit
        self.value_list = value_list
        self.value_range = value_range

    def __repr__(self):
        return f"piid: {self.iid} ({self.description}): ({self.format}, unit: {self.unit}) (acc: {self.access}, value-list: {self.value_list}, value-range: {self.value_range})"

    def __str__(self):
        return self.__repr__()


@dataclass
class Action(DataClassJsonMixin):
    iid: int
    type: UrnExpression
    description: str
    out: List = field(default_factory=list)
    in_: List = field(default_factory=list, metadata=config(field_name="in"))

    def __init__(self, iid, type, description, out, in_):
        self.iid = iid
        self.type = UrnExpression(type)
        self.description = description
        self.out = out
        self.in_ = in_

    def __repr__(self):
        return f"aiid {self.iid} {self.description}: in: {self.in_} -> out: {self.out}"

    def __str__(self):
        return self.__repr__()


@dataclass
class Event(DataClassJsonMixin):
    iid: int
    type: UrnExpression
    description: str
    arguments: List

    def __init__(self, iid, type, description, arguments):
        self.iid = iid
        self.type = UrnExpression(type)
        self.description = description
        self.arguments = arguments

    def __repr__(self):
        return f"eiid {self.iid} ({self.description}): (args: {self.arguments})"

    def __str__(self):
        return self.__repr__()


@dataclass
class Service(DataClassJsonMixin):
    iid: int
    type: UrnExpression
    description: str
    properties: List[Property] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)

    def __init__(self, iid, type, description, properties, actions, events):
        self.iid = iid
        self.type = UrnExpression(type)
        self.description = description
        self.properties = properties
        self.actions = actions
        self.events = events

    def find_property(self, name):
        return next(p for p in self.properties if p.type.name == name)

    def find_property_by_iid(self, iid):
        return next(p for p in self.properties if p.iid == iid)


def __repr__(self):
    return f"siid {self.iid}: ({self.description}): {len(self.properties)} props, {len(self.actions)} actions"


def __str__(self):
    return self.__repr__()


@dataclass
class DeviceSpec(DataClassJsonMixin):
    type: UrnExpression
    description: str
    services: List[Service] = field(default_factory=list)

    def __init__(self, type, description, services):
        self.type = UrnExpression(type)
        self.description = description
        self.services = services

    def find_service(self, name: str):
        return next(s for s in self.services if s.type.name == name)

    def find_service_by_iid(self, iid: int):
        return next(s for s in self.services if s.iid == iid)

    def find_service_and_property(self, service_name, property_name):
        service = self.find_service(service_name)
        property = service.find_property(property_name)
        return service, property

    def contains(self, service_name, property_name) -> bool:
        try:
            service = self.find_service(service_name)
            service.find_property(property_name)
            return True
        except StopIteration:
            return False

    @staticmethod
    def load(file_name):
        try:
            import importlib.resources as pkg_resources
        except ImportError:
            # Try backported to PY<37 `importlib_resources`.
            import importlib_resources as pkg_resources

        try:
            from . import miot_specs

            spec = pkg_resources.read_text(miot_specs, file_name)
            return DeviceSpec.from_json(spec)
        except FileNotFoundError:
            try:
                import os

                with open(
                    os.path.join(os.path.dirname(__file__), "miot_specs", file_name)
                ) as file:
                    json = file.read()
                    return DeviceSpec.from_json(json)
            except FileNotFoundError:
                raise FileNotFoundError("file is not found: " + file_name)
