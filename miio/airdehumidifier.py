import enum
import logging
from collections import defaultdict
from typing import Any, Dict, Optional

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceInfo, DeviceStatus
from .exceptions import DeviceError, DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_DEHUMIDIFIER_V1 = "nwt.derh.wdh318efw1"

AVAILABLE_PROPERTIES = {
    MODEL_DEHUMIDIFIER_V1: [
        "on_off",
        "mode",
        "fan_st",
        "buzzer",
        "led",
        "child_lock",
        "humidity",
        "temp",
        "compressor_status",
        "fan_speed",
        "tank_full",
        "defrost_status",
        "alarm",
        "auto",
    ]
}


class AirDehumidifierException(DeviceException):
    pass


class OperationMode(enum.Enum):
    On = "on"
    Auto = "auto"
    DryCloth = "dry_cloth"


class FanSpeed(enum.Enum):
    Sleep = 0
    Low = 1
    Medium = 2
    High = 3
    Strong = 4


class AirDehumidifierStatus(DeviceStatus):
    """Container for status reports from the air dehumidifier."""

    def __init__(self, data: Dict[str, Any], device_info: DeviceInfo) -> None:
        """Response of a Air Dehumidifier (nwt.derh.wdh318efw1):

        {'on_off': 'on', 'mode': 'auto', 'fan_st': 2,
         'buzzer': 'off', 'led': 'on', 'child_lock': 'off',
         'humidity': 47, 'temp': 34, 'compressor_status': 'off',
         'fan_speed': 0, 'tank_full': 'off', 'defrost_status': 'off,
         'alarm': 'ok','auto': 50}
        """

        self.data = data
        self.device_info = device_info

    @property
    def power(self) -> str:
        """Power state."""
        return self.data["on_off"]

    @property
    def is_on(self) -> bool:
        """True if device is turned on."""
        return self.power == "on"

    @property
    def mode(self) -> OperationMode:
        """Operation mode.

        Can be either on, auth or dry_cloth.
        """
        return OperationMode(self.data["mode"])

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature, if available."""
        if "temp" in self.data and self.data["temp"] is not None:
            return self.data["temp"]
        return None

    @property
    def humidity(self) -> int:
        """Current humidity."""
        return self.data["humidity"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"] == "on"

    @property
    def led(self) -> bool:
        """LED brightness if available."""
        return self.data["led"] == "on"

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"] == "on"

    @property
    def target_humidity(self) -> Optional[int]:
        """Target humiditiy.

        Can be either 40, 50, 60 percent.
        """
        if "auto" in self.data and self.data["auto"] is not None:
            return self.data["auto"]
        return None

    @property
    def fan_speed(self) -> Optional[FanSpeed]:
        """Current fan speed."""
        if "fan_speed" in self.data and self.data["fan_speed"] is not None:
            return FanSpeed(self.data["fan_speed"])
        return None

    @property
    def tank_full(self) -> bool:
        """The remaining amount of water in percent."""
        return self.data["tank_full"] == "on"

    @property
    def compressor_status(self) -> bool:
        """Compressor status."""
        return self.data["compressor_status"] == "on"

    @property
    def defrost_status(self) -> bool:
        """Defrost status."""
        return self.data["defrost_status"] == "on"

    @property
    def fan_st(self) -> int:
        """Fan st."""
        return self.data["fan_st"]

    @property
    def alarm(self) -> str:
        """Alarm."""
        return self.data["alarm"]


class AirDehumidifier(Device):
    """Implementation of Xiaomi Mi Air Dehumidifier."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_DEHUMIDIFIER_V1,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_DEHUMIDIFIER_V1

        self.device_info: DeviceInfo

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "Temperature: {result.temperature} °C\n"
            "Humidity: {result.humidity} %\n"
            "Buzzer: {result.buzzer}\n"
            "LED : {result.led}\n"
            "Child lock: {result.child_lock}\n"
            "Target humidity: {result.target_humidity} %\n"
            "Fan speed: {result.fan_speed}\n"
            "Tank Full: {result.tank_full}\n"
            "Compressor Status: {result.compressor_status}\n"
            "Defrost Status: {result.defrost_status}\n"
            "Fan st: {result.fan_st}\n"
            "Alarm: {result.alarm}\n",
        )
    )
    def status(self) -> AirDehumidifierStatus:
        """Retrieve properties."""

        if self.device_info is None:
            self.device_info = self.info()

        properties = AVAILABLE_PROPERTIES[self.model]

        values = self.get_properties(properties, max_properties=1)

        return AirDehumidifierStatus(
            defaultdict(lambda: None, zip(properties, values)), self.device_info
        )

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        try:
            return self.send("set_mode", [mode.value])
        except DeviceError as error:
            # {'code': -6011, 'message': 'device_poweroff'}
            if error.code == -6011:
                self.on()
                return self.send("set_mode", [mode.value])
            raise

    @command(
        click.argument("fan_speed", type=EnumType(FanSpeed)),
        default_output=format_output("Setting fan level to {fan_speed}"),
    )
    def set_fan_speed(self, fan_speed: FanSpeed):
        """Set the fan speed."""
        try:
            return self.send("set_fan_level", [fan_speed.value])
        except DeviceError as ex:
            if ex.code == -10000:
                raise AirDehumidifierException(
                    "Unable to set fan speed, this can happen if device is turned off."
                ) from ex

            raise

    @command(
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED" if led else "Turning off LED"
        ),
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        if led:
            return self.send("set_led", ["on"])
        else:
            return self.send("set_led", ["off"])

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if buzzer:
            return self.send("set_buzzer", ["on"])
        else:
            return self.send("set_buzzer", ["off"])

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        if lock:
            return self.send("set_child_lock", ["on"])
        else:
            return self.send("set_child_lock", ["off"])

    @command(
        click.argument("humidity", type=int),
        default_output=format_output("Setting target humidity to {humidity}"),
    )
    def set_target_humidity(self, humidity: int):
        """Set the auto target humidity."""
        if humidity not in [40, 50, 60]:
            raise AirDehumidifierException(
                "Invalid auto target humidity: %s" % humidity
            )

        return self.send("set_auto", [humidity])
