import logging
import enum
from typing import Any, Dict, Optional
from collections import defaultdict
from .device import Device, DeviceException


class AirConditioningCompanionStatus:
    """Container for status reports of the Xiaomi AC Companion."""

    def __init__(self, data):
        self.data = data

    @property
    def ac_power(self):
        """Current power state of the air conditioner."""
        return self.data[2]

    @property
    def ac_model(self):
        """Model of the air conditioner."""
        return str(self.data[0][0:2] + self.data[0][8:16])

    @property
    def power(self):
        """Current power state."""
        return self.data[1][2:3]

    # FIXME: Introduce a container class
    @property
    def wind_force(self):
        """Current wind force."""
        if self.data[1][4:5] == '0':
            return 'low'
        elif self.data[1][4:5] == '1':
            return 'medium'
        elif self.data[1][4:5] == '2':
            return 'high'
        else:
            return 'auto'

    @property
    def sweep(self) -> bool:
        """True if sweep is turned on."""
        return self.data[1][5:6] == '0'

    @property
    def temp(self) -> int:
        """Current temperature."""
        return int(self.data[1][6:8], 16)

    # FIXME: Merge both properties
    @property
    def mode(self):
        """Current mode."""
        return self.data[1][3:4]

    # FIXME: Introduce a container class
    @property
    def operation(self):
        if self.data[1][2:3] == '0':
            return 'off'
        else:
            if self.data[1][3:4] == '0':
                return 'heat'
            elif self.data[1][3:4] == '1':
                return 'cool'
            else:
                return 'auto'


class AirConditioningCompanion(Device):
    """Main class representing Xiaomi Air Conditioning Companion."""

    def status(self) -> AirConditioningCompanionStatus:
        """Return device status."""
        status = self.send("get_model_and_state", [])
        return AirConditioningCompanionStatus(status)

    def learn(self):
        """Learn an infrared command."""
        return self.send("start_ir_learn", [30])

    def learn_result(self):
        """Read the learned command."""
        return self.send("get_ir_learn_result", [])

    def learn_stop(self):
        """Stop learning of a infrared command."""
        return self.send("end_ir_learn", [30])

    def send_ir_code(self, command: str):
        """Play a captured command.

        :param str command: Command to execute"""
        return self.send("send_ir_code", [str(command)])

    def send_command(self, command: str):
        """Send a command to the air conditioner.

        :param str command: Command to execute"""
        return self.send("send_cmd", [str(command)])
