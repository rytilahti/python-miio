import logging
from typing import Any, List, Optional

from pydantic import BaseModel, Field

_LOGGER = logging.getLogger(__name__)


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

    @classmethod
    def serialize(cls, v):
        return str(v)


class MiotEvent(BaseModel):
    """Presentation of miot event."""

    description: str
    eiid: int = Field(alias="iid")
    urn: str = Field(alias="type")
    arguments: Any

    class Config:
        extra = "forbid"


class MiotEnumValue(BaseModel):
    """Enum value for miot."""

    description: str
    value: int

    class Config:
        extra = "forbid"


class MiotAction(BaseModel):
    """Action presentation for miot."""

    description: str
    aiid: int = Field(alias="iid")
    urn: str = Field(alias="type")
    inputs: Any = Field(alias="in")
    output: Any = Field(alias="out")

    class Config:
        extra = "forbid"


class MiotProperty(BaseModel):
    """Property presentation for miot."""

    description: str
    piid: int = Field(alias="iid")
    urn: str = Field(alias="type")
    unit: str = Field(default="unknown")
    format: MiotFormat
    access: Any = Field(default=["read"])
    range: Optional[List[int]] = Field(alias="value-range")
    choices: Optional[List[MiotEnumValue]] = Field(alias="value-list")

    class Config:
        extra = "forbid"


class MiotService(BaseModel):
    """Service presentation for miot."""

    description: str
    siid: int = Field(alias="iid")
    urn: str = Field(alias="type")
    properties: List[MiotProperty] = Field(default=[], repr=False)
    events: Optional[List[MiotEvent]] = Field(default=[], repr=False)
    actions: Optional[List[MiotAction]] = Field(default=[], repr=False)

    class Config:
        extra = "forbid"


class DeviceModel(BaseModel):
    """Device presentation for miot."""

    description: str
    urn: str = Field(alias="type")
    services: List[MiotService] = Field(repr=False)
    model: Optional[str] = None

    class Config:
        extra = "forbid"
