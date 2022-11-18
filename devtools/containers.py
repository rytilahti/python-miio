import logging
from dataclasses import dataclass, field
from operator import attrgetter
from typing import Any, Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, config

_LOGGER = logging.getLogger(__name__)


def pretty_name(name):
    return name.replace(" ", "_").replace("-", "_")


def python_type_for_type(x):
    if "int" in x:
        return "int"
    if x == "string":
        return "str"
    if x in ["float", "bool"]:
        return x

    return f"unknown type {x}"


def indent(data, level=4):
    indented = ""
    for x in data.splitlines(keepends=True):
        indented += " " * level + x

    return indented


@dataclass
class InstanceInfo:
    model: str
    status: str
    type: str
    version: int

    @property
    def filename(self) -> str:
        return f"{self.model}_{self.status}_{self.version}.json"


@dataclass
class ModelMapping(DataClassJsonMixin):
    instances: List[InstanceInfo]

    def info_for_model(self, model: str, *, status_filter="released") -> InstanceInfo:
        matches = [inst for inst in self.instances if inst.model == model]

        if len(matches) > 1:
            _LOGGER.warning(
                "more than a single match for model %s: %s, filtering with status=%s",
                model,
                matches,
                status_filter,
            )

        released_versions = [inst for inst in matches if inst.status == status_filter]
        if not released_versions:
            raise Exception(f"No releases for {model}, adjust status_filter if you ")

        _LOGGER.debug("Got %s releases, picking the newest one", released_versions)

        match = max(released_versions, key=attrgetter("version"))
        _LOGGER.debug("Using %s", match)

        return match


@dataclass
class Property(DataClassJsonMixin):
    iid: int
    type: str
    description: str
    format: str
    access: List[str]

    value_list: Optional[List[Dict[str, Any]]] = field(
        default_factory=list, metadata=config(field_name="value-list")
    )  # type: ignore
    value_range: Optional[List[int]] = field(
        default=None, metadata=config(field_name="value-range")
    )

    unit: Optional[str] = None

    def __repr__(self):
        return f"piid: {self.iid} ({self.description}): ({self.format}, unit: {self.unit}) (acc: {self.access})"

    def __str__(self):
        return self.__repr__()

    def _generate_enum(self):
        s = f"class {self.pretty_name()}Enum(enum.Enum):\n"
        for value in self.value_list:
            s += f"    {pretty_name(value['description'])} = {value['value']}\n"
        s += "\n"
        return s

    def pretty_name(self):
        return pretty_name(self.description)

    def _generate_value_and_range(self):
        s = ""
        if self.value_range:
            s += f"    Range: {self.value_range}\n"
        if self.value_list:
            s += f"    Values: {self.pretty_name()}Enum\n"
        return s

    def _generate_docstring(self):
        return (
            f"{self.description} (siid: {self.siid}, piid: {self.iid}) - {self.type} "
        )

    def _generate_getter(self):
        s = ""
        s += (
            f"def read_{self.pretty_name()}() -> {python_type_for_type(self.format)}:\n"
        )
        s += f'    """{self._generate_docstring()}\n'
        s += self._generate_value_and_range()
        s += '    """\n\n'

        return s

    def _generate_setter(self):
        s = ""
        s += f"def write_{self.pretty_name()}(var: {python_type_for_type(self.format)}):\n"
        s += f'    """{self._generate_docstring()}\n'
        s += self._generate_value_and_range()
        s += '    """\n'
        s += "\n"
        return s

    def as_code(self, siid):
        s = ""
        self.siid = siid

        if self.value_list:
            s += self._generate_enum()

        if "read" in self.access:
            s += self._generate_getter()
        if "write" in self.access:
            s += self._generate_setter()

        return s


@dataclass
class Action(DataClassJsonMixin):
    iid: int
    type: str
    description: str
    out: List[Any] = field(default_factory=list)
    in_: List[Any] = field(default_factory=list, metadata=config(field_name="in"))

    def __repr__(self):
        return f"aiid {self.iid} {self.description}: in: {self.in_} -> out: {self.out}"

    def pretty_name(self):
        return pretty_name(self.description)

    def as_code(self, siid):
        self.siid = siid
        s = ""
        s += f"def {self.pretty_name()}({self.in_}) -> {self.out}:\n"
        s += f'    """{self.description} (siid: {self.siid}, aiid: {self.iid}) {self.type}"""\n\n'
        return s


@dataclass
class Event(DataClassJsonMixin):
    iid: int
    type: str
    description: str
    arguments: List[int]

    def __repr__(self):
        return f"eiid {self.iid} ({self.description}): (args: {self.arguments})"


@dataclass
class Service(DataClassJsonMixin):
    iid: int
    type: str
    description: str
    properties: List[Property] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)

    def __repr__(self):
        return f"siid {self.iid}: ({self.description}): {len(self.properties)} props, {len(self.actions)} actions"

    def as_code(self):
        s = ""
        s += f"class {pretty_name(self.description)}(MiOTService):\n"
        s += '    """\n'
        s += f"    {self.description} ({self.type}) (siid: {self.iid})\n"
        s += f"    Events: {len(self.events)}\n"
        s += f"    Properties: {len(self.properties)}\n"
        s += f"    Actions: {len(self.actions)}\n"
        s += '    """\n\n'
        s += "#### PROPERTIES ####\n"
        for property in self.properties:
            s += indent(property.as_code(self.iid))
        s += "#### PROPERTIES END ####\n\n"
        s += "#### ACTIONS ####\n"
        for act in self.actions:
            s += indent(act.as_code(self.iid))
        s += "#### ACTIONS END ####\n\n"
        return s


@dataclass
class Device(DataClassJsonMixin):
    type: str
    description: str
    services: List[Service] = field(default_factory=list)

    def as_code(self):
        s = ""
        s += '"""'
        s += f"Support template for {self.description} ({self.type})\n\n"
        s += f"Contains {len(self.services)} services\n"
        s += '"""\n\n'

        for serv in self.services:
            s += serv.as_code()

        return s
