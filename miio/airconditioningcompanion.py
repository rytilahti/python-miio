from .device import Device
import enum
from typing import Optional


class OperationMode(enum.Enum):
    Heating = 0
    Cooling = 1
    Auto = 2


class FanSpeed(enum.Enum):
    Low = 0
    Medium = 1
    High = 2
    Auto = 3


STORAGE_SLOT_ID = 30


class AirConditioningCompanionStatus:
    """Container for status reports of the Xiaomi AC Companion."""

    def __init__(self, data):
        # Device model: lumi.acpartner.v2
        #
        # Response of "get_model_and_state":
        # ['010500978022222102', '010201190280222221', '2']
        self.data = data

    @property
    def air_condition_power(self) -> str:
        """Current power state of the air conditioner."""
        return str(self.data[2])

    @property
    def air_condition_model(self) -> str:
        """Model of the air conditioner."""
        return str(self.data[0][0:2] + self.data[0][8:16])

    @property
    def power(self) -> str:
        """Current power state."""
        return 'on' if (self.data[1][2:3] == '1') else 'off'

    @property
    def is_on(self) -> bool:
        """True if the device is turned on."""
        return self.power == 'on'

    @property
    def temperature(self) -> int:
        """Current temperature."""
        return int(self.data[1][6:8], 16)

    @property
    def swing_mode(self) -> bool:
        """True if swing mode is enabled."""
        return self.data[1][5:6] == '0'

    @property
    def fan_speed(self) -> Optional[FanSpeed]:
        """Current fan speed."""
        speed = int(self.data[1][4:5])
        if speed is not None:
            return FanSpeed(speed)

        return None

    @property
    def mode(self) -> Optional[OperationMode]:
        """Current operation mode."""
        mode = int(self.data[1][3:4])
        if mode is not None:
            return OperationMode(mode)

        return None


class AirConditioningCompanion(Device):
    """Main class representing Xiaomi Air Conditioning Companion."""

    def status(self) -> AirConditioningCompanionStatus:
        """Return device status."""
        status = self.send("get_model_and_state", [])
        return AirConditioningCompanionStatus(status)

    def learn(self):
        """Learn an infrared command."""
        return self.send("start_ir_learn", [STORAGE_SLOT_ID])

    def learn_result(self):
        """Read the learned command."""
        return self.send("get_ir_learn_result", [])

    def learn_stop(self):
        """Stop learning of a infrared command."""
        return self.send("end_ir_learn", [STORAGE_SLOT_ID])

    def send_ir_code(self, command: str):
        """Play a captured command.

        :param str command: Command to execute"""
        return self.send("send_ir_code", [str(command)])

    def send_command(self, command: str):
        """Send a command to the air conditioner.

        :param str command: Command to execute"""
        return self.send("send_cmd", [str(command)])
