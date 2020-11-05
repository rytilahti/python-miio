import enum
import warnings
import logging

import click

from typing import Any, Dict
from .click_common import EnumType, command, format_output
from .exceptions import DeviceException
from .miot_device import MiotDevice

_LOGGER = logging.getLogger(__name__)
_MAPPING = {
        # # Source http://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:curtain:0000A00C:lumi-hagl05:1
        # Curtain
        "motor_control": {"siid": 2, "piid": 2}, # 0 - Pause, 1 - Open, 2 - Close, 3 - auto
        "current_position": {"siid": 2, "piid": 3}, # Range: [0, 100, 1]
        "status": {"siid": 2, "piid": 6}, # 0 - Stopped, 1 - Opening, 2 - Closing
        "target_position": {"siid": 2, "piid": 7}, # Range: [0, 100, 1]
        # curtain_cfg
        "manual_enabled": {"siid": 4, "piid": 1}, #
        "polarity": {"siid": 4, "piid": 2},
        "position_limit": {"siid": 4, "piid": 3},
        "night_tip_light": {"siid": 4, "piid": 4},
        "run_time": {"siid": 4, "piid": 5}, # Range: [0, 255, 1]
        # motor_controller
        "adjust_value": {"siid": 5, "piid": 1}, # Range: [-100, 100, 1]
}

# Model: ZNCLDJ21LM (also known as "Xiaomiyoupin Curtain Controller (Wi-Fi)"
MODEL_CURTAIN_HAGL05 = "lumi.curtain.hagl05"

class MotorControl(enum.Enum):
    Pause = 0
    Open = 1
    Close = 2
    Auto = 3

class Status(enum.Enum):
    Stopped = 0
    Opening = 1
    Closing = 2

class Polarity(enum.Enum):
    Positive = 0
    Reverse = 1

class ManualEnabled(enum.Enum):
    Disable = 0
    Enable = 1

class PosLimit(enum.Enum):
    Unlimit = 0
    Limit = 1

class NightTipLight(enum.Enum):
    Disable = 0
    Enable = 1


class CurtainStatus:
    def __init__(self, data: Dict[str, Any]) -> None:
        """ Response from device
            {'id': 1, 'result': [
                {'did': 'motor_control', 'siid': 2, 'piid': 2, 'code': -4001},
                {'did': 'current_position', 'siid': 2, 'piid': 3, 'code': 0, 'value': 0},
                {'did': 'status', 'siid': 2, 'piid': 6, 'code': 0, 'value': 0},
                {'did': 'target_position', 'siid': 2, 'piid': 7, 'code': 0, 'value': 0},
                {'did': 'manual_enabled', 'siid': 4, 'piid': 1, 'code': 0, 'value': 1},
                {'did': 'polarity', 'siid': 4, 'piid': 2, 'code': 0, 'value': 0},
                {'did': 'position_limit', 'siid': 4, 'piid': 3, 'code': 0, 'value': 0},
                {'did': 'night_tip_light', 'siid': 4, 'piid': 4, 'code': 0, 'value': 1},
                {'did': 'run_time', 'siid': 4, 'piid': 5, 'code': 0, 'value': 0},
                {'did': 'adjust_value', 'siid': 5, 'piid': 1, 'code': -4000}
            ]}
        """
        self.data = data

    @property
    def status(self) -> Status:
        """ Device status """
        return Status(self.data["status"])

    """ curtain_cfg """
    @property
    def manual_enabled(self) -> ManualEnabled:
        """Manual control enable status
        """
        return ManualEnabled(self.data["manual_enabled"])

    @property
    def polarity(self) -> Polarity:
        """Polarity
        """
        return Polarity(self.data["polarity"])

    @property
    def position_limit(self) -> PosLimit:
        """Position limit
        """
        return PosLimit(self.data["position_limit"])

    @property
    def night_tip_light(self) -> NightTipLight:
        """Night tip light status
        """
        return NightTipLight(self.data["night_tip_light"])

    @property
    def run_time(self) -> int:
        """Run time
        """
        return self.data["run_time"]

    @property
    def current_position(self) -> int:
        """Current position
        """
        return self.data["current_position"]

    @property
    def target_position(self) -> int:
        """Target position
        """
        return self.data["target_position"]

    @property
    def adjust_value(self) -> int:
        """ Adjust value
        """
        return self.data["adjust_value"]

    def __repr__(self) -> str:
        s = (
            "<CurtainStatus"
            "status=%s,"
            "polarity=%s,"
            "position_limit=%s,"
            "night_tip_light=%s,"
            "run_time=%s,"
            "current_position=%s,"
            "target_position=%s,"
            "adjust_value=%s>"
            % (
                self.status,
                self.polarity,
                self.position_limit,
                self.night_tip_light,
                self.run_time,
                self.current_position,
                self.target_position,
                self.adjust_value
            )
        )
        return s

class CurtainMiot(MiotDevice):
    """Main class representing the lumi.curtain.hagl05 curtain."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(_MAPPING, ip, token, start_id, debug, lazy_discover)

    @command(
        default_output=format_output(
            "",
            "Device status: {result.status}\n"
            "Manual enabled: {result.manual_enabled}\n"
            "Polarity: {result.polarity}\n"
            "Position limit: {result.position_limit}\n"
            "Enabled night tip light: {result.night_tip_light}\n"
            "Run time: {result.run_time}\n"
            "Current position: {result.current_position}\n"
            "Target position: {result.target_position}\n"
            "Adjust value: {result.adjust_value}\n",
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
        """Set motor control.
        """
        self.set_property("motor_control", motor_control.value)

    @command(
        click.argument("target_position", type=int),
        default_output=format_output("Set target position to {target_position}"),
    )
    def set_target_position(self, target_position: int):
        """Set target position.
        """
        if target_position < 0 or target_position  > 100:
            raise ValueError("Value must be between [0, 100] value, was %s" % target_position)
        self.set_property("target_position", target_position)

    @command(
        click.argument("manual_enabled", type=EnumType(ManualEnabled)),
        default_output=format_output("Set manual control {manual_enabled}"),
    )
    def set_manual_enabled(self, manual_enabled: ManualEnabled):
        """Set manual control of curtain.
        """
        self.set_property("manual_enabled", manual_enabled.value)

    @command(
        click.argument("polarity", type=EnumType(Polarity)),
        default_output=format_output("Set polarity to {polarity}"),
    )
    def set_polarity(self, polarity: Polarity):
        """Set polarity of the motor.
        """
        self.set_property("polarity", polarity.value)

    @command(
        click.argument("pos_limit", type=EnumType(PosLimit)),
        default_output=format_output("Set position limit to {pos_limit}"),
    )
    def set_position_limit(self, pos_limit: PosLimit):
        """Set position limit parameter.
        """
        self.set_property("position_limit", pos_limit.value)

    @command(
        click.argument("night_tip_light", type=EnumType(NightTipLight)),
        default_output=format_output("Setting night tip light {night_tip_light"),
    )
    def set_night_tip_light(self, night_tip_light: NightTipLight):
        """Set night tip light.
        """
        self.set_property("night_tip_light", night_tip_light.value)

    """ motor_controller """
    @command(
        click.argument("adjust_value", type=int),
        default_output=format_output("Set adjust value to {adjust_value}"),
    )
    def set_adjust_value(self, adjust_value: int):
        """Set adjust value.
        """
        if adjust_value < -100 or adjust_value > 100:
            raise ValueError("Value must be between [-100, 100] value, was %s" % adjust_value)
        self.set_property("adjust_value", adjust_value)

