import logging
from enum import Enum
from typing import Any, Union

import click

from .click_common import EnumType, command
from .device import Device

_LOGGER = logging.getLogger(__name__)


class MiotValueType(Enum):
    Int = int
    Float = float
    Bool = bool
    Str = str


class MiotDevice(Device):
    """Main class representing a MIoT device."""

    mapping = None

    def get_properties_for_mapping(self) -> list:
        """Retrieve raw properties based on mapping."""

        # We send property key in "did" because it's sent back via response and we can identify the property.
        properties = [{"did": k, **v} for k, v in self.mapping.items()]

        return self.get_properties(
            properties, property_getter="get_properties", max_properties=15
        )

    @command(
        click.argument("siid", type=int),
        click.argument("piid", type=int),
    )
    def get_property_by(self, siid: int, piid: int):
        """Get a single property (siid/piid)."""
        return self.send(
            "get_properties", [{"did": f"{siid}-{piid}", "siid": siid, "piid": piid}]
        )

    @command(
        click.argument("siid", type=int),
        click.argument("piid", type=int),
        click.argument("value"),
        click.argument(
            "value_type", type=EnumType(MiotValueType), required=False, default=None
        ),
    )
    def set_property_by(
        self,
        siid: int,
        piid: int,
        value: Union[int, float, str, bool],
        value_type: Any = None,
    ):
        """Set a single property (siid/piid) to given value.

        value_type can be given to convert the value to wanted type,
        allowed types are: int, float, bool, str
        """
        if value_type is not None:
            value = value_type.value(value)

        return self.send(
            "set_properties",
            [{"did": f"set-{siid}-{piid}", "siid": siid, "piid": piid, "value": value}],
        )

    def set_property(self, property_key: str, value):
        """Sets property value using the existing mapping."""
        return self.send(
            "set_properties",
            [{"did": property_key, **self.mapping[property_key], "value": value}],
        )
