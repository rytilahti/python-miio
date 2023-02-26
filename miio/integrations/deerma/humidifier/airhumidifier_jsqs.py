import enum
import logging
from typing import Any, Dict, Optional

import click

from miio.click_common import EnumType, command, format_output
from miio.miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)
_MAPPING = {
    # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:humidifier:0000A00E:deerma-jsqs:2
    # Air Humidifier (siid=2)
    "power": {"siid": 2, "piid": 1},  # bool
    "fault": {"siid": 2, "piid": 2},  # 0
    "mode": {"siid": 2, "piid": 5},  # 1 - lvl1, 2 - lvl2, 3 - lvl3, 4 - auto
    "target_humidity": {"siid": 2, "piid": 6},  # [40, 80] step 1
    # Environment (siid=3)
    "relative_humidity": {"siid": 3, "piid": 1},  # [0, 100] step 1
    "temperature": {"siid": 3, "piid": 7},  # [-30, 100] step 1
    # Alarm (siid=5)
    "buzzer": {"siid": 5, "piid": 1},  # bool
    # Light (siid=6)
    "led_light": {"siid": 6, "piid": 1},  # bool
    # Other (siid=7)
    "water_shortage_fault": {"siid": 7, "piid": 1},  # bool
    "tank_filed": {"siid": 7, "piid": 2},  # bool
    "overwet_protect": {"siid": 7, "piid": 3},  # bool
}

SUPPORTED_MODELS = [
    "deerma.humidifier.jsqs",
    "deerma.humidifier.jsq5",
    "deerma.humidifier.jsq2w",
]
MIOT_MAPPING = {model: _MAPPING for model in SUPPORTED_MODELS}


class OperationMode(enum.Enum):
    Low = 1
    Mid = 2
    High = 3
    Auto = 4


class AirHumidifierJsqsStatus(DeviceStatus):
    """Container for status reports from the air humidifier.

    Xiaomi Mi Smart Humidifer S (deerma.humidifier.[jsqs, jsq5, jsq2w]) response (MIoT format)::

        [
            {'did': 'power', 'siid': 2, 'piid': 1, 'code': 0, 'value': True},
            {'did': 'fault', 'siid': 2, 'piid': 2, 'code': 0, 'value': 0},
            {'did': 'mode', 'siid': 2, 'piid': 5, 'code': 0, 'value': 1},
            {'did': 'target_humidity', 'siid': 2, 'piid': 6, 'code': 0, 'value': 50},
            {'did': 'relative_humidity', 'siid': 3, 'piid': 1, 'code': 0, 'value': 40},
            {'did': 'temperature', 'siid': 3, 'piid': 7, 'code': 0, 'value': 22.7},
            {'did': 'buzzer', 'siid': 5, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'led_light', 'siid': 6, 'piid': 1, 'code': 0, 'value': True},
            {'did': 'water_shortage_fault', 'siid': 7, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'tank_filed', 'siid': 7, 'piid': 2, 'code': 0, 'value': False},
            {'did': 'overwet_protect', 'siid': 7, 'piid': 3, 'code': 0, 'value': False}
        ]
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    # Air Humidifier

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.data["power"]

    @property
    def power(self) -> str:
        """Return power state."""
        return "on" if self.is_on else "off"

    @property
    def error(self) -> int:
        """Return error state."""
        return self.data["fault"]

    @property
    def mode(self) -> OperationMode:
        """Return current operation mode."""

        try:
            mode = OperationMode(self.data["mode"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse mode: %s", e)
            return OperationMode.Auto

        return mode

    @property
    def target_humidity(self) -> Optional[int]:
        """Return target humidity."""
        return self.data.get("target_humidity")

    # Environment

    @property
    def relative_humidity(self) -> Optional[int]:
        """Return current humidity."""
        return self.data.get("relative_humidity")

    @property
    def temperature(self) -> Optional[float]:
        """Return current temperature, if available."""
        return self.data.get("temperature")

    # Alarm

    @property
    def buzzer(self) -> Optional[bool]:
        """Return True if buzzer is on."""
        return self.data.get("buzzer")

    # Indicator Light

    @property
    def led_light(self) -> Optional[bool]:
        """Return status of the LED."""
        return self.data.get("led_light")

    # Other

    @property
    def tank_filed(self) -> Optional[bool]:
        """Return the tank filed."""
        return self.data.get("tank_filed")

    @property
    def water_shortage_fault(self) -> Optional[bool]:
        """Return water shortage fault."""
        return self.data.get("water_shortage_fault")

    @property
    def overwet_protect(self) -> Optional[bool]:
        """Return True if overwet mode is active."""
        return self.data.get("overwet_protect")


class AirHumidifierJsqs(MiotDevice):
    """Main class representing the air humidifier which uses MIoT protocol."""

    _mappings = MIOT_MAPPING

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Error: {result.error}\n"
            "Target Humidity: {result.target_humidity} %\n"
            "Relative Humidity: {result.relative_humidity} %\n"
            "Temperature: {result.temperature} °C\n"
            "Water tank detached: {result.tank_filed}\n"
            "Mode: {result.mode}\n"
            "LED light: {result.led_light}\n"
            "Buzzer: {result.buzzer}\n"
            "Overwet protection: {result.overwet_protect}\n",
        )
    )
    def status(self) -> AirHumidifierJsqsStatus:
        """Retrieve properties."""

        return AirHumidifierJsqsStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.set_property("power", True)

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.set_property("power", False)

    @command(
        click.argument("humidity", type=int),
        default_output=format_output("Setting target humidity {humidity}%"),
    )
    def set_target_humidity(self, humidity: int):
        """Set target humidity."""
        if humidity < 40 or humidity > 80:
            raise ValueError(
                "Invalid target humidity: %s. Must be between 40 and 80" % humidity
            )
        return self.set_property("target_humidity", humidity)

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set working mode."""
        return self.set_property("mode", mode.value)

    @command(
        click.argument("light", type=bool),
        default_output=format_output(
            lambda light: "Turning on LED light" if light else "Turning off LED light"
        ),
    )
    def set_light(self, light: bool):
        """Set led light."""
        return self.set_property("led_light", light)

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        return self.set_property("buzzer", buzzer)

    @command(
        click.argument("overwet", type=bool),
        default_output=format_output(
            lambda overwet: "Turning on overwet" if overwet else "Turning off overwet"
        ),
    )
    def set_overwet_protect(self, overwet: bool):
        """Set overwet mode on/off."""
        return self.set_property("overwet_protect", overwet)
