import enum
import logging
from collections import defaultdict
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .device import Device
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_HUMIDIFIER_MJJSQ = "deerma.humidifier.mjjsq"

AVAILABLE_PROPERTIES = {
    MODEL_HUMIDIFIER_MJJSQ: [
        "OnOff_State",
        "TemperatureValue",
        "Humidity_Value",
        "HumiSet_Value",
        "Humidifier_Gear",
        "Led_State",
        "TipSound_State",
        "waterstatus",
        "watertankstatus",
    ]
}


class AirHumidifierException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Low = 1
    Medium = 2
    High = 3
    Humidity = 4


class AirHumidifierStatus:
    """Container for status reports from the air humidifier mjjsq."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Air Humidifier (deerma.humidifier.mjjsq):

        {'Humidifier_Gear': 4, 'Humidity_Value': 44, 'HumiSet_Value': 54,
         'Led_State': 1, 'OnOff_State': 0, 'TemperatureValue': 21,
         'TipSound_State': 1, 'waterstatus': 1, 'watertankstatus': 1}
        """

        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.data["OnOff_State"] == 1 else "off"

    @property
    def is_on(self) -> bool:
        """True if device is turned on."""
        return self.power == "on"

    @property
    def mode(self) -> OperationMode:
        """Operation mode. Can be either low, medium, high or humidity."""
        return OperationMode(self.data["Humidifier_Gear"])

    @property
    def temperature(self) -> int:
        """Current temperature in degree celsius."""
        return self.data["TemperatureValue"]

    @property
    def humidity(self) -> int:
        """Current humidity in percent."""
        return self.data["Humidity_Value"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["TipSound_State"] == 1

    @property
    def led(self) -> bool:
        """True if LED is turned on."""
        return self.data["Led_State"] == 1

    @property
    def target_humidity(self) -> int:
        """Target humiditiy in percent."""
        return self.data["HumiSet_Value"]

    @property
    def no_water(self) -> bool:
        """True if the water tank is empty."""
        return self.data["waterstatus"] == 0

    @property
    def water_tank_detached(self) -> bool:
        """True if the water tank is detached."""
        return self.data["watertankstatus"] == 0

    def __repr__(self) -> str:
        s = (
            "<AirHumidiferStatus power=%s, "
            "mode=%s, "
            "temperature=%s, "
            "humidity=%s%%, "
            "led_brightness=%s, "
            "buzzer=%s, "
            "target_humidity=%s%%, "
            "no_water=%s, "
            "water_tank_detached=%s>"
            % (
                self.power,
                self.mode,
                self.temperature,
                self.humidity,
                self.led,
                self.buzzer,
                self.target_humidity,
                self.no_water,
                self.water_tank_detached,
            )
        )
        return s

    def __json__(self):
        return self.data


class AirHumidifierMjjsq(Device):
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_HUMIDIFIER_MJJSQ,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_HUMIDIFIER_MJJSQ

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "Temperature: {result.temperature} °C\n"
            "Humidity: {result.humidity} %\n"
            "LED: {result.led}\n"
            "Buzzer: {result.buzzer}\n"
            "Target humidity: {result.target_humidity} %\n"
            "No water: {result.no_water}\n"
            "Water tank detached: {result.water_tank_detached}\n",
        )
    )
    def status(self) -> AirHumidifierStatus:
        """Retrieve properties."""

        properties = AVAILABLE_PROPERTIES[self.model]
        values = self.get_properties(properties, max_properties=1)

        return AirHumidifierStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("Set_OnOff", [1])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("Set_OnOff", [0])

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.send("Set_HumidifierGears", [mode.value])

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        return self.send("SetLedState", [int(led)])

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        return self.send("SetTipSound_Status", [int(buzzer)])

    @command(
        click.argument("humidity", type=int),
        default_output=format_output("Setting target humidity to {humidity}"),
    )
    def set_target_humidity(self, humidity: int):
        """Set the target humidity in percent."""
        if humidity < 0 or humidity > 99:
            raise AirHumidifierException("Invalid target humidity: %s" % humidity)

        return self.send("Set_HumiValue", [humidity])
