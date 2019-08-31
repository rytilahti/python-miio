import enum
import logging
from typing import Any, Dict

import click

from .click_common import command, format_output, EnumType
from .device import Device

_LOGGER = logging.getLogger(__name__)

MODEL_TOILET_V1 = 'tinymu.toiletlid.v1'

AVAILABLE_PROPERTIES_COMMON = [
    'work_state',
    'filter_use_flux',
    'filter_use_time',
]

AVAILABLE_PROPERTIES = {
    MODEL_TOILET_V1: AVAILABLE_PROPERTIES_COMMON
}


class AmbientLightColor(enum.Enum):
    White = 0
    Yellow = 1
    Powder = 2
    Green = 3
    Purple = 4
    Blue = 5
    Orange = 6
    Red = 7


class ToiletStatus:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def is_use(self) -> bool:
        """True if device is currently on."""
        return self.work != 1

    @property
    def filter_use_percentage(self) -> str:
        return "{}%".format(self.data["filter_use_flux"])

    @property
    def filter_remaining_time(self) -> str:
        return self.data["filter_use_time"]

    def __repr__(self) -> str:
        return "<ToiletStatus work=%s, " \
               "filter_use_percentage=%s, " \
               "filter_remaining_time=%s>" % \
               (
                   self.is_use,
                   self.filter_use_percentage,
                   self.filter_remaining_time
               )


class Toilet(Device):
    def __init__(self, ip: str = None, token: str = None, start_id: int = 0,
                 debug: int = 0, lazy_discover: bool = True,
                 model: str = MODEL_TOILET_V1) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_TOILET_V1

    @command(
        default_output=format_output(
            "",
            "Use: {result.use}\n"
            "Filter remaining: {result.filter_use_percentage} %\n"
            "Filter remaining time: {result.filter_remaining_time}\n"
        )
    )
    def status(self) -> ToiletStatus:
        """Retrieve properties."""
        properties = AVAILABLE_PROPERTIES[self.model]

        # A single request is limited to 16 properties. Therefore the
        # properties are divided into multiple requests
        _props_per_request = 15

        _props = properties.copy()
        values = []
        while _props:
            values.extend(self.send("get_prop", _props[:_props_per_request]))
            _props[:] = _props[_props_per_request:]

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.error(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return ToiletStatus(dict(zip(properties, values)))

    @command(
        default_output=format_output("Nozzle clean"),
    )
    def nozzle_clean(self):
        """Nozzle clean."""
        return self.send("nozzle_clean", ["on"])

    @command(
        click.argument("color", type=EnumType(AmbientLightColor, False)),
        default_output=format_output(
            "Set the ambient light to {color} color the next time you start it.")
    )
    def set_ambient_light(self, color: AmbientLightColor):
        """Set Ambient light color."""
        return self.send("set_aled_v_of_uid", ["", color.value])

    @command(
        default_output=format_output(
            "Get the Ambient light color.")
    )
    def get_ambient_light(self) -> AmbientLightColor:
        """Set Ambient light color."""
        color = self.send("get_aled_v_of_uid", [""])
        if color:
            return AmbientLightColor(color[0])
        else:
            return AmbientLightColor(0)
