import enum
import logging
import random
from typing import Any

from miio import Device, DeviceStatus
from miio.click_common import command, format_output
from miio.devicestatus import sensor, setting

_LOGGER = logging.getLogger(__name__)

MODEL_ACPARTNER_MCN02 = "lumi.acpartner.mcn02"


class OperationMode(enum.Enum):
    Cool = "cool"
    Heat = "heat"
    Auto = "auto"
    Ventilate = "wind"
    Dehumidify = "dry"


class FanSpeed(enum.Enum):
    Auto = "auto_fan"
    Low = "small_fan"
    Medium = "medium_fan"
    High = "large_fan"


class SwingMode(enum.Enum):
    On = "on"
    Off = "off"


class AirConditioningCompanionStatus(DeviceStatus):
    """Container for status reports of the Xiaomi AC Companion."""

    def __init__(self, data):
        """Status constructor.

        Example response (lumi.acpartner.mcn02):
        * ['power', 'mode', 'tar_temp', 'fan_level', 'ver_swing', 'load_power']
        * ['on',    'dry',   16,        'small_fan', 'off',        84.0]
        """
        self.data = data

    @property
    @sensor("Load Power", unit="W")
    def load_power(self) -> int:
        """Current power load of the air conditioner."""
        return int(self.data[-1])

    @property
    @sensor("Power")
    def power(self) -> str:
        """Current power state."""
        return self.data[0]

    @property
    def is_on(self) -> bool:
        """True if the device is turned on."""
        return self.power == "on"

    @property
    @setting("Mode", setter_name="send_command", choices=OperationMode)
    def mode(self) -> OperationMode | None:
        """Current operation mode."""
        try:
            mode = self.data[1]
            return OperationMode(mode)
        except TypeError:
            return None

    @property
    @setting(
        "Target Temperature",
        setter_name="send_command",
        unit="°C",
    )
    def target_temperature(self) -> int | None:
        """Target temperature."""
        try:
            return self.data[2]
        except TypeError:
            return None

    @property
    @setting("Fan Speed", setter_name="send_command", choices=FanSpeed)
    def fan_speed(self) -> FanSpeed | None:
        """Current fan speed."""
        try:
            speed = self.data[3]
            return FanSpeed(speed)
        except TypeError:
            return None

    @property
    @setting("Swing Mode", setter_name="send_command", choices=SwingMode)
    def swing_mode(self) -> SwingMode | None:
        """Current swing mode."""
        try:
            mode = self.data[4]
            return SwingMode(mode)
        except TypeError:
            return None


class AirConditioningCompanionMcn02(Device):
    """Main class representing Xiaomi Air Conditioning Companion V1 and V2."""

    _supported_models = [MODEL_ACPARTNER_MCN02]

    def __init__(
        self,
        ip: str | None = None,
        token: str | None = None,
        start_id: int | None = None,
        debug: int = 0,
        lazy_discover: bool = True,
        timeout: int | None = None,
        *,
        model: str = MODEL_ACPARTNER_MCN02,
    ) -> None:
        if start_id is None:
            start_id = random.randint(0, 999)  # noqa: S311
        super().__init__(
            ip, token, start_id, debug, lazy_discover, timeout=timeout, model=model
        )

        if model != MODEL_ACPARTNER_MCN02:
            _LOGGER.error(
                "Device model %s unsupported. Please use AirConditioningCompanion",
                model,
            )

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Load power: {result.load_power}\n"
            "Target temperature: {result.target_temperature} °C\n"
            "Swing mode: {result.swing_mode}\n"
            "Fan speed: {result.fan_speed}\n"
            "Mode: {result.mode}\n",
        )
    )
    def status(self) -> AirConditioningCompanionStatus:
        """Return device status."""
        data = self.send(
            "get_prop",
            ["power", "mode", "tar_temp", "fan_level", "ver_swing", "load_power"],
        )
        return AirConditioningCompanionStatus(data)

    @command(default_output=format_output("Powering the air condition on"))
    def on(self):
        """Turn the air condition on by infrared."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering the air condition off"))
    def off(self):
        """Turn the air condition off by infrared."""
        return self.send("set_power", ["off"])

    @command(
        default_output=format_output("Sending a command to the air conditioner"),
    )
    def send_command(self, command: str, parameters: Any | None = None) -> Any:
        """Send a command to the air conditioner.

        :param str command: Command to execute
        """
        return self.send(command, parameters)
