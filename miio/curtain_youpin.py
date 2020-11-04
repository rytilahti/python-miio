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
        "pos_limit": {"siid": 4, "piid": 3},
        "en_night_tip_light": {"siid": 4, "piid": 4},
        "run_time": {"siid": 4, "piid": 5}, # Range: [0, 255, 1]
        # motor_controller
        "adjust_value": {"siid": 5, "piid": 1}, # Range: [-100, 100, 1]
}

# Model: ZNCLDJ21LM (also known as "Xiaomiyoupin Curtain Controller (Wi-Fi)"
MODEL_CURTAIN_HAGL05 = "lumi.curtain.hagl05"

class CurtainMiotException(DeviceException):
    pass

class MotorControl(enum.Enum):
    Pause = 0
    Open = 1
    Close = 2
    auto = 3

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
                {'did': 'pos_limit', 'siid': 4, 'piid': 3, 'code': 0, 'value': 0},
                {'did': 'en_night_tip_light', 'siid': 4, 'piid': 4, 'code': 0, 'value': 1},
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
        """
        Values: ManualEnabled
        """
        return ManualEnabled(self.data["manual_enabled"])

    @property
    def polarity(self) -> Polarity:
        """
        Values: Polarity
        """
        return Polarity(self.data["polarity"])

    @property
    def pos_limit(self) -> PosLimit:
        """
        Values: PosLimit
        """
        return PosLimit(self.data["pos_limit"])

    @property
    def en_night_tip_light(self) -> NightTipLight:
        """
        Values: NightTipLight
        """
        return NightTipLight(self.data["en_night_tip_light"])

    @property
    def run_time(self) -> int:
        """
        Range: [0, 255, 1]
        """
        return self.data["run_time"]

    @property
    def current_position(self) -> int:
        """Current Position
        Range: [0, 100, 1]
        """
        return self.data["current_position"]

    @property
    def target_position(self) -> int:
        """Target Position
        Range: [0, 100, 1]
        """
        return self.data["target_position"]

    @property
    def adjust_value(self) -> int:
        """ Adjust value
        Range: [-100, 100, 1]
        """
        return self.data["adjust_value"]

    def __repr__(self) -> str:
        s = (
            "<CurtainStatus"
            "status=%s,"
            "polarity=%s,"
            "pos_limit=%s,"
            "en_night_tip_light=%s,"
            "run_time=%s,"
            "current_position=%s,"
            "target_position=%s,"
            "adjust_value=%s>"
            % (
                self.status,
                self.polarity,
                self.pos_limit,
                self.en_night_tip_light,
                self.run_time,
                self.current_position,
                self.target_position,
                self.adjust_value
            )
        )
        return s

class CurtainMiot(MiotDevice):
    """Main class representing the curtain which uses MIoT protocol."""

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
            "Position limit: {result.pos_limit}\n"
            "Enabled night tip light: {result.en_night_tip_light}\n"
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
        default_output=format_output(""),
    )
    def set_Motor_Control(self, motor_control: MotorControl):
        """Motor Control
        Values: MotorControl
        """
        try:
            self.set_property("motor_control", motor_control.value)
        except DeviceError as error:
            raise

    @command(
        click.argument("target-position", type=int),
        default_output=format_output(""),
    )
    def set_Target_Position(self, var: int):
        """Target Position
        Range: [0, 100, 1]
        """
        self.set_property("target_position", var)

    @command(
        click.argument("manual_enabled", type=EnumType(ManualEnabled)),
        default_output=format_output(""),
    )
    def set_manual_enabled(self, manual_enabled: ManualEnabled):
        """
        Values: ManualEnabled
        """
        try:
            self.set_property("manual_enabled", manual_enabled.value)
        except DeviceError as error:
            raise

    @command(
        click.argument("polarity", type=EnumType(Polarity)),
        default_output=format_output(""),
    )
    def set_polarity(self, polarity: Polarity):
        """
        Values: Polarity
        """
        try:
            self.set_property("polarity", polarity.value)
        except DeviceError as error:
            raise

    @command(
        click.argument("pos_limit", type=EnumType(PosLimit)),
        default_output=format_output(""),
    )
    def set_pos_limit(self, pos_limit: PosLimit):
        """
        Values: PosLimit
        """
        try:
            self.set_property("pos_limit", pos_limit.value)
        except DeviceError as error:
            raise

    @command(
        click.argument("en-night-tip-light", type=EnumType(NightTipLight)),
        default_output=format_output(""),
    )
    def set_en_night_tip_light(self, en_night_tip_light: NightTipLight):
        """
        Values: NightTipLight 
        """
        try:
            self.set_property("en_night_tip_light", en_night_tip_light.value)
        except DeviceError as error:
            raise

    """ motor_controller """
    @command(
        click.argument("adjust", type=int),
        default_output=format_output("Set adjust value"),
    )
    def set_adjust_value(self, var: int):
        """
        Range: [-100, 100, 1]
        """
        self.set_property("adjust_value", var)

