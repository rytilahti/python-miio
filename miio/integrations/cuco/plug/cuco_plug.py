import enum
import logging
from typing import Any, Dict

from miio import DeviceStatus, MiotDevice
from miio.click_common import command, format_output

_LOGGER = logging.getLogger(__name__)
_MAPPINGS = {
    "cuco.plug.v2eur": {
        # Source https://home.miot-spec.com/spec?type=urn:miot-spec-v2:device:outlet:0000A002:cuco-v2eur:1
        "power": {"siid": 2, "piid": 1},
        "fault": {"siid": 2, "piid": 3},
        "power_consumption": {"siid": 11, "piid": 1},
        "electric_power": {"siid": 11, "piid": 2},
        "indicator_light": {"siid": 13, "piid": 1}
    }
}


class DeviceFault(enum.Enum):
    NoFaults = 0
    OverTemperature = 1
    Overload = 2


class CucoPlugMiotStatus(DeviceStatus):

    def __init__(self, data: Dict[str, Any], model: str) -> None:
        self.data = data
        self.model = model

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.is_on else "off"

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return self.data["power"]

    @property
    def power_consumption(self) -> float:
        """True if device is currently on."""
        return self.data["power_consumption"]

    @property
    def electric_power(self) -> int:
        """True if device is currently on."""
        return self.data["electric_power"]

    @property
    def indicator_light(self) -> bool:
        """True if device is currently on."""
        return self.data["indicator_light"]

    @property
    def fault(self) -> DeviceFault:
        value = self.data["fault"]
        return DeviceFault(value)


class CucoPlugMiot(MiotDevice):

    _mappings = _MAPPINGS

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Power consumption: {result.power_consumption}\n"
            "Electric power: {result.electric_power} watt\n"
            "LED indicator: {result.indicator_light}\n"
        )
    )
    def status(self) -> CucoPlugMiotStatus:
        return CucoPlugMiotStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            },
            self.model,
        )

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.set_property("power", True)

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.set_property("power", False)
