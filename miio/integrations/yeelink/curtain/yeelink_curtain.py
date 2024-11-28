import enum
import logging
from typing import Any, Dict

import click

from miio import DeviceStatus, MiotDevice
from miio.click_common import EnumType, command, format_output

_LOGGER = logging.getLogger(__name__)


# Model: YLCDJ-0007 (also known as "Yeelight Automatic Curtain Opener"
MODEL_CURTAIN_CTMT2 = "yeelink.curtain.ctmt2"

_MAPPINGS = {
    MODEL_CURTAIN_CTMT2: {
        # # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:curtain:0000A00C:yeelink-ctmt2:1
        # Curtain
        "motor_control": {
            "siid": 2,
            "piid": 2,
        },  # 0 - Pause, 1 - Open, 2 - Close
        "current_position": {"siid": 2, "piid": 4},  # Range: [0, 100, 1]
        "target_position": {"siid": 2, "piid": 5},  # Range: [0, 100, 1]
    }
}


class MotorControl(enum.Enum):
    Pause = 0
    Open = 1
    Close = 2


class CurtainStatus(DeviceStatus):
    def __init__(self, data: Dict[str, Any]) -> None:
        """Response from device.

        {'id': 1, 'result': [
            {'did': 'current_position', 'siid': 2, 'piid': 4, 'code': 0, 'value': 0},
            {'did': 'target_position', 'siid': 2, 'piid': 5, 'code': 0, 'value': 0},
        ]}
        """
        self.data = data

    @property
    def current_position(self) -> int:
        """Current curtain position."""
        return self.data["current_position"]

    @property
    def target_position(self) -> int:
        """Target curtain position."""
        return self.data["target_position"]


class CurtainYeelight(MiotDevice):
    """Main class representing the yeelink.curtain.ctmt2."""

    _mappings = _MAPPINGS

    @command(
        default_output=format_output(
            "",
            "Current position: {result.current_position}\n"
            "Target position: {result.target_position}\n"
        )
    )
    def status(self) -> CurtainStatus:
        """Retrieve properties."""

        return CurtainStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(
        click.argument("motor_control", type=EnumType(MotorControl)),
        default_output=format_output("Set motor control to {motor_control}"),
    )
    def set_motor_control(self, motor_control: MotorControl):
        """Set motor control."""
        return self.set_property("motor_control", motor_control.value)

    @command(
        click.argument("target_position", type=int),
        default_output=format_output("Set target position to {target_position}"),
    )
    def set_target_position(self, target_position: int):
        """Set target position."""
        if target_position < 0 or target_position > 100:
            raise ValueError(
                "Value must be between [0, 100] value, was %s" % target_position
            )
        return self.set_property("target_position", target_position)

