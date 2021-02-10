import enum
import logging
from typing import Any, Dict, List

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus

_LOGGER = logging.getLogger(__name__)

MODEL_TOILETLID_V1 = "tinymu.toiletlid.v1"

AVAILABLE_PROPERTIES_COMMON = ["work_state", "filter_use_flux", "filter_use_time"]

AVAILABLE_PROPERTIES = {MODEL_TOILETLID_V1: AVAILABLE_PROPERTIES_COMMON}


class AmbientLightColor(enum.Enum):
    White = "0"
    Yellow = "1"
    Powder = "2"
    Green = "3"
    Purple = "4"
    Blue = "5"
    Orange = "6"
    Red = "7"


class ToiletlidOperatingMode(enum.Enum):
    Vacant = 0
    Occupied = 1
    RearCleanse = 2
    FrontCleanse = 3
    NozzleClean = 6


class ToiletlidStatus(DeviceStatus):
    def __init__(self, data: Dict[str, Any]) -> None:
        # {"work_state": 1,"filter_use_flux": 100,"filter_use_time": 180, "ambient_light": "Red"}
        self.data = data

    @property
    def work_state(self) -> int:
        """Device state code."""
        return self.data["work_state"]

    @property
    def work_mode(self) -> ToiletlidOperatingMode:
        """Device working mode."""
        return ToiletlidOperatingMode((self.work_state - 1) // 16)

    @property
    def is_on(self) -> bool:
        return self.work_state != 1

    @property
    def filter_use_percentage(self) -> str:
        """Filter percentage of remaining life."""
        return "{}%".format(self.data["filter_use_flux"])

    @property
    def filter_remaining_time(self) -> int:
        """Filter remaining life days."""
        return self.data["filter_use_time"]

    @property
    def ambient_light(self) -> str:
        """Ambient light color."""
        return self.data["ambient_light"]


class Toiletlid(Device):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_TOILETLID_V1,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_TOILETLID_V1

    @command(
        default_output=format_output(
            "",
            "Work: {result.is_on}\n"
            "State: {result.work_state}\n"
            "Work Mode: {result.work_mode}\n"
            "Ambient Light: {result.ambient_light}\n"
            "Filter remaining: {result.filter_use_percentage}\n"
            "Filter remaining time: {result.filter_remaining_time}\n",
        )
    )
    def status(self) -> ToiletlidStatus:
        """Retrieve properties."""
        properties = AVAILABLE_PROPERTIES[self.model]
        values = self.get_properties(properties)

        color = self.get_ambient_light()
        return ToiletlidStatus(dict(zip(properties, values), ambient_light=color))

    @command(default_output=format_output("Nozzle clean"))
    def nozzle_clean(self):
        """Nozzle clean."""
        return self.send("nozzle_clean", ["on"])

    @command(
        click.argument("color", type=EnumType(AmbientLightColor)),
        click.argument("xiaomi_id", type=str, default=""),
        default_output=format_output(
            "Set the ambient light to {color} color the next time you start it."
        ),
    )
    def set_ambient_light(self, color: AmbientLightColor, xiaomi_id: str = ""):
        """Set Ambient light color."""
        return self.send("set_aled_v_of_uid", [xiaomi_id, color.value])

    @command(
        click.argument("xiaomi_id", type=str, default=""),
        default_output=format_output("Get the Ambient light color."),
    )
    def get_ambient_light(self, xiaomi_id: str = "") -> str:
        """Get Ambient light color."""
        color = self.send("get_aled_v_of_uid", [xiaomi_id])
        try:
            return AmbientLightColor(color[0]).name
        except ValueError:
            _LOGGER.warning(
                "Get ambient light response error, return unknown value: %s.", color[0]
            )
            return "Unknown"

    @command(default_output=format_output("Get user list."))
    def get_all_user_info(self) -> List[Dict]:
        """Get All bind user."""
        users = self.send("get_all_user_info")
        return users

    @command(
        click.argument("xiaomi_id", type=str),
        click.argument("band_mac", type=str),
        click.argument("alias", type=str),
        default_output=format_output("Bind xiaomi band to xiaomi id."),
    )
    def bind_xiaomi_band(self, xiaomi_id: str, band_mac: str, alias: str):

        """Bind xiaomi band to xiaomi id."""
        return self.send("uid_mac_op", [xiaomi_id, band_mac, alias, "bind"])

    @command(
        click.argument("xiaomi_id", type=str),
        click.argument("band_mac", type=str),
        default_output=format_output("Unbind xiaomi band to xiaomi id."),
    )
    def unbind_xiaomi_band(self, xiaomi_id: str, band_mac: str):
        """Unbind xiaomi band to xiaomi id."""
        return self.send("uid_mac_op", [xiaomi_id, band_mac, "", "unbind"])
