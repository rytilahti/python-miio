import logging
from enum import Enum
from functools import partial
from typing import Any, Union

import click

from .click_common import EnumType, LiteralParamType, command
from .device import Device
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)


def _str2bool(x):
    """Helper to convert string to boolean."""
    return x.lower() in ("true", "1")


# partial is required here for str2bool, see https://stackoverflow.com/a/40339397
class MiotValueType(Enum):
    Int = int
    Float = float
    Bool = partial(_str2bool)
    Str = str


class MiotDevice(Device):
    """Main class representing a MIoT device."""

    mapping = None

    def get_properties_for_mapping(self) -> list:
        """Retrieve raw properties based on mapping."""

        # We send property key in "did" because it's sent back via response and we can identify the property.
        properties = [
            {"did": k, **v} for k, v in self.mapping.items() if "aiid" not in v
        ]

        return self.get_properties(
            properties, property_getter="get_properties", max_properties=15
        )

    @command(
        click.argument("name", type=str),
        click.argument("params", type=LiteralParamType(), required=False),
    )
    def call_action(self, name: str, params=None):
        """Call an action by a name in the mapping."""
        action = self.mapping.get(name)
        if "siid" not in action or "aiid" not in action:
            raise DeviceException(f"{name} is not an action (missing siid or aiid)")

        return self.call_action_by(action["siid"], action["aiid"], params)

    @command(
        click.argument("siid", type=int),
        click.argument("aiid", type=int),
        click.argument("params", type=LiteralParamType(), required=False),
    )
    def call_action_by(self, siid, aiid, params=None):
        """Call an action."""
        if params is None:
            params = []
        payload = {
            "did": f"call-{siid}-{aiid}",
            "siid": siid,
            "aiid": aiid,
            "in": params,
        }

        return self.send("action", payload)

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
